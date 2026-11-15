// Shared AI interface; the original guided assistant below remains the offline path.
(() => {
  const make=(tag,text,cls)=>{const e=document.createElement(tag);if(text)e.textContent=text;if(cls)e.className=cls;return e;};
  const launcher=make('button','✦ Ghinova AI','ai-launcher');launcher.type='button';launcher.setAttribute('aria-controls','ai-dialog');launcher.setAttribute('aria-expanded','false');
  const dialog=make('dialog',null,'ai-dialog');dialog.id='ai-dialog';dialog.setAttribute('aria-labelledby','ai-dialog-title');
  dialog.innerHTML=`<div class="ai-bar"><span class="ai-avatar" aria-hidden="true">✦</span><strong id="ai-dialog-title">Ghinova AI</strong><div><button type="button" id="ai-clear">Clear</button><button type="button" id="ai-close" aria-label="Close assistant">✕</button></div></div>
    <div class="ai-tabs"><button type="button" id="ai-tab" aria-pressed="true">AI chat</button><button type="button" id="guide-tab" aria-pressed="false">Offline guide</button><label for="ai-language">Language<select id="ai-language"><option value="en">English</option><option value="fr">Français</option></select></label></div>
    <div id="ai-chat"><p class="ai-note" id="ai-privacy"></p><div id="ai-log" class="ai-log" role="log" aria-live="polite" aria-label="Conversation"></div><div id="ai-starters" class="ai-starters"></div><form class="ai-form" id="ai-form"><label for="ai-question" id="ai-question-label">Your question</label><textarea id="ai-question" maxlength="800" required rows="2"></textarea><button type="submit" id="ai-send">Send</button></form><p class="ai-note" id="ai-status" role="status"></p></div><div id="ai-offline" hidden></div>`;
  document.body.append(dialog,launcher);
  const $=id=>document.getElementById(id), lang=$('ai-language');
  const original=document.querySelector('.assistant-panel');
  if(original)$('ai-offline').append(original);
  else {const p=make('p','Explore the original guided recommendations and inquiry builder on the homepage.','ai-note');const a=make('a','Open guided assistant →');a.href='index.html#assistant';$('ai-offline').append(p,a);}
  let history=[],controller=null,requestId=0;
  const words={en:{welcome:'Hi, I’m Ghinova AI ✦ What are you curious about? We can explore an idea or figure out what to build next.',privacy:'AI service: questions and recent conversation are sent to the configured backend and model. Do not share private information. No chat is saved by this interface.',send:'Send',question:'Your question',waiting:'Thinking…',offline:'AI is not connected or is temporarily unavailable. Try the free guides, browse the shop, or contact Ginwa.',more:'Learn More',buy:'Buy Now',download:'Download',quote:'Request a Quote',clear:'Clear',guide:'Offline guide',chat:'AI chat',close:'Close assistant'},fr:{welcome:'Bonjour, moi c’est Ghinova AI ✦ Qu’aimeriez-vous explorer ? Une idée à comprendre, ou un projet à construire ensemble ?',privacy:'Service IA : vos questions et la conversation récente sont envoyées au serveur et au modèle configurés. Ne partagez pas de données privées. Cette interface ne sauvegarde pas la conversation.',send:'Envoyer',question:'Votre question',waiting:'Réflexion en cours…',offline:'L’IA n’est pas connectée ou est temporairement indisponible. Consultez les guides gratuits, la boutique ou contactez Ginwa.',more:'En savoir plus',buy:'Acheter',download:'Télécharger',quote:'Demander un devis',clear:'Effacer',guide:'Guide hors ligne',chat:'Chat IA',close:'Fermer l’assistant'}};
  const t=()=>words[lang.value];
  function scrollChat(){ $('ai-log').scrollTo({top:$('ai-log').scrollHeight,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'}); }
  function starters(){ $('ai-starters').replaceChildren(); for(const text of (lang.value==='fr'?['Explique-moi le RAG','Par où commencer en Python ?']:['Explain RAG simply','Where do I start with Python?'])){const b=make('button',text);b.type='button';b.onclick=()=>{$('ai-question').value=text;$('ai-question').focus();};$('ai-starters').append(b);} }
  function localize(){ $('ai-send').textContent=t().send;$('ai-question-label').textContent=t().question;$('ai-privacy').textContent=t().privacy;$('ai-clear').textContent=t().clear;$('guide-tab').textContent=t().guide;$('ai-tab').textContent=t().chat;$('ai-close').setAttribute('aria-label',t().close);$('ai-chat').lang=lang.value;starters();}
  function add(text,role='assistant'){const p=make('p',text,'ai-message '+role);$('ai-log').append(p);scrollChat();}
  function safeURL(value){if(typeof value!=='string')return null;try {const u=new URL(value,location.href);if(!['http:','https:'].includes(u.protocol))return null;if(u.origin===location.origin)return u.href;if(u.protocol==='https:'&&['whop.com','cal.com','ghinwafakih.github.io'].includes(u.hostname))return u.href;}catch{}return null;}
  function link(parent,label,url){const href=safeURL(url);if(!href)return;const a=make('a',label);a.href=href;parent.append(a);}
  function cards(rows){for(const r of (Array.isArray(rows)?rows:[]).slice(0,3)){const box=make('div',null,'ai-resource');box.append(make('strong',r.name),make('p',r.status),make('p',r.price));if(r.note)box.append(make('p',r.note));link(box,t().more,r.url);if(r.checkout)link(box,t().buy,r.checkout);if(r.download)link(box,t().download,r.download);if(r.contact)link(box,t().quote,r.contact);$('ai-log').append(box);}}
  function fallback(){add(t().offline);const box=make('div',null,'ai-resource');link(box,lang.value==='fr'?'Guide Python gratuit':'Free Python guide','guides/pdf-chatbot-python/');link(box,lang.value==='fr'?'Boutique':'Digital Shop','shop.html');link(box,'Contact','index.html#contact');$('ai-log').append(box);}
  function reset(){requestId++;controller?.abort();controller=null;history=[];$('ai-status').classList.remove('ai-typing');$('ai-log').setAttribute('aria-busy','false');$('ai-log').replaceChildren();$('ai-status').textContent='';$('ai-send').disabled=false;$('ai-question').value='';$('ai-send').textContent=t().send;$('ai-question-label').textContent=t().question;$('ai-privacy').textContent=t().privacy;$('ai-clear').textContent=t().clear;$('guide-tab').textContent=t().guide;$('ai-tab').textContent=t().chat;$('ai-close').setAttribute('aria-label',t().close);$('ai-chat').lang=lang.value;$('ai-starters').hidden=false;localize();add(t().welcome);}
  function tab(ai){$('ai-chat').hidden=!ai;$('ai-offline').hidden=ai;$('ai-tab').setAttribute('aria-pressed',String(ai));$('guide-tab').setAttribute('aria-pressed',String(!ai));}
  function open(offline=false){if(!dialog.open)dialog.show();launcher.setAttribute('aria-expanded','true');tab(!offline);(offline?$('guide-tab'):$('ai-question')).focus();}
  function close(){dialog.close();launcher.setAttribute('aria-expanded','false');launcher.focus();}
  launcher.addEventListener('click',()=>dialog.open?close():open());$('ai-close').addEventListener('click',close);dialog.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();close();}});
  $('ai-clear').addEventListener('click',reset);lang.addEventListener('change',()=>{localize();tab(true);});$('ai-tab').addEventListener('click',()=>tab(true));$('guide-tab').addEventListener('click',()=>tab(false));
  document.querySelectorAll('[data-open-assistant]').forEach(b=>b.addEventListener('click',()=>open()));
  function revealHash(){let target;try{target=document.getElementById(decodeURIComponent(location.hash.slice(1)));}catch{return;}if(!target)return;let p=target.parentElement;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement;}if(location.hash==='#assistant')open(true);else {if(dialog.open){dialog.close();launcher.setAttribute('aria-expanded','false');}target.scrollIntoView();}}
  document.querySelectorAll('.site-menu a').forEach(a=>a.addEventListener('click',()=>{a.closest('details').open=false;}));
  window.addEventListener('hashchange',revealHash);if(location.hash)revealHash();
  $('ai-form').addEventListener('submit',async e=>{
    e.preventDefault();const message=$('ai-question').value.trim();if(!message||message.length>800||controller)return;
    $('ai-starters').hidden=true;add(message,'user');$('ai-question').value='';
    let endpoint=window.GHINOVA_ASSISTANT_API||'';
    if(!endpoint&&['127.0.0.1','localhost'].includes(location.hostname))endpoint='http://127.0.0.1:8787/api/chat';
    if(!endpoint){fallback();return;}
    try {const u=new URL(endpoint);if(u.protocol!=='https:'&&!(u.protocol==='http:'&&['127.0.0.1','localhost'].includes(u.hostname)&&['127.0.0.1','localhost'].includes(location.hostname)))throw new Error();}catch{fallback();return;}
    controller=new AbortController();const active=controller,id=++requestId;const timer=setTimeout(()=>active.abort(),75000);$('ai-send').disabled=true;$('ai-status').textContent=t().waiting;$('ai-status').classList.add('ai-typing');$('ai-log').setAttribute('aria-busy','true');
    try {const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message,language:lang.value,history:history.slice(-6)}),signal:active.signal,credentials:'omit',redirect:'error'});
      if(!response.ok)throw new Error('Service unavailable');const data=await response.json();if(id!==requestId)return;
      if(typeof data.answer!=='string')throw new Error('Invalid answer');add(data.answer);cards(data.resources);$('ai-status').textContent=data.notice||'';history.push({role:'user',content:message},{role:'assistant',content:(data.answer+'\n'+JSON.stringify(data.resources||[])).slice(0,1200)});history=history.slice(-6);
    }catch{if(id===requestId){fallback();$('ai-status').textContent='';}}
    finally{clearTimeout(timer);if(id===requestId){controller=null;$('ai-status').classList.remove('ai-typing');$('ai-log').setAttribute('aria-busy','false');$('ai-send').disabled=false;$('ai-question').focus();scrollChat();}}
  });
  reset();
})();

