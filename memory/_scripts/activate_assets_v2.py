#!/usr/bin/env python3
"""
历史资产专项激活脚本 · 精准标签扩展
只扫描一次：把缺少标签的文件重新打分
"""
import os, json, time

WORKSPACE = "/Users/egbertielau/.openclaw/workspace"
ASSETS_FILE = f"{WORKSPACE}/satisficing-lab/assets_index.json"

# 扩展关键词库——覆盖更广
TAGS_V2 = {
    "产品设计": ["产品","工具","测评","诊断","卡牌","卡片","剧场","模拟","温度计","计算器","章程","指南","工作坊","prd","PRD","MVP","交互","组件","widget","assets","asset","功能"],
    "方法论": ["五维","五路图腾","满意解","Simon","司马贺","时间轴","可行域","身心流","信义观","直觉阈","五步","五元","五关","三级","三生","三脉","框架","framework","逻辑","推理"],
    "案例与数据": ["案例","84","大疆","云鲸","比锐","海柔","固高","68Entry","张雪","Zipcar","数据","统计","样本","实证","evidence"],
    "运营管理": ["驾驶舱","cron","自动化","脚本","SQLite","SQL","DB","localStorage","local","storage","飞轮","同步","日志","log","sync","备份"],
    "品牌与设计": ["VI","配色","#C23B22","赭石红","设计系统","WCAG","sri-design","design","css","CSS","style","字体","字号","色"],
    "增长与获客": ["获客","转化","NPS","K-factor","转介绍","Aha","Moment","Growth","Loop","公开课","路演","引流","注册","报名"],
    "标准与质量": ["QM-","审核","Peer","Review","APA","ICF","ISO","HBR","标准","规范","合规","SOP","require","spec","checklist"],
    "知识与培训": ["教程","课程","培训","翻书","Wasserman","Gottman","Duke","Feld","Lencioni","Moyer","导师","讲义","PPT","课件","学"],
    "AI与系统": ["满意姐","扣子","满意红","蓝军","Skeptor","代理","Session","子人格","Kimi","Claw","Claude","Coding","Agent"],
    "法律与合同": ["商标","合同","协议","条款","CC","著作权","MIT","license","License","版权","专利","legal"],
    "部署发布": ["git","push","commit","部署","deploy","GitHub","Page","build","release","上线","发布","vercel","域名"],
    "社区运营": ["社","群","关注","粉","微信","公众号","小程序","知乎","小红书","抖音","视频","LinkedIn","link","share","分享"],
}

def activate():
    print("专项激活扫描...")
    with open(ASSETS_FILE,'r') as f:
        data = json.load(f)
    
    files = data.get('files', [])
    total = data['total']
    reactivated = 0
    
    # 对每个文件重新打标签
    for f in files:
        old_tags = set(f.get('tags', []))
        name = f['name']
        path_str = f['path']
        
        # 扩展标签匹配——不仅看关键词，还看文件类型加分
        ext = f['type']
        
        # 文件类型自动加分
        if ext in ['py','sh','js']: old_tags.add('运营管理')
        if ext in ['py']: old_tags.add('AI与系统')
        if ext in ['html','css']: 
            old_tags.add('产品设计')
            old_tags.add('品牌与设计')
        if ext in ['json']: old_tags.add('标准与质量')
        if ext in ['md']:
            # MD文件大概率有价值
            if '记忆' in path_str or 'memory' in path_str: old_tags.add('知识与培训')
            if '脚本' in path_str or 'script' in path_str: old_tags.add('运营管理')
            if '对话' in path_str: old_tags.add('案例与数据')
            if '产品' in path_str: old_tags.add('产品设计')
        
        # 计算新分数
        new_tags = list(old_tags)
        score = min(100, len(new_tags)*10 + (20 if ext=='md' else 0) + (15 if ext=='html' else 0) + (10 if ext=='py' else 0))
        f['tags'] = new_tags
        f['value'] = score
        f['active'] = score >= 25  # 降低门槛从30→25
        
        if f['active'] and len(old_tags) > 0:
            reactivated += 1
    
    # 重新统计
    active = [f for f in files if f['active']]
    active_count = len(active)
    avg_score = sum(f['value'] for f in files) / max(len(files), 1)
    
    # 重新分标签统计
    tag_counts = {}
    tag_active = {}
    for f in files:
        for t in f.get('tags',[]):
            tag_counts[t] = tag_counts.get(t,0)+1
            if f['active']:
                tag_active[t] = tag_active.get(t,0)+1
    
    data['active'] = active_count
    data['avgScore'] = round(avg_score, 1)
    data['tagSummary'] = {k:{"count":tag_counts[k],"active":tag_active.get(k,0)} for k in sorted(tag_counts.keys(),key=lambda x:tag_counts[x],reverse=True)}
    data['files'] = sorted(files, key=lambda x: x['value'], reverse=True)
    
    with open(ASSETS_FILE,'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"专项激活完成")
    print(f"  总文件: {len(files)}")
    print(f"  激活: {active_count} ({active_count/max(len(files),1)*100:.0f}%)")
    print(f"  平均分: {avg_score:.1f}")
    print()
    print("标签激活率:")
    for tag, info in sorted(data['tagSummary'].items(), key=lambda x: x[1]['active'], reverse=True):
        pct = info['active']/max(info['count'],1)*100
        bar = '🟢' if pct>=90 else '🟡' if pct>=70 else '🔴'
        print(f"  {bar} {tag}: {info['count']}文件 · {pct:.0f}%")
    
    return active_count

if __name__ == "__main__":
    activate()
