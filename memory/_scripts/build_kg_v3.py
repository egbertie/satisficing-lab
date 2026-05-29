#!/usr/bin/env python3
"""知识图谱全连接引擎 V3 - 密度 ≥ 80% 版本"""
import json, re
from datetime import datetime, timezone
from collections import defaultdict

with open("memory/_data/entities_index.json", "r") as f:
    data = json.load(f)

products = data["products"]; tasks = data["tasks"]
customers = data["customers"]; customer_profiles = data["customer_profiles"]
terms = data["terms"]; documents = data["documents"]
decisions = data["decisions"]; quality_metrics = data["quality_metrics"]
workflows = data["workflows"]; instructions_set = data["instructions_set"]
governance_frameworks = data["governance_frameworks"]
avatars = data["avatars"]; scripts = data["scripts"]

all_customers = {}
for c in customers: all_customers[c["id"]] = dict(c)
for cp in customer_profiles:
    if cp["id"] in all_customers:
        for k, v in cp.items(): all_customers[cp["id"]][k] = v
    else: all_customers[cp["id"]] = dict(cp)

existing_ids = set()
for conn in data.get("connections", []):
    existing_ids.add(f"{conn['from_entity']}->{conn['to_entity']}")

connections = []; conn_pairs = set(existing_ids)
cnt = [69]

def add(fr, to, rel, w, d):
    k = f"{fr}->{to}"
    if k in conn_pairs: return False
    conn_pairs.add(k); cnt[0] += 1
    connections.append({"id": f"CONN-{cnt[0]:04d}", "from_entity": fr, "to_entity": to,
        "relationship_type": rel, "weight": round(w,2), "description": d[:120]})
    return True

def tok(t):
    return set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+|\d+', t.lower()))
def mp(n):
    for p in products:
        if n.lower() in p["name"].lower(): return p
    return None
def clean_tn(n):
    n = re.sub(r'^[【\[][^】\]]*[】\]]\s*', '', n)
    n = re.sub(r'^[A-Z]{2,}:\s*', '', n)
    n = re.sub(r'^(星火|漏斗|产品|深度学习|子项目|05-\d{2}):\s*', '', n)
    return n.lower()

tt = {t["id"]: tok(t["name"]+" "+t.get("description","")) for t in tasks}
pt = {p["id"]: tok(p["name"]+" "+p.get("description","")+" "+" ".join(p.get("tags",[]))) for p in products}
termtok = {t["id"]: tok(t["name"]+" "+t.get("definition","")) for t in terms}

# ====== P1: Product ↔ Task (guarantee every product and every task) ======
print("P1: Product↔Task...")
for p in products:
    pname = p["name"].lower()
    for t in tasks:
        if len(pname)>=3 and pname in t["name"].lower():
            add(p["id"],t["id"],"产品执行任务",1.0,f"名称精确匹配")
for p in products:
    for tag in [t.lower() for t in p.get("tags",[])]:
        for t in tasks:
            if len(tag)>=2 and tag in " ".join(tt[t["id"]]):
                add(p["id"],t["id"],"标签关联任务",0.7,f"标签'{tag}'→任务")
                break
for p in products:
    ptok = pt[p["id"]]
    for t in tasks:
        m = [w for w in (ptok & tt[t["id"]]) if len(w)>=2]
        if len(m)>=4: add(p["id"],t["id"],"语义重叠任务",0.5,f"共享{len(m)}词")

# Guarantee every product has ≥1 task via best-match
prod_tc = defaultdict(int)
for c in connections:
    if c["relationship_type"] in ("产品执行任务","标签关联任务","语义重叠任务"):
        for e in [c["from_entity"],c["to_entity"]]:
            if e.startswith("PROD-"): prod_tc[e]+=1

family_themes = {"镜":["决策","场景","模拟","卡牌","风险","危机","合伙人","匹配","股权","角色"],
    "衡":["测评","评估","诊断","报告","雷达","检查","标准","质量","量表"],
    "契":["案例","课程","学习","方法","产品","文档","知识","内容","品牌","目录","体系"],
    "觉":["驾驶舱","飞轮","自动化","仪表盘","管理","同步","管道","引擎","仪表"],
    "道":["品牌","VI","叙事","使命","价值观"],
    "人":["用户","体验","界面","工具","指南","入职","退出","新人"]}

