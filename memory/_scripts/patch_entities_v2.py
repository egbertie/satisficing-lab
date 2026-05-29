#!/usr/bin/env python3
"""Patch entities_index.json with 7 new entity arrays."""
import json
import os
from datetime import datetime

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
INDEX_PATH = os.path.join(WORKSPACE, "memory/_data/entities_index.json")

with open(INDEX_PATH, "r") as f:
    data = json.load(f)

# ========== 1. quality_metrics ==========
quality_metrics = [
    # 飞书驾驶舱 V1 QM
    {"id": "QM-001", "name": "L0提案审核", "description": "提案阶段需通过L0级基础审核，包括一致性、规范性和完整性检查", "target": "P0", "current_value": "待执行", "unit": "状态", "priority": "P0", "status": "待执行"},
    {"id": "QM-002", "name": "L1方法论审核", "description": "方法论层面审核产品/方案是否遵循满意解框架标准", "target": "100%", "current_value": "55%", "unit": "%", "priority": "P0", "status": "进行中"},
    {"id": "QM-003", "name": "四关通过率≥80%", "description": "提案需通过四关审查流程，通过率不低于80%", "target": "≥80%", "current_value": "96%", "unit": "%", "priority": "P0", "status": "达标"},
    {"id": "QM-004", "name": "商标注册", "description": "满意解研究所及子品牌商标在中国大陆完成注册", "target": "已申请", "current_value": "未申请", "unit": "状态", "priority": "P0", "status": "待启动"},
    # 系统级质量标准（从 immune_scan.sh 提取）
    {"id": "QM-005", "name": "全站HTML结构完整性", "description": "免疫扫描L2检测所有HTML文件结构完整性（DOCTYPE/head/body闭合）", "target": "100%", "current_value": "100%", "unit": "%", "priority": "P0", "status": "达标"},
    {"id": "QM-006", "name": "CSS变量一致性", "description": "所有HTML文件的CSS变量与VI标准(:root)保持一致", "target": "100%", "current_value": "98%", "unit": "%", "priority": "P1", "status": "达标"},
    {"id": "QM-007", "name": "术语统一率", "description": "全站术语(观自在→水月观音、四骑士→关系危机信号、决策教练→决策外脑)统一率", "target": "100%", "current_value": "100%", "unit": "%", "priority": "P0", "status": "达标"},
    {"id": "QM-008", "name": "导航链接有效性", "description": "所有内部导航链接目标文件存在且可访问", "target": "100%", "current_value": "100%", "unit": "%", "priority": "P1", "status": "达标"},
    {"id": "QM-009", "name": "Git提交规范性", "description": "Git提交遵循Conventional Commits规范(feat/fix/docs/chore)", "target": "100%", "current_value": "100%", "unit": "%", "priority": "P1", "status": "达标"},
    {"id": "QM-010", "name": "免疫扫描执行频率", "description": "每小时免疫扫描正常执行且无延迟", "target": "每小时", "current_value": "每小时", "unit": "频率", "priority": "P0", "status": "达标"},
    {"id": "QM-011", "name": "数据管道执行频率", "description": "每6小时数据管道正常执行，文件扫描+实体发现", "target": "每6h", "current_value": "每6h", "unit": "频率", "priority": "P1", "status": "达标"},
    {"id": "QM-012", "name": "Cron心跳健康度", "description": "15个Cron任务全部在线无失联", "target": "15/15", "current_value": "15/15", "unit": "个", "priority": "P0", "status": "达标"},
    {"id": "QM-013", "name": "MD5基线完整性", "description": "免疫L0每日MD5基线快照正常更新", "target": "每日", "current_value": "每日", "unit": "频率", "priority": "P1", "status": "达标"},
]

