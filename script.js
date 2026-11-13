function sendMail(e){e.preventDefault();const name=document.getElementById('name').value;const email=document.getElementById('email').value;const course=document.getElementById('course').value;const level=document.getElementById('level').value;const msg=document.getElementById('message').value;const subject=encodeURIComponent('GHINOVA inquiry — '+course);const body=encodeURIComponent(`Hi Ghinwa,\n\nMy name is ${name}.\nEmail: ${email}\nI'm contacting you about: ${course}\nLevel / project stage: ${level}\n\n${msg}\n\nBest,\n${name}`);window.location.href=`mailto:?subject=${subject}&body=${body}`}

// Keep project inquiries connected to the service the visitor selected.
document.querySelectorAll('[data-service]').forEach(link => {
  link.addEventListener('click', () => {
    const interest = document.getElementById('course');
    const stage = document.getElementById('level');
    if (interest) interest.value = link.dataset.service;
    if (stage) stage.value = 'I have a project idea';
  });
});