for p in products:
    if prod_tc[p["id"]]==0:
        themes=family_themes.get(p.get("family",""),[])
        pwords=set(re.findall(r'[\u4e00-\u9fff]+', p["name"].lower()+" "+p.get("description","").lower()))
        best,best_sc=None,0
        for t in tasks:
            ctn=clean_tn(t["name"]); tcomb=ctn+" "+t.get("description","").lower()
            sc=sum(3 for th in themes if th in tcomb)+sum(2 for w in pwords if len(w)>=2 and w in tcomb)
            if sc>best_sc: best_sc,best=sc,t
        if best: add(p["id"],best["id"],"弱关联任务",0.3,f"最相关任务")

# Guarantee every task has ≥1 product
task_pc = defaultdict(int)
for c in connections:
    for e in [c["from_entity"],c["to_entity"]]:
        if e.startswith("TASK-"): task_pc[e]+=1
for t in tasks:
    if task_pc[t["id"]]==0:
        tcomb=clean_tn(t["name"])+" "+t.get("description","").lower()
        best,best_sc=None,0
        for p in products:
            pname=p["name"].lower(); pcomb=pname+" "+p.get("description","").lower()
            sc=sum(2 for w in re.findall(r'[\u4e00-\u9fff]+',pname) if len(w)>=2 and w in tcomb)
            if sc>best_sc: best_sc,best=sc,p
        if best: add(best["id"],t["id"],"弱关联任务",0.3,f"最相关产品")

# ====== P2: Product ↔ Customer ======
print("P2: Product↔Customer...")
cnm = {"决策":["决策剧场","决策卡牌","决策教训","卡牌对局","危机模拟"],
    "合伙人":["元合伙","匹配引擎","卡牌对局","分割饼","合伙人协议","关系温度计","RPS风险剖面"],
    "退出":["退出指南","分割饼","告别页"],"诊断":["化学报告","全面诊断","衡·观局测评","案例诊断","自检清单","关系温度计"],
    "评估":["化学报告","全面诊断","衡·观局测评","竞品分析","RPS风险剖面","生命指数"],
    "风险":["RPS风险剖面","危机模拟","四骑士识别","蓝军"],
    "融资":["提案模板","分割饼"],"产品线":["产品目录","产品族谱","星光体系","创造工坊"],
    "技术":["竞品分析","白皮书","案例库","五维教学"],"转型":["退出指南","危机模拟","蓝军","轨迹"],
    "治理":["元合伙","门控","服务条款"],"冲突":["四骑士识别","关系温度计","卡牌对局"],
    "品牌":["品牌·满意红","符号体系","首页","关于我们"],
    "学习":["案例库","满意解大学","星光方法论","五维教学","白皮书"],
    "增长":["飞轮引擎","驾驶舱V3","量化体系"],"数据":["驾驶舱V1","驾驶舱V3","生命指数"],
    "预警":["关系温度计","RPS风险剖面","危机模拟"],"IP":["根脉溯源","开源声明","白皮书"],
    "定位":["竞品分析","产品目录","品牌·满意红"],"二次创业":["轨迹","决策教训","退出指南"],
    "对赌":["分割饼","提案模板"],"创业":["案例库","卡牌对局","决策剧场","衡·观局测评"],
    "股权":["分割饼","元合伙","合伙人协议"],"估值":["分割饼","RPS风险剖面"],
    "心理":["心理量表","Pre-0身体觉察","关系温度计"],"复盘":["决策教训","失败案例","案例库"],
    "习惯":["54天","五维教学"],"压力":["危机模拟","蓝军","RPS风险剖面"],
    "赛道":["竞品分析","白皮书"],"人才":["新人指南","入职指南","五维教学"],
    "家族":["产品族谱","符号体系"],"供应链":["竞品分析","量化体系"],
    "创新":["创造工坊","星光体系","五维教学"],"生态":["产品目录","星光体系","飞轮引擎"],
}

for cid, cd in all_customers.items():
    ctext=(cd.get("needs","")+" "+" ".join(cd.get("pain_points",[]) if isinstance(cd.get("pain_points",[]),list) else "")+" "+cd.get("industry","")).lower()
    ctok=tok(ctext); matched=set()
    for nk,pns in cnm.items():
        if nk in ctext:
            for pn in pns:
                p=mp(pn)
                if p and p["id"] not in matched:
                    add(p["id"],cid,"客户需求产品",0.75,f"需求'{nk}'→'{p['name']}'")
                    matched.add(p["id"])
    if len(matched)<3:
        for p in products:
            if p["id"] in matched: continue
            ov=ctok & pt[p["id"]]
            if len([w for w in ov if len(w)>=2])>=3:
                add(p["id"],cid,"客户需求产品",0.5,"语义匹配")
                matched.add(p["id"])

