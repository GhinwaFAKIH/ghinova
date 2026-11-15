"""Production ASGI API. Uvicorn proxy headers must remain disabled."""
import asyncio
import hashlib
import hmac
import ipaddress
import json
import logging
import math
import os
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
try:
    from . import server
    from .controls import Ledger, BudgetExceeded
except ImportError:
    import server
    from controls import Ledger, BudgetExceeded

LOG=logging.getLogger('ghinova')
logging.basicConfig(level=logging.INFO,format='%(message)s')
for name in ('httpx','httpcore'):logging.getLogger(name).setLevel(logging.WARNING)

@dataclass
class Settings:
    environment:str='development'
    provider:str='ollama'
    model:str='llama3.2:latest'
    model_url:str='http://127.0.0.1:11434/api/chat'
    api_key:str=''
    origins:tuple=('http://127.0.0.1:8765',)
    db:str='backend/data/usage.sqlite3'
    daily:int=2_000_000
    monthly:int=20_000_000
    per_client:int=10
    global_rate:int=60
    rate_mode:str='direct'
    salt:str='local-development-only'
    trusted_proxies:tuple=()
    timeout:float=45
    max_input:int=24000
    max_output:int=600
    # Conservative rates above currently published Standard GPT-6 Luna pricing.
    input_rate:Decimal=Decimal('0.25')
    output_rate:Decimal=Decimal('1.0')
    @classmethod
    def env(cls):
        return cls(environment=os.getenv('APP_ENV','development'),provider=os.getenv('MODEL_PROVIDER','ollama'),model=os.getenv('MODEL_NAME','llama3.2:latest'),model_url=os.getenv('MODEL_URL','http://127.0.0.1:11434/api/chat'),api_key=os.getenv('MODEL_API_KEY',''),origins=tuple(x.strip() for x in os.getenv('ALLOWED_ORIGINS','http://127.0.0.1:8765').split(',') if x.strip()),db=os.getenv('BUDGET_DB','backend/data/usage.sqlite3'),daily=int(Decimal(os.getenv('DAILY_BUDGET_USD','2'))*1_000_000),monthly=int(Decimal(os.getenv('MONTHLY_BUDGET_USD','20'))*1_000_000),per_client=int(os.getenv('RATE_LIMIT','10')),global_rate=int(os.getenv('GLOBAL_RATE_LIMIT','60')),rate_mode=os.getenv('CLIENT_RATE_MODE','direct'),salt=os.getenv('RATE_HASH_KEY','local-development-only'),trusted_proxies=tuple(x for x in os.getenv('TRUSTED_PROXY_CIDRS','').split(',') if x),timeout=float(os.getenv('MODEL_TIMEOUT','45')))
    def validate(self):
        u=urlsplit(self.model_url)
        if u.username or u.password or u.query or u.fragment:raise ValueError('Invalid model endpoint')
        if self.provider=='ollama':
            if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost','::1'):raise ValueError('Ollama must be loopback-only')
        elif self.provider=='openai':
            if self.model_url!='https://api.openai.com/v1/chat/completions' or not self.api_key or self.model!='gpt-6-luna':raise ValueError('Configure the supported OpenAI endpoint, model and server secret')
        else:raise ValueError('Unsupported model provider')
        if not self.origins:raise ValueError('Explicit origins required')
        for origin in self.origins:
            u=urlsplit(origin)
            if u.scheme not in ('http','https') or not u.hostname or u.path or u.query or u.fragment or u.username or '*' in origin:raise ValueError('Invalid origin')
            if self.environment=='production' and u.scheme!='https':raise ValueError('Production origins require HTTPS')
        if self.environment=='production':
            if self.provider!='openai':raise ValueError('Production profile uses hosted OpenAI, never laptop Ollama')
            if not Path(self.db).is_absolute() or len(self.salt)<32:raise ValueError('Persistent absolute budget path and strong rate hash key required')
        if self.rate_mode not in ('direct','global','trusted-proxy'):raise ValueError('Invalid rate mode')
        if self.rate_mode=='trusted-proxy' and not self.trusted_proxies:raise ValueError('Explicit trusted proxy CIDRs required')
        for cidr in self.trusted_proxies:ipaddress.ip_network(cidr)
        if min(self.daily,self.monthly,self.per_client,self.global_rate,self.max_input,self.max_output,self.timeout)<=0:raise ValueError('Limits must be positive')

