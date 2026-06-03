# 多Agent分身设计方案

## 设计原则（基于AIRES-004 agency-agents + AIRES-007 简单设计原则）

> **每增加一个Agent，就多一个故障点；每次交接，就是上下文死亡一次。**
> **一个Agent，一个任务，可衡量的输出。**

---

## 当前系统: 87个系统 → 专业化Agent分身

### 核心原则
- **专才 > 通才**: 每个Agent只精通一个领域
- **简单优先**: 避免复杂多Agent链
- **独立交付**: 每个Agent可直接输出结果

---

## Agent分身架构

### 第一层: 核心治理Agent（5个）

| Agent | 职责 | 对应现有系统 | 输出 |
|-------|------|--------------|------|
| **QualityGuard** | 质量门禁 | quality-gate-system, quality-assurance | 通过/不通过报告 |
| **TokenWatch** | Token监控 | token-budget-enforcer | 预警/节流建议 |
| **BlueSentinel** | 蓝军审计 | blue-army-interceptor | 审计报告 |
| **BackupKeeper** | 备份验证 | backup-verification | 健康评分 |
| **CronMaster** | 定时任务 | cron-automation | 任务状态报告 |

### 第二层: 业务专业Agent（5个）

| Agent | 职责 | 专长领域 | 输出 |
|-------|------|----------|------|
| **FinanceAnalyst** | 财务分析 | 财报解读、估值模型 | 财务健康报告 |
| **LegalAdvisor** | 法律咨询 | 合同审查、合规检查 | 风险提示 |
| **MarketStrategist** | 市场策略 | 竞品分析、市场定位 | 策略建议 |
| **PartnerMatcher** | 合伙人匹配 | 硬科技转化、合伙人评估 | 匹配报告 |
| **Researcher** | 深度研究 | 行业调研、技术趋势 | 研究报告 |

### 第三层: 辅助工具Agent（3个）

| Agent | 职责 | 对应Skill | 输出 |
|-------|------|-----------|------|
| **DocProcessor** | 文档处理 | summarize, md-to-pdf | 处理后的文档 |
| **DataMiner** | 数据挖掘 | tavily-search, brave-search | 数据报告 |
| **KnowledgeCurator** | 知识管理 | knowledge-ingestion | 入库确认 |

---

## Agent交互模式

### 模式A: 单Agent独立执行（推荐）
```
用户请求 → 路由判断 → 专业Agent执行 → 直接输出
```

### 模式B: 并行多Agent（需要时）
```
用户请求 → 分发到多个Agent → 各自执行 → 结果聚合 → 统一输出
```

### 避免模式: 串行链式Agent
```
❌ Agent A → Agent B → Agent C
   (信息损耗在每次交接)
```

---

## 实施路径

### Phase 1（本周）: 核心治理Agent
- [ ] QualityGuard: 复用现有quality-gate-system
- [ ] TokenWatch: 复用token-budget-enforcer
- [ ] BlueSentinel: 复用blue-army-interceptor

### Phase 2（下周）: 业务专业Agent
- [ ] PartnerMatcher: 基于PFI产品构建
- [ ] Researcher: 基于kimi-search构建

### Phase 3（下月）: 完整生态
- [ ] FinanceAnalyst: 对接QVeris数据API
- [ ] LegalAdvisor: 合同模板库+风险识别
- [ ] MarketStrategist: 竞品数据库

---

## 技术实现

每个Agent = SKILL.md + 专用Prompt + 工具集

```
skills/agents/
├── quality-guard/
│   ├── SKILL.md
│   ├── prompt.md
│   └── tools.json
├── partner-matcher/
│   ├── SKILL.md
│   ├── prompt.md
│   └── tools.json
└── ...
```

---

## 与现有系统的关系

| 现有系统 | 映射Agent | 迁移方式 |
|----------|-----------|----------|
| 11个5标准化系统 | 5个核心治理Agent | 直接复用 |
| 87个系统 | 13个专业Agent | 逐步整合 |
| 306个Skill | 工具集 | 按需调用 |

---

*设计完成: 2026-03-27*
*参考: AIRES-004 agency-agents, AIRES-007 简单设计原则*

## 知识内化记录
**内化时间**: 2026-03-31 | **状态**: ✅ 已内化