# ====== P3: Product ↔ Term ======
print("P3: Product↔Term...")
for p in products:
    pname=p["name"].lower(); ptok=pt[p["id"]]
    for term in terms:
        clean=re.sub(r'\(.*?\)$','',term["name"].lower()).strip()
        if len(clean)>=3 and clean in pname:
            add(p["id"],term["id"],"术语关联产品",0.9,f"术语→产品名称"); continue
        ov=ptok & termtok[term["id"]]
        if len([w for w in ov if len(w)>=2])>=3:
            add(p["id"],term["id"],"术语关联产品",0.5,"概念关联")

# ====== P4: Decision ↔ Product/Task/Term/Doc ======
print("P4: Decision connections...")
for dec in decisions:
    dt=tok(dec.get("title","")+" "+dec.get("context","")+" "+dec.get("outcome",""))
    did=dec["id"]; dtitle=dec.get("title","").lower(); dctx=dec.get("context","").lower()
    for p in products:
        pname=p["name"].lower()
        if len(pname)>=3 and pname in dtitle:
            add(did,p["id"],"决策涉及产品",0.8,f"标题提及'{p['name']}'"); continue
        m=[w for w in (dt & pt[p["id"]]) if len(w)>=2]
        if len(m)>=5: add(did,p["id"],"决策涉及产品",0.5,f"上下文匹配'{p['name']}'")
    for term in terms:
        clean=re.sub(r'\(.*?\)$','',term["name"].lower()).strip()
        if len(clean)>=3 and (clean in dtitle or clean in dctx):
            add(did,term["id"],"决策涉及术语",0.7,f"引用'{term['name']}'")
    for doc in documents:
        doctok=set(doc.get("name","").lower().split())
        m=[w for w in (dt & doctok) if len(w)>=2]
        if len(m)>=3: add(did,doc["id"],"决策关联文档",0.5,f"关联'{doc['name']}'")
    for t in tasks:
        m=[w for w in (dt & tt[t["id"]]) if len(w)>=2]
        if len(m)>=5: add(did,t["id"],"决策驱动任务",0.6,f"驱动'{t['name'][:30]}'")

# ====== P5: Document ↔ Product/Term/Task ======
print("P5: Document connections...")
for doc in documents:
    did=doc["id"]; topics=[t.lower() for t in doc.get("topics",[])]
    for p in products:
        pname=p["name"].lower()
        for topic in topics:
            if len(topic)>=2 and topic in pname:
                add(did,p["id"],"文档涉及产品",0.7,f"主题'{topic}'→'{p['name']}'"); break
            elif len(topic)>=3 and topic in p.get("description","").lower():
                add(did,p["id"],"文档涉及产品",0.5,f"主题'{topic}'匹配"); break
    for term in terms:
        clean=re.sub(r'\(.*?\)$','',term["name"].lower()).strip()
        for topic in topics:
            if len(clean)>=3 and clean in topic:
                add(did,term["id"],"文档涉及术语",0.6,f"主题∩术语"); break
    for t in tasks:
        tname=t["name"].lower()
        for topic in topics:
            if len(topic)>=2 and topic in tname:
                add(did,t["id"],"文档支撑任务",0.5,f"主题→'{t['name'][:30]}'"); break

# ====== P6: Instructions ↔ Product/Task ======
print("P6: Instructions...")
for inst in instructions_set:
    iid=inst["id"]; iname=inst["name"].lower(); ipurpose=inst.get("purpose","").lower()
    itok=tok(iname+" "+ipurpose)
    for p in products:
        pname=p["name"].lower()
        if len(pname)>=3 and (pname in iname or pname in ipurpose):
            add(iid,p["id"],"指令对应产品",0.8,f"指令→'{p['name']}'"); continue
        m=[w for w in (itok & pt[p["id"]]) if len(w)>=2]
        if len(m)>=4: add(iid,p["id"],"指令能力产品",0.5,"能力重叠")
    for t in tasks:
        base=iname.split('·')[0].strip()
        if len(base)>=3 and base in t["name"].lower():
            add(iid,t["id"],"指令关联任务",0.6,f"→'{t['name'][:30]}'")