OUTPUT_SCHEMA={'type':'object','additionalProperties':False,'required':['intent','resource_ids','explanation'],'properties':{'intent':{'type':'string','enum':['recommend','explain','contact','unknown']},'resource_ids':{'type':'array','maxItems':3,'items':{'type':'string'}},'explanation':{'type':'string'}}}

class ProviderError(Exception):
    pass

class Adapter:
    def __init__(self,settings,client):self.s=settings;self.client=client
    def prepare(self,message,language,history):
        messages=server.messages_for(message,language,history)
        # UTF-8 bytes conservatively upper-bound byte-token text; reserve framing overhead.
        bound=sum(len(m['content'].encode('utf-8'))+128 for m in messages)+256
        if bound>self.s.max_input:raise ValueError('Context too long')
        cost=int((Decimal(bound)*self.s.input_rate+Decimal(self.s.max_output)*self.s.output_rate).to_integral_value(rounding=ROUND_CEILING))
        if self.s.provider=='openai':
            messages[0]['role']='developer'
            payload={'model':self.s.model,'messages':messages,'reasoning_effort':'none','max_completion_tokens':self.s.max_output,'response_format':{'type':'json_schema','json_schema':{'name':'ghinova_answer','strict':True,'schema':OUTPUT_SCHEMA}},'store':False}
        else:payload={'model':self.s.model,'messages':messages,'stream':False,'format':OUTPUT_SCHEMA,'options':{'temperature':0,'num_predict':self.s.max_output,'num_ctx':8192}}
        return payload,cost
    async def call(self,payload):
        headers={'Content-Type':'application/json'}
        if self.s.provider=='openai':headers['Authorization']='Bearer '+self.s.api_key
        async with self.client.stream('POST',self.s.model_url,json=payload,headers=headers) as response:
            if response.status_code!=200:raise ProviderError('upstream_status')
            chunks=bytearray()
            async for chunk in response.aiter_bytes():
                chunks.extend(chunk)
                if len(chunks)>65536:raise ProviderError('upstream_size')
        try:
            raw=json.loads(chunks)
            if self.s.provider=='openai':
                choice=raw['choices'][0]
                if choice['finish_reason']!='stop' or choice['message'].get('refusal'):raise ValueError()
                content=choice['message']['content'];usage=raw.get('usage',{})
            else:
                if raw.get('done_reason')=='length' or not raw.get('done'):raise ValueError()
                content=raw['message']['content'];usage={}
            value=json.loads(content)
            if not isinstance(value,dict) or set(value)!={'intent','resource_ids','explanation'}:raise ValueError()
            if value['intent'] not in ('recommend','explain','contact','unknown'):raise ValueError()
            if not isinstance(value['resource_ids'],list) or len(value['resource_ids'])>3 or not all(isinstance(x,str) for x in value['resource_ids']):raise ValueError()
            if not isinstance(value['explanation'],str) or len(value['explanation'])>1600:raise ValueError()
            safe_usage={k:v for k,v in usage.items() if k in ('prompt_tokens','completion_tokens') and type(v) is int and 0<=v<=1_000_000}
            return value,safe_usage
        except (ValueError,KeyError,TypeError,IndexError):raise ProviderError('upstream_schema') from None

def identity(request,s):
    if s.rate_mode=='global':return None
    peer=request.client.host if request.client else 'unknown'
    if s.rate_mode=='trusted-proxy':
        nets=[ipaddress.ip_network(x) for x in s.trusted_proxies]
        def trusted(ip):
            try:return any(ipaddress.ip_address(ip) in n for n in nets)
            except ValueError:return False
        if trusted(peer):
            chain=[x.strip() for x in request.headers.get('x-forwarded-for','').split(',') if x.strip()]+[peer]
            while len(chain)>1 and trusted(chain[-1]):chain.pop()
            peer=chain[-1]
    return hmac.new(s.salt.encode(),peer.encode(),hashlib.sha256).hexdigest()

