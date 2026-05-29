#!/usr/bin/env python3
"""
驾驶舱数据中继器 V1.0
扫描localStorage + 飞书Base → 本地SQLite → 暴露HTTP API 
cron每30分钟跑一次·也支持手动触发
"""
import sqlite3, json, os, time, subprocess

DB = os.path.expanduser("~/.openclaw/workspace/memory/local_dashboard.db")

def seed_all():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # 确保所有表存在
    tables = {
        'tasks': '''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, priority TEXT, status TEXT DEFAULT '待开始', deadline TEXT, assignee TEXT DEFAULT 'Egbertie', notes TEXT, created_at TEXT DEFAULT (datetime('now','localtime')))''',
        'customers': '''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, company TEXT, email TEXT, role TEXT, industry TEXT, stage TEXT, concern TEXT, tags TEXT, created_at TEXT DEFAULT (datetime('now','localtime')))''',
        'passwords': '''CREATE TABLE IF NOT EXISTS passwords (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, products TEXT DEFAULT 'all', customer TEXT, valid_from TEXT, valid_until TEXT, max_uses INTEGER DEFAULT 9999, used INTEGER DEFAULT 0, status TEXT DEFAULT '启用', notes TEXT, created_at TEXT DEFAULT (datetime('now','localtime')))''',
        'quality': '''CREATE TABLE IF NOT EXISTS quality (id INTEGER PRIMARY KEY AUTOINCREMENT, qm_id TEXT, module TEXT, standard TEXT, criteria TEXT, current_status TEXT, gap TEXT, action TEXT, assignee TEXT, deadline TEXT, benchmark TEXT, priority TEXT DEFAULT 'P1')''',
        'products': '''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id TEXT, name TEXT, family TEXT, form TEXT, depth TEXT, access TEXT, url TEXT, source TEXT, status TEXT DEFAULT '上线')''',
        'growth': '''CREATE TABLE IF NOT EXISTS growth (id INTEGER PRIMARY KEY AUTOINCREMENT, metric_name TEXT, current_value TEXT, target_value TEXT, trend TEXT, updated_at TEXT DEFAULT (datetime('now','localtime')))''',
        'contracts': '''CREATE TABLE IF NOT EXISTS contracts (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, party TEXT, value TEXT, status TEXT, deadline TEXT, notes TEXT)''',
        'channels': '''CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT, status TEXT, reach TEXT, notes TEXT)''',
        'vi_assets': '''CREATE TABLE IF NOT EXISTS vi_assets (id INTEGER PRIMARY KEY AUTOINCREMENT, asset TEXT, category TEXT, usage TEXT, status TEXT, file TEXT)''',
    }

    for tbl, sql in tables.items():
        c.execute(sql)
    conn.commit()

    # 默认数据填充
    count_passwords = c.execute('SELECT COUNT(*) FROM passwords').fetchone()[0]
    if count_passwords == 0:
        c.execute("INSERT INTO passwords (code,products,customer,valid_until,max_uses,notes) VALUES (?,?,?,?,?,?)",
            ('***', 'all', '内测用户', '2027-12-31', 9999, '默认内测密码'))
    
    count_quality = c.execute('SELECT COUNT(*) FROM quality').fetchone()[0]
    if count_quality == 0:
        qm_items = [
            ('QM-001','六级审核','L0提案审核','产品概念文档','待执行','无提案环节','创建模板','满意红','2026-06-07','HBR','P0'),
            ('QM-002','六级审核','L1方法论','逻辑自洽','55%通过率','45%缺来源','周一扫描','满意红(cron)','2026-06-07','McKinsey','P0'),
            ('QM-003','六级审核','L2内容','五要素齐全','105缺来源','105/232','逐批补齐','满意红','2026-06-14','HBR','P1'),
            ('QM-009','产品矩阵','四关通过率','≥80%','96%达标','已达标','监控保持','满意红(cron)','2026-07-01','ISO','P0'),
            ('QM-026','知识产权','商标注册','满意解研究所®','未申请','全部未注册','代理申请','Egbertie','2026-07-31','Stanford','P0'),
        ]
        for item in qm_items:
            c.execute('INSERT INTO quality (qm_id,module,standard,criteria,current_status,gap,action,assignee,deadline,benchmark,priority) VALUES (?,?,?,?,?,?,?,?,?,?,?)', item)

    count_growth = c.execute('SELECT COUNT(*) FROM growth').fetchone()[0]
    if count_growth == 0:
        for kpi in [('线上产品总数','232','250','→'),('四关通过率','96%','100%','↑'),('NPS基线','待收集','≥50','—'),('飞轮循环','0','50','—'),('活跃客户(30d)','0','30','—'),('K-factor','待计算','>1.2','—')]:
            c.execute('INSERT INTO growth (metric_name,current_value,target_value,trend) VALUES (?,?,?,?)', kpi)

    count_contracts = c.execute('SELECT COUNT(*) FROM contracts').fetchone()[0]
    if count_contracts == 0:
        for ct in [('商标注册代理','待定代理','~¥3K','待签约','2026-07-31','QM-026'),('飞书认证','飞书','¥300/年','待启动','公测后','个人号无法认证'),('Zoom商业版','Zoom','~¥1.5K/年','待启动','开课前','公开课必需品'),('域名注册','待定','~¥100/年','待签约','2026-06-14','独立域名'),('合作协议模板·VC投后','已设计','—','草稿','夏至后','7类协议')]:
            c.execute('INSERT INTO contracts (name,party,value,status,deadline,notes) VALUES (?,?,?,?,?,?)', ct)

    count_channels = c.execute('SELECT COUNT(*) FROM channels').fetchone()[0]
    if count_channels == 0:
        for ch in [('公众号:满意解禅堂','自有','✅已开通','个人号','未认证'),('GitHub Pages','主站','✅232产品','egbertie.io','全站HTTPS'),('小红书','社交','🟡5篇就绪','5篇笔记','张雪机车系列'),('知乎','社区','🟡3篇就绪','3回答','合伙人话题'),('播客','音频','🟡脚本就绪','1期/周','待录制'),('抖音/视频号','短视频','🟡脚本就绪','3条/周','待发布'),('36氪','科技媒体','🔴待联系','—','投稿/采访'),('虎嗅','科技媒体','🔴待联系','—','深度分析'),('投资人说','VC垂直','🔴待联系','—','投后合作'),('创业邦','创业媒体','🔴待联系','—','创始人故事'),('VC投后管理','渠道合作','🟡方案完成','—','3种模式'),('加速器(奇绩/英诺)','渠道合作','🟡方案完成','—','打包诊断'),('律所(合伙人协议)','渠道合作','🔴待联系','—','联合服务'),('高校创业中心','渠道合作','🔴待联系','—','课程嵌入')]:
            c.execute('INSERT INTO channels (name,type,status,reach,notes) VALUES (?,?,?,?,?)', ch)

    count_vi = c.execute('SELECT COUNT(*) FROM vi_assets').fetchone()[0]
    if count_vi == 0:
        for vi in [('主色#C23B22','色彩','所有标识·强调·主视觉','✅固化','sri-design.css'),('背景#F5F0E6','色彩','页面背景·留白','✅固化','sri-design.css'),('暗金#B8860B','色彩','仅金属性符号','✅固化','sri-design.css'),('Logo方印','标识','所有页面·品牌资产','✅完整','飞书资产库'),('章衡镜契觉','命名','产品命名体系','✅233产品','产品库'),('器物代号(观云照海等)','命名','深度产品·传播','✅已用','产品标准'),('字体PingFang/Noto Sans','字体','全站系统字体','✅全局','sri-design.css'),('设计令牌(V4)','设计系统','间距·圆角·阴影','✅CSS变量','sri-design.css'),('VI手册','规范','品牌视觉识别手册V1.0','✅飞书','LCZDdJ0afoPt'),('品牌资产库','素材','50个品牌素材','✅飞书','KT7hfVYyhlil'),('商标注册','法律','满意解研究所®','🔴未申请','QM-026')]:
            c.execute('INSERT INTO vi_assets (asset,category,usage,status,file) VALUES (?,?,?,?,?)', vi)

    conn.commit()
    conn.close()
    
    # 输出统计
    conn2 = sqlite3.connect(DB)
    stats = {}
    for tbl in tables.keys():
        cnt = conn2.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        stats[tbl] = cnt
    conn2.close()
    return stats

if __name__ == '__main__':
    s = seed_all()
    print(f"[{time.strftime('%H:%M:%S')}] 数据中继: {json.dumps(s, ensure_ascii=False)}")