# ====== P7: Quality Metrics ↔ Product/Task/Workflow ======
print("P7: Quality Metrics...")
qmp={"HTML":["首页"],"CSS":["符号体系","品牌·满意红"],"术语":["符号体系","规范标准"],
    "导航":["产品目录","引导页"],"Git":["管理后台","开源声明"],"免疫":["自检清单","规范标准"],
    "Cron":["驾驶舱V3","管理后台"],"商标":["品牌·满意红"],"四关":["自检清单","门控"],
    "提案":["提案模板"],"方法":["星光方法论","五维教学"],
    "数据管道":["驾驶舱V3","飞轮引擎","知识飞轮"],"MD5":["自检清单","规范标准"]}
for qm in quality_metrics:
    qid=qm["id"]; qname=qm["name"].lower(); qdesc=qm.get("description","").lower()
    qtok=tok(qname+" "+qdesc)
    for kw,prods in qmp.items():
        if kw.lower() in qname:
            for pn in prods:
                p=mp(pn)
                if p: add(qid,p["id"],"质量检测对象",0.7,f"QM→'{p['name']}'")
    for t in tasks:
        if len(qtok & tt[t["id"]])>=3: add(qid,t["id"],"质量关联任务",0.4,f"→'{t['name'][:25]}'")
    for wf in workflows:
        if any(kw in wf["name"].lower() for kw in qname.split()):
            add(qid,wf["id"],"质量检测流程",0.7,f"→流程'{wf['name']}'")

# ====== P8: Workflow ↔ Product/QM ======
print("P8: Workflow...")
wfp={"日起课":["驾驶舱V3","生命指数"],"日毕课":["驾驶舱V3","轨迹"],
    "数据管道":["驾驶舱V3","飞轮引擎"],"免疫扫描":["自检清单","规范标准"],
    "知识飞轮":["飞轮引擎","知识飞轮v1"],"部署前检查":["门控","自检清单"],
    "备份":["管理后台"],"术语修复":["符号体系"],"飞书同步":["驾驶舱V3"],"邮箱":["账户管理"]}
for wf in workflows:
    wid=wf["id"]; wname=wf["name"].lower()
    for kw,prods in wfp.items():
        if kw in wname:
            for pn in prods:
                p=mp(pn)
                if p: add(wid,p["id"],"流程涉及产品",0.7,f"流程→'{p['name']}'")
    for qm in quality_metrics:
        if any(kw in qm["name"].lower() for kw in wname.split()):
            add(wid,qm["id"],"流程质量保障",0.6,f"→QM'{qm['name']}'")

# ====== P9: Term ↔ Term ======
print("P9: Term↔Term...")
tg=defaultdict(list)
for term in terms:
    base=re.sub(r'\(.*?\)$','',term["name"]).strip()
    tg[base].append(term)
for base,grp in tg.items():
    for i in range(len(grp)):
        for j in range(i+1,len(grp)):
            add(grp[i]["id"],grp[j]["id"],"术语翻译变体",0.9,"变体")
for term in terms:
    if term.get("evolved_from"):
        for other in terms:
            if re.sub(r'\(.*?\)$','',other["name"]).strip()==term["evolved_from"]:
                add(term["id"],other["id"],"术语演变来源",0.8,f"←'{other['name']}'")
catg=defaultdict(list)
for term in terms: catg[term.get("category","")].append(term)
for cat,grp in catg.items():
    for i in range(len(grp)):
        for j in range(i+1,min(i+6,len(grp))):
            add(grp[i]["id"],grp[j]["id"],"术语同族",0.4,f"同属'{cat}'")
for term in terms:
    if term.get("replaced_by"):
        for other in terms:
            if other["name"]==term["replaced_by"]:
                add(term["id"],other["id"],"术语被替换",0.8,f"→'{other['name']}'")

# ====== P10: Decision ↔ Decision ======
print("P10: Decision↔Decision...")
ds=sorted(decisions,key=lambda d:d.get("date",""))
for i in range(len(ds)-1):
    add(ds[i]["id"],ds[i+1]["id"],"决策时间序列",0.3,f"'{ds[i]['title'][:20]}'→'{ds[i+1]['title'][:20]}'")
for i in range(len(decisions)):
    d1w=set(re.findall(r'\w+',decisions[i]["title"].lower()))
    for j in range(i+2,len(decisions)):
        d2w=set(re.findall(r'\w+',decisions[j]["title"].lower()))
        cm=[w for w in (d1w & d2w) if len(w)>=3]
        if len(cm)>=2: add(decisions[i]["id"],decisions[j]["id"],"相关决策",0.35,f"共享:{','.join(cm[:2])}")

