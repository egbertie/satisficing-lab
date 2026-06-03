"""
yitang_methodology_kit.py
一堂方法论数字资产工具箱

来源:
- 一堂5亿烧钱案例集 (Feishu Doc) — 129个案例目录全量提取
- 一堂AI加速包 (Feishu Wiki) — 课程结构与元数据
- 一堂·AI未来实验室 (Feishu Wiki) — Coze智能体与提示词知识库导航
- 两节实操/地图课 (yitang.top) — 受登录保护，已登记为外部引用

版本: V1.0
生成时间: 2026-04-09
处理流程: 文件内化标准作业流程 V1.0（Web链路适配版）
说明: 本资产将一堂公开可获取的方法论材料结构化为可运行的Python工具箱，
      对受保护内容建立注册表与追踪机制，避免知识丢失。
"""

from typing import List, Dict, Optional, Tuple


class LeanStartupSpectrum:
    """
    一堂低成本创业成本光谱模型（源自《一堂低成本创业全景图谱·超级小抄》）
    
    核心洞察：创业成本不是二元选择（做 vs 不做），而是连续光谱。
    从"最省成本"到"最高成本"有6个可操作的策略节点，每个节点对应
    一套落地武器库（tactics）。
    """

    SPECTRUM_STAGES: List[Dict] = [
        {
            "stage_id": "direct_test",
            "name": "直接测试",
            "cost_level": "min",
            "mindset": "不做产品，直接验证",
            "tactics": {
                "假产品": [
                    "假电商页面，投流测试",
                    "假商品包装，挂店测试",
                    "假商品包装，用户测试",
                    "假产品页面，模拟使用",
                    "假购买页，留邮箱线索",
                    "假注册页，留下手机号",
                    "假按钮，看用户点击",
                    "假开店传单，留微信或电话",
                    "假菜单，看新品吸引力",
                    "假视频广告Demo，看用户反馈",
                    "假宣传产品图册，测试需求",
                ],
                "讲故事": [
                    "写一个竞争故事，看用户兴趣",
                    "写一个品牌概念，找种子用户",
                    "写新闻稿，打动员工",
                    "写商业计划BP，测试创业热度",
                ],
                "直接预售": [
                    "预售专家服务，争取意向订单",
                    "预售大众消费品，进行拼团",
                    "预售SaaS产品，招募天使客户",
                    "预售高科技产品，进行众筹",
                ],
            },
            "sri_mapping": "SKU-A 合伙人匹配诊断的核心思想：在投入重资产前，用最小成本验证'匹配假设'。",
        },
        {
            "stage_id": "human_vip",
            "name": "人工VIP服务",
            "cost_level": "low",
            "mindset": "模拟产品，提供VIP服务",
            "tactics": {
                "提供人工VIP服务": [
                    "用CEO跑腿，替代产品研发",
                    "用个性咨询，替代课程研发",
                    "用人工定制，替代标准化服务",
                    "用人工摆摊，替代直接租门店",
                ],
            },
            "sri_mapping": "高价值合伙人匹配可先采用1v1深度咨询（CEO亲自服务），验证需求后再产品化。",
        },
        {
            "stage_id": "borrow_tools",
            "name": "借用工具",
            "cost_level": "low-mid",
            "mindset": "提供产品，但用现成工具",
            "tactics": {
                "用好流量工具": [
                    "用好电商平台，用卖货平台",
                    "用好内容平台，小宇宙/简书",
                    "用好课程平台，荔枝/千聊/喜马拉雅",
                    "用好朋友圈，直接获得种子用户",
                    "用好论坛社区，B站/知乎/小红书/贴吧",
                ],
                "直接搭建产品": [
                    "用搭建产品原型，直接用最佳实践",
                    "搭建产品界面，直接用原型工具（墨刀/Axure）",
                    "搭建知识产品，直接用课程工具（小鹅通等）",
                    "搭建内容产品，直接用在线文档（飞书/石墨）",
                    "搭建订单系统，直接用表格（EXCEL/飞书多维表格）",
                    "搭建CRM，直接用表单工具（麦客/问卷星/简道云）",
                    "搭建客服系统，直接用IM社群（企业微信）",
                    "搭建活动系统，直接用活动工具（活动行/互动吧/百格活动）",
                    "搭建直播系统，用线上协作（ZOOM/腾讯会议/钉钉）",
                ],
                "借用别人资源": [
                    "借用别人产品，偷偷帮卖",
                    "借用别人产品，合作销售",
                    "借用别人的资源，以租代买/省下采购",
                    "借用现有专家，替代专家团队（在行）",
                    "借用已有/同行销售，不招聘销售",
                    "借用工厂，用别人生产能力",
                    "借用别人门店，承包而不开店",
                    "借用现成高端通用产品，代替专用产品",
                ],
            },
            "sri_mapping": "满意解研究所早期可借用飞书/企微/Zoom等现成工具构建服务交付体系，无需自研SaaS。",
        },
        {
            "stage_id": "human_replace",
            "name": "人工替代",
            "cost_level": "mid",
            "mindset": "极小开发，尽量用人工替代",
            "tactics": {
                "先用人工/避免重投入": [
                    "不做智能硬件，用人工模拟处理",
                    "不做AI算法，用人工运营替代",
                    "不做调度系统，用人工协调处理",
                    "不做订单系统，用人工表格替代",
                    "不做外呼系统，用人工电话替代",
                    "不做选品系统，用人工调研替代",
                    "不做定价规则，用销售人工测试",
                    "不做客服系统，用人工客服",
                ],
            },
            "sri_mapping": "合伙人评估报告的早期生成可以部分依赖专家人工撰写，而非一上来就建立全自动AI评估模型。",
        },
        {
            "stage_id": "mvp",
            "name": "最小版本",
            "cost_level": "mid-high",
            "mindset": "开始开发，但只做最小版本",
            "tactics": {
                "只发布最小版本": [
                    "只做产品内核，只做最小功能集",
                    "只做产品小样，测试用户需求",
                    "只做小批量生产，避免大量压库存",
                    "只提供新菜品试吃，引导给反馈",
                    "只做品鉴会，用原型试用",
                    "只做游戏核心玩法，替代完整游戏",
                    "只做快闪店，替代直接开店",
                    "只做租赁吧台，替代直接开店",
                ],
                "努力砍功能": [
                    "只开发一半，要求团队砍掉50%",
                    "砍掉成长体系（等级/勋章/积分）",
                    "砍掉多账号平台登录",
                    "砍掉专业全套视觉VI",
                    "砍掉公司精美官网",
                    "砍掉精装修，做简装门店",
                ],
            },
            "sri_mapping": "合伙人匹配系统的V1.0只需核心功能：信息录入→评估维度计算→报告输出。砍掉社区、积分、进阶课程等。",
        },
        {
            "stage_id": "full_dev",
            "name": "全量开发",
            "cost_level": "max",
            "mindset": "开发筹备所有东西，然后发布",
            "tactics": {
                "投入全量研发": [
                    "直接开发全部软件系统",
                    "直接开发全部硬件系统",
                    "直接开发细节完备的产品",
                    "直接开面积很大的店",
                    "直接定义大而全的专家服务",
                ],
                "投入全量资源": [
                    "模型没跑通，进非常多的货物",
                    "模型没跑通，签违约金很高的合同",
                    "模型没跑通，花费大量精力搞定资源",
                    "模型没跑通，直接组建专业服务团队",
                ],
                "投入全量扩张": [
                    "1家店没有，直接开N家",
                    "1节课没有，直接做N节",
                    "1款产品没有，直接发布N款",
                    "1个平台没有，直接对接N个",
                ],
            },
            "sri_mapping": "🚨 满意解研究所当前阶段应避免的动作：全量扩张、重资产平台开发、盲目组建大规模团队。",
        },
    ]

    LOW_COST_PRINCIPLES: List[str] = [
        "尽早发布",
        "小步快跑",
        "克制设计",
        "拥抱变化",
    ]

    FATAL_WASTES: List[Dict] = [
        {"id": "wrong_problem", "name": "问题找错", "antidote": "用一堂五步法反复验证'关键假设'", "sri_relevance": "合伙人匹配中最致命的错误：帮客户找错'合适的合伙人'标准。"},
        {"id": "wrong_solution", "name": "方案做错", "antidote": "用'直接测试'和'假产品'快速验证方案", "sri_relevance": "提供的评估框架如果与客户实际场景脱节，就是方案做错。"},
        {"id": "premature_detail", "name": "过早细化", "antidote": "在MVP验证前不做完整视觉/多平台/成长体系", "sri_relevance": "不要在合伙人匹配系统V1.0中过度设计UI、积分体系、社交功能。"},
        {"id": "premature_expansion", "name": "过早扩张", "antidote": "单点模型跑通前，不开分店/不扩团队/不加SKU", "sri_relevance": "先服务10-15个真实案例，再考虑规模化和SaaS化。"},
        {"id": "ivory_tower", "name": "闭门造车", "antidote": "强迫自己每周至少与客户沟通3次", "sri_relevance": "合伙人评估模型必须扎根于真实案例反馈，不能仅从理论推导。"},
        {"id": "blind_persistence", "name": "盲目坚持", "antidote": "建立清晰的NO-GO/DEFER决策标准", "sri_relevance": "当客户与合伙人实际匹配度极低时，要敢于说'不'，而不是硬撮合。"},
    ]

    @classmethod
    def get_stage(cls, stage_id: str) -> Optional[Dict]:
        for s in cls.SPECTRUM_STAGES:
            if s["stage_id"] == stage_id:
                return s
        return None

    @classmethod
    def get_tactics_by_stage(cls, stage_id: str) -> Dict[str, List[str]]:
        stage = cls.get_stage(stage_id)
        return stage["tactics"] if stage else {}

    @classmethod
    def sri_adaptation_report(cls) -> Dict:
        """生成一堂低成本创业模型对满意解研究所的映射报告。"""
        return {
            "advice": "满意解研究所当前应集中在'直接测试→人工VIP→借用工具'三阶段。",
            "current_stage_recommendation": ["direct_test", "human_vip", "borrow_tools"],
            "avoid_stages": ["full_dev"],
            "top_3_fatal_wastes_to_watch": ["wrong_problem", "premature_expansion", "ivory_tower"],
            "principles_to_embed": cls.LOW_COST_PRINCIPLES,
        }