def create_app(settings=None,transport=None):
    s=settings or Settings.env()
    @asynccontextmanager
    async def lifespan(app):
        s.validate()
        app.state.ledger=Ledger(s.db)
        app.state.client=httpx.AsyncClient(transport=transport,timeout=s.timeout,follow_redirects=False,trust_env=False)
        app.state.adapter=Adapter(s,app.state.client)
        app.state.active=0
        yield
        await app.state.client.aclose()
    app=FastAPI(lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url=None)
    def reply(status,data,origin='',request_id='',retry=None):
        headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Vary':'Origin','X-Request-ID':request_id}
        if origin in s.origins:headers['Access-Control-Allow-Origin']=origin
        if retry:headers['Retry-After']=str(retry)
        return JSONResponse(data,status_code=status,headers=headers)
    @app.get('/health')
    async def health():return {'status':'ok','model_ready':'not checked'}
    @app.get('/ready')
    async def ready():
        try:await asyncio.to_thread(app.state.ledger.ready)
        except Exception:return reply(503,{'status':'unavailable'})
        return {'status':'ready','model_ready':'not checked'}
    @app.options('/api/chat')
    async def options(request:Request):
        origin=request.headers.get('origin','')
        if origin not in s.origins or request.headers.get('access-control-request-method','POST')!='POST':return reply(403,{'error':'Origin or method not allowed'})
        response=reply(204,None,origin)
        response.headers['Access-Control-Allow-Methods']='POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers']='Content-Type'
        return response
    @app.post('/api/chat')
    async def chat(request:Request):
        rid=uuid.uuid4().hex;start=time.monotonic();origin=request.headers.get('origin','');lang='en';status=503;category='internal';reserved=0;usage={}
        def respond(code,data,kind,retry=None):
            nonlocal status,category
            status=code;category=kind
            return reply(code,data,origin,rid,retry)
        try:
            if origin not in s.origins:return respond(403,{'error':'Origin not allowed'},'origin')
            allowed=await asyncio.to_thread(app.state.ledger.rate,identity(request,s),s.per_client,s.global_rate,time.time())
            if not allowed:return respond(429,{'error':'Too many requests'},'rate',60)
            if request.headers.get('content-type','').split(';')[0]!='application/json':return respond(415,{'error':'Use application/json'},'content_type')
            body=bytearray()
            try:
                async with asyncio.timeout(10):
                    async for chunk in request.stream():
                        body.extend(chunk)
                        if len(body)>8192:return respond(413,{'error':'Request too large'},'size')
                message,lang,history=server.validate_request(json.loads(body))
                payload,cost=app.state.adapter.prepare(message,lang,history)
            except (ValueError,UnicodeError,TimeoutError):return respond(400,{'error':'Invalid request or excessive context'},'input')
            if app.state.active>=2:return respond(503,server.fallback(lang),'busy',5)
            app.state.active+=1
            try:
                await asyncio.to_thread(app.state.ledger.reserve,cost,s.daily,s.monthly)
                reserved=cost
                async with asyncio.timeout(s.timeout):value,usage=await app.state.adapter.call(payload)
                return respond(200,server.render(value,lang,message),'ok')
            finally:app.state.active-=1
        except BudgetExceeded:
            data=server.fallback(lang);data['code']='budget_exhausted'
            return respond(503,data,'budget')
        except (httpx.HTTPError,TimeoutError,ProviderError):return respond(503,server.fallback(lang),'provider')
        except Exception:return respond(503,server.fallback(lang),'internal')
        finally:
            # Fixed allowlist only. Never interpolate user input, exception strings or keys.
            LOG.info(json.dumps({'event':'chat','request_id':rid,'status':status,'category':category,'duration_ms':round((time.monotonic()-start)*1000),'reserved_micro_usd':reserved,**usage}))
    return app

app=create_app()
