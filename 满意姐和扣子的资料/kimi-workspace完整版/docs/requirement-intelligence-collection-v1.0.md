---
kia-version: 1.0
tier: T0
title: 项目情报采集系统需求文档
source: docs/requirement-intelligence-collection-v1.0.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchD-docs-04]
---

> 生成时间: 2026-04-03 19:41+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# 项目情报采集系统需求文档

> 需求版本: v1.0  
> 提出方: 满意解研究所 / Egbertie  
> 目标: 硬科技领域项目情报自动采集、AI摘要、飞书推送  

---

## 系统定位

**不是**: 全网爬虫/通用搜索引擎  
**是**: 垂直领域情报助手，专注硬科技创业项目的早期发现与跟踪

**核心价值**:
- 减少信息噪音 (只关注硬科技+早期阶段)
- AI辅助摘要 (快速了解项目要点)
- 智能告警 (关键词/赛道/阶段匹配)
- 飞书集成 (研究团队协作)

---

## 采集数据源

### 优先级P0 (必须)

| 数据源 | 数据类型 | 采集方式 | 更新频率 |
|--------|----------|----------|----------|
| IT桔子 | 融资事件、公司信息 | API/RSS | 每日 |
| 36氪 | 行业报道、融资新闻 | RSS/爬虫 | 每日 |
| 动脉网 | 医疗科技项目 | RSS | 每日 |

### 优先级P1 (可选)

| 数据源 | 数据类型 | 采集方式 |
|--------|----------|----------|
| 企名片 | 公司工商、融资 | API |
| Crunchbase | 国际项目 | API |
| 科创板/创业板公告 | 上市公司动态 | RSS |

---

## 数据模型

### 项目情报 (ProjectIntelligence)

```python
@dataclass
class ProjectIntelligence:
    id: str                      # UUID
    source: str                  # 数据来源 (itjuzi/36kr/etc)
    source_url: str             # 原始链接
    source_id: str              # 源站ID
    
    # 基础信息
    company_name: str           # 公司名称
    company_full_name: str      # 公司全称
    industry: str               # 行业 (硬科技子领域)
    sub_industry: str           # 细分领域
    
    # 融资信息
    funding_stage: str          # 融资阶段 (天使/A/B/C/IPO)
    funding_amount: str         # 融资金额 (如 "数千万人民币")
    funding_date: date          # 融资日期
    investors: List[str]        # 投资方列表
    
    # 团队信息
    founders: List[FounderInfo] # 创始人信息
    team_size: int              # 团队规模
    
    # 项目描述
    description: str            # 原始描述
    ai_summary: str             # AI生成的摘要
    key_tags: List[str]         # 关键词标签
    
    # 采集元数据
    collected_at: datetime      # 采集时间
    processed_at: datetime      # 处理时间
    pushed_to_feishu: bool      # 是否已推送
    
    # 匹配度评分 (针对用户需求)
    relevance_score: float      # 相关度评分 0-100
    match_reason: str           # 匹配原因

@dataclass
class FounderInfo:
    name: str
    title: str                  # 职位
    background: str             # 背景简述
    education: str              # 教育背景
    previous_experience: str    # 过往经历
```

---

## 采集策略

### 1. 筛选条件

**硬科技领域定义**:
```python
HARD_TECH_KEYWORDS = [
    "AI芯片", "GPU", "传感器", "生物医药", "基因",
    "新能源", "新材料", "机器人", "航空航天", "量子",
    "半导体", "集成电路", "自动驾驶", "脑机接口",
    "合成生物", "储能", "氢能", "光伏"
]
```

**融资阶段筛选**:
```python
TARGET_STAGES = ["天使轮", "pre-A", "A轮", "A+轮", "B轮"]
# 排除: C轮以后、IPO、并购
```

**地域筛选 (优先级)**:
```python
PRIORITY_REGIONS = [
    "深圳", "北京", "上海", "杭州", "苏州",
    "广州", "成都", "合肥", "西安"
]
```

### 2. 采集调度

```python
class CollectionScheduler:
    """采集调度器"""
    
    SCHEDULE = {
        "itjuzi": {"frequency": "daily", "time": "09:00"},
        "36kr": {"frequency": "daily", "time": "10:00"},
        "动脉网": {"frequency": "daily", "time": "11:00"}
    }
    
    def run_collection(self):
        # 1. 采集原始数据
        raw_data = self.collect_from_sources()
        
        # 2. 过滤硬科技项目
        hard_tech_projects = self.filter_hard_tech(raw_data)
        
        # 3. 去重
        unique_projects = self.deduplicate(hard_tech_projects)
        
        # 4. AI摘要
        for project in unique_projects:
            project.ai_summary = self.generate_summary(project)
            project.key_tags = self.extract_tags(project)
        
        # 5. 存储
        self.store_projects(unique_projects)
        
        # 6. 推送告警
        self.push_alerts(unique_projects)
```

---

## AI摘要生成

### Prompt模板

```python
SUMMARY_PROMPT = """
你是一位硬科技投资分析师。请根据以下项目信息，生成一份专业的项目摘要。

【项目信息】
公司名称: {company_name}
行业: {industry}
融资阶段: {funding_stage}
融资金额: {funding_amount}
投资方: {investors}
项目描述: {description}

【输出要求】
请用以下JSON格式输出:
{{
    "one_line_summary": "一句话概括项目核心价值 (30字以内)",
    "key_points": [
        "技术优势/创新点",
        "市场空间/应用场景",
        "团队背景亮点",
        "投资方背书"
    ],
    "investment_highlights": "投资亮点总结 (100字)",
    "risk_considerations": "潜在风险提示 (50字)",
    "tags": ["标签1", "标签2", "标签3"]
}}

注意: 只输出JSON，不要其他内容。
"""
```