# ========== 2. growth_metrics ==========
growth_metrics = [
    {"id": "GR-001", "name": "飞轮循环", "current": 0, "target": 100, "unit": "次", "trend": "待启动"},
    {"id": "GR-002", "name": "线上产品", "current": 233, "target": 250, "unit": "个", "trend": "↑"},
    {"id": "GR-003", "name": "活跃客户30d", "current": 0, "target": 10, "unit": "人", "trend": "待启动"},
    {"id": "GR-004", "name": "公众号文章发布", "current": 7, "target": 20, "unit": "篇", "trend": "↑"},
    {"id": "GR-005", "name": "Cron任务就绪", "current": 15, "target": 15, "unit": "个", "trend": "→"},
    {"id": "GR-006", "name": "替身激活数", "current": 6, "target": 23, "unit": "个", "trend": "↑"},
    {"id": "GR-007", "name": "案例库填充", "current": 16, "target": 84, "unit": "个", "trend": "↑"},
    {"id": "GR-008", "name": "论文入库", "current": 38, "target": 38, "unit": "篇", "trend": "→"},
    {"id": "GR-009", "name": "日活访客(估算)", "current": 0, "target": 100, "unit": "人/天", "trend": "待启动"},
    {"id": "GR-010", "name": "夏至倒计时", "current": 22, "target": 0, "unit": "天", "trend": "↓"},
]

# ========== 3. vi_standards ==========
vi_standards = [
    {"id": "VI-001", "name": "宣纸白", "css_variable": "--paper-white", "hex_value": "#F5F0E6", "usage": "页面底色+大面积背景", "category": "color"},
    {"id": "VI-002", "name": "卡片白", "css_variable": "--card-white", "hex_value": "#FFFFFF", "usage": "卡片/面板背景", "category": "color"},
    {"id": "VI-003", "name": "暖白", "css_variable": "--card-warm", "hex_value": "#FAF6EF", "usage": "重点卡片/特色面板", "category": "color"},
    {"id": "VI-004", "name": "墨色", "css_variable": "--ink", "hex_value": "#4A3728", "usage": "正文/标题文字", "category": "color"},
    {"id": "VI-005", "name": "绀红", "css_variable": "--accent-red", "hex_value": "#C23B22", "usage": "主强调色·关注+紧迫感", "category": "color"},
    {"id": "VI-006", "name": "古铜金", "css_variable": "--accent-gold", "hex_value": "#B8860B", "usage": "辅强调色·方法论历史深度", "category": "color"},
    {"id": "VI-007", "name": "暖边界", "css_variable": "--border-warm", "hex_value": "#E0D5C8", "usage": "边框/分割线/进度条背景", "category": "color"},
    {"id": "VI-008", "name": "达标绿", "css_variable": "--green-ok", "hex_value": "#3D7A4F", "usage": "健康/达标/完成标识", "category": "color"},
    {"id": "VI-009", "name": "警示金", "css_variable": "--amber-warn", "hex_value": "#C2780A", "usage": "警告/注意/待处理标识", "category": "color"},
    {"id": "VI-010", "name": "红色警报", "css_variable": "--red-alert", "hex_value": "#C23B22", "usage": "严重警告/异常/死亡状态", "category": "color"},
    {"id": "VI-011", "name": "浅墨色", "css_variable": "--ink-light", "hex_value": "#7A6958", "usage": "副标题/描述文字/标签", "category": "color"},
    {"id": "VI-012", "name": "更浅墨色", "css_variable": "--ink-lighter", "hex_value": "#A89880", "usage": "提示/hint/placeholder", "category": "color"},
    {"id": "VI-013", "name": "暖背景", "css_variable": "--bg-warm", "hex_value": "#FBF8F2", "usage": "全局背景色(与宣纸白微暖区分)", "category": "color"},
    {"id": "VI-014", "name": "微阴影", "css_variable": "--shadow-subtle", "hex_value": "rgba(74,55,40,0.06)", "usage": "卡片轻微阴影", "category": "shadows"},
    {"id": "VI-015", "name": "中阴影", "css_variable": "--shadow-medium", "hex_value": "rgba(74,55,40,0.10)", "usage": "悬停/弹出阴影", "category": "shadows"},
    {"id": "VI-016", "name": "正文字体栈", "css_variable": "font-family", "hex_value": "-apple-system,BlinkMacSystemFont,'SF Pro Text','PingFang SC','Microsoft YaHei',sans-serif", "usage": "全局正文字体", "category": "typography"},
    {"id": "VI-017", "name": "行高标准", "css_variable": "line-height", "hex_value": "1.6", "usage": "全局正文行高", "category": "typography"},
    {"id": "VI-018", "name": "标题字重", "css_variable": "font-weight", "hex_value": "300", "usage": "标题使用Light字重（轻盈感）", "category": "typography"},
    {"id": "VI-019", "name": "标题字距", "css_variable": "letter-spacing", "hex_value": "0.06-0.08em", "usage": "标题字母间距", "category": "typography"},
    {"id": "VI-020", "name": "圆角标准", "css_variable": "border-radius", "hex_value": "10-24px", "usage": "卡片/按钮/输入框圆角", "category": "spacing"},
]