class ProductKernelMetrics:
    """
    一堂产品内核·十大典型指标
    
    来源：一堂产品内核课程（2026-04-09 关键图解归档）
    将产品健康度拆解为获客→服务→复购三段漏斗，每段有明确可操作指标。
    """

    METRICS_TREE: Dict[str, List[Dict]] = {
        "获客环节": [
            {"metric": "销转率", "definition": "看潜在客户转化为实际购买客户的比例", "sri_mapping": "咨询意向客户 → 实际购买SKU-A/B/C诊断服务的比例"},
            {"metric": "动销率", "definition": "看有销售的商品品种数与所有商品总品种数的比例", "sri_mapping": "合伙人评估工具/模板中，被实际使用过的比例"},
            {"metric": "捕获率", "definition": "看进店消费人数占总经过人流量的比例", "sri_mapping": "内容/公域曝光 → 实际进入私域/预约咨询的比例"},
        ],
        "服务环节": [
            {"metric": "留存率", "definition": "看使用产品的用户，N天/周/月后还在持续使用的比例", "sri_mapping": "购买SKU-A诊断后，30天内继续购买SKU-B教练服务的比例"},
            {"metric": "完课率", "definition": "看用户是不是能完成履约和最后学习", "sri_mapping": "合伙人决策教练服务中，客户是否完成全部评估流程并拿到最终报告"},
            {"metric": "退款率", "definition": "看服务履约中，用户退款的比例", "sri_mapping": "因评估结果不满意或服务未达预期导致的退款比例（警戒线<3%）"},
            {"metric": "满意率", "definition": "看用户接受完服务，满意度的比例和打分", "sri_mapping": "NPS/CSAT评分，目标是>8分（满分10分）"},
        ],
        "复购环节": [
            {"metric": "复购率", "definition": "看消费购买后，会继续购买的比例", "sri_mapping": "SKU-A → SKU-B 的转化率（诊断客户升级为教练客户）"},
            {"metric": "续费率", "definition": "看续费用户数占现有用户数的比例", "sri_mapping": "SKU-C年度托管服务的续约率（长期关系质量指标）"},
            {"metric": "推荐率", "definition": "看用户是否愿意主动推荐的比率", "sri_mapping": "客户主动推荐其他创始人使用合伙人匹配服务（NPS推荐者比例）"},
        ],
    }

    @classmethod
    def get_metrics_by_stage(cls, stage: str) -> List[Dict]:
        return cls.METRICS_TREE.get(stage, [])

    @classmethod
    def sri_funnel_report(cls) -> Dict:
        """生成满意解研究所基于十大指标的服务漏斗报告模板。"""
        return {
            "business_name": "满意解研究所合伙人匹配服务",
            "funnel_stages": {
                "获客": {m["metric"]: {"target": "TBD", "current": "TBD", "definition": m["definition"]} for m in cls.METRICS_TREE["获客环节"]},
                "服务": {m["metric"]: {"target": "TBD", "current": "TBD", "definition": m["definition"]} for m in cls.METRICS_TREE["服务环节"]},
                "复购": {m["metric"]: {"target": "TBD", "current": "TBD", "definition": m["definition"]} for m in cls.METRICS_TREE["复购环节"]},
            },
            "health_check_rules": {
                "销转率_<5%": "获客渠道或价值主张需优化",
                "完课率_<70%": "服务流程过重或客户动力不足，需简化或加强交付设计",
                "退款率_>5%": "服务预期管理或评估准确性出现系统性问题",
                "推荐率_<20%": "产品口碑尚未形成，需聚焦超预期交付",
            },
        }


