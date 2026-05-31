const fs = require("fs");
const html = fs.readFileSync("satisficing-lab/dashboard-v3.html", "utf8");
const js = html.match(/<script>([\s\S]*?)<\/script>/)[1];

// 找出全局变量
const globalDecls = new Set();
const globalRegex = /^var\s+(\w+)/gm;
let m;
while ((m = globalRegex.exec(js)) !== null) {
  const before = js.substring(0, m.index);
  const depth = (before.match(/\{/g) || []).length - (before.match(/\}/g) || []).length;
  if (depth <= 1) globalDecls.add(m[1]);
}

// 检查每个函数
const funcRegex = /^function\s+(\w+)\s*\(([^)]*)\)/gm;
while ((m = funcRegex.exec(js)) !== null) {
  const funcName = m[1];
  const params = m[2].split(",").map(p => p.trim()).filter(Boolean);
  
  // 找函数体
  const start = m.index;
  let depth = 0, inFunc = false, bodyEnd = start;
  for (let i = start; i < js.length; i++) {
    if (js[i] === "{") { depth++; inFunc = true; }
    else if (js[i] === "}") { depth--; if (inFunc && depth === 0) { bodyEnd = i+1; break; } }
  }
  const body = js.substring(start, bodyEnd);
  
  // 函数内的 var 声明
  const localVars = new Set(params);
  const localRegex = /\bvar\s+(\w+)/g;
  let lm;
  while ((lm = localRegex.exec(body)) !== null) localVars.add(lm[1]);
  
  // 提取函数内所有标识符 (排除字符串)
  const textBody = body.replace(/"[^"]*"|'[^']*'/g, '""');
  const words = textBody.match(/\b([a-zA-Z_]\w+)\b/g) || [];
  
  // 已知的全局函数
  const globalFuncs = new Set([
    'h','a','setDate','dataBase','boot','buildNav','switchTab','renderOverview',
    'ov','renderProducts','renderDetailRows','setProdFilt','toggleDetail',
    'toggleSel','updateCmpBar','clearSel','openCmp','closeCmp','renderTasks',
    'renderHealth','renderActivity','renderCustomers','renderKnowledge',
    'renderGovernance','renderOrganization','renderArchaeology','renderCities',
    'renderFlows','renderFlywheel','renderChemistry','renderHelp',
    'switchHelpView','sc'
  ]);
  
  // 内置 + DOM
  const builtins = new Set([
    'document','window','console','location','sessionStorage','localStorage',
    'alert','Date','Math','Error','Promise','setTimeout','Array','Object',
    'String','RegExp','JSON','parseInt','parseFloat','Number','Boolean',
    'fetch','NaN','isNaN','undefined','true','false','null','this','arguments',
    'new','return','if','else','for','while','do','switch','case','break','continue',
    'typeof','instanceof','throw','try','catch','finally','function','var','in','of',
    'hasOwnProperty','toFixed','apply','call','bind','toString'
  ]);
  
  // DOM 属性和方法 (不报 ReferenceError)
  const domProps = new Set([
    'length','push','indexOf','splice','slice','sort','concat','join','split','replace',
    'substring','substr','trim','toLowerCase','toUpperCase','charAt','charCodeAt',
    'getElementById','querySelector','querySelectorAll','createElement',
    'getAttribute','setAttribute','addEventListener','removeEventListener',
    'getItem','setItem','removeItem','clear','keys','values','entries','forEach','map','filter','reduce',
    'innerHTML','textContent','value','checked','style','classList','parentNode',
    'id','className','tagName','nodeName','nodeType','children','childNodes',
    'firstChild','lastChild','nextSibling','previousSibling','parentElement',
    'add','remove','toggle','contains','replace','get','set','has',
    'display','background','color','fontSize','fontWeight','margin','padding','border',
    'width','height','opacity','cursor','textAlign','borderRadius','boxShadow',
    'transition','transform','overflow','whiteSpace','textDecoration',
    'flexDirection','alignItems','justifyContent','gap','flexWrap','gridTemplateColumns',
    'disabled','readOnly','placeholder','href','target','rel','type','name','title',
    'onclick','onkeydown','onchange','oninput','onsubmit','onload','onerror',
    'active','hidden','show','none','block','flex','grid','inline','inlineBlock','inlineFlex',
    'autofocus','selected','multiple','required','min','max','step','pattern',
    'checked','indeterminate','defaultChecked','defaultValue','defaultSelected',
    'getDate','getDay','getFullYear','getHours','getMinutes','getMonth','getSeconds','getTime',
    'padStart','padEnd','toLocaleString','toLocaleDateString','toLocaleTimeString',
    'now','parse','UTC','floor','ceil','round','abs','max','min','pow','sqrt','random',
    'fromCharCode','charCodeAt'
  ]);
  
  // HTML 中的常见词
  const htmlWords = new Set([
    'div','span','p','h1','h2','h3','h4','h5','h6','a','ul','li','ol','table','thead','tbody','tr','th','td',
    'button','input','select','option','textarea','label','form','img','iframe','canvas','video','audio',
    'header','footer','nav','main','section','article','aside','details','summary','figure','figcaption',
    'strong','em','i','b','u','s','small','sub','sup','code','pre','blockquote','br','hr',
    'tab','panel','card','bar','badge','icon','btn','col','row','cell','wrap','grid',
    'section','head','detail','overview','filt','filters','products','tasks','knowledge',
    'activity','customers','governance','organization','archaeology','health','help','chemistry',
    'flywheel','flows','cities','windows','admin','catalog','cron','crons',
    'prod','prods','task','cust','dec','doc','docs','terms','insts','avatars',
    'hlp','mgr','dev','user','manager','view','link','noopener','rel','checkbox',
    'outline','cnt','pct','idx','arr','num','sub','item','items','el','elem',
    'json','amp','lt','gt','quot','amp','msg','note','info','warn','error','success',
    'ok','bad','good','fine','cool','warm','hot','cold','old','new','big','small',
    'top','left','right','bottom','center','middle','between','around','stretch',
    'red','green','blue','gold','amber','white','black','ink','light','lighter',
    'background','border','color','font','size','weight','margin','padding',
    'solid','dashed','dotted','double','groove','ridge','inset','outset',
    'transparent','inherit','initial','unset','none','auto',
    'repeat','noRepeat','round','space','template','column','columns',
    'text','nowrap','decoration','opacity','cursor','pointer',
    'timestamp','schedule','trigger','kind','priority','source','status','description',
    'resolution','outcome','industry','stage','tier','phase','cycle','version',
    'confidence','context','significance','era','purpose','definition','dimension',
    'element','language','frequency','category','topics','needs','scene','domain',
    'file_path','relationship_type','target_user','decision_type','decision_value',
    'needs_summary','contribution_score','lifecycle_stage','target_date',
    'avg_score','health_score','stability_score','quality_score','quality_confidence',
    'speed_multiplier','learning_progress','total_heat','total_cogs','totalCount','aliveCount',
    'total_entities','total_connections','total_entities_covered','verified_connections',
    'total_crons','cron_connected','online_count','premium_count','doc_count',
    'orphan_products','zombie_tasks','broken','dormant','idle','degraded','failed','stale',
    'launchable','active','demoted','promoted','killed','merged','archived',
    'strong_connections','medium_connections','weak_connections',
    'knowledge_graph_density','product_index_consistency',
    'total_runs','total_scanned','total_issues','total_before','total_after',
    'quality_score_note','product_families','living_rules','living_rules_status',
    'biological_health','orchestration_health','perpetual_control','capacity','scan',
    'events','scripts','workflows','documents','customers','cities','connections',
    'milestones','instructions_set','customer_profiles','decisions','clusters',
    'projects','quality_metrics','growth_metrics','vi_standards','lifecycle_stages',
    'governance_frameworks','content_assets','scoring_models','simulation_scenarios',
    'historical_artifacts','additional_discoveries','living_rules',
    'total_scripts','total_stages','llm_stats','products_evaluated',
    'heat','heating','chem','chemistry','org','pc','ls','fw','lr','bh','bd','pf','meta',
    'first_run_complete','simulation_rounds','signals','cognition_events',
    'action_events','verification_events','learning_events',
    'flow_model','flow_layers','combined','by_type','change_log','consistency_check',
    'health_audit_report','lifecycle_management','portfolio_rationalization',
    'product_audit','recent_runs','rerank','standards_version','last_run',
    'last_run_elapsed_ms','elapsed_ms','run_id','events_count','json_size_mb',
    'products_under_60','products_under_40','health_score','check','checked_at',
    'oldAvg','diff','vs','actual','expected','root_cause',
    'avatar_rankings','llm_avg','distribution','braking','effect',
    'total_open','open','high','medium','low',
    'report','updated','file','path','data','key','keys','val','value','label',
    'rank','score','weight','unit','ha','lk','lyrs','ts','ms','mb',
    'prefix','suffix','separator','placeholder','default','readonly','required',
    'focus','blur','change','click','submit','reset','load','waiting','complete','ready','done',
    'local','remote','host','port','protocol','hostname','pathname','search','hash','origin',
    'all','body','head','html','title','base','link','meta','script','noscript','style',
    'String','replace','h','a','sc','ov',
    'breakdown','cron_connected','four_layer_coverage','anti_island',
    'B8860B','C23B22','C2780A','e67e22','e74c3c','f0f7ff','f0fff4','faf5ff',
    'f8f4f8','f8fdf8','fdf2f2','fdf8f0','fdedec','fef9e7','d5f5e3','ebdef0',
    'egbertie','github','githubusercontent','htmlpreview','raw','satisficing','lab',
    'com','io','org','https','http','url','URL','Pages','GitHub','absolute',
    'L1','L2','L3','L4','L5','R1','R2','R3','P0','P1','P2','Pre',
    'MB','ms','ha','lk','lyrs','ts'
  ]);
  
  const unknown = new Set();
  words.forEach(w => {
    if (builtins.has(w)) return;
    if (domProps.has(w)) return;
    if (htmlWords.has(w)) return;
    if (localVars.has(w)) return;
    if (globalDecls.has(w)) return;
    if (globalFuncs.has(w)) return;
    if (w === funcName) return;
    unknown.add(w);
  });
  
  if (unknown.size > 0) {
    console.log(`[${funcName}] unknown: ${[...unknown].join(', ')}`);
  }
}

console.log(`\nGlobal vars: ${[...globalDecls].join(', ')}`);
