<script>
/* ================================================================
   管理后台 v3.0 · 9管理域·36子模块·三级穿透
   驾驶舱的二层核心基石 — 数据统一源·双向协同
   ================================================================ */
var DB=null,loadError=false,currentView=null,sortState={key:null,asc:true};
var currentDomain=null;
var LC_LABELS={L0_概念:'💡概念',L1_原型:'🔬原型',L2_内测:'🧪内测',L3_打磨:'✨打磨',L4_精品:'💎精品',L5_维护:'🔄维护',L6_退役:'📦退役'};
var MAT_LABELS={M0_种子:'🌱种子',M1_萌芽:'🌿萌芽',M2_成型:'🌳成型',M3_成熟:'🍎成熟',M4_标杆:'🏆标杆'};
var LAYERS=[{k:'physical',icon:'🔩',label:'物理层',color:'var(--l-phy)'},{k:'chemical',icon:'⚗️',label:'化学层',color:'var(--l-chem)'},{k:'biological',icon:'🧬',label:'生物层',color:'var(--l-bio)'},{k:'psychological',icon:'🧠',label:'心理层',color:'var(--l-psy)'}];

var NAV=[
  {id:'strategy',label:'📊 战略仪表盘',children:[
    {id:'strategy-kpi',label:'KPI仪表盘',desc:'核心指标实时监控'},
    {id:'strategy-map',label:'战略地图',desc:'BSC四视角联动'},
    {id:'strategy-milestone',label:'里程碑看板',desc:'时间线·关键事件'},
    {id:'strategy-risk',label:'风险雷达',desc:'识别·评级·应对'}
  ]},
  {id:'product',label:'📦 产品全生命周期',children:[
    {id:'product-overview',label:'产品总览',desc:'312产品·7阶段·8族'},
    {id:'product-pipeline',label:'研发管道',desc:'概念→原型→内测→打磨→精品'},
    {id:'product-quality',label:'质量中心',desc:'四维评分·审计·改进'},
    {id:'product-release',label:'版本与发布',desc:'版本历史·变更·部署'}
  ]},
  {id:'customer',label:'👤 客户关系',children:[
    {id:'customer-360',label:'客户360',desc:'档案·画像·决策风格'},
    {id:'customer-pipeline',label:'销售管道',desc:'线索→商机→提案→签约'},
    {id:'customer-delivery',label:'交付与满意度',desc:'项目·反馈·NPS'},
    {id:'customer-success',label:'客户成功',desc:'续约·增购·案例'}
  ]},
  {id:'finance',label:'💰 财务与定价',children:[
    {id:'finance-overview',label:'收入仪表盘',desc:'收入·成本·利润'},
    {id:'finance-pricing',label:'产品定价',desc:'SKU·折扣·许可'},
    {id:'finance-cost',label:'成本跟踪',desc:'开发·运营·销售'},
    {id:'finance-budget',label:'预算与预测',desc:'预算vs实际·滚动预测'}
  ]},
  {id:'knowledge',label:'🧬 知识资产',children:[
    {id:'knowledge-graph',label:'知识图谱',desc:'实体·连接·密度'},
    {id:'knowledge-content',label:'内容生命周期',desc:'创建·审核·发布·归档'},
    {id:'knowledge-term',label:'术语管理',desc:'词汇产权·映射·一致性'},
    {id:'knowledge-learn',label:'学习与培训',desc:'课程·认证·技能矩阵'}
  ]},
  {id:'ops',label:'⚙️ 运营与流程',children:[
    {id:'ops-tasks',label:'任务看板',desc:'P0-P3·状态·截止'},
    {id:'ops-decisions',label:'决策记录',desc:'日志·链条·结果'},
    {id:'ops-cron',label:'自动化引擎',desc:'Cron·触发·执行日志'},
    {id:'ops-workflow',label:'流程管理',desc:'工作流·审批·SOP'}
  ]},
  {id:'governance',label:'🛡️ 免疫与治理',children:[
    {id:'gov-immune',label:'免疫系统',desc:'L0-L6七层·事件'},
    {id:'gov-rules',label:'规则引擎',desc:'48规则·激活·反馈'},
    {id:'gov-quality-gate',label:'质量门禁',desc:'代码·内容·设计·数据'},
    {id:'gov-compliance',label:'合规与审计',desc:'隐私·安全·许可'}
  ]},
  {id:'archaeology',label:'🏺 考古与洞察',children:[
    {id:'arch-timeline',label:'时间线',desc:'105天·6阶段·19关键时刻'},
    {id:'arch-artifacts',label:'历史文物',desc:'35件·来源·意义'},
    {id:'arch-simulations',label:'模拟与场景',desc:'16场景·30天随访'},
    {id:'arch-insights',label:'发现与洞察',desc:'趋势·模式·异常'}
  ]},
  {id:'people',label:'👥 组织与人',children:[
    {id:'people-avatars',label:'替身管理',desc:'激活·休眠·唤醒'},
    {id:'people-experts',label:'专家团',desc:'角色·专长·可用性'},
    {id:'people-council',label:'五路评议会',desc:'图腾·编排·决议'},
    {id:'people-network',label:'协作者网络',desc:'关系图·协同效率'}
  ]}
];