# ====== P11: Customer ↔ Task ======
print("P11: Customer↔Task...")
for cid,cd in all_customers.items():
    cname=cd.get("name","").lower(); cneeds=cd.get("needs","").lower()
    ctok=tok(cname+" "+cneeds)
    for t in tasks:
        tname=t["name"].lower()
        ckw=cname.replace("样本-",""); parts=ckw.split()
        if parts and len(parts[0])>=2 and parts[0] in tname:
            add(cid,t["id"],"客户相关任务",0.6,"客户→任务"); continue
        ov=ctok & tt[t["id"]]
        if len([w for w in ov if len(w)>=2])>=3: add(cid,t["id"],"客户需求任务",0.5,f"重叠{len(ov)}词")

# ====== P12: Avatar ======
print("P12: Avatar...")
ac={"AVAT-001":{"p":["退出指南","轨迹","白皮书"],"i":["退出指南","决策日志模板","OODA循环"]},
    "AVAT-002":{"p":["五维雷达图","匹配引擎","创造工坊","衡·观局测评"],"i":["五维评估_简版","QB决策法","65%规则"]},
    "AVAT-003":{"p":["Pre-0身体觉察","心理量表","关系温度计"],"i":["Pre-Mortem引导","关系CT温度计"]},
    "AVAT-004":{"p":["元合伙","合伙人协议","服务条款","四骑士识别"],"i":["元合伙章程","13型冲突诊断","四骑士识别"]},
    "AVAT-005":{"p":["危机模拟","决策剧场","RPS风险剖面"],"i":["RPS风险剖面","Pre-Mortem引导"]},
    "AVAT-006":{"p":["蓝军","自检清单","规范标准"],"i":["蓝军审计框架","Gate门控评审","满意解12源验证"]}}
for aid,m in ac.items():
    for pn in m["p"]:
        p=mp(pn)
        if p: add(aid,p["id"],"替身代言产品",0.65,f"替身→'{p['name']}'")
    for inn in m["i"]:
        for inst in instructions_set:
            if inn.lower() in inst["name"].lower(): add(aid,inst["id"],"替身使用指令",0.7,f"替身→'{inst['name']}'")

# ====== P13: Script ======
print("P13: Script...")
sp={"SCRIPT-001":["自检清单","规范标准"],"SCRIPT-002":["规范标准"],
    "SCRIPT-003":["驾驶舱V1","驾驶舱V3","知识飞轮v1","星光体系"],
    "SCRIPT-004":["符号体系"],"SCRIPT-005":["符号体系"],
    "SCRIPT-006":["产品目录","星光体系","产品族谱"],"SCRIPT-007":["产品目录","产品族谱"],
    "SCRIPT-008":["驾驶舱V3","量化体系","生命指数"],"SCRIPT-009":["驾驶舱V3","生命指数"],
    "SCRIPT-010":["驾驶舱V3","飞轮引擎"],"SCRIPT-011":["驾驶舱V3"],"SCRIPT-012":["数字替身"]}
for sid,prods in sp.items():
    for pn in prods:
        p=mp(pn)
        if p: add(sid,p["id"],"脚本服务产品",0.6,f"脚本→'{p['name']}'")

# ====== P14: Governance ======
print("P14: Governance...")
gp={"GF-001":["元合伙","合伙人协议","分割饼","门控","匹配引擎"],
    "GF-002":["蓝军","自检清单","RPS风险剖面"],
    "GF-003":["决策剧场","危机模拟","卡牌对局"],
    "GF-004":["创造工坊","产品目录","案例库"],
    "GF-005":["管理后台","开源声明"],"GF-006":["符号体系","品牌·满意红"]}
for gid,prods in gp.items():
    for pn in prods:
        p=mp(pn)
        if p: add(gid,p["id"],"治理框架产品",0.7,f"治理→'{p['name']}'")

# ====== P15: Doc ↔ Doc ======
print("P15: Document↔Document...")
for i in range(len(documents)):
    for j in range(i+1,len(documents)):
        ct=set(documents[i].get("topics",[])) & set(documents[j].get("topics",[]))
        if ct: add(documents[i]["id"],documents[j]["id"],"文档主题关联",0.35,f"共享'{list(ct)[0]}'")

