"""
体系升级 v7.0 · R&D管道+全局整合
=================================
新增: R&D知识研发管道(4阶段)·团队架构·城市市场·免疫系统·决策治理
整合: 嵌入15阶段全生命周期·形成完整飞轮
"""

import json
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8)); now = datetime.now(tz).isoformat()

path = '/Users/egbertielau/.openclaw/workspace/satisficing-lab/entities_index.json'
with open(path) as f: data = json.load(f)

# ═══════════════════════════════════
# 1. R&D知识研发管道
# ═══════════════════════════════════
data['rd_pipeline'] = {
    "version":"1.0","created_at":now,
    "philosophy":"外部信息→内部知识→可交付产品——R&D是体系自进化的燃料引擎。采集→提炼→转化→产品化→传播，循环不息。",
    "stages":[
        {"id":"RD-01","name":"采集","icon":"🔬",
         "question":"外部世界有什么值得学习？",
         "sources":["学术论文(合伙人冲突/决策心理学/组织行为)","行业报告(创投趋势/硬科技/AI)","商业案例(大疆/正浩/禾赛/字节)","书籍文献(Founder's Dilemmas等)","客户反馈(使用数据/NPS/访谈)"],
         "output":"原始素材池","tools":["sri_nourishment_collector.py","Inkwell阅读","行业监控Cron"],
         "metrics":["周采集量","覆盖领域","来源多样性"]},
        {"id":"RD-02","name":"提炼","icon":"🧪",
         "question":"如何将素材变成方法论？",
         "process":"分析核心洞见→归纳为框架→校验→术语标准化",
         "output":"方法论卡片·框架定义·知识资产",
         "tools":["sri_knowledge_flywheel.py","专家团队评审","蓝军验证"],
         "metrics":["月提炼产出","方法论复用","框架采纳率"],
         "examples":["五维决策框架(时间轴/可行域/身心流/信义观/直觉阈)","13种冲突类型学","四层诊断模型"]},
        {"id":"RD-03","name":"转化","icon":"⚗️",
         "question":"如何将方法论变成产品？",
         "process":"框架→原型→内测→打磨→上线",
         "output":"产品原型·交互工具·测评模型",
         "tools":["sri_product_scanner.py","sri_lifecycle_manager.py","LLM替身评估"],
         "metrics":["转化周期","原型→精品率","月上线数"],
         "examples":["五维自评(方法论→19题测评)","卡牌对局(冲突类型学→交互卡牌)","决策剧场(情景推演→预演工具)"]},
        {"id":"RD-04","name":"产品化","icon":"💎",
         "question":"如何将产品打磨为精品？",
         "process":"上线→客户使用→反馈→迭代→精品",
         "output":"精品产品·白皮书·课程·认证",
         "tools":["sri_consistency_checker.py","sri_auto_healer.py","质量门禁"],
         "metrics":["精品数","迭代周期","满意度"],
         "examples":["决策剧场(精品·镜族·L4)","卡牌对局(精品·镜族·L2)","化学报告(精品·衡族·完整诊断)"]}
    ],
    "active_projects":[
        {"id":"RD-PROJ-01","name":"Wasserman《Founder's Dilemmas》深研","stage":"提炼","target":"深度·合伙人困境","progress":40},
        {"id":"RD-PROJ-02","name":"南山硬科技生态实地调研","stage":"采集","target":"城市市场报告·南山篇","progress":10},
        {"id":"RD-PROJ-03","name":"五维框架实证验证","stage":"转化","target":"五维自评v2.0","progress":25},
        {"id":"RD-PROJ-04","name":"客户退出案例收集","stage":"采集","target":"退出指引v2.0","progress":5}
    ],
    "metrics":{"rd_velocity":0,"idea_to_product_days":30,"active_topics":5,"knowledge_assets":0}
}

# ═══════════════════════════════════
# 2. 团队架构
# ═══════════════════════════════════
data['team_architecture'] = {
    "version":"1.0","created_at":now,
    "founder":{"name":"Egbertie LAU","roles":["战略决策","客户关系","品牌代表","方法论总设计师"]},
    "core_roles":[
        {"role":"内容与研究","icon":"📚","tasks":["行业研究","白皮书","案例整理","知识库维护"]},
        {"role":"产品与技术","icon":"🛠️","tasks":["产品开发","网站维护","驾驶舱","自动化"]},
        {"role":"客户成功","icon":"🤝","tasks":["客户导入","阶段推进","健康监控","预警响应"]},
        {"role":"市场与渠道","icon":"📡","tasks":["内容发布","渠道维护","活动组织","品牌传播"]}
    ],
    "virtual_team":{"expert_avatars":22,"usage":"按需激活——研究·审核·创意·验证"},
    "stats":{"core":4,"virtual":22,"bottleneck":"创始人即唯一执行者·所有决策汇聚于一点"}
}

