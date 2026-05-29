// 统一密码门禁 · 共享 localStorage · 一处验证全部页面通行
(function(){
  var HASH='6460662e217c7a9f899208dd70a2c28abdea42f128666a9b78e6c0c064846493';
  var saved=localStorage.getItem('sri_dash_auth_hash');
  if(localStorage.getItem('sri_dashboard_auth')==='true' && saved===(localStorage.getItem('sri_dash_hash')||HASH)){
    return; // 已验证，不插入门禁层
  }
  localStorage.removeItem('sri_dashboard_auth');
  
  var curHash=localStorage.getItem('sri_dash_hash')||HASH;
  
  // 插入门禁HTML
  var d=document.createElement('div');
  d.id='gateLayer';
  d.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;background:#F5F0E6;z-index:9999;display:flex;align-items:center;justify-content:center;font-family:-apple-system,sans-serif;';
  d.innerHTML=`
<div style="background:#fff;border-radius:20px;padding:40px 28px;max-width:360px;width:90%;text-align:center;box-shadow:0 4px 24px rgba(0,0,0,0.08);border:2px solid #C23B22;" id="gateBox">
<div style="font-size:40px;margin-bottom:12px;">🔐</div>
<h2 style="font-size:18px;color:#2A2A2A;margin-bottom:4px;">内部工具 · 授权访问</h2>
<p style="font-size:12px;color:#6E6E6E;margin-bottom:16px;">请输入6位数字密码</p>
<div style="display:flex;gap:6px;justify-content:center;margin-bottom:12px;">
<input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" id="gd0" style="width:42px;height:52px;border:2px solid #D4C5A0;border-radius:10px;text-align:center;font-size:22px;font-weight:700;font-family:monospace;background:#F5F0E6;">
<input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" id="gd1" style="width:42px;height:52px;border:2px solid #D4C5A0;border-radius:10px;text-align:center;font-size:22px;font-weight:700;font-family:monospace;background:#F5F0E6;">
<input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" id="gd2" style="width:42px;height:52px;border:2px solid #D4C5A0;border-radius:10px;text-align:center;font-size:22px;font-weight:700;font-family:monospace;background:#F5F0E6;">
<input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" id="gd3" style="width:42px;height:52px;border:2px solid #D4C5A0;border-radius:10px;text-align:center;font-size:22px;font-weight:700;font-family:monospace;background:#F5F0E6;">
<input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" id="gd4" style="width:42px;height:52px;border:2px solid #D4C5A0;border-radius:10px;text-align:center;font-size:22px;font-weight:700;font-family:monospace;background:#F5F0E6;">
<input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" id="gd5" style="width:42px;height:52px;border:2px solid #D4C5A0;border-radius:10px;text-align:center;font-size:22px;font-weight:700;font-family:monospace;background:#F5F0E6;">
</div>
<p id="gateError" style="color:#C23B22;font-size:12px;min-height:18px;margin:4px 0;"></p>
<button onclick="window._gateVerify()" style="width:100%;padding:12px;border:none;border-radius:12px;background:#C23B22;color:#fff;font-size:14px;font-weight:600;cursor:pointer;">验证 →</button>
<p style="font-size:11px;margin-top:12px;opacity:0.5;"><a href="javascript:void(0)" onclick="window._gateForgot()" style="color:#6E6E6E;">忘记密码？</a></p>
</div>`;
  document.body.insertBefore(d, document.body.firstChild);

  var gateFailCount=parseInt(localStorage.getItem('sri_gate_fails')||'0');
  var gateLockUntil=parseInt(localStorage.getItem('sri_gate_lock')||'0');

  window._gateNext=function(el){
    el.value=el.value.replace(/[^0-9]/g,'');
    if(el.value&&el.nextElementSibling&&el.nextElementSibling.classList.contains('gateDigit')) el.nextElementSibling.focus();
    var err=document.getElementById('gateError'); if(err) err.textContent='';
  };

  window._gatePrev=function(e,el){
    if(e.key==='Backspace'&&!el.value&&el.previousElementSibling&&el.previousElementSibling.classList.contains('gateDigit')) el.previousElementSibling.focus();
  };

  window._gateVerify=async function(){
    var now=Date.now();
    if(gateLockUntil>now){
      var sec=Math.ceil((gateLockUntil-now)/1000);
      document.getElementById('gateError').textContent='已锁定·请等待'+sec+'秒';
      return;
    }
    var code='';
    for(var i=0;i<6;i++){ var v=document.getElementById('gd'+i).value; if(!v){document.getElementById('gateError').textContent='请输入完整6位密码';return;} code+=v; }
    var hash=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(code));
    var h=Array.from(new Uint8Array(hash)).map(function(b){return b.toString(16).padStart(2,'0')}).join('');
    if(h===curHash){
      localStorage.setItem('sri_gate_fails','0');
      localStorage.setItem('sri_dashboard_auth','true');
      localStorage.setItem('sri_dash_auth_hash',curHash);
      document.getElementById('gateLayer').style.display='none';
    } else {
      gateFailCount++;
      localStorage.setItem('sri_gate_fails',gateFailCount);
      if(gateFailCount>=3){
        localStorage.setItem('sri_gate_lock',Date.now()+300000);
        document.getElementById('gateError').textContent='已锁定5分钟·连续3次错误';
        localStorage.setItem('sri_gate_fails','0');
      } else {
        document.getElementById('gateError').textContent='密码错误('+gateFailCount+'/3)';
      }
      var digits=document.querySelectorAll('.gateDigit');
      digits.forEach(function(d){d.classList.add('error');setTimeout(function(){d.value='';d.classList.remove('error')},600)});
      document.getElementById('gd0').focus();
    }
  };

  window._gateForgot=function(){
    var box=document.getElementById('gateBox');
    box.innerHTML=`
    <div style="font-size:28px;margin-bottom:8px;">🔧</div>
    <h2 style="font-size:18px;color:#2A2A2A;margin-bottom:4px;">变更密码</h2>
    <p style="font-size:12px;color:#6E6E6E;margin-bottom:12px;">输入当前密码 + 新密码</p>
    <div style="text-align:left;font-size:12px;margin-bottom:8px;">
      <label style="color:#4A4A4A;font-weight:600;">当前密码</label>
      <div style="display:flex;gap:6px;justify-content:center;margin:4px 0 10px;" id="oldDigits">
        <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" style="width:38px;height:44px;border:2px solid #D4C5A0;border-radius:8px;text-align:center;font-size:20px;font-weight:700;font-family:monospace;background:#F5F0E6;">
        <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" style="width:38px;height:44px;border:2px solid #D4C5A0;border-radius:8px;text-align:center;font-size:20px;font-weight:700;font-family:monospace;background:#F5F0E6;">
        <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" style="width:38px;height:44px;border:2px solid #D4C5A0;border-radius:8px;text-align:center;font-size:20px;font-weight:700;font-family:monospace;background:#F5F0E6;">
        <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" style="width:38px;height:44px;border:2px solid #D4C5A0;border-radius:8px;text-align:center;font-size:20px;font-weight:700;font-family:monospace;background:#F5F0E6;">
        <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" style="width:38px;height:44px;border:2px solid #D4C5A0;border-radius:8px;text-align:center;font-size:20px;font-weight:700;font-family:monospace;background:#F5F0E6;">
        <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" style="width:38px;height:44px;border:2px solid #D4C5A0;border-radius:8px;text-align:center;font-size:20px;font-weight:700;font-family:monospace;background:#F5F0E6;">
      </div>
      <label style="color:#4A4A4A;font-weight:600;">新密码（6位数字）</label>
      <div style="display:flex;gap:6px;justify-content:center;margin:4px 0;" id="newDigits">
        <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" style="width:38px;height:44px;border:2px solid #D4C5A0;border-radius:8px;text-align:center;font-size:20px;font-weight:700;font-family:monospace;background:#F5F0E6;">
        <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" style="width:38px;height:44px;border:2px solid #D4C5A0;border-radius:8px;text-align:center;font-size:20px;font-weight:700;font-family:monospace;background:#F5F0E6;">
        <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" style="width:38px;height:44px;border:2px solid #D4C5A0;border-radius:8px;text-align:center;font-size:20px;font-weight:700;font-family:monospace;background:#F5F0E6;">
        <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" style="width:38px;height:44px;border:2px solid #D4C5A0;border-radius:8px;text-align:center;font-size:20px;font-weight:700;font-family:monospace;background:#F5F0E6;">
        <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" style="width:38px;height:44px;border:2px solid #D4C5A0;border-radius:8px;text-align:center;font-size:20px;font-weight:700;font-family:monospace;background:#F5F0E6;">
        <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" style="width:38px;height:44px;border:2px solid #D4C5A0;border-radius:8px;text-align:center;font-size:20px;font-weight:700;font-family:monospace;background:#F5F0E6;">
      </div>
    </div>
    <button onclick="window._gateDoChange()" style="width:100%;padding:12px;border:none;border-radius:12px;background:#C23B22;color:#fff;font-size:14px;font-weight:600;cursor:pointer;">变更密码</button>
    <p style="font-size:11px;margin-top:8px;"><a href="javascript:void(0)" onclick="window._gateBack()" style="color:#6E6E6E;">← 返回登录</a></p>`;
  };

  window._gateDoChange=async function(){
    var oldDigits=document.getElementById('oldDigits').querySelectorAll('input');
    var newDigits=document.getElementById('newDigits').querySelectorAll('input');
    var old=''; for(var i=0;i<6;i++){if(!oldDigits[i].value){document.getElementById('gateError').textContent='请输入当前密码';return;} old+=oldDigits[i].value;}
    var np=''; for(var i=0;i<6;i++){if(!newDigits[i].value){document.getElementById('gateError').textContent='请输入新密码';return;} np+=newDigits[i].value;}
    if(np===old){document.getElementById('gateError').textContent='新密码不能与当前密码相同';return;}
    var oh=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(old));
    var ohash=Array.from(new Uint8Array(oh)).map(function(b){return b.toString(16).padStart(2,'0')}).join('');
    if(ohash!==curHash){document.getElementById('gateError').textContent='当前密码错误';return;}
    var nh=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(np));
    var nhash=Array.from(new Uint8Array(nh)).map(function(b){return b.toString(16).padStart(2,'0')}).join('');
    localStorage.setItem('sri_dash_hash',nhash);
    localStorage.setItem('sri_gate_fails','0');
    localStorage.setItem('sri_dashboard_auth','true');
    localStorage.setItem('sri_dash_auth_hash',nhash);
    document.getElementById('gateLayer').style.display='none';
  };

  window._gateBack=function(){
    document.getElementById('gateBox').innerHTML=`
    <div style="font-size:40px;margin-bottom:12px;">🔐</div>
    <h2 style="font-size:18px;color:#2A2A2A;margin-bottom:4px;">内部工具 · 授权访问</h2>
    <p style="font-size:12px;color:#6E6E6E;margin-bottom:16px;">请输入6位数字密码</p>
    <div style="display:flex;gap:6px;justify-content:center;margin-bottom:12px;" id="digitGroup">
      <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" id="gd0" style="width:42px;height:52px;border:2px solid #D4C5A0;border-radius:10px;text-align:center;font-size:22px;font-weight:700;font-family:monospace;background:#F5F0E6;">
      <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" id="gd1" style="width:42px;height:52px;border:2px solid #D4C5A0;border-radius:10px;text-align:center;font-size:22px;font-weight:700;font-family:monospace;background:#F5F0E6;">
      <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" id="gd2" style="width:42px;height:52px;border:2px solid #D4C5A0;border-radius:10px;text-align:center;font-size:22px;font-weight:700;font-family:monospace;background:#F5F0E6;">
      <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" id="gd3" style="width:42px;height:52px;border:2px solid #D4C5A0;border-radius:10px;text-align:center;font-size:22px;font-weight:700;font-family:monospace;background:#F5F0E6;">
      <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" id="gd4" style="width:42px;height:52px;border:2px solid #D4C5A0;border-radius:10px;text-align:center;font-size:22px;font-weight:700;font-family:monospace;background:#F5F0E6;">
      <input type="password" class="gateDigit" maxlength="1" inputmode="numeric" pattern="[0-9]" id="gd5" style="width:42px;height:52px;border:2px solid #D4C5A0;border-radius:10px;text-align:center;font-size:22px;font-weight:700;font-family:monospace;background:#F5F0E6;">
    </div>
    <p id="gateError" style="color:#C23B22;font-size:12px;min-height:18px;margin:4px 0;"></p>
    <button onclick="window._gateVerify()" style="width:100%;padding:12px;border:none;border-radius:12px;background:#C23B22;color:#fff;font-size:14px;font-weight:600;cursor:pointer;">验证 →</button>
    <p style="font-size:11px;margin-top:12px;opacity:0.5;"><a href="javascript:void(0)" onclick="window._gateForgot()" style="color:#6E6E6E;">变更密码？</a></p>`;
    document.getElementById('gd0').focus();
  };

  // 绑定事件
  document.addEventListener('input',function(e){if(e.target.classList.contains('gateDigit'))window._gateNext(e.target)});
  document.addEventListener('keydown',function(e){if(e.target.classList.contains('gateDigit'))window._gatePrev(e,e.target)});
  document.addEventListener('paste',function(e){
    if(document.getElementById('gateLayer').style.display==='none') return;
    var p=(e.clipboardData||window.clipboardData).getData('text').replace(/[^0-9]/g,'');
    if(p.length===6){ e.preventDefault(); for(var i=0;i<6;i++) document.getElementById('gd'+i).value=p[i]; window._gateVerify(); }
  });

  // 聚焦第一个输入框
  setTimeout(function(){var gd=document.getElementById('gd0');if(gd)gd.focus()},100);
})();