# ========== 4. lifecycle_stages ==========
lifecycle_stages = [
    {"id": "LC-001", "name": "概念", "order": 1, "description": "产品创意阶段：识别需求、验证假设、确定可行域", "entry_criteria": "发现明确的决策痛点且满意解方法论可覆盖", "exit_criteria": "概念验证通过（60%信任指数），进入L0提案审核"},
    {"id": "LC-002", "name": "原型", "order": 2, "description": "快速原型阶段：MVP构建、内部测试、评分引擎初调", "entry_criteria": "概念通过L0提案审核+方法论校准", "exit_criteria": "原型可通过自检清单+四关内审≥60%"},
    {"id": "LC-003", "name": "内侧", "order": 3, "description": "内部测试阶段：蓝军审计、压力测试、体验打磨", "entry_criteria": "原型四关通过率≥60%+蓝军独立审计通过", "exit_criteria": "内侧无P0缺陷+四关通过率≥80%+客户替身交叉验证OK"},
    {"id": "LC-004", "name": "公开", "order": 4, "description": "公开上线/发布阶段：对外发布、宣发、社群建设", "entry_criteria": "内侧全部P0缺陷清零+术语统一完成+VI标准化", "exit_criteria": "上线后7天无严重Bug+客户反馈采集管道就绪"},
    {"id": "LC-005", "name": "精品", "order": 5, "description": "精品化阶段：迭代优化、评级提升、案例积累", "entry_criteria": "上线后获得首批真实客户反馈+至少3个正面案例", "exit_criteria": "产品星级≥4★+活跃用户留存≥60%+至少1篇深度客户案例"},
    {"id": "LC-006", "name": "维护", "order": 6, "description": "稳定维护阶段：常规更新、兼容性维护、知识归档", "entry_criteria": "产品星级稳定≥4★+需求量下降或用户群稳定", "exit_criteria": "触发退役条件：连续6月无活跃使用或发现根本性设计缺陷"},
    {"id": "LC-007", "name": "退役", "order": 7, "description": "产品下线/归档：经验萃取、知识迁移、用户迁移引导", "entry_criteria": "触发维护退出条件+决策日志确认退役", "exit_criteria": "经验/教训归档完成+关联产品已更新+用户已迁移至替代方案"},
]

