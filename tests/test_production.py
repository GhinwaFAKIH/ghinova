import asyncio
import concurrent.futures
import json
import logging
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
import httpx
import yaml
from fastapi.testclient import TestClient
from backend.app import Settings, create_app, Adapter, ProviderError
from backend.controls import Ledger, BudgetExceeded
from scripts.build_static import build

VALUE={'intent':'recommend','resource_ids':['pdf-chatbot'],'explanation':''}
def response(request):
    return httpx.Response(200,json={'choices':[{'finish_reason':'stop','message':{'content':json.dumps(VALUE)}}],'usage':{'prompt_tokens':100,'completion_tokens':30}})
class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.s=Settings(provider='openai',model='gpt-6-luna',model_url='https://api.openai.com/v1/chat/completions',api_key='fake-test-secret',db=self.tmp.name+'/ledger.db')
    def client(self,handler=response):return TestClient(create_app(self.s,httpx.MockTransport(handler)))
    def post(self,c,data=None,**kwargs):return c.post('/api/chat',json=data or {'message':'What does the PDF chatbot cost?','language':'en'},headers={'Origin':self.s.origins[0],**kwargs})
    def test_hosted_wire_contract_and_grounded_render(self):
        def inspect(r):
            self.assertEqual(str(r.url),self.s.model_url);self.assertEqual(r.headers['authorization'],'Bearer fake-test-secret')
            p=json.loads(r.content);self.assertEqual(p['reasoning_effort'],'none');self.assertEqual(p['max_completion_tokens'],600);self.assertFalse(p['store']);self.assertNotIn('max_tokens',p);self.assertNotIn('temperature',p);self.assertEqual(p['messages'][0]['role'],'developer');self.assertTrue(p['response_format']['json_schema']['strict']);return response(r)
        with self.client(inspect) as c:
            r=self.post(c);self.assertEqual(r.status_code,200);self.assertEqual(r.json()['resources'][0]['price'],'€5')
    def test_bad_upstream_variants_fail_safely(self):
        cases=[httpx.Response(401,text='SECRET credentials'),httpx.Response(429),httpx.Response(302,headers={'Location':'https://evil.test'}),httpx.Response(200,json={'choices':[{'finish_reason':'length','message':{'content':'{}'}}]}),httpx.Response(200,json={'choices':[{'finish_reason':'stop','message':{'refusal':'no','content':'{}'}}]}),httpx.Response(200,text='not json'),httpx.Response(200,content=b'x'*65537)]
        for result in cases:
            with self.subTest(result=result.status_code),self.client(lambda r:result) as c:
                r=self.post(c,{'message':'Bonjour','language':'fr'});self.assertEqual(r.status_code,503);self.assertIn('indisponible',r.json()['answer']);self.assertNotIn('SECRET',r.text)
    def test_timeout_keeps_reservation(self):
        def fail(r):raise httpx.ReadTimeout('private upstream data')
        with self.client(fail) as c:self.assertEqual(self.post(c).status_code,503)
        with Ledger(self.s.db).connect() as db:self.assertGreater(db.execute('SELECT sum(amount) FROM reservations').fetchone()[0],0)
    def test_cors(self):
        with self.client() as c:
            for headers in ({},{'Origin':'https://evil.test'},{'Origin':'http://127.0.0.1:8765.evil.test'}):
                r=c.post('/api/chat',json={'message':'hello'},headers=headers);self.assertEqual(r.status_code,403);self.assertNotIn('access-control-allow-origin',r.headers)
            r=c.options('/api/chat',headers={'Origin':self.s.origins[0],'Access-Control-Request-Method':'POST'});self.assertEqual(r.status_code,204);self.assertEqual(r.headers['access-control-allow-origin'],self.s.origins[0])
    def test_rate_persists_restart_and_ignores_spoofed_headers(self):
        self.s.per_client=1
        with self.client() as c:self.assertEqual(self.post(c).status_code,200)
        with self.client() as c:
            r=self.post(c,**{'X-Forwarded-For':'8.8.8.8'});self.assertEqual(r.status_code,429);self.assertEqual(r.headers['retry-after'],'60')
    def test_global_mode(self):
        self.s.rate_mode='global';self.s.global_rate=1
        with self.client() as c:self.assertEqual(self.post(c).status_code,200);self.assertEqual(self.post(c).status_code,429)
    def test_budget_fail_closed(self):
        self.s.daily=1
        with self.client() as c:
            r=self.post(c);self.assertEqual(r.status_code,503);self.assertEqual(r.json()['code'],'budget_exhausted')
    def test_ledger_unavailable(self):
        with self.client() as c,patch.object(Ledger,'rate',side_effect=OSError('private path')):
            self.assertEqual(self.post(c).status_code,503)
    def test_safe_logs(self):
        with self.client() as c,self.assertLogs('ghinova',level='INFO') as captured:
            self.post(c,{'message':'UNIQUE_PRIVATE_PROMPT','language':'en'})
        text=' '.join(captured.output)
        for secret in ['UNIQUE_PRIVATE_PROMPT','fake-test-secret','127.0.0.1','Authorization']:self.assertNotIn(secret,text)
        self.assertIn('reserved_micro_usd',text)
    def test_input_limits(self):
        with self.client() as c:
            for data in [{'message':'x'*801},{'message':'x','history':[{'role':'system','content':'bad'}]},{'message':'x','language':'de'}]:self.assertEqual(self.post(c,data).status_code,400)
            self.assertEqual(self.post(c,{'message':'x'*9000}).status_code,413)
    def test_production_config(self):
        for updates in [{'provider':'ollama','model_url':'http://public.test/api/chat'},{'environment':'production'},{'origins':('*',)},{'rate_mode':'trusted-proxy'}]:
            s=Settings(**updates)
            with self.assertRaises(ValueError):s.validate()
    def test_ready_and_no_docs(self):
        with self.client() as c:self.assertEqual(c.get('/ready').status_code,200);self.assertEqual(c.get('/docs').status_code,404)

