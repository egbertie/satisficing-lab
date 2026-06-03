-- 核心数据库 Schema
-- 文件登记元数据表
CREATE TABLE file_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    source VARCHAR(50), -- 'feishu', 'wechat', 'upload', 'email'
    file_hash VARCHAR(64) UNIQUE, -- SHA-256校验
    file_size BIGINT,
    mime_type VARCHAR(100),
    content_summary TEXT, -- AI生成的摘要
    totem_category VARCHAR(20), -- '刘禹锡(土)', '司马贺(金)', '观自在(水)', '孔子(木)', '慧能(火)'
    ingestion_status VARCHAR(20), -- 'registered', 'parsing', 'digesting', 'verified', 'archived'
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB -- 扩展字段
);

-- 内化过程追踪表
CREATE TABLE internalization_process (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES file_registry(id),
    pass_1_reading TIME, -- 第一遍通读耗时
    pass_2_notes TIME, -- 第二遍笔记耗时
    pass_3_summary TIME, -- 第三遍总结耗时
    comprehension_score INT, -- 理解度评分0-100
    verification_score INT, -- 验证评分0-100
    status VARCHAR(20), -- 'processing', 'passed', 'failed', 'rework'
    reviewer VARCHAR(50), -- 审核人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 蓝军审计日志
CREATE TABLE blue_team_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50), -- 'file', 'skill', 'workflow'
    entity_id UUID,
    audit_type VARCHAR(50), -- 'compliance', 'quality', 'security'
    severity VARCHAR(20), -- 'info', 'warning', 'critical'
    finding TEXT,
    auditor VARCHAR(50) DEFAULT 'Skeptor-7',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3-2-1备份追踪
CREATE TABLE backup_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES file_registry(id),
    backup_type VARCHAR(20), -- 'local', 'nas', 'cloud'
    location VARCHAR(500),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 五维指标表
CREATE TABLE metrics_time (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type VARCHAR(50),
    duration_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE metrics_quality (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_time_success BOOLEAN,
    rework_count INT DEFAULT 0,
    verification_score INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE metrics_cost (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model VARCHAR(50),
    prompt_tokens INT,
    completion_tokens INT,
    total_cost_yuan FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE metrics_reuse (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID,
    asset_type VARCHAR(50),
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 物化视图：五维指标综合
CREATE MATERIALIZED VIEW mv_five_dimensions AS
WITH time_metrics AS (
    SELECT 
        DATE_TRUNC('day', created_at) as date,
        AVG(duration_seconds) as avg_task_duration
    FROM metrics_time
    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY DATE_TRUNC('day', created_at)
),
quality_metrics AS (
    SELECT 
        DATE_TRUNC('day', created_at) as date,
        AVG(CASE WHEN first_time_success THEN 1 ELSE 0 END) * 100 as first_time_success_rate
    FROM metrics_quality
    GROUP BY DATE_TRUNC('day', created_at)
),
cost_metrics AS (
    SELECT 
        DATE_TRUNC('day', timestamp) as date,
        SUM(total_cost_yuan) as daily_cost
    FROM metrics_cost
    GROUP BY DATE_TRUNC('day', timestamp)
)
SELECT t.date, t.avg_task_duration, q.first_time_success_rate, c.daily_cost
FROM time_metrics t
LEFT JOIN quality_metrics q ON t.date = q.date
LEFT JOIN cost_metrics c ON t.date = c.date
ORDER BY t.date DESC;