# ========== 5. instructions_set ==========
instructions_set = [
    {"id": "INST-001", "name": "五维评估_简版", "file_path": "替身/Skills/五维评估_简版.md", "purpose": "快速五维决策评估：28题简版问卷→评分→CTAs", "status": "活跃"},
    {"id": "INST-002", "name": "RPS风险剖面", "file_path": "替身/Skills/RPS风险剖面.md", "purpose": "风险评估：概率×影响×检测难度三维评估，输出风险水位图", "status": "活跃"},
    {"id": "INST-003", "name": "Pre-Mortem引导", "file_path": "替身/Skills/Pre-Mortem引导.md", "purpose": "前置验尸：假设项目失败→倒推死因→反推预防措施", "status": "活跃"},
    {"id": "INST-004", "name": "关系CT温度计", "file_path": "替身/Skills/关系CT温度计.md", "purpose": "合作关系健康度检测：4题自评+风险预警+分层干预建议", "status": "活跃"},
    {"id": "INST-005", "name": "决策日志模板", "file_path": "替身/Skills/决策日志模板.md", "purpose": "标准化决策记录：背景-选项-评估-决定-签名五段式", "status": "活跃"},
    {"id": "INST-006", "name": "元合伙章程", "file_path": "替身/Skills/元合伙章程.md", "purpose": "合伙人决策前置规范：角色定义、流程规则、冲突解决机制", "status": "活跃"},
    {"id": "INST-007", "name": "13型冲突诊断", "file_path": "替身/Skills/13型冲突诊断.md", "purpose": "创业团队13种典型冲突类型识别+匹配干预方案", "status": "活跃"},
    {"id": "INST-008", "name": "退出指南", "file_path": "替身/Skills/退出指南.md", "purpose": "创业退出策略框架：时机评估+路径选择+过渡方案", "status": "活跃"},
    {"id": "INST-009", "name": "四骑士识别", "file_path": "替身/Skills/四骑士识别.md", "purpose": "Gottman四骑士(批评/蔑视/防御/冷战)在合作关系中的识别与干预", "status": "活跃"},
    {"id": "INST-010", "name": "SlicingPie动态股权", "file_path": "替身/Skills/SlicingPie动态股权.md", "purpose": "基于贡献的动态股权分配方法论", "status": "活跃"},
    {"id": "INST-011", "name": "DACI治理框架", "file_path": "对话/2026-05-29/替身激活/DACI元治理框架_V1.0_草案.md", "purpose": "Driver-Approver-Contributor-Informed决策权分配", "status": "活跃"},
    {"id": "INST-012", "name": "QB决策法", "file_path": "替身/Skills/QB决策法.md", "purpose": "Question-Based决策法：以问题驱动而非方案驱动", "status": "活跃"},
    {"id": "INST-013", "name": "65%规则", "file_path": "替身/Skills/65%规则.md", "purpose": "满意解核心数学边界：S≥0.65×P(完美解)·Wasserman", "status": "活跃"},
    {"id": "INST-014", "name": "OODA循环", "file_path": "替身/Skills/OODA循环.md", "purpose": "John Boyd观察-定向-决策-行动循环", "status": "活跃"},
    {"id": "INST-015", "name": "三生万物产品体系", "file_path": "替身/Skills/三生万物产品体系.md", "purpose": "产品三脉体系：品牌脉络+产品脉络+知识脉络", "status": "活跃"},
    {"id": "INST-016", "name": "四层漏斗策略", "file_path": "替身/Skills/四层漏斗策略.md", "purpose": "客户转化四层漏斗：认知→评估→决策→落地", "status": "活跃"},
    {"id": "INST-017", "name": "VC投后访谈提纲", "file_path": "对话/2026-05-29/替身激活/VC投后访谈提纲_V1.0_草案.md", "purpose": "VC投后企业诊断标准化访谈框架", "status": "活跃"},
    {"id": "INST-018", "name": "YTT战略建议模板", "file_path": "对话/2026-05-29/替身激活/YTT战略建议_1页纸决策提交.md", "purpose": "一页纸战略建议提交模板(YTT格式)", "status": "活跃"},
    {"id": "INST-019", "name": "星火自评量表", "file_path": "替身/Skills/星火自评量表.md", "purpose": "飞书Base版五维测评自评量表", "status": "活跃"},
    {"id": "INST-020", "name": "蓝军审计框架", "file_path": "替身/Skills/蓝军审计框架.md", "purpose": "蓝军Skeptor-7独立审计标准与流程", "status": "活跃"},
    {"id": "INST-021", "name": "满意解12源验证", "file_path": "替身/Skills/满意解12源验证.md", "purpose": "自检清单12源交叉验证框架", "status": "活跃"},
    {"id": "INST-022", "name": "Gate门控评审", "file_path": "替身/Skills/Gate门控评审.md", "purpose": "四关门控评审标准(L0提案/L1方法/L2质量/L3客户)", "status": "活跃"},
    {"id": "INST-023", "name": "案例诊断框架", "file_path": "替身/Skills/案例诊断框架.md", "purpose": "84案例分类诊断12×8矩阵分析框架", "status": "活跃"},
    {"id": "INST-024", "name": "冬眠模式策略", "file_path": "替身/Skills/冬眠模式策略.md", "purpose": "低功耗维护策略：产品休眠唤醒条件", "status": "活跃"},
    {"id": "INST-025", "name": "54天习惯养成", "file_path": "替身/Skills/54天习惯养成.md", "purpose": "54天分阶段决策习惯训练框架", "status": "活跃"},
]