class KeyMethodologyImageArchive:
    """
    关键方法论图片归档追踪器
    
    使命：对"系统、方法论、逻辑"类关键图片建立永久归档，
    对"对话或示意类"图片不做强制归档，避免信息噪音。
    """

    ARCHIVE_ROOT: str = "archive/key_methodology_images/"

    IMAGE_REGISTRY: List[Dict] = [
        {
            "archive_id": "IMG-20260409-001",
            "original_name": "51aa1f7ad83f1e2e7e5e13572def0236.png",
            "archived_name": "yitang_lean_startup_cheatsheet.png",
            "title": "一堂低成本创业全景图谱·超级小抄",
            "category": "方法论/系统框架",
            "source": "一堂课程资料（用户上传）",
            "archived_at": "2026-04-09T20:00:00+08:00",
            "archive_path": "archive/key_methodology_images/2026-04-09/yitang_lean_startup_cheatsheet.png",
            "status": "archived_and_extracted",
            "extracted_modules": ["LeanStartupSpectrum", "LOW_COST_PRINCIPLES", "FATAL_WASTES"],
            "verification_status": "pending_user_review",
        },
        {
            "archive_id": "IMG-20260409-002",
            "original_name": "80c1764d2d19d147e2cb8f4dfaddf889.png",
            "archived_name": "yitang_product_kernel_10_metrics.png",
            "title": "一堂产品内核·十大典型指标",
            "category": "方法论/指标体系",
            "source": "一堂课程资料（用户上传）",
            "archived_at": "2026-04-09T20:00:00+08:00",
            "archive_path": "archive/key_methodology_images/2026-04-09/yitang_product_kernel_10_metrics.png",
            "status": "archived_and_extracted",
            "extracted_modules": ["ProductKernelMetrics"],
            "verification_status": "pending_user_review",
        },
        {
            "archive_id": "IMG-20260409-003",
            "original_name": "4ec6f9fbe63f8f86a209a3ed24a97e6f.png",
            "title": "待下载后识别",
            "category": "待确认",
            "status": "download_failed_http_429",
            "retry_plan": "下次心跳或用户再次上传时重试",
        },
        {
            "archive_id": "IMG-20260409-004",
            "original_name": "fc91b4d17d550bf25cc08738c6ea0b44.png",
            "title": "待下载后识别",
            "category": "待确认",
            "status": "download_failed_http_429",
            "retry_plan": "下次心跳或用户再次上传时重试",
        },
        {
            "archive_id": "IMG-20260409-005",
            "original_name": "21e0e8c800d385f59fef61cbbaadfd00.png",
            "title": "待下载后识别",
            "category": "待确认",
            "status": "download_failed_http_429",
            "retry_plan": "下次心跳或用户再次上传时重试",
        },
        {
            "archive_id": "IMG-20260409-006",
            "original_name": "19d7232e-bcf2-88fe-8000-000082a13904_image.png",
            "archived_name": "yitang_startup_roadmap_entrepreneur.png",
            "title": "一堂创业地图：高潜力创业者修炼全景图",
            "category": "方法论/系统框架",
            "source": "一堂课程资料（用户上传）",
            "archived_at": "2026-04-09T20:15:00+08:00",
            "archive_path": "archive/key_methodology_images/2026-04-09/yitang_startup_roadmap_entrepreneur.png",
            "md_path": "A-manyige/参考资料/一堂方法论/创业地图/一堂创业地图_高潜力创业者修炼全景图.md",
            "status": "archived_and_extracted",
            "extracted_modules": ["YitangStartupRoadmap"],
            "verification_status": "pending_user_review",
        },
        {
            "archive_id": "IMG-20260409-007",
            "original_name": "19d7232f-ddf2-8f7d-8000-0000c3bd0bb2_image.png",
            "archived_name": "yitang_management_roadmap_leader.png",
            "title": "一堂管理地图：高潜力管理者修炼全景图",
            "category": "方法论/系统框架",
            "source": "一堂课程资料（用户上传）",
            "archived_at": "2026-04-09T20:15:00+08:00",
            "archive_path": "archive/key_methodology_images/2026-04-09/yitang_management_roadmap_leader.png",
            "md_path": "A-manyige/参考资料/一堂方法论/管理地图/一堂管理地图_高潜力管理者修炼全景图.md",
            "status": "archived_and_extracted",
            "extracted_modules": ["YitangManagementRoadmap"],
            "verification_status": "pending_user_review",
        },
        {
            "archive_id": "IMG-20260409-008",
            "original_name": "19d72330-b2f2-805d-8000-00002909ea08_image.png",
            "title": "待下载后识别",
            "category": "待确认",
            "status": "download_failed_http_429",
            "retry_plan": "下次心跳或用户再次上传时重试",
        },
        {
            "archive_id": "IMG-20260409-009",
            "original_name": "19d7237f-7e62-889d-8000-000001c66269_image.png",
            "archived_name": "yitang_personal_roadmap_growth.png",
            "title": "一堂个人地图：高潜力成长者修炼全景图",
            "category": "方法论/系统框架",
            "source": "一堂课程资料（用户上传）",
            "archived_at": "2026-04-09T21:00:00+08:00",
            "archive_path": "archive/key_methodology_images/2026-04-09/yitang_personal_roadmap_growth.png",
            "md_path": "A-manyige/参考资料/一堂方法论/个人地图/一堂个人地图_高潜力成长者修炼全景图.md",
            "status": "archived_and_extracted",
            "extracted_modules": ["YitangPersonalRoadmap"],
            "verification_status": "pending_user_review",
        },
    ]

    @classmethod
    def list_archived(cls) -> List[Dict]:
        return [img for img in cls.IMAGE_REGISTRY if img.get("status") == "archived_and_extracted"]

    @classmethod
    def list_pending(cls) -> List[Dict]:
        return [img for img in cls.IMAGE_REGISTRY if "failed" in img.get("status", "")]

    @classmethod
    def get_by_id(cls, archive_id: str) -> Optional[Dict]:
        for img in cls.IMAGE_REGISTRY:
            if img.get("archive_id") == archive_id:
                return img
        return None