(() => {
 const host=document.getElementById('guide-content');if(!host)return;
 const status=document.getElementById('assistant-status');
 const services=[
 ['RAG Chatbot','Answers from documents','A chatbot that retrieves relevant passages from your PDFs or manuals and provides source references.'],
 ['Multilingual AI Assistant','Support in several languages','An assistant using approved content in Arabic, French and English.'],
 ['AI Agents & Automation','Automate a repeated task','A focused workflow for document extraction, summaries or response drafts, with human review where needed.'],
 ['Knowledge Graphs & GraphRAG','Connect complex information','Domain modelling, RDF, SPARQL and graph-based retrieval for connected data.'],
 ['AI Prototype / Technical Review','Test an idea or review a prototype','A focused proof of concept or technical review, with documented findings and next steps.'],
 ['Team AI Workshop','Train my team','Practical workshops on Python, generative AI, RAG or agents, adapted to your team.']
 ];
 let notes='',timing='';
 function el(tag,text,cls){const node=document.createElement(tag);if(text)node.textContent=text;if(cls)node.className=cls;return node;}
 function page(title,copy,focus=true){host.replaceChildren();const h=el('h3',title);h.tabIndex=-1;host.append(h);if(copy)host.append(el('p',copy));if(focus)h.focus({preventScroll:true});status.textContent='Your choices stay in this page.';}
 function button(text,fn,cls='secondary',parent=host){const b=el('button',text,cls);b.type='button';b.addEventListener('click',fn);parent.append(b);return b;}
 function link(text,href){const a=el('a',text,'secondary');a.href=href;host.append(a);}
 function choices(items){const box=el('div',null,'guide-choices');host.append(box);items.forEach(([label,fn])=>button(label,fn,'',box));}
 function home(focus=true){page('What brings you here today?','Choose a path to get a practical recommendation.',focus);choices([['I want to learn Python or AI',learn],['I have a project for my business',serviceList],['I want to contact Ginwa',()=>{location.hash='contact';document.getElementById('name').focus({preventScroll:true});}]]);}
 function learn(){page('How would you like to learn?');choices([['I’m new to AI — learn at my own pace',()=>recommend('Start with AI & NLP Fundamentals','Level 1 is designed for beginners. It includes five downloadable slide lessons and a guided Python/Colab lab. The listed launch price is €59, with any applicable tax shown at checkout.','Explore the course','#courses')],['I want live, personalised support',()=>recommend('Try a private training session','Live online lessons cover Python or AI at your level. A 60-minute session is €20 before applicable tax. Packages are €90 for five hours or €170 for ten hours.','See training options','#book')],['I already know the basics',()=>recommend('Build a focused learning plan','Explore RAG, AI agents or knowledge graphs through personalised training, or browse the digital shop. The self-paced Level 2 course is planned and is not available yet.','Explore learning topics','#learn',true)]]);button('← Back',()=>home(),'guide-back');}
 function recommend(title,text,label,href,advanced=false){page(title,text);link(label+' →',href);if(advanced)link('Browse digital resources →','shop.html');button('← Other learning options',learn,'guide-back');}
 function serviceList(){page('What would you like to build?','Choose the closest match. Service projects are scoped and quoted individually.');choices(services.map(s=>[s[1],()=>service(s)]));button('Not sure yet',()=>service(['Freelance AI Project','Explore my project idea','Describe the problem you want to solve and Ginwa can help clarify a practical first step.']));button('← Back',()=>home(),'guide-back');}
 function service(s){page(s[0],s[2]);host.append(el('p','Pricing depends on the scope. Hosting, model usage and ongoing support are discussed separately in the proposal.'));button('Prepare my inquiry',()=>brief(s),'primary');button('← Other services',serviceList,'guide-back');}
 function brief(s){page('Describe your project','These details only fill your draft. Nothing is sent until you review and submit the contact form.');
  const label=el('label','What problem would you like to solve?');const input=el('textarea');input.id='guide-goal';input.maxLength=1800;input.placeholder='Your goal, intended users, and documents or tools involved…';input.value=notes;input.dir='auto';label.htmlFor=input.id;host.append(label,input);
  const label2=el('label','Preferred timeline (optional)');const when=el('input');when.id='guide-timeline';when.maxLength=160;when.placeholder='For example, explore a prototype next month';when.value=timing;label2.htmlFor=when.id;host.append(label2,when);
  button('Review in contact form →',()=>{notes=input.value.trim();timing=when.value.trim();if(!notes){status.textContent='Please describe your project first.';input.focus();return;}
   const draft=`Service: ${s[0]}\n\nProject goal: ${notes}${timing?'\n\nPreferred timeline: '+timing:''}`;
   const field=document.getElementById('message'),interest=document.getElementById('course');
   if(!Array.from(interest.options).some(o=>o.value===s[0]))return;
   if(!field.value.includes(draft))field.value=field.value.trim()?field.value+'\n\n'+draft:draft;
   interest.value=s[0];document.getElementById('level').value='I have a project idea';location.hash='contact';field.focus({preventScroll:true});status.textContent='Draft added to the contact form. Review it before sending.';
  },'primary');button('← Back to this service',()=>{notes=input.value;timing=when.value;service(s);},'guide-back');
 }
 document.getElementById('assistant-reset').addEventListener('click',()=>{notes='';timing='';home();});home(false);
})();