# ========== 6. workflows ==========
workflows = [
    {"id": "WF-001", "name": "日起课", "trigger": "每日06:00 Cron触发", "steps": ["检查夜间Cron执行报告", "读取Token报告+昨日日志", "更新生命体征仪表盘", "生成今日任务优先级排序", "发送日起简报至飞书群"], "status": "active"},
    {"id": "WF-002", "name": "日毕课", "trigger": "每日22:00 Cron触发", "steps": ["统计当日完成任务数", "汇总今日决策日志", "更新知识飞轮消化进度", "生成日毕归档文件(memory/YYYY-MM-DD.md)", "发送日毕简报至飞书群"], "status": "active"},
    {"id": "WF-003", "name": "数据管道", "trigger": "每6小时Cron触发", "steps": ["扫描workspace文件变化", "提取新增实体/文档/脚本", "更新files_index.json", "更新entities_index.json", "生成驾驶舱种子数据", "发现异常发送警报"], "status": "active"},
    {"id": "WF-004", "name": "免疫扫描", "trigger": "每小时Cron触发", "steps": ["MD5基线比对(L0自身耐受)", "HTML结构完整性检查(L1物理屏障)", "术语统一性扫描(L2先天免疫)", "CSS变量一致性检查", "导航链接有效性验证", "生成immune_memory.json", "发现异常发送免疫警报"], "status": "active"},
    {"id": "WF-005", "name": "知识飞轮", "trigger": "新知识摄入时自动触发", "steps": ["摄入: 接收外部信息(网页/文档/对话)", "消化: 提取关键概念+标注可信度", "吸收: 与已有知识图谱建立连接", "同化: 转化为可执行的方法论/模板", "代谢: 淘汰过时/错误知识，归档经验"], "status": "active"},
    {"id": "WF-006", "name": "部署前检查(Hook)", "trigger": "Git push / 发布前", "steps": ["pre_delivery_gate.py执行四关检查", "蓝军快速审计(敏感信息检测)", "术语一致性终检", "导航链接闭环验证", "生成部署前报告"], "status": "active"},
    {"id": "WF-007", "name": "备份流程", "trigger": "每日23:55 Cron触发 / 手动触发", "steps": ["star_backup.sh执行全量备份", "压缩workspace关键目录", "生成MD5校验文件", "上传至备份存储", "记录备份日志"], "status": "active"},
    {"id": "WF-008", "name": "术语修复流程", "trigger": "术语扫描发现不一致时自动触发", "steps": ["term_sync_engine.py扫描全站术语", "生成不一致清单", "自动执行安全替换(仅site/目录)", "重新扫描确认100%统一", "生成修复报告"], "status": "active"},
    {"id": "WF-009", "name": "飞书同步", "trigger": "每日23:00 Cron触发", "steps": ["连接飞书Base多维表格", "下载任务/客户增量数据", "更新dashboard_seed_v2.json", "写入新发现实体到飞书知识库", "同步生命体征到飞书消息群"], "status": "active"},
    {"id": "WF-010", "name": "邮箱检查", "trigger": "每日10:00+18:00 Cron触发", "steps": ["连接邮箱manyi_hong@sina.com", "检查未读邮件", "分类：客户咨询/系统告警/其他", "客户咨询自动生成跟进任务", "发送邮件摘要"], "status": "active"},
    {"id": "WF-011", "name": "每周生态审计", "trigger": "每周三10:00 Cron触发", "steps": ["L7生态健康检查", "知识债务统计(未消化知识数)", "Cron健康度评估", "替身贡献/激活统计", "生成生态周报"], "status": "active"},
    {"id": "WF-012", "name": "每周决策评估", "trigger": "每周一09:00 Cron触发", "steps": ["回顾上周所有决策记录", "评估决策执行效果", "更新决策优先级", "标记过时/错误决策", "生成决策周报"], "status": "active"},
]

