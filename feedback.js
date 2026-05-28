/* 统一反馈组件 · 所有页面共享 */
.feedback-bar { 
  max-width:600px; margin:24px auto; padding:0 16px; 
  text-align:center; font-size:13px;
}
.feedback-bar .fb-question { 
  color:var(--title); font-weight:600; margin-bottom:10px; 
}
.feedback-bar .fb-actions { 
  display:flex; gap:8px; justify-content:center; margin-bottom:6px; 
}
.feedback-btn { 
  padding:8px 18px; border-radius:20px; border:1.5px solid var(--border); 
  background:#fff; cursor:pointer; font-size:13px; transition:0.2s;
  display:flex; align-items:center; gap:6px;
}
.feedback-btn:hover,.feedback-btn.chosen { 
  border-color:var(--sri-red); background:rgba(194,59,34,0.04); 
}
.feedback-btn .icon { font-size:18px; }
.feedback-textarea { 
  width:100%; max-width:400px; height:60px; border:1.5px solid var(--border); 
  border-radius:10px; padding:10px; font-size:13px; font-family:inherit; 
  background:#fff; display:none; margin:8px auto; resize:vertical;
}
.feedback-textarea.show { display:block; }
.feedback-thanks { 
  display:none; color:#4A8C5C; font-weight:600; padding:8px; 
}
.feedback-thanks.show { display:block; }
.feedback-tally { font-size:11px; color:#999; margin-top:4px; }
</style>''' + '''
<div class="feedback-bar">
  <div class="fb-question" id="fbQuestion">这个工具对你有用吗？</div>
  <div class="fb-actions" id="fbActions">
    <button class="feedback-btn" onclick="submitFeedback('up')"><span class="icon">👍</span>有用</button>
    <button class="feedback-btn" onclick="showFeedbackText()"><span class="icon">💬</span>有建议</button>
  </div>
  <textarea class="feedback-textarea" id="fbText" placeholder="你的建议会帮我们改进..."></textarea>
  <button class="feedback-btn" id="fbSubmit" style="display:none;margin:8px auto;" onclick="submitFeedbackText()">发送反馈 →</button>
  <div class="feedback-thanks" id="fbThanks">收到！感谢你的反馈。</div>
  <div class="feedback-tally" id="fbTally"></div>
  <p style="font-size:10px;opacity:0.4;margin-top:8px;">
    <a href="go.html" style="color:inherit;">返回决策通道</a>
  </p>
</div>
<script>
(function(){
  let page=location.pathname.split('/').pop();
  let key='sri_fb_'+page;
  let data=JSON.parse(localStorage.getItem(key)||'{}');
  if(data.sent) document.getElementById('fbQuestion').textContent='感谢你的反馈！';
  // Load tally from localStorage
  let tally=JSON.parse(localStorage.getItem('sri_fb_tally_'+page)||'{"up":0,"text":0}');
  if(tally.up+tally.text>0) document.getElementById('fbTally').textContent='👍'+tally.up+' 💬'+tally.text;
  
  window.submitFeedback=function(type){
    tally[type]=(tally[type]||0)+1;
    localStorage.setItem('sri_fb_tally_'+page,JSON.stringify(tally));
    data.sent=true;data.type=type;data.time=new Date().toISOString();
    localStorage.setItem(key,JSON.stringify(data));
    let fb=document.getElementById('fbThanks');
    document.getElementById('fbActions').style.display='none';
    document.getElementById('fbQuestion').textContent='感谢你的反馈！';
    document.getElementById('fbTally').textContent='👍'+tally.up+' 💬'+tally.text;
    fb.classList.add('show');
  };
  window.showFeedbackText=function(){
    document.getElementById('fbText').classList.add('show');
    document.getElementById('fbSubmit').style.display='inline-block';
  };
  window.submitFeedbackText=function(){
    let text=document.getElementById('fbText').value.trim();
    if(!text) return;
    tally.text=(tally.text||0)+1;
    localStorage.setItem('sri_fb_tally_'+page,JSON.stringify(tally));
    data.sent=true;data.type='text';data.text=text;data.time=new Date().toISOString();
    localStorage.setItem(key,JSON.stringify(data));
    document.getElementById('fbActions').style.display='none';
    document.getElementById('fbText').classList.remove('show');
    document.getElementById('fbSubmit').style.display='none';
    document.getElementById('fbQuestion').textContent='收到！感谢你的建议。';
    document.getElementById('fbTally').textContent='👍'+tally.up+' 💬'+tally.text;
  };
})();
</script>
</body>
</html>
'''
