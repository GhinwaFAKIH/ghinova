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