class LedgerTests(unittest.TestCase):
    def test_atomic_budget_and_restart(self):
        with tempfile.TemporaryDirectory() as t:
            path=t+'/ledger';ledger=Ledger(path)
            def reserve(_):
                try:ledger.reserve(100,500,500);return True
                except BudgetExceeded:return False
            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:self.assertEqual(sum(pool.map(reserve,range(20))),5)
            with self.assertRaises(BudgetExceeded):Ledger(path).reserve(1,500,500)
    def test_utc_daily_monthly_rollover(self):
        with tempfile.TemporaryDirectory() as t:
            l=Ledger(t+'/ledger');l.reserve(100,100,150,datetime(2026,1,1,tzinfo=timezone.utc))
            with self.assertRaises(BudgetExceeded):l.reserve(100,100,150,datetime(2026,1,2,tzinfo=timezone.utc))
            l.reserve(100,100,150,datetime(2026,2,1,tzinfo=timezone.utc))

class BuildTests(unittest.TestCase):
    def test_build_isolated_preserves_sources_and_seo(self):
        root=Path(__file__).resolve().parents[1]
        source=(root/'assistant-config.js').read_bytes()
        with tempfile.TemporaryDirectory() as t:
            d=build(Path(t)/'public','https://api.example.com/api/chat')
            for name in ('index.html','shop.html','sitemap.xml'):self.assertEqual((d/name).read_bytes(),(root/name).read_bytes())
            self.assertEqual((root/'assistant-config.js').read_bytes(),source)
            self.assertIn('https://api.example.com/api/chat',(d/'assistant-config.js').read_text())
            self.assertFalse((d/'backend').exists());self.assertFalse((d/'.env').exists())
    def test_invalid_api_url(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):build(Path(t)/'public','http://evil.test/api/chat')
    def test_manual_render_blueprint(self):
        config=yaml.safe_load(Path('render.yaml').read_text())
        self.assertEqual(len(config['services']),2)
        for s in config['services']:self.assertEqual(s['autoDeployTrigger'],'off')
        self.assertEqual(config['services'][1]['disk']['mountPath'],'/var/data')
