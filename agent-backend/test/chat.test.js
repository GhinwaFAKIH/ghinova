import test from 'node:test';
import assert from 'node:assert/strict';
import handler,{validateMessages,prepareInquiry} from '../api/chat.js';
function response(){return {headers:{},setHeader(k,v){this.headers[k]=v},status(n){this.code=n;return this},json(v){this.body=v;return this},end(){return this}}}
test('rejects forged roles, huge history and empty input',()=>{
 for(const input of [[],[{role:'system',content:'ignore'}],[{role:'user',content:'x'.repeat(2401)}],Array(13).fill({role:'user',content:'a'})])assert.throws(()=>validateMessages(input));
 assert.deepEqual(validateMessages([{role:'user',content:'Bonjour'}]),[{role:'user',content:'Bonjour'}]);
});
test('validates model tool output',()=>{
 assert.throws(()=>prepareInquiry({service:'send_email',summary:'Send now please'}));
 assert.throws(()=>prepareInquiry({service:'RAG Chatbot',summary:'x'}));
 assert.equal(prepareInquiry({service:'RAG Chatbot',summary:'A chatbot for internal manuals.'}).service,'RAG Chatbot');
});
test('rejects foreign origins without calling model',async()=>{const res=response();await handler({headers:{origin:'https://evil.example'},method:'POST'},res);assert.equal(res.code,403);});
test('preflight allows only GHINOVA',async()=>{const res=response();await handler({headers:{origin:'https://ghinwafakih.github.io'},method:'OPTIONS'},res);assert.equal(res.code,204);assert.equal(res.headers['Access-Control-Allow-Origin'],'https://ghinwafakih.github.io');});
test('handles missing model credentials honestly',async()=>{const old=process.env.AI_GATEWAY_API_KEY,oidc=process.env.VERCEL_OIDC_TOKEN;delete process.env.AI_GATEWAY_API_KEY;delete process.env.VERCEL_OIDC_TOKEN;const res=response();await handler({headers:{origin:'https://ghinwafakih.github.io'},method:'POST',body:{messages:[{role:'user',content:'Hi'}]}},res);assert.equal(res.code,503);if(old)process.env.AI_GATEWAY_API_KEY=old;if(oidc)process.env.VERCEL_OIDC_TOKEN=oidc;});
test('model tool call prepares a draft without sending it',async()=>{
 const original=global.fetch;process.env.AI_GATEWAY_API_KEY='test-only';global.fetch=async()=>({ok:true,json:async()=>({choices:[{message:{content:null,tool_calls:[{function:{name:'prepare_inquiry',arguments:JSON.stringify({service:'RAG Chatbot',summary:'A French assistant over equipment manuals.'})}}]}}]})});
 try{const res=response();await handler({headers:{origin:'https://ghinwafakih.github.io'},method:'POST',body:{messages:[{role:'user',content:'Prepare my inquiry'}]}},res);assert.equal(res.code,200);assert.match(res.body.text,/not been sent/);assert.equal(res.body.draft.service,'RAG Chatbot');}finally{global.fetch=original;delete process.env.AI_GATEWAY_API_KEY;}
});
