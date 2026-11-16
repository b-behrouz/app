// No form data, response bodies or server details are included in diagnostics.
(function(){
 const seen=new Set();let ready=false,styleFailed=false;
 function show(){const box=document.getElementById('app-boot-error');if(box){box.hidden=false;box.querySelector('button').onclick=()=>location.reload();}}
 function fail(code,error){
  if(code==='STYLE_FAILED')styleFailed=true;
  if(!seen.has(code)){seen.add(code);console.error('[Rahnamaye Salamat startup]',code,error?.name||'Error');}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',show,{once:true});else show();
 }
 const timer=setTimeout(()=>{if(!ready){const pending=[...document.querySelectorAll('link[rel=stylesheet]')].filter(link=>!link.sheet);if(pending.length){styleFailed=true;pending.forEach(link=>link.disabled=true);fail('STYLE_TIMEOUT')}fail('BOOT_TIMEOUT')}},45000);
 window.__RAHNAMA_BOOT__={fail,ready(){ready=true;clearTimeout(timer);document.documentElement.dataset.appReady='true';const root=document.getElementById('root');root?.removeAttribute('inert');root?.removeAttribute('aria-busy');if(!styleFailed){const box=document.getElementById('app-boot-error');if(box)box.hidden=true;}}};
 window.addEventListener('error',event=>{const target=event.target;if(target?.tagName==='SCRIPT'&&target.hasAttribute('data-app-runtime'))fail('APP_SCRIPT_FAILED');else if(target?.tagName==='LINK'&&target.rel==='stylesheet')fail('STYLE_FAILED');else if(event instanceof ErrorEvent&&!ready)fail('RUNTIME_FAILED',event.error);},true);
 window.addEventListener('unhandledrejection',event=>{if(!ready)fail('BOOT_REJECTION',event.reason)});
})();