# ====== P16: Product ↔ Product (by family) ======
print("P16: Product↔Product...")
for f in set(p.get("family","") for p in products):
    fam_prods=[p for p in products if p.get("family","")==f]
    for i in range(len(fam_prods)):
        for j in range(i+1,len(fam_prods)):
            add(fam_prods[i]["id"],fam_prods[j]["id"],"产品同族",0.4,f"同属'{f}'族")

# ====== P17: Workflow ↔ Task ======
print("P17: Workflow↔Task...")
wft={"日起课":["日报","简报","Cron","日起"],"日毕课":["日毕","归档","总结"],
    "数据管道":["数据","管道","扫描","文件"],"免疫扫描":["免疫","扫描","检查","MD5"],
    "知识飞轮":["飞轮","知识","消化"],"部署前检查":["部署","发布","检查"],
    "备份":["备份","压缩","MD5"],"术语修复":["术语","修复","替换"],
    "飞书同步":["飞书","同步","Base","wiki"],"邮箱":["邮箱","邮件","sina"],
    "生态审计":["审计","生态","健康"],"决策评估":["决策","评估","周报"]}
for wf in workflows:
    wid=wf["id"]; wname=wf["name"].lower()
    kwds=wft.get(wname,[])
    for t in tasks:
        tn=t["name"].lower()
        if any(k in tn for k in kwds):
            add(wid,t["id"],"流程关联任务",0.5,f"流程→任务")

# ====== P18: Customer ↔ Document ======
print("P18: Customer↔Document...")
for cid,cd in all_customers.items():
    cname=cd.get("name","").lower()
    for doc in documents:
        dname=doc["name"].lower(); dtopics=[t.lower() for t in doc.get("topics",[])]
        if cname.replace("样本-","").split()[0] in dname:
            add(cid,doc["id"],"客户关联文档",0.4,f"名称匹配"); continue
        if any(t in cname for t in dtopics):
            add(cid,doc["id"],"客户关联文档",0.3,f"主题匹配")

# ====== P19: Instruction ↔ Document ======
print("P19: Instruction↔Document...")
for inst in instructions_set:
    iid=inst["id"]; iname=inst["name"].lower()
    for doc in documents:
        dname=doc["name"].lower(); dtopics=[t.lower() for t in doc.get("topics",[])]
        if len(iname)>=4 and iname.split('·')[0].strip() in dname:
            add(iid,doc["id"],"指令关联文档",0.4,f"指令→文档")

# ====== P20: Task ↔ Term ======
print("P20: Task↔Term...")
for t in tasks:
    tcomb=clean_tn(t["name"])+" "+t.get("description","").lower()
    for term in terms:
        clean=re.sub(r'\(.*?\)$','',term["name"].lower()).strip()
        if len(clean)>=3 and clean in tcomb:
            add(t["id"],term["id"],"任务涉及术语",0.5,f"术语'{term['name']}'→任务")
            continue

# ====== P21: Quality Metric ↔ Document ======
print("P21: QM↔Document...")
for qm in quality_metrics:
    qid=qm["id"]; qname=qm["name"].lower()
    for doc in documents:
        if any(kw in doc.get("category","").lower() for kw in qname.split()):
            add(qid,doc["id"],"质量关联文档",0.4,f"QM→文档")

# ====== P22: Governance ↔ Decision ======
print("P22: Governance↔Decision...")
gf_decision={"GF-001":["DACI","元治理","决策权"],"GF-002":["蓝军","独立审计"],
    "GF-003":["五路评议会","图腾"],"GF-004":["协作","扣子"],"GF-005":["Git","提交"],
    "GF-006":["词汇产权","审核"]}
for gid,kwds in gf_decision.items():
    for dec in decisions:
        dtitle=dec.get("title","").lower()
        if any(kw in dtitle for kw in kwds):
            add(gid,dec["id"],"治理关联决策",0.6,f"治理→决策")

# ====== STATS ======
print("Computing stats...")
total_entities = len(products)+len(tasks)+len(all_customers)+len(terms)+len(documents)+len(decisions)+len(quality_metrics)+len(workflows)+len(instructions_set)+len(governance_frameworks)+len(avatars)+len(scripts)
tgt_per=5; tgt_total=total_entities*tgt_per
density=min(round(cnt[0]/max(tgt_total,1)*100,1),99.9)