class YitangPersonalRoadmap:
    """
    一堂个人地图：高潜力成长者修炼全景图

    核心洞察：个人成长天花板由底层能力构建深度决定。
    三层结构：追求层（人生红点） → 领先层（成长竞争力6+1） → 基础层（四大支柱）
    """

    LAYERS: Dict[str, Dict] = {
        "pursuit": {
            "name": "追求层",
            "core": "人生红点",
            "definition": "你的人生北极星，决定所有成长的方向感",
            "sri_mapping": "Egbertie的人生红点：帮助硬科技创始人在合伙人选择这一高风险决策点上提升胜率",
        },
        "leading": {
            "name": "领先层",
            "core": "成长竞争力 6+1",
            "competencies": [
                {"id": "decision", "name": "决策力", "sri_status": "核心竞争力", "evidence": "22年双系统经验 + CBIIP认证"},
                {"id": "learning", "name": "学习力", "sri_status": "强", "evidence": "持续将方法论内化到代码资产"},
                {"id": "product", "name": "产品力", "sri_status": "构建中", "evidence": "SKU-A/B/C产品设计与服务流程"},
                {"id": "leadership", "name": "领导力", "sri_status": "中上", "evidence": "儒商伦理框架 + 守护型陪伴"},
                {"id": "sales", "name": "销售力", "sri_status": "待系统打磨", "evidence": "内容获客和口碑转介绍为主"},
                {"id": "hard_skill", "name": "硬能力", "sri_status": "强", "evidence": "金融分析(CFP/CFC/FAIAA) + 软件工程(MSE)"},
            ],
            "energy": {"name": "心力", "role": "核心能量", "sri_mapping": "睡眠优化、压力测试、能量治疗保障心力可持续"},
        },
        "foundation": {
            "name": "基础层",
            "pillars": [
                {"name": "时间管理", "tool": "四象限审计 + Q2健康度", "source": "一堂复盘营"},
                {"name": "知识管理", "tool": "输入→加工→输出三层架构", "source": "一堂复盘营"},
                {"name": "科学成长", "tool": "刻意练习飞轮 + 基本功清单", "source": "一堂复盘营"},
                {"name": "科学复盘", "tool": "复盘四问 + 红点洞察", "source": "一堂复盘营"},
            ],
        },
    }

    GROWTH_RINGS: List[Dict] = [
        {"name": "有驱动", "source": "人生红点", "failure_mode": "有驱动无支撑 → 理想主义者"},
        {"name": "有支撑", "source": "成长系统（四大支柱）", "failure_mode": "有支撑无驱动 → 高效机器"},
        {"name": "有空间", "source": "心力状态", "failure_mode": "驱动和支撑都有但心力不足 → burnout"},
    ]

    @classmethod
    def get_competency(cls, competency_id: str) -> Optional[Dict]:
        comps = cls.LAYERS["leading"]["competencies"]
        for c in comps:
            if c["id"] == competency_id:
                return c
        return None

    @classmethod
    def sri_assessment(cls) -> Dict:
        """生成 Egbertie 个人成长地图的当前状态评估。"""
        comps = cls.LAYERS["leading"]["competencies"]
        strengths = [c for c in comps if c["sri_status"] in ("核心竞争力", "强")]
        build_zones = [c for c in comps if c["sri_status"] in ("构建中", "待系统打磨")]
        return {
            "strengths": strengths,
            "build_zones": build_zones,
            "protection_zone": ["心力", "睡眠", "能量管理"],
            "next_6_month_focus": ["产品力", "销售力"],
        }

    @classmethod
    def roadmap_trilogy(cls) -> Dict:
        """一堂三张地图的完整关系。"""
        return {
            "创业地图": {"goal": "概率", "question": "如何构建一家有价值的公司", "scope": "公司"},
            "管理地图": {"goal": "段位", "question": "如何带领团队和组织", "scope": "组织"},
            "个人地图": {"goal": "天花板", "question": "我是谁、我要去哪里", "scope": "个体"},
        }