### 摘要质量标准

- 一句话摘要: ≤30字，捕捉核心价值
- 关键点: 3-4条，覆盖技术/市场/团队/资金
- 投资亮点: 100字，突出吸引力
- 风险提示: 50字，平衡视角
- 标签: 3-5个，便于分类检索

---

## 飞书推送集成

### 推送触发条件

**自动推送**:
- 每日09:30 推送昨日新增项目汇总
- 实时推送高相关度项目 (relevance_score >= 80)

**关键词告警**:
```python
ALERT_KEYWORDS = [
    "合伙人", "融资", "硬科技", "AI芯片",
    # 用户可自定义关键词
]
```

**赛道告警**:
- 关注特定子领域 (如 "生物医药-A轮")

### 飞书消息格式

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {
        "tag": "plain_text",
        "content": "🔥 新项目情报 | {company_name} | {funding_stage}"
      },
      "template": "blue"
    },
    "elements": [
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "**一句话**: {one_line_summary}\n\n**融资**: {funding_amount} | {investors}\n**标签**: {tags}"
        }
      },
      {
        "tag": "action",
        "actions": [
          {
            "tag": "button",
            "text": {
              "tag": "plain_text",
              "content": "查看详情"
            },
            "url": "{source_url}"
          }
        ]
      }
    ]
  }
}
```

---

## 存储设计

### SQLite 表结构

```sql
-- 项目情报表
CREATE TABLE project_intelligence (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_url TEXT,
    source_id TEXT UNIQUE,
    company_name TEXT NOT NULL,
    company_full_name TEXT,
    industry TEXT,
    sub_industry TEXT,
    funding_stage TEXT,
    funding_amount TEXT,
    funding_date DATE,
    investors TEXT,  -- JSON array
    description TEXT,
    ai_summary TEXT,
    key_tags TEXT,   -- JSON array
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    pushed_to_feishu BOOLEAN DEFAULT FALSE,
    relevance_score REAL,
    match_reason TEXT
);

-- 采集日志表
CREATE TABLE collection_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    items_collected INTEGER,
    items_filtered INTEGER,
    items_stored INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT,  -- success/partial/failed
    error_message TEXT
);

-- 索引
CREATE INDEX idx_industry ON project_intelligence(industry);
CREATE INDEX idx_funding_stage ON project_intelligence(funding_stage);
CREATE INDEX idx_funding_date ON project_intelligence(funding_date);
CREATE INDEX idx_collected_at ON project_intelligence(collected_at);
```

---

## 配置管理

### 配置文件 (`config.yaml`)

```yaml
# 数据源配置
data_sources:
  itjuzi:
    enabled: true
    api_key: "${ITJUZI_API_KEY}"
    base_url: "https://www.itjuzi.com/api"
  
  36kr:
    enabled: true
    rss_url: "https://36kr.com/feed"
  
  动脉网:
    enabled: true
    rss_url: "https://www.vbdata.cn/feed"

# 采集策略
collection:
  hard_tech_keywords: [...]
  target_stages: ["天使轮", "pre-A", "A轮", "A+轮", "B轮"]
  priority_regions: ["深圳", "北京", "上海"]
  daily_limit: 50  # 每日最多采集项目数

# AI摘要
ai_summary:
  model: "kimi-k2p5"  # 使用Kimi模型
  max_length: 500
  
# 飞书推送
feishu:
  webhook_url: "${FEISHU_WEBHOOK_URL}"
  daily_digest_time: "09:30"
  alert_threshold: 80  # 相关度≥80时实时推送

# 关键词告警
alerts:
  keywords: ["合伙人", "融资"]
  industries: ["AI芯片", "生物医药"]
  stages: ["天使轮", "A轮"]
```

---

## CLI工具

```bash
# 手动触发采集
python3 scripts/collect.py --source itjuzi --date 2026-04-03

# 查看最近项目
python3 scripts/query.py --limit 10 --industry AI芯片

# 生成每日摘要
python3 scripts/digest.py --date yesterday --push-feishu

# 测试飞书推送
python3 scripts/test_feishu.py --message "测试消息"
```

---

## 交付物

| # | 交付物 | 路径 | 说明 |
|---|--------|------|------|
| 1 | 采集模块 | `scripts/collectors/` | 各数据源采集器 |
| 2 | AI摘要模块 | `scripts/ai_summarizer.py` | 摘要生成 |
| 3 | 飞书推送模块 | `scripts/feishu_pusher.py` | 消息推送 |
| 4 | 数据模型 | `scripts/models.py` | SQLAlchemy模型 |
| 5 | 调度器 | `scripts/scheduler.py` | 定时任务 |
| 6 | CLI工具 | `scripts/main.py` | 命令行入口 |
| 7 | 配置文件 | `config.yaml.example` | 配置模板 |
| 8 | 测试用例 | `tests/` | 单元+集成测试 |
| 9 | 部署文档 | `README.md` | 使用指南 |

---

## 验收标准

1. **采集**: 至少3个数据源正常运行
2. **筛选**: 硬科技项目识别准确率 >= 90%
3. **摘要**: AI摘要质量人工评估 >= 4/5分
4. **推送**: 飞书消息正常接收，格式美观
5. **稳定**: 连续运行7天无故障

---

## 风险与限制

1. **数据源稳定性**: RSS/API可能变更，需监控
2. **反爬限制**: 需遵守robots.txt，控制频率
3. **AI成本**: 摘要生成消耗Token，需预算控制
4. **数据时效**: 融资信息有延迟，非实时

---

**期望交付时间**: 收到需求后 10-14 个工作日  
**紧急程度**: P1 (重要但不阻塞主线)