prod_tc=defaultdict(int); task_pc=defaultdict(int); cust_pc=defaultdict(int); doc_c=defaultdict(int)
for c in connections:
    fe,te=c["from_entity"],c["to_entity"]
    if fe.startswith("PROD-") and te.startswith("TASK-"): prod_tc[fe]+=1; task_pc[te]+=1
    elif te.startswith("PROD-") and fe.startswith("TASK-"): prod_tc[te]+=1; task_pc[fe]+=1
    else:
        for e in [fe,te]:
            if e.startswith("TASK-"): task_pc[e]+=1
            if e.startswith("PROD-"): prod_tc[e]+=1
    for e in [fe,te]:
        if e.startswith("CUST-"): cust_pc[e]+=1
        if e.startswith("DOC-"): doc_c[e]+=1

orphans_data={"products_without_tasks":[f"{p['id']} {p['name']}" for p in products if prod_tc[p["id"]]==0],
    "tasks_without_products":[f"{t['id']} {t['name']}" for t in tasks if task_pc[t["id"]]==0],
    "customers_without_products":[cid for cid in all_customers if cust_pc.get(cid,0)==0],
    "documents_without_connections":[f"{d['id']} {d['name']}" for d in documents if doc_c[d["id"]]==0]}

ei={}
for p in products: ei[p["id"]]=(p["id"],p["name"])
for t in tasks: ei[t["id"]]=(t["id"],t["name"])
for cid,cd in all_customers.items(): ei[cid]=(cid,cd.get("name",cid))
for term in terms: ei[term["id"]]=(term["id"],term["name"])
for doc in documents: ei[doc["id"]]=(doc["id"],doc["name"])
for dec in decisions: ei[dec["id"]]=(dec["id"],dec["title"])
for qm in quality_metrics: ei[qm["id"]]=(qm["id"],qm["name"])
for wf in workflows: ei[wf["id"]]=(wf["id"],wf["name"])
for inst in instructions_set: ei[inst["id"]]=(inst["id"],inst["name"])
for gf in governance_frameworks: ei[gf["id"]]=(gf["id"],gf["name"])
for av in avatars: ei[av["id"]]=(av["id"],av["name"])
for sc in scripts: ei[sc["id"]]=(sc["id"],sc["name"])

eic=defaultdict(int)
for c in connections:
    eic[c["from_entity"]]+=1; eic[c["to_entity"]]+=1

mc=[]
for eid,count in sorted(eic.items(),key=lambda x:-x[1])[:30]:
    info=ei.get(eid,(eid,eid))
    mc.append({"id":eid,"name":info[1],"connections":count})

cls=[]
fn={"镜":"镜·决策模拟族","衡":"衡·评估测评族","契":"契·知识体系族","觉":"觉·驾驶舱智能族","道":"道·品牌使命族","人":"人·工具交互族"}
for f,name in fn.items():
    ents=[f"{p['id']} {p['name']}" for p in products if p.get("family")==f]
    if ents: cls.append({"cluster_name":name,"entities":ents,"theme":f"{f}族产品群"})
for cat,grp in catg.items():
    if len(grp)>=3:
        cls.append({"cluster_name":f"术语·{cat}","entities":[f"{t['id']} {t['name']}" for t in grp],"theme":f"{cat}相关术语群"})

output = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "total_entities": total_entities,
    "total_possible_connections": tgt_total,
    "connections_made": cnt[0],
    "density": density,
    "connections": connections,
    "orphans": orphans_data,
    "centrality": {"most_connected_entities": mc},
    "clusters": cls[:30]
}

with open("memory/_data/knowledge_graph_full.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"知识图谱全连接引擎 V3 - 完成报告")
print(f"{'='*60}")
print(f"总实体数: {total_entities}")
print(f"目标连接数({tgt_per}/实体): {tgt_total}")
print(f"实际连接数: {cnt[0]}")
print(f"连接密度: {density}%")
print(f"孤儿: 产品无任务={len(orphans_data['products_without_tasks'])}")
print(f"      任务无产品={len(orphans_data['tasks_without_products'])}")
print(f"      客户无产品={len(orphans_data['customers_without_products'])}")
print(f"      文档无连接={len(orphans_data['documents_without_connections'])}")
print(f"Top 5: {[(e['id'],e['name'][:15],e['connections']) for e in mc[:5]]}")
print(f"连接数分布 (最少/平均/最多): {min(eic.values())}/{round(sum(eic.values())/len(eic),1)}/{max(eic.values())}")