(() => {
 const endpoint='https://ghinova-assistant-ghinova.vercel.app/api/chat';
 const form=document.getElementById('assistant-form');
 if(!form)return;
 const input=document.getElementById('assistant-input'),log=document.getElementById('assistant-log'),status=document.getElementById('assistant-status'),submit=form.querySelector('button[type="submit"]');
 let history=[],busy=false,controller=null,generation=0;
 function bubble(text,role){const p=document.createElement('p');p.className='assistant-message '+role;p.dir='auto';p.textContent=text;log.append(p);log.scrollTop=log.scrollHeight;return p;}
 async function send(text){
  if(busy||!text.trim())return;
  const current=++generation;busy=true;submit.disabled=true;input.disabled=true;status.textContent='Thinking…';
  bubble(text,'user');const candidate=[...history,{role:'user',content:text}].slice(-9);controller=new AbortController();const timeout=setTimeout(()=>controller?.abort(),42000);
  try{
   const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:candidate}),signal:controller.signal});
   const data=await response.json();if(current!==generation)return;
   if(!response.ok)throw Error(data.error||'The assistant is unavailable. Please use the contact form.');
   if(typeof data.text!=='string')throw Error('Please try again.');
   bubble(data.text,'agent');history=[...candidate,{role:'assistant',content:data.text}];input.value='';
   if(data.draft&&typeof data.draft.summary==='string'&&typeof data.draft.service==='string'){
    const card=document.createElement('div');card.className='assistant-draft';
    const title=document.createElement('strong');title.textContent='Project brief · review before sending';
    const p=document.createElement('p');p.dir='auto';p.textContent=data.draft.summary;
    const button=document.createElement('button');button.type='button';button.className='secondary';button.textContent='Review in contact form →';
    button.addEventListener('click',()=>{
     const field=document.getElementById('message'),interest=document.getElementById('course');
     if(!Array.from(interest.options).some(o=>o.value===data.draft.service))return;
     // Preserve an existing inquiry instead of silently overwriting it.
     if(field.value.trim()&&field.value.trim()!==data.draft.summary.trim()){field.value+='\n\nAI-assisted project brief:\n'+data.draft.summary;}else{field.value=data.draft.summary;}
     interest.value=data.draft.service;document.getElementById('level').value='I have a project idea';
     document.getElementById('contact').scrollIntoView({behavior:'smooth'});field.focus({preventScroll:true});button.disabled=true;button.textContent='Added to your inquiry';
    });card.append(title,p,button);log.append(card);log.scrollTop=log.scrollHeight;
   }
   status.textContent='Ready';
  }catch(error){if(current===generation){bubble(error.name==='AbortError'?'The request took too long. Please try again or use the contact form.':error.message,'error');status.textContent='Could not connect';}}
  finally{clearTimeout(timeout);if(current===generation){busy=false;submit.disabled=false;input.disabled=false;input.focus({preventScroll:true});}}
 }
 form.addEventListener('submit',e=>{e.preventDefault();send(input.value.trim());});
 document.querySelectorAll('[data-assistant-prompt]').forEach(b=>b.addEventListener('click',()=>{input.value=b.dataset.assistantPrompt;send(input.value);}));
 document.getElementById('assistant-reset').addEventListener('click',()=>{generation++;controller?.abort();history=[];busy=false;submit.disabled=false;input.disabled=false;input.value='';log.replaceChildren();bubble('Hi! I’m the GHINOVA AI assistant. Tell me what you want to learn or build. You can write in English, français ou العربية.','agent');status.textContent='New conversation';});
})();
