// gate-check.js — Quality Gate Check
// 满意解研究所 · 12-Gate质量门禁
(function(){
  var gatePassed = true;
  var results = [];
  
  // Gate 1: HTML结构完整性
  if (!document.querySelector('html') || !document.querySelector('body')) {
    results.push('Gate1: HTML结构不完整');
    gatePassed = false;
  }
  
  // Gate 2: VI颜色变量存在
  var style = getComputedStyle(document.documentElement);
  if (!style.getPropertyValue('--sri-red')) {
    results.push('Gate2: VI颜色变量缺失');
    gatePassed = false;
  }
  
  // Gate 3: 品牌一致性
  var body = document.body.innerText||'';
  if (body.indexOf('满意红') > -1) {
    results.push('Gate3: 品牌残留"满意红"');
    gatePassed = false;
  }
  
  // 输出结果到控制台
  if (results.length > 0) {
    console.warn('Gate Check:', results);
  }
  
  // 暴露到全局
  window.gateCheck = { passed: gatePassed, results: results };
})();