# ========== 7. customer_profiles (detailed) ==========
customer_profiles = [
    # 前5条来自原有 customers 数组但详细化
    {"id": "CUST-001", "name": "硬科技创始人", "company": "硬科技创业公司(通用场景)", "role": "创始人/CEO", "industry": "硬科技", "needs": "凌晨一点决策支持·合伙人关系·融资压力·技术路线分歧", "decision_type": "左脑工程师+右脑创始人", "pain_points": ["合伙人要退出", "技术路线分歧", "融资压力vs产品节奏", "投资人要求换CEO", "不知道下一步怎么走"], "source": "替身/客户/硬科技创始人.md"},
    {"id": "CUST-002", "name": "VC投后负责人", "company": "风险投资机构(通用场景)", "role": "投后管理合伙人", "industry": "风险投资", "needs": "投后诊断·退出策略·冲突调解·CEO评估", "decision_type": "数据驱动·风险控制·管理干预", "pain_points": ["被投企业CEO冲突信号延迟发现", "退出时机判断不准确", "投后管理工具缺失", "缺乏独立的第三方诊断视角"], "source": "替身/客户/VC投后负责人.md"},
    {"id": "CUST-003", "name": "律所合伙人", "company": "律师事务所(通用场景)", "role": "合伙人律师", "industry": "法律服务", "needs": "协议嵌入式决策框架·风险防火墙·合伙协议标准化", "decision_type": "法律框架驱动·风险规避·流程合规", "pain_points": ["协议模板缺乏决策场景嵌入式条款", "客户合伙纠纷法律滞后", "需要标准化的合伙冲突解决工具箱", "法律诉讼vs商业调解平衡"], "source": "替身/客户/律所合伙人.md"},
    {"id": "CUST-004", "name": "政府园区负责人", "company": "地方政府/产业园区(通用场景)", "role": "招商/园区管理负责人", "industry": "公共管理", "needs": "企业诊断·政策匹配·招商决策·园区生态评估", "decision_type": "政策驱动·系统性思维·多方利益平衡", "pain_points": ["招商企业质量评估标准缺失", "园区企业风险预警滞后", "缺乏科学的入驻企业筛选工具", "政策资源与企业需求匹配效率低"], "source": "替身/客户/政府园区负责人.md"},
    {"id": "CUST-005", "name": "独立董事/顾问", "company": "咨询/独立顾问(通用场景)", "role": "独立董事/战略顾问", "industry": "咨询", "needs": "独立数据·预警触发·审计视角·第三方验证", "decision_type": "独立判断·审计视角·数据驱动", "pain_points": ["缺少独立于管理层的数据来源", "预警信号发现不及时", "董事会决策缺乏量化支撑", "需要结构化的独立判断框架"], "source": "替身/客户/独立董事.md"},
    # 飞书驾驶舱 26 个客户 SEED 数据（选关键样本）
    {"id": "CUST-006", "name": "张雪", "company": "张雪机车", "role": "创业者", "industry": "机械制造", "needs": "产品线决策+市场定位", "decision_type": "技术驱动·产品导向", "pain_points": ["产品方向选择困难", "市场验证不足"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-007", "name": "样本-凯越合伙人A", "company": "凯越集团(化名)", "role": "合伙人", "industry": "综合集团", "needs": "合伙人关系治理+决策权分配", "decision_type": "关系驱动·权力平衡", "pain_points": ["合伙人间决策权模糊", "战略方向分歧"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-008", "name": "样本-再创业者B", "company": "某激光科技公司(化名)", "role": "创业者", "industry": "激光科技", "needs": "二次创业风险管理+团队重建", "decision_type": "经验驱动·风险规避", "pain_points": ["二次创业心理负担", "老团队信任重建"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-009", "name": "胡小波", "company": "创鑫激光→镭神智能", "role": "创业者", "industry": "激光雷达", "needs": "转型决策+技术路线选择", "decision_type": "技术前瞻·战略转型", "pain_points": ["赛道切换风险高", "技术路线选择压力大"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-010", "name": "样本-升级期C", "company": "某AI机器人公司(化名)", "role": "技术合伙人", "industry": "AI+机器人", "needs": "产品升级+技术合伙人角色定位", "decision_type": "技术驱动·产品迭代", "pain_points": ["产品升级方向分歧", "合伙人角色边界模糊"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-011", "name": "正浩创新-苏炜", "company": "正浩创新(EcoFlow)", "role": "合伙人(前)", "industry": "新能源/储能", "needs": "合伙人退出经验吸取+冲突预防", "decision_type": "经验复盘·事前预防", "pain_points": ["合伙人退出处理经验总结", "退出后关系维护"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-012", "name": "样本-转型期D", "company": "某硬件创业公司(化名)", "role": "创业者", "industry": "硬件/IoT", "needs": "企业转型决策+业务重心调整", "decision_type": "市场驱动·灵活调整", "pain_points": ["转型窗口期短", "组织惯性大"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-013", "name": "样本-转型期D2", "company": "某储能公司(化名)", "role": "合伙人", "industry": "储能", "needs": "能源赛道定位+伙伴生态构建", "decision_type": "趋势驱动·生态思维", "pain_points": ["储能赛道竞争激烈", "伙伴关系脆弱"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-014", "name": "疯孩科技创始人", "company": "疯孩科技(Crazybaby)", "role": "创业者", "industry": "消费电子", "needs": "产品创新+品牌定位", "decision_type": "产品驱动·品牌导向", "pain_points": ["品牌差异化难建立", "资金链压力大"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-015", "name": "港中文教授", "company": "港中文(深圳)教授创业案(化名)", "role": "创业者", "industry": "学术创业", "needs": "学术转商业+IP转化", "decision_type": "学术驱动·谨慎保守", "pain_points": ["学术思维vs商业思维冲突", "IP估值与股权分配不当"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-016", "name": "样本-打磨期E", "company": "某半导体设备公司(化名)", "role": "技术合伙人", "industry": "半导体设备", "needs": "技术打磨+客户验证", "decision_type": "技术精益·客户导向", "pain_points": ["产品打磨周期过长", "客户验证不充分"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-017", "name": "样本-打磨期E2", "company": "某光通信公司(化名)", "role": "创业者", "industry": "光通信", "needs": "技术突破+市场切入", "decision_type": "技术壁垒·精准切入", "pain_points": ["技术领先但市场滞后", "人才流失风险"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-018", "name": "泡面吧-技术合伙人", "company": "泡面吧(化名)", "role": "技术合伙人", "industry": "互联网/教育", "needs": "冲突复盘+合伙人教训总结", "decision_type": "复盘驱动·教训吸取", "pain_points": ["经典合伙人冲突案例", "信任破裂后遗症"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-019", "name": "样本-次年危机F", "company": "某无人机公司(化名)", "role": "创业者", "industry": "无人系统", "needs": "危机管理+战略调整", "decision_type": "危机驱动·快速调整", "pain_points": ["融资后第二年产品危机", "团队信心崩塌"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-020", "name": "龙华无人机创始人", "company": "龙华无人机公司(化名)", "role": "创业者", "industry": "无人系统", "needs": "产业定位+供应链决策", "decision_type": "产业驱动·供应链思维", "pain_points": ["供应链不稳定", "产品竞争力下降"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-021", "name": "样本-关系定位G", "company": "某新材料公司(化名)", "role": "合伙人", "industry": "新材料", "needs": "合伙人关系重新定位+角色再分配", "decision_type": "关系驱动·角色重塑", "pain_points": ["合伙人角色重叠", "贡献认定不一致"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-022", "name": "大疆-朱晓蕊", "company": "大疆创新(DJI)", "role": "技术合伙人(前)", "industry": "消费级无人机", "needs": "经典案例研究+技术合伙人退出教训", "decision_type": "案例研究·教训总结", "pain_points": ["技术合伙人退出经典案例", "知识产权归属争议"], "source": "飞书驾驶舱SEED"},
    {"id": "CUST-023", "name": "样本-技术合伙人H", "company": "某机器人公司(化