/* ===== 辅助函数 ===== */
function escH(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function escA(s){return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;')}
function q(s){return JSON.stringify(String(s))}
function renderDegrade(){return'<div class="loading"><div class="spinner" style="border-top-color:var(--red)"></div><p style="margin-top:16px;color:var(--red)">⚠️ 数据加载失败</p><p style="font-size:.8em;color:var(--ink-light)">请检查 entities_index.json</p></div>'}
function placeholder(title,desc){return'<div class="placeholder-card"><div class="ph-icon">🏗️</div><div class="ph-title">'+escH(title)+'</div><div class="ph-desc">'+escH(desc)+'</div></div>'}
function toolbar(id,ph,filts){
  var h='<div class="panel-toolbar"><input type="text" placeholder="'+ph+'" id="srch-'+id+'" oninput="filtPane(\''+id+'\',this.value)">';
  if(filts&&filts.length){h+='<select id="filt-'+id+'" onchange="filtPane(\''+id+'\',document.getElementById(\'srch-'+id+'\').value,this.value)"><option value="">全部</option>';for(var i=0;i<filts.length;i++)h+='<option value="'+escA(filts[i])+'">'+escH(filts[i])+'</option>';h+='</select>'}
  h+='</div>';return h;
}
function toggleDetail(id){var r=document.getElementById(id);if(r)r.classList.toggle('show')}
function filtPane(id,text,cat){
  text=(text||'').toLowerCase();var rows=document.querySelectorAll('#tbody-'+id+' tr');
  for(var i=0;i<rows.length;i++){var row=rows[i];if(row.className.indexOf('empty-row')>=0||row.className.indexOf('detail-row')>=0)continue;var m=true;
  if(text&&(row.textContent||'').toLowerCase().indexOf(text)<0)m=false;
  if(cat&&m){var tags=row.querySelectorAll('.tag');var cm=false;for(var j=0;j<tags.length;j++){if((tags[j].textContent||'').indexOf(cat)>=0){cm=true;break}}if(!cm&&(row.textContent||'').indexOf(cat)<0)cm=false;if(!cm)m=false}
  row.style.display=m?'':'none';var nx=row.nextElementSibling;if(nx&&nx.className.indexOf('detail-row')>=0)nx.style.display='none'}
}

var PANE_DATA={};
function fillTbl(id,rows,rowBld,emptyMsg){
  var tb=document.getElementById('tbody-'+id);if(!tb)return;
  if(!rows||!rows.length){tb.innerHTML='<tr class="empty-row"><td colspan="12">'+(emptyMsg||'暂无数据')+'</td></tr>';return}
  var h='';for(var i=0;i<rows.length;i++)h+=rowBld(rows[i],i);tb.innerHTML=h;
}
function sortTbl(id,key,th){
  var rows=PANE_DATA[id];if(!rows)return;var asc=sortState.key===key?!sortState.asc:true;sortState={key:key,asc:asc};
  rows.sort(function(a,b){var va=a[key]||'',vb=b[key]||'';if(typeof va==='number')return asc?va-vb:vb-va;va=String(va);vb=String(vb);return asc?va.localeCompare(vb,'zh'):vb.localeCompare(va,'zh')});
  var arrows=document.querySelectorAll('#tbl-'+id+' .sort-arrow');for(var i=0;i<arrows.length;i++)arrows[i].textContent='';
  if(th){var ar=th.querySelector('.sort-arrow');if(ar)ar.textContent=asc?' ▲':' ▼'}
  fillTbl(id,rows,rowBuilders[id],'暂无数据');
}
var rowBuilders={};

/* ===== 密码门 ===== */
function checkGate(btn){
  var pw=document.getElementById('gpw').value;
  try{if(!sessionStorage)throw new Error('no');sessionStorage.setItem('_at','1');sessionStorage.removeItem('_at')}catch(e){document.getElementById('gate-degrade').style.display='block'}
  if(pw==='123654'){try{sessionStorage.setItem('_admin_auth','1')}catch(e){}document.getElementById('gate').classList.add('hidden');document.getElementById('app').classList.add('show');initApp()}else{document.getElementById('gate-error').textContent='密码错误'}
}

/* ===== 初始化 ===== */
function initApp(){
  renderSidebar();
  fetch('entities_index.json').then(function(r){if(!r.ok)throw new Error('HTTP '+r.status);return r.json()}).then(function(j){
    DB=j;loadError=false;renderSidebar();navTo('strategy-kpi');
  }).catch(function(err){console.error(err);loadError=true;DB=null;renderSidebar();navTo('strategy-kpi')});
}

/* ===== 侧栏 ===== */
function renderSidebar(){
  var h='<div class="sidebar-header"><h3>🩸 毛细血管</h3><div class="sub">满意红 · 管理后台 v3.0</div></div>';
  h+='<a href="dashboard-v3.html" class="sidebar-back">◂ 返回驾驶舱</a><div class="sidebar-nav-wrap">';
  for(var i=0;i<NAV.length;i++){
    var d=NAV[i],openClass=(currentDomain===d.id||!currentDomain&&i===0)?' open':'';
    h+='<div class="nav-domain'+openClass+'" id="domain-'+d.id+'"><div class="nav-domain-header" onclick="toggleDomain(\''+d.id+'\')"><span class="domain-label"><span>'+d.label+'</span></span><span class="domain-arrow">▶</span></div><div class="nav-children">';
    for(var j=0;j<d.children.length;j++){
      var ch=d.children[j],activeClass=currentView===ch.id?' active':'';
      h+='<div class="nav-child'+activeClass+'" onclick="navTo(\''+ch.id+'\',this)" id="nav-'+ch.id+'">'+ch.label+'</div>';
    }
    h+='</div></div>';
  }
  h+='</div>';
  h+='<div class="sidebar-footer">数据 v'+(DB?DB.meta.version:'?.?')+' · '+(DB?DB.meta.updated:'加载中…')+'<br>9域·36模块·三级穿透</div>';
  document.getElementById('sidebar').innerHTML=h;
}
function toggleDomain(id){
  var el=document.getElementById('domain-'+id);if(el)el.classList.toggle('open');
  currentDomain=id;
}
function navTo(viewId,el){
  if(currentView===viewId)return;
  currentView=viewId;
  // Update nav active
  var allNav=document.querySelectorAll('.nav-child');for(var i=0;i<allNav.length;i++)allNav[i].classList.remove('active');
  var navEl=document.getElementById('nav-'+viewId);if(navEl)navEl.classList.add('active');
  // Auto-open domain
  for(var di=0;di<NAV.length;di++){var d=NAV[di];for(var cj=0;cj<d.children.length;cj++){if(d.children[cj].id===viewId){var domEl=document.getElementById('domain-'+d.id);if(domEl)domEl.classList.add('open');currentDomain=d.id}}}
  // Clear main
  var mc=document.getElementById('main-content');if(!mc)return;
  mc.innerHTML='<div class="loading"><div class="spinner"></div><p style="margin-top:12px">加载中...</p></div>';
  sortState={key:null,asc:true};
  setTimeout(function(){renderView(viewId)},10);
}
function setMain(h){var mc=document.getElementById('main-content');if(mc)mc.innerHTML=h}

/* ===== 面包屑 ===== */
function breadcrumb(domainId,moduleLabel){
  var dom=null;for(var i=0;i<NAV.length;i++){if(NAV[i].id===domainId){dom=NAV[i];break}}
  return'<div class="breadcrumb">管理后台 / <span>'+(dom?dom.label:domainId)+'</span> / '+moduleLabel+'</div>';
}

/* ===== 四层详情通用函数 ===== */
function renderLayerDetail(p,showDesc){
  var h='';
  if(showDesc&&p.description)h+='<div class="field"><span class="field-label">📝 描述</span><div class="field-value">'+escH(p.description)+'</div></div>';
  h+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:8px;margin-top:8px">';
  // 物理层
  h+='<div class="layer-section l-phy"><div class="layer-title t-phy">🔩 物理层</div>';
  h+='<div style="font-size:.73em">ID: '+escH(p.id||'—')+' · 类型: '+escH(p.type||p.category||'—')+' · 族: '+escH(p.family||'—')+'</div>';
  if(p.url)h+='<div style="font-size:.73em">路径: <code>'+escH(p.url)+'</code></div>';
  if(p.source)h+='<div style="font-size:.73em">来源: '+escH(p.source)+' · 置信度: '+escH(String(p.confidence||'—'))+'</div>';
  h+='</div>';
  // 化学层
  h+='<div class="layer-section l-chem"><div class="layer-title t-chem">⚗️ 化学层</div>';
  var qs=p.quality_score||0,vi=p.vi_compliance||0,ca=p.content_accuracy||0,ux=p.ux_rating||0;
  h+='<div style="font-size:.73em">质量: '+qs+' · VI: '+vi+' · 内容: '+ca+' · UX: '+ux+'</div>';
  if(p.lifecycle_stage)h+='<div style="font-size:.73em">阶段: '+LC_LABELS[p.lifecycle_stage]+' · 成熟度: '+escH(p.maturity||'—')+'</div>';
  if(p.dev_batch)h+='<div style="font-size:.73em">批次: '+escH(p.dev_batch)+' · '+escH(p.dev_start||'')+' → '+escH(p.dev_deadline||'')+'</div>';
  if(p.quality_issues&&p.quality_issues.length)h+='<div style="font-size:.73em">问题: '+p.quality_issues.map(function(x){return'<span class="tag tag-red">'+escH(x)+'</span>'}).join(' ')+'</div>';
  h+='</div>';
  // 生物层
  h+='<div class="layer-section l-bio"><div class="layer-title t-bio">🧬 生物层</div>';
  if(p.trigger_conditions)h+='<div style="font-size:.73em">触发: '+escH(p.trigger_conditions)+'</div>';
  if(p.feedback_loop)h+='<div style="font-size:.73em">反馈: '+escH(p.feedback_loop)+'</div>';
  if(p.adaptation_rule)h+='<div style="font-size:.73em">适应: '+escH(p.adaptation_rule)+'</div>';
  if(p.connected_rules&&p.connected_rules.length)h+='<div style="font-size:.73em">关联规则: '+p.connected_rules.map(function(r){return'<span class="tag tag-gold">'+escH(r)+'</span>'}).join(' ')+'</div>';
  h+='</div>';
  // 心理层
  h+='<div class="layer-section l-psy"><div class="layer-title t-psy">🧠 心理层</div>';
  if(p.audience_persona)h+='<div style="font-size:.73em">👤 '+escH(p.audience_persona)+'</div>';
  if(p.use_scenario)h+='<div style="font-size:.73em">🎬 '+escH(p.use_scenario)+'</div>';
  var dv=p.decision_value||0;
  if(p.decision_value_desc)h+='<div style="font-size:.73em">💡 决策价值: '+dv+' — '+escH(p.decision_value_desc)+'</div>';
  if(p.pricing_tier)h+='<div style="font-size:.73em">💰 '+escH(p.pricing_tier)+'</div>';
  if(p.self_description)h+='<div style="font-size:.73em">📋 '+escH(p.self_description)+'</div>';
  h+='</div></div>';
  return h;
}

/* ===== 视图路由 ===== */
function renderView(id){
  if(!DB){setMain(renderDegrade());return}
  var fn=viewRenderers[id];
  if(fn){setMain(fn())}else{setMain(placeholder('建设中',id+' · 该子模块数据待完善'))}
}
var viewRenderers={};

/* ================================================================
   01 战略仪表盘
   ================================================================ */
viewRenderers['strategy-kpi']=function(){
  var m=DB.meta||{},prods=DB.products||[],rules=DB.living_rules||[],tasks=DB.tasks||[];
  var qsAvg=prods.length?Math.round(prods.reduce(function(s,p){return s+(p.quality_score||0)},0)/prods.length):0;
  var activeRules=rules.filter(function(r){return r.status==='active'}).length;
  var openTasks=tasks.filter(function(t){return!/已完成/.test(t.status||'')}).length;
  var h=breadcrumb('strategy','KPI仪表盘');
  h+='<div class="panel-header"><div><h2>📊 核心KPI仪表盘</h2><div class="meta">实时监控 · 驾驶舱协同</div></div></div>';
  h+='<div class="graph-stat">';
  h+='<div class="stat-card" onclick="navTo(\'product-overview\')"><div class="stat-num">'+m.product_total+'</div><div class="stat-label">📦 产品总数</div><div class="stat-bar"><div class="fill fill-gold" style="width:100%"></div></div></div>';
  h+='<div class="stat-card" onclick="navTo(\'knowledge-graph\')"><div class="stat-num">'+m.knowledge_graph_density+'%</div><div class="stat-label">🕸️ 知识图谱密度</div><div class="stat-bar"><div class="fill fill-red" style="width:'+m.knowledge_graph_density+'%"></div></div></div>';
  h+='<div class="stat-card" onclick="navTo(\'product-quality\')"><div class="stat-num">'+qsAvg+'</div><div class="stat-label">✅ 平均质量分</div><div class="stat-bar"><div class="fill fill-green" style="width:'+qsAvg+'%"></div></div></div>';
  h+='<div class="stat-card" onclick="navTo(\'gov-rules\')"><div class="stat-num">'+activeRules+'</div><div class="stat-label">🧬 活跃规则</div><div class="stat-bar"><div class="fill fill-gold" style="width:100%"></div></div></div>';
  h+='</div>';
  h+='<div class="graph-stat">';
  h+='<div class="stat-card" onclick="navTo(\'ops-tasks\')"><div class="stat-num">'+openTasks+'</div><div class="stat-label">⚡ 未闭环任务</div><div class="stat-bar"><div class="fill fill-warn" style="width:100%"></div></div></div>';
  h+='<div class="stat-card" onclick="navTo(\'strategy-milestone\')"><div class="stat-num">'+m.total_entities+'</div><div class="stat-label">📊 实体总数</div><div class="stat-bar"><div class="fill fill-gold" style="width:100%"></div></div></div>';
  h+='<div class="stat-card" onclick="navTo(\'customer-360\')"><div class="stat-num">'+(DB.customers||[]).length+'</div><div class="stat-label">👤 核心客户</div><div class="stat-bar"><div class="fill fill-gold" style="width:100%"></div></div></div>';
  h+='<div class="stat-card"><div class="stat-num">16</div><div class="stat-label">⏰ Cron活跃</div><div class="stat-bar"><div class="fill fill-green" style="width:100%"></div></div></div>';
  h+='</div>';
  // 四层覆盖度
  if(m.four_layer_coverage){var flc=m.four_layer_coverage;
    h+='<h3 style="font-size:.92em;margin:16px 0 8px">🏗️ 四层覆盖度</h3><div class="graph-stat">';
    var fll=[{k:'physical',l:'🔩 物理层'},{k:'chemical',l:'⚗️ 化学层'},{k:'biological',l:'🧬 生物层'},{k:'psychological',l:'🧠 心理层'}];
    for(var fli=0;fli<fll.length;fli++){var flk=fll[fli],fls=(flc[flk.k]||{}).score||0;h+='<div class="stat-card"><div class="stat-num">'+fls+'%</div><div class="stat-label">'+flk.l+'</div><div class="stat-bar"><div class="fill fill-green" style="width:'+fls+'%"></div></div></div>'}
    h+='</div>';
  }
  return h;
};

viewRenderers['strategy-map']=function(){
  var h=breadcrumb('strategy','战略地图')+'<div class="panel-header"><div><h2>🗺️ BSC四视角战略地图</h2><div class="meta">财务·客户·流程·学习 — 四视角联动</div></div></div>';
  h+='<div class="graph-stat">';
  h+='<div class="stat-card" style="border-left:4px solid var(--red)" onclick="navTo(\'finance-overview\')"><div class="stat-num" style="color:var(--red)">💰</div><div class="stat-label">财务视角</div><div style="font-size:.73em;color:var(--ink-light);margin-top:4px">收入·成本·利润·定价</div></div>';
  h+='<div class="stat-card" style="border-left:4px solid var(--gold)" onclick="navTo(\'customer-360\')"><div class="stat-num" style="color:var(--gold)">👤</div><div class="stat-label">客户视角</div><div style="font-size:.73em;color:var(--ink-light);margin-top:4px">满意度·获客·留存·NPS</div></div>';
  h+='<div class="stat-card" style="border-left:4px solid var(--green)" onclick="navTo(\'product-overview\')"><div class="stat-num" style="color:var(--green)">⚙️</div><div class="stat-label">内部流程视角</div><div style="font-size:.73em;color:var(--ink-light);margin-top:4px">质量·效率·创新·合规</div></div>';
  h+='<div class="stat-card" style="border-left:4px solid var(--blue)" onclick="navTo(\'knowledge-learn\')"><div class="stat-num" style="color:var(--blue)">🌱</div><div class="stat-label">学习与成长视角</div><div style="font-size:.73em;color:var(--ink-light);margin-top:4px">人才·知识·技术·组织</div></div>';
  h+='</div>';
  h+=placeholder('战略地图详情','BSC四视角因果链将在数据完善后可视化呈现。当前可点击上方卡片跳转各管理域');
  return h;
};

viewRenderers['strategy-milestone']=function(){
  var h=breadcrumb('strategy','里程碑看板')+'<div class="panel-header"><div><h2>🏁 里程碑看板</h2><div class="meta">105天·6阶段·19关键时刻·3波次开发</div></div></div>';
  h+='<div class="stat-grid">';
  h+='<div class="stat-card"><div class="stat-num">2/15</div><div class="stat-label">💡 满意姐初驻</div><div class="stat-bar"><div class="fill fill-green" style="width:100%"></div></div></div>';
  h+='<div class="stat-card"><div class="stat-num">3/26</div><div class="stat-label">🧪 试运营</div><div class="stat-bar"><div class="fill fill-gold" style="width:100%"></div></div></div>';
  h+='<div class="stat-card"><div class="stat-num">4/24</div><div class="stat-label">✨ 54天完成</div><div class="stat-bar"><div class="fill fill-green" style="width:100%"></div></div></div>';
  h+='<div class="stat-card"><div class="stat-num">5/30</div><div class="stat-label">📦 312产品名录</div><div class="stat-bar"><div class="fill fill-gold" style="width:100%"></div></div></div>';
  h+='</div>';
  h+='<div class="stat-grid">';
  h+='<div class="stat-card"><div class="stat-num">6/01</div><div class="stat-label">🌊 第一波·253件</div><div class="stat-bar"><div class="fill fill-red" style="width:70%"></div></div></div>';
  h+='<div class="stat-card"><div class="stat-num">6/14</div><div class="stat-label">✅ 第一波截止</div><div class="stat-bar"><div class="fill fill-gold" style="width:100%"></div></div></div>';
  h+='<div class="stat-card"><div class="stat-num">7/01</div><div class="stat-label">🌊 第二波·43件</div><div class="stat-bar"><div class="fill fill-gold" style="width:40%"></div></div></div>';
  h+='<div class="stat-card"><div class="stat-num">8/01</div><div class="stat-label">🌊 第三波·16件</div><div class="stat-bar"><div class="fill fill-green" style="width:30%"></div></div></div>';
  h+='</div>';
  return h;
};

viewRenderers['strategy-risk']=function(){
  var h=breadcrumb('strategy','风险雷达')+'<div class="panel-header"><div><h2>🎯 风险雷达</h2><div class="meta">识别·评级·应对 · 四骑士信号监测</div></div></div>';
  var risks=[
    {l:'数据资产丢失',s:'中',d:'Git历史已净化·备份机制运行中·但缺少异地容灾'},
    {l:'知识图谱密度不足',s:'中',d:'43.9%密度·需持续加强连接·目标≥70%'},
    {l:'产品UX评级偏低',s:'高',d:'平均42.1分·228件原型阶段·需第一波打磨'},
    {l:'心理层数据覆盖弱',s:'中',d:'v2.0补齐至100%·但数据质量为算法推测·需人工审核'},
    {l:'驾驶舱实时同步缺失',s:'低',d:'JSON fetch替代方案运行稳定·SQLite中间件延期'}
  ];
  h+='<table class="data-table"><thead><tr><th>风险项</th><th>等级</th><th>说明</th></tr></thead><tbody>';
  for(var ri=0;ri<risks.length;ri++){var rk=risks[ri],sc=rk.s==='高'?'tag-red':(rk.s==='中'?'tag-gold':'tag-gray');h+='<tr><td><b>'+escH(rk.l)+'</b></td><td><span class="tag '+sc+'">'+rk.s+'</span></td><td style="font-size:.78em">'+escH(rk.d)+'</td></tr>'}
  h+='</tbody></table>';
  return h;
};

/* ================================================================
   02 产品全生命周期
   ================================================================ */
viewRenderers['product-overview']=function(){
  var prods=DB.products||[],m=DB.meta||{},ls=m.lifecycle_stages||{},so=['L0_概念','L1_原型','L2_内测','L3_打磨','L4_精品','L5_维护','L6_退役'];
  var h=breadcrumb('product','产品总览')+'<div class="panel-header"><div><h2>📦 产品全生命周期总览</h2><div class="meta">'+prods.length+' 产品 · 7阶段 · '+Object.keys(m.product_families||{}).length+' 族</div></div></div>';
  h+='<div class="stat-grid">';
  for(var si=0;si<so.length;si++){var sk=so[si],sv=ls[sk]||0;if(sv>0){h+='<div class="stat-card" onclick="navTo(\'product-pipeline\')"><div class="stat-num">'+sv+'</div><div class="stat-label">'+LC_LABELS[sk]+'</div><div class="stat-bar"><div class="fill fill-gold" style="width:'+Math.min(sv/312*400,100)+'%"></div></div></div>'}}
  h+='</div>';
  // 质量快速筛选
  h+='<div style="margin:12px 0"><h3 style="font-size:.85em;margin-bottom:6px">🎯 质量筛选</h3><div class="chip-wrap">';
  h+='<div class="chip" onclick="filtQuality(85,100)">🟢 优秀(85-100)</div><div class="chip" onclick="filtQuality(70,84)">🟡 良好(70-84)</div><div class="chip" onclick="filtQuality(50,69)">🟠 待改进(50-69)</div><div class="chip" onclick="filtQuality(0,49)">🔴 不合格(<50)</div><div class="chip" style="background:var(--warm)" onclick="resetFilt()">🔄 全部</div></div></div>';
  var fks=Object.keys(m.product_families||{});var sf=so.map(function(k){return LC_LABELS[k]});
  h+=toolbar('prod-ov','搜索产品名/描述...',fks.concat(sf));
  h+='<div style="overflow-x:auto"><table class="data-table" id="tbl-prod-ov"><thead><tr><th onclick="sortTbl(\'prod-ov\',\'id\',this)">ID<span class="sort-arrow"></span></th><th onclick="sortTbl(\'prod-ov\',\'name\',this)">产品名<span class="sort-arrow"></span></th><th onclick="sortTbl(\'prod-ov\',\'family\',this)">族<span class="sort-arrow"></span></th><th onclick="sortTbl(\'prod-ov\',\'lifecycle_stage\',this)">生命周期<span class="sort-arrow"></span></th><th onclick="sortTbl(\'prod-ov\',\'quality_score\',this)">质量<span class="sort-arrow"></span></th><th onclick="sortTbl(\'prod-ov\',\'decision_value\',this)">决策价值<span class="sort-arrow"></span></th><th onclick