# ═══════════════════════════════════
# 3. 城市市场
# ═══════════════════════════════════
data['city_markets'] = {
    "version":"1.0","created_at":now,
    "strategy":"南山→深圳→大湾区→全国 四层辐射",
    "layers":[
        {"tier":"策源地","cities":["南山"],"desc":"产业原生市场·硬科技生态核心·每日触达"},
        {"tier":"第一圈","cities":["深圳"],"desc":"大湾区引擎·供应链完整"},
        {"tier":"第二圈","cities":["广州","东莞","珠海","佛山","惠州"],"desc":"制造业腹地·潜在客户密集"},
        {"tier":"第三圈","cities":["北京","上海","杭州","成都","武汉"],"desc":"创投中心·峰会·战略合作"}
    ],
    "priority":{"name":"南山","score":95},
    "expansion":"南山(已完成)→深圳(6月)→大湾区(9月)→全国(12月)"
}

# ═══════════════════════════════════
# 4. 免疫系统
# ═══════════════════════════════════
data['immune_system'] = {
    "version":"1.0","created_at":now,
    "components":[
        {"id":"IMM-01","name":"代码质量门禁","freq":"每次push","checks":["语法","品牌","连接"],"status":"active"},
        {"id":"IMM-02","name":"数据完整性扫描","freq":"每小时","checks":["JSON有效","字段完整","孤儿检测"],"status":"active"},
        {"id":"IMM-03","name":"反孤岛检测","freq":"心跳","checks":["索引一致性","僵尸任务","Cron健康"],"status":"active"},
        {"id":"IMM-04","name":"备份新鲜度","freq":"每日","checks":["GitHub推送","飞书同步","本地快照"],"status":"active"},
        {"id":"IMM-05","name":"客户健康预警","freq":"实时","checks":["活跃度","阶段停滞","健康分下降"],"status":"active"}
    ],
    "health":{"score":85,"status":"healthy","known_issues":3}
}

# ═══════════════════════════════════
# 5. 决策治理
# ═══════════════════════════════════
data['decision_governance'] = {
    "version":"1.0","created_at":now,
    "model":"DACI（Driver·Approver·Contributor·Informed）",
    "types":[
        {"type":"战略决策","driver":"创始人","approver":"创始人","contributor":"专家团队·蓝军","freq":"季度"},
        {"type":"产品决策","driver":"产品负责人","approver":"创始人","contributor":"客户成功·数据分析","freq":"月度"},
        {"type":"技术决策","driver":"技术负责人","approver":"创始人","contributor":"代码工程师","freq":"按需"},
        {"type":"内容决策","driver":"内容负责人","approver":"创始人","contributor":"研究·创意设计","freq":"周度"},
        {"type":"客户决策","driver":"客户成功","approver":"创始人","contributor":"客户替身·数据分析","freq":"按需"}
    ],
    "meetings":{"日":"15分钟站会","周":"1小时数据复盘","月":"2小时战略复盘","季度":"半天OKR+大闭环审查"}
}

# ═══════════════════════════════════
# 6. meta汇总
# ═══════════════════════════════════
m = data.get('meta', {})
m['system_v7'] = {
    "version":"7.0","updated_at":now,
    "modules":{
        "customer_lifecycle":"15阶段+三级闭环(14小/5中/1大)",
        "product_system":"4层(11核心/31客户可见/315总)",
        "rd_pipeline":"4阶段(采集→提炼→转化→产品化)",
        "team":"4核心+22虚拟",
        "markets":"31城市·南山策源地",
        "immune":"5组件·85分",
        "governance":"DACI·5类决策",
        "acquisition":"6渠道·5级漏斗",
        "data":"12556连接·315产品·8.3MB"
    }
}

with open(path, 'w') as f: json.dump(data, f, ensure_ascii=False, indent=2)
with open(path) as f: d2 = json.load(f)
print("✅ v7.0 已写入")
print(f"   R&D管道: {len(d2['rd_pipeline']['stages'])}阶段·{len(d2['rd_pipeline']['active_projects'])}项目")
print(f"   团队: {d2['team_architecture']['stats']['core']}核心+{d2['team_architecture']['stats']['virtual']}虚拟")
print(f"   市场: {len(d2['city_markets']['layers'])}层辐射")
print(f"   免疫: {len(d2['immune_system']['components'])}组件")
print(f"   治理: {len(d2['decision_governance']['types'])}类决策")