class YitangMethodologyKit:
    """
    一堂方法论统一入口。
    整合复盘营PDF（project_operation_playbook.py）与线上补充资料。
    """

    # 2026-04-09 从 Feishu Doc 全量提取的129个案例目录
    CASE_STUDY_CATALOG: Dict[str, List[str]] = {
        "第一章：关键假设相关": [
            "餐饮调味料平台", "新零售实体店", "瑜伽课程预约平台", "美业（美发店）供应链",
            "房产项目", "幼儿园教育项目", "跑步项目", "孕产服务项目",
            "互联网医疗项目（慢性病）", "5G项目", "社区餐饮服务", "橱窗新媒体",
            "新医药培训", "幼儿园手偶剧", "花木电商", "法务项目",
            "K12学习能力的直播平台", "凉皮产品", "治疗颈椎疾病", "鲜辣条",
            "设计对接平台", "养老SaaS", "球鞋潮服进销存SaaS", "本地建材O2O项目",
            "少儿口才教育", "户外教育营地项目", "少儿财商", "在线画廊",
            "旅行约伴", "文具实体店", "世界上最大的牙膏", "酒店智能管家",
            "针对大学生的独立电商", "个性营养配餐", "第三方电商服务商", "智能电子飞镖靶",
            "周边旅游度假订阅", "医疗视频问诊", "在线抽奖平台", "3个农村市场的项目",
            "代餐减肥服务", "茶文化", "智能美妆", "医美SaaS",
            "潜水旅游平台", "智能门禁项目",
        ],
        "第二章：需求判断相关": [
            "中小企业共享设计中心", "社区生活项目", "室内设计服务", "美业服务平台",
            "中小工程服务商", "旅行摄影O2O平台", "白领早餐外卖", "求职平台",
            "甜品店连锁", "儿童游戏化百科全书", "室内设计服务(重复)", "车队管理类SaaS",
            "孕产恢复项目", "客户CRM系统", "眼视光行业B2B平台", "住院病人营养膳食定制",
            "绿色包装材料", "房产买方经纪平台", "智能皮肤检测", "保险聊天机器人",
            "滋补品新零售", "智能客服", "医务工作者社区", "Airbnb",
            "女性社群创业教育", "自动洗头机", "茶叶消费品", "自助会议空间",
            "婴幼儿健康管理", "义齿交易平台", "新式茶饮的项目", "酒店采购平台",
            "茶叶社区团购", "校服补定", "国际中文在线教育", "低碳无糖健康饮食",
            "精酿啤酒屋", "线下健康咨询和调理", "在线招聘", "3个反思案例",
            "在线教育", "数字广告追踪SaaS", "托幼地产教育", "设计类专业服务公司",
            "线下咖啡店分析", "精酿啤酒项目", "运动类产品找基准值",
        ],
        "第三章：产品内核相关": [],  # 目录中归入第二章连续性展示
        "第四章：商业模式相关": [],
        "第五章：调研相关": [
            "场馆的租金调研", "线下培训公考项目", "早托门店选址调研", "电话机器人",
            "生鲜零售", "3D打印美甲", "酒店婚礼堂", "前衍化学平台",
            "驾考考试", "面包店调研", "洗车店", "青年旅舍",
            "留学产品", "工业设计算法平台", "调研方法集", "老年大学",
            "郑州地区酒店的调研", "物联网esim虚拟运营商", "栗子智能无人售货机",
        ],
        "第六章：精益相关": [
            "社群电商", "海外O2O订餐", "社区新零售", "工业品硬件项目",
            "手工实体店", "鲜奶品牌", "共享模具设计师", "保险行业培训",
            "跨城市的O2O物流", "智能录音笔", "VR项目", "小餐饮加盟",
            "老人运动健身服务", "珠宝电商", "绿植电商", "酒店共享空气净化器",
            "家庭终身教育平台",
        ],
    }

    # AI加速包课程结构（2026-04-09 提取）
    AI_ACCELERATION_PACK: Dict = {
        "title": "一堂AI加速包",
        "source": "https://yitanger.feishu.cn/wiki/Vq7WwkOvCijkTakdRxBcDsSXnVc",
        "components": [
            {
                "name": "OpenClaw实战分享",
                "type": "直播回放",
                "links": {
                    "live_replay": "https://air.yitang.top/live/YYOkdYDSJ2?rs=1831",
                    "transcript_doc": "https://yitang.top/fs-doc/56dbad0849d63c80e592efd116ed5394/W7U9dkBraowtu6xpoRac3OmsnDe",
                },
                "access_status": "需登录",
            },
            {
                "name": "Coze从入门到落地",
                "type": "直播回放",
                "links": {
                    "live_replay": "https://air.yitang.top/live/451DGBoBVD?rs=0123",
                },
                "access_status": "需登录",
                "lecturer": "于陆",
                "lecturer_bio": [
                    "一堂课程产品经理，负责AI俱乐部",
                    "曾讲《人工智能第一课》《提示词必修课》",
                    "18年技术研发经验+两次创业经历",
                    "少校军官，曾在部队做研究",
                ],
            },
        ],
    }

    # 受保护/需登录的外部资源注册表（避免丢失）
    LOCKED_RESOURCE_REGISTRY: List[Dict] = [
        {
            "name": "实操案例课《精益案例：我的3个新业务实验》",
            "lecturer": "张磊（一堂合伙人）",
            "url": "https://yitang.top/lesson/5WdV5f34d2d94267",
            "barrier": "微信扫码登录墙",
            "status": "待用户手动提取",
        },
        {
            "name": "一堂24年新版《一堂新学期地图课》",
            "lecturer": "Truman",
            "url": "https://yitang.top/lesson/luvS64ef293fbe0d",
            "barrier": "微信扫码登录墙",
            "status": "待用户手动提取",
        },
        {
            "name": "OpenClow实战分享-文稿",
            "url": "https://yitang.top/fs-doc/56dbad0849d63c80e592efd116ed5394/W7U9dkBraowtu6xpoRac3OmsnDe",
            "barrier": "微信扫码登录墙",
            "status": "待用户手动提取",
        },
        {
            "name": "一堂·AI未来实验室（CozePrompt知识库）",
            "url": "https://yitanger.feishu.cn/wiki/DUqzwFT7oiUFFekTh2WcDzepnzc",
            "sections": [
                "M. 奇迹层：AI未来幻想",
                "U. 使用层：AI工具使用",
                "U1. 提示词 Prompt",
                "U2. 智能体 Agent",
                "提示词大赛系列（5/9/10/11）",
                "于陆：Coze实践汇总",
            ],
            "barrier": "Wiki导航页可浏览，子页面详情需逐层展开",
            "status": "已提取知识库骨架，详情页待补充",
        },
    ]

    # 全体案例提取时间戳
    EXTRACTED_AT = "2026-04-09T17:20:00+08:00"

    def __init__(self):
        self._build_flat_index()

    def _build_flat_index(self):
        self._flat_cases = []
        for chapter, cases in self.CASE_STUDY_CATALOG.items():
            for c in cases:
                if "(重复)" in c:
                    continue
                self._flat_cases.append({"chapter": chapter, "case": c})

    def search_cases(self, keyword: str) -> List[Dict]:
        """按关键词搜索案例。"""
        k = keyword.lower()
        return [item for item in self._flat_cases if k in item["case"].lower()]

    def get_chapter_cases(self, chapter: str) -> List[str]:
        """获取指定章节的所有案例。"""
        return self.CASE_STUDY_CATALOG.get(chapter, [])

    def case_stats(self) -> Dict:
        """案例集统计信息。"""
        return {
            "total_unique_cases": len(self._flat_cases),
            "chapter_count": len(self.CASE_STUDY_CATALOG),
            "chapter_breakdown": {k: len(v) for k, v in self.CASE_STUDY_CATALOG.items()},
            "extracted_at": self.EXTRACTED_AT,
        }

    def export_report(self) -> Dict:
        """导出一堂方法论当前资产状态报告。"""
        return {
            "methodology_name": "一堂方法论",
            "version": "V1.2",
            "generated_at": self.EXTRACTED_AT,
            "case_studies": self.case_stats(),
            "ai_acceleration": self.AI_ACCELERATION_PACK,
            "locked_resources": {
                "total": len(self.LOCKED_RESOURCE_REGISTRY),
                "items": self.LOCKED_RESOURCE_REGISTRY,
            },
            "lean_startup_spectrum": {
                "stages": len(LeanStartupSpectrum.SPECTRUM_STAGES),
                "sri_adaptation": LeanStartupSpectrum.sri_adaptation_report(),
            },
            "product_kernel_metrics": {
                "metric_count": 10,
                "sri_funnel_template": ProductKernelMetrics.sri_funnel_report(),
            },
            "personal_roadmap": {
                "layers": list(YitangPersonalRoadmap.LAYERS.keys()),
                "sri_assessment": YitangPersonalRoadmap.sri_assessment(),
                "trilogy": YitangPersonalRoadmap.roadmap_trilogy(),
            },
            "image_archive": {
                "archived": len(KeyMethodologyImageArchive.list_archived()),
                "pending": len(KeyMethodologyImageArchive.list_pending()),
                "items": KeyMethodologyImageArchive.IMAGE_REGISTRY,
            },
        }

    @staticmethod
    def get_sri_adaptation() -> Dict:
        """快速获取一堂方法论对满意解研究所的适配建议。"""
        return {
            "cost_spectrum": LeanStartupSpectrum.sri_adaptation_report(),
            "metrics": ProductKernelMetrics.sri_funnel_report(),
            "personal_growth": YitangPersonalRoadmap.sri_assessment(),
            "fatal_wastes_to_watch": [
                w for w in LeanStartupSpectrum.FATAL_WASTES
                if w["id"] in LeanStartupSpectrum.sri_adaptation_report()["top_3_fatal_wastes_to_watch"]
            ],
        }
