"""
满意解研究所 · 数据模型 v2.0
===========================
从第一性原理重构：关系数据是核心资产
颗粒度细化到每个行为事件、每次页面访问、每个决策环节
"""

CREATE_TABLES = """
-- ═══════════════════════════════════════
-- 1. 客户主表（360° 画像）
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 基础信息
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    phone TEXT DEFAULT '',
    avatar_url TEXT DEFAULT '',
    
    -- 企业画像
    company TEXT DEFAULT '',
    position TEXT DEFAULT '',
    industry TEXT DEFAULT '',          -- 行业赛道
    company_stage TEXT DEFAULT '',     -- 企业阶段
    company_size TEXT DEFAULT '',      -- 团队规模
    city TEXT DEFAULT '',              -- 城市
    funding TEXT DEFAULT '',           -- 已融资金额
    
    -- 决策画像
    decision_style TEXT DEFAULT '',    -- 五维类型（如：土金水木火组合）
    decision_maturity TEXT DEFAULT '', -- 决策成熟度评分
    pain_points TEXT DEFAULT '',       -- 核心痛点（JSON数组）
    goals TEXT DEFAULT '',             -- 目标（JSON数组）
    
    -- 生命周期
    lifecycle_stage TEXT DEFAULT 'visitor',  -- visitor→lead→trial→active→paying→churned→reactivated
    role TEXT DEFAULT 'trial',               -- trial/free/premium/vip/partner
    source TEXT DEFAULT '',                  -- 获客来源
    source_detail TEXT DEFAULT '',           -- 来源详情（如具体文章/广告/推荐人）
    utm_source TEXT DEFAULT '',
    utm_medium TEXT DEFAULT '',
    utm_campaign TEXT DEFAULT '',
    
    -- 时间线
    first_visit_at TEXT,
    registered_at TEXT DEFAULT (datetime('now','localtime')),
    activated_at TEXT,                 -- 首次完成核心动作（如完成自评）
    converted_at TEXT,                 -- 付费时间
    last_active_at TEXT,
    churned_at TEXT,

    -- 风险信号
    risk_score INTEGER DEFAULT 0,      -- 流失风险分（0-100）
    health_score INTEGER DEFAULT 50,   -- 客户健康分（0-100）
    nps_score INTEGER,                 -- 净推荐值
    churn_reason TEXT DEFAULT '',
    
    -- 标签体系
    tags TEXT DEFAULT '',              -- JSON数组
    segments TEXT DEFAULT '',          -- 自动分群
    
    -- 状态
    email_verified INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    is_test INTEGER DEFAULT 0,        -- 测试账户标记
    
    created_at TEXT DEFAULT (datetime('now','localtime')),
    updated_at TEXT DEFAULT (datetime('now','localtime'))
);


-- ═══════════════════════════════════════
-- 2. 行为事件表（核心数据资产）
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    session_id TEXT,                   -- 会话ID（匿名用户追踪）
    
    -- 事件分类
    category TEXT NOT NULL,            -- page_view | product_use | decision | conversion | social | email
    action TEXT NOT NULL,              -- 具体动作：e.g. 'assessment_start', 'radar_view', 'register', 'login'
    label TEXT DEFAULT '',             -- 附加标签
    
    -- 关联实体
    product_id TEXT DEFAULT '',        -- 关联产品
    page_url TEXT DEFAULT '',          -- 页面URL
    referrer TEXT DEFAULT '',          -- 来源页面
    
    -- 事件数据（JSON，灵活存储）
    properties TEXT DEFAULT '{}',      -- {timeSpent: 120, stepsCompleted: 3, score: 85, ...}
    
    -- 设备环境
    ip_address TEXT DEFAULT '',
    user_agent TEXT DEFAULT '',
    device_type TEXT DEFAULT '',       -- desktop | mobile | tablet
    browser TEXT DEFAULT '',
    os TEXT DEFAULT '',
    
    -- 地理位置
    country TEXT DEFAULT '',
    region TEXT DEFAULT '',            -- 省
    city TEXT DEFAULT '',              -- 市
    
    -- 时效
    client_time TEXT DEFAULT '',       -- 客户端时间
    created_at TEXT DEFAULT (datetime('now','localtime')),
    
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);

-- 事件索引
CREATE INDEX IF NOT EXISTS idx_events_customer ON events(customer_id);
CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
CREATE INDEX IF NOT EXISTS idx_events_action ON events(action);
CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at);
CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_product ON events(product_id);


-- ═══════════════════════════════════════
-- 3. 会话表（用户访问链路追踪）
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS sessions_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    session_id TEXT UNIQUE NOT NULL,
    
    -- 会话信息
    start_at TEXT NOT NULL,
    end_at TEXT,
    duration_seconds INTEGER DEFAULT 0,
    page_views INTEGER DEFAULT 0,
    events_count INTEGER DEFAULT 0,
    
    -- 来源
    entry_page TEXT DEFAULT '',
    exit_page TEXT DEFAULT '',
    referrer TEXT DEFAULT '',
    utm_source TEXT DEFAULT '',
    utm_medium TEXT DEFAULT '',
    utm_campaign TEXT DEFAULT '',
    
    -- 转化标记
    converted INTEGER DEFAULT 0,       -- 本会话是否产生转化
    conversion_type TEXT DEFAULT '',   -- register | contact | purchase
    
    -- 设备
    device_type TEXT DEFAULT '',
    browser TEXT DEFAULT '',
    ip_address TEXT DEFAULT '',
    
    created_at TEXT DEFAULT (datetime('now','localtime')),
    
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_customer ON sessions_tracking(customer_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions_tracking(created_at);


-- ═══════════════════════════════════════
-- 4. 产品交付表
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    product_family TEXT DEFAULT '',    -- 镜/衡/契/觉/其他
    
    -- 交付状态
    status TEXT DEFAULT 'active',      -- active | expired | revoked | paused
    granted_at TEXT DEFAULT (datetime('now','localtime')),
    activated_at TEXT,
    expires_at TEXT,
    last_used_at TEXT,
    usage_count INTEGER DEFAULT 0,
    
    -- 授权信息
    granted_by TEXT DEFAULT '',        -- 授予人
    grant_reason TEXT DEFAULT '',      -- 授予原因
    
    -- 交付文件
    download_token TEXT DEFAULT '',    -- 一次性下载凭证
    download_count INTEGER DEFAULT 0,
    download_limit INTEGER DEFAULT 10,
    
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_deliveries_customer ON deliveries(customer_id);
CREATE INDEX IF NOT EXISTS idx_deliveries_product ON deliveries(product_id);


-- ═══════════════════════════════════════
-- 5. 客户留言/咨询表
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS inquiries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    
    name TEXT NOT NULL,
    email TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    company TEXT DEFAULT '',
    
    message TEXT NOT NULL,
    category TEXT DEFAULT 'general',   -- general | product | partnership | complaint
    
    -- 处理跟踪
    status TEXT DEFAULT 'new',         -- new | assigned | in_progress | resolved | closed
    priority TEXT DEFAULT 'normal',    -- low | normal | high | urgent
    assigned_to TEXT DEFAULT '',
    notes TEXT DEFAULT '',             -- 内部备注
    
    replied_at TEXT,
    replied_by TEXT,
    resolved_at TEXT,
    
    -- 满意度
    satisfaction_score INTEGER,        -- 1-5
    
    created_at TEXT DEFAULT (datetime('now','localtime')),
    
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_inquiries_customer ON inquiries(customer_id);
CREATE INDEX IF NOT EXISTS idx_inquiries_status ON inquiries(status);


-- ═══════════════════════════════════════
-- 6. 转介绍追踪表
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id INTEGER NOT NULL,      -- 推荐人
    referred_id INTEGER,               -- 被推荐人（注册后）
    
    -- 推荐信息
    referral_code TEXT UNIQUE NOT NULL,-- 唯一推荐码
    referred_email TEXT DEFAULT '',    -- 被推荐人邮箱
    referred_name TEXT DEFAULT '',
    
    -- 状态追踪
    status TEXT DEFAULT 'sent',        -- sent | clicked | registered | activated | converted
    reward_status TEXT DEFAULT 'pending', -- pending | granted | claimed
    
    -- 时间线
    sent_at TEXT DEFAULT (datetime('now','localtime')),
    clicked_at TEXT,
    registered_at TEXT,
    converted_at TEXT,
    
    -- 渠道
    channel TEXT DEFAULT 'link',       -- link | email | wechat | manual
    
    FOREIGN KEY (referrer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (referred_id) REFERENCES customers(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referrals_code ON referrals(referral_code);


-- ═══════════════════════════════════════
-- 7. 邮件日志表
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS email_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    
    to_email TEXT NOT NULL,
    to_name TEXT DEFAULT '',
    subject TEXT NOT NULL,
    template_id TEXT DEFAULT '',       -- 邮件模板标识
    category TEXT DEFAULT '',          -- transactional | marketing | notification | onboarding
    
    -- 状态
    status TEXT DEFAULT 'sent',        -- queued | sent | delivered | opened | clicked | bounced | complained
    provider_message_id TEXT DEFAULT '', -- 飞书邮件API返回的ID
    
    -- 追踪
    sent_at TEXT DEFAULT (datetime('now','localtime')),
    delivered_at TEXT,
    opened_at TEXT,
    clicked_at TEXT,
    bounced_at TEXT,
    
    -- 数据
    metadata TEXT DEFAULT '{}',        -- JSON，模板变量数据
    
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_email_logs_customer ON email_logs(customer_id);
CREATE INDEX IF NOT EXISTS idx_email_logs_category ON email_logs(category);


-- ═══════════════════════════════════════
-- 8. API 调用日志（安全审计）
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS api_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    
    ip_address TEXT DEFAULT '',
    user_agent TEXT DEFAULT '',
    request_body TEXT DEFAULT '',      -- 脱敏后的请求体
    
    created_at TEXT DEFAULT (datetime('now','localtime')),
    
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_logs_created ON api_logs(created_at);


-- ═══════════════════════════════════════
-- 9. 系统配置表
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT DEFAULT '',
    updated_at TEXT DEFAULT (datetime('now','localtime'))
);


-- ═══════════════════════════════════════
-- 10. 知识资产（脱敏版·可外发）
-- ═══════════════════════════════════════
-- 客户决策案例（脱敏）
CREATE TABLE IF NOT EXISTS decision_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    
    title TEXT NOT NULL,
    scenario TEXT DEFAULT '',          -- 场景描述
    challenge TEXT DEFAULT '',         -- 面临的挑战
    approach TEXT DEFAULT '',          -- 采用的方案
    outcome TEXT DEFAULT '',           -- 结果
    lessons TEXT DEFAULT '',           -- 经验教训
    
    -- 关联
    product_ids TEXT DEFAULT '',       -- 使用的产品IDs
    decision_type TEXT DEFAULT '',     -- 决策类型（合伙人选择/股权分配/退出等）
    
    -- 数据脱敏
    is_public INTEGER DEFAULT 0,       -- 是否可对外展示
    anonymized INTEGER DEFAULT 0,     -- 是否已脱敏
    
    created_at TEXT DEFAULT (datetime('now','localtime')),
    
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);


-- ═══════════════════════════════════════
-- 11. 会话验证（JWT支持）
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    token_hash TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    ip_address TEXT DEFAULT '',
    device_info TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);


-- ═══════════════════════════════════════
-- 12. 验证码表
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS verification_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    code TEXT NOT NULL,
    purpose TEXT DEFAULT 'email_verify',
    used INTEGER DEFAULT 0,
    expires_at TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now','localtime'))
);
"""

# 预置数据：系统配置
SEED_CONFIG = [
    ("app_version", "2.0.0", "应用版本号"),
    ("email_sender", "hello@satisficing.io", "系统发件邮箱（待配置域名）"),
    ("referral_reward", '{"referrer":"延长1个月使用权","referred":"首月9折"}', "转介绍奖励配置"),
    ("product_categories", '["镜","衡","契","觉","其他"]', "产品五大族"),
    ("customer_segments", '["硬科技创始人","HRVP/CHO","投资人","创业服务机构"]', "客户分群"),
    ("lifecycle_stages", '["visitor","lead","trial","active","paying","churned"]', "客户生命周期阶段"),
]
