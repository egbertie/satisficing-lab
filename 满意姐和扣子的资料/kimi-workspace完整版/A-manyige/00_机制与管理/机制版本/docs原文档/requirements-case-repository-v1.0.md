---
kia-version: 1.0
tier: T0
title: 案例库管理Skill - 外求需求文档
source: docs/requirements-case-repository-v1.0.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchD-docs-04]
---

> 生成时间: 2026-04-04 09:56+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# 案例库管理Skill - 外求需求文档

> **文档版本**: v1.1 (补充更新)  
> **创建时间**: 2026-04-03  
> **更新时间**: 2026-04-04  
> **需求方**: 满意解研究所 (Egbertie)  
> **用途**: 外包开发招标/技术合作伙伴沟通  
> **补充内容**: SECI知识转化模型、知识图谱增强、CLI命令设计

---

## 0. 理论深度解析 (新增)

### 0.1 SECI知识转化模型在案例库中的应用

根据野中郁次郎（Nonaka）和竹内弘高（Takeuchi）的SECI知识转化模型，知识创造是一个螺旋上升的过程：

| SECI阶段 | 知识形态转化 | 案例库功能支撑 |
|----------|--------------|----------------|
| **社会化(Socialization)**<br>隐性→隐性 | 资深合伙人教练与创始人深度访谈，传递"识人直觉" | 录音/笔记存档、访谈模板库、经验萃取工作坊记录 |
| **外显化(Externalization)**<br>隐性→显性 | 将"为什么选A不选B"的决策直觉，转化为结构化决策依据 | **核心功能**：案例创建与复盘模板通过结构化字段强制外显化关键决策逻辑 |
| **组合化(Combination)**<br>显性→显性 | 将多个案例的成功因素交叉分析，形成"硬科技合伙人匹配最佳实践指南" | 相似案例聚类、标签云分析、跨案例统计看板 |
| **内隐化(Internalization)**<br>显性→隐性 | 新顾问通过阅读复盘报告，形成"芯片行业需要什么样的合伙人"的直觉 | 复盘报告生成、沉浸式案例浏览、决策路径可视化 |

> **关键洞察**: 案例库不是简单的文档存储，而是外显化(Externalization)的核心基础设施。

### 0.2 知识图谱增强的案例表示理论

传统关键词检索无法捕捉案例间的深层语义关联。引入知识图谱嵌入技术：

- **实体**: 每个案例视为知识图谱中的实体
- **关系**: 案例间的关系（行业相似、阶段相同、合伙人类型一致）
- **模型**: TransH模型（优于基础TransE，能处理多对多关系）

**优势**: 能发现"表面不同但本质相似"的案例（如：AI芯片与GPU芯片在合伙人需求上的深层相似性）

---

## 1. 项目背景

### 1.1 为什么需要案例库
满意解研究所的核心价值是**合伙人匹配决策教练**服务。每个服务案例都是宝贵的知识资产：

- **复用价值**: 相似背景的创始人可以参考历史案例
- **算法训练**: 合伙人匹配引擎需要历史数据训练
- **信任建立**: 向新客户展示过往成功案例
- **复盘学习**: 从失败案例中提炼教训

### 1.2 当前痛点
- 案例散落在各个文档中，难以检索
- 没有统一的数据结构，无法分析
- 无法快速找到"相似案例"作为参考
- 缺乏复盘模板，经验难以沉淀

### 1.3 首年目标
**积累30个高质量案例库**，形成可检索、可分析、可复用的知识资产。

---

## 2. 核心诉求

### 2.1 一句话描述
开发一个**案例库管理系统**，能够结构化存储合伙人匹配案例，支持多维度检索、相似案例推荐、复盘模板生成。

### 2.2 输入输出定义

**输入 - 案例创建**:
```json
{
  "case_id": "自动生成",
  "case_name": "案例名称（如：深圳芯片项目A合伙人匹配）",
  "created_date": "2026-04-03",
  
  "founder_profile": {
    "industry": "硬科技细分领域",
    "stage": "初创期/成长期",
    "funding_status": "天使轮/A轮/政府补贴",
    "team_size": "当前团队规模",
    "core_tech": "核心技术描述",
    "main_challenge": "主要挑战"
  },
  
  "partner_requirements": {
    "role_type": "商业合伙人/技术合伙人/运营合伙人",
    "must_have": ["必备条件"],
    "nice_to_have": ["加分条件"],
    "deal_breakers": ["一票否决项"]
  },
  
  "matching_process": {
    "candidates_considered": 5,
    "candidates_interviewed": 3,
    "final_candidates": 2,
    "decision_method": "满意解/多轮面试/压力测试",
    "time_spent_days": 45
  },
  
  "selected_partner": {
    "background": "候选人背景",
    "key_strengths": ["核心优势"],
    "risk_factors": ["风险点"],
    "match_score": 85
  },
  
  "outcome": {
    "result": "成功合作/失败/待定",
    "success_metrics": {
      "funding_raised": "融资额",
      "valuation_change": "估值变化",
      "team_stability": "团队稳定性评分"
    },
    "key_success_factors": ["成功关键因素"],
    "lessons_learned": ["教训"],
    "if_redo": "如果重做，会改变什么"
  },
  
  "tags": ["标签1", "标签2"],
  "confidentiality": "公开/脱敏/内部",
  "created_by": "记录人"
}
```

**输出 - 案例检索**:
```json
{
  "query": "芯片行业 初创期 商业合伙人",
  "results": [
    {
      "case_id": "CASE-001",
      "case_name": "深圳芯片项目A合伙人匹配",
      "relevance_score": 0.92,
      "similarity_factors": {
        "industry": 1.0,
        "stage": 1.0,
        "partner_type": 1.0
      },
      "key_takeaway": "成功的关键在于候选人具备芯片行业渠道资源",
      "outcome": "成功合作，后续融资5000万"
    }
  ],
  "summary": "找到3个相似案例，成功率67%，关键成功因素是行业资源匹配"
}
```

**输出 - 复盘报告**:
```markdown
# 案例复盘报告：深圳芯片项目A合伙人匹配

## 基本情况
- 行业：AI芯片
- 阶段：天使轮后
- 匹配周期：45天
- 结果：✅ 成功合作

## 关键决策点
1. **放弃清华系候选人**：虽然背景光鲜，但缺乏芯片行业资源
2. **选择华为退休高管**：渠道资源直接对接目标客户
3. **股权设计**：采用分期兑现，降低早期风险

## 满意解分析
- 阈值设定：行业经验>7分，商业能力>8分
- 首个满足候选人即停止搜索
- 搜索成本：45天（行业平均60天）

## 可复用经验
- 硬科技领域，行业资源比通用商业能力更重要
- 分期股权是降低早期风险的有效手段

## 标签
#AI芯片 #天使轮 #商业合伙人 #成功案例 #渠道资源
```

---

## 3. 案例数据结构详细定义

### 3.1 核心字段（必填）

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| case_id | string | 唯一标识 | CASE-2026-001 |
| case_name | string | 案例名称 | 深圳芯片项目A合伙人匹配 |
| created_date | date | 创建日期 | 2026-04-03 |
| industry | enum | 硬科技细分领域 | AI芯片/生物医药/新能源/... |
| stage | enum | 项目阶段 | 初创期/成长期/扩张期 |
| partner_type | enum | 合伙人类型 | 商业/技术/运营/财务 |
| outcome | enum | 结果 | 成功/失败/待定/进行中 |

### 3.2 创始人画像（必填）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| founder_background | enum | 创始人背景：技术/商业/混合 |
| core_tech | text | 核心技术描述 |
| funding_status | enum | 融资阶段 |
| main_strength | text | 主要优势 |
| main_weakness | text | 主要短板 |

### 3.3 匹配过程（选填）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| candidates_count | int | 考虑候选人数量 |
| time_spent_days | int | 匹配周期（天） |
| decision_method | text | 决策方法描述 |
| key_criteria | array | 关键评估标准 |

### 3.4 结果与复盘（必填）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| result | enum | 结果：成功/失败/待定 |
| success_factors | array | 成功关键因素 |
| failure_reasons | array | 失败原因（如适用） |
| lessons_learned | array | 教训 |
| if_redo | text | 如果重做会改变什么 |

### 3.5 标签体系（多选）

**行业标签**:
- AI芯片、GPU芯片、传感器、生物医药、新能源、新材料、机器人、航空航天

**阶段标签**:
- 天使轮、Pre-A、A轮、B轮、政府补贴、 Bootstrapped

**合伙人类型标签**:
- 商业合伙人、技术合伙人、运营合伙人、财务合伙人、战略合伙人

**结果标签**:
- 成功案例、失败案例、边界案例、进行中

**特征标签**:
- 渠道资源、融资能力、团队管理、行业经验、学习能力、价值观冲突

---

## 4. 功能需求

### 4.1 案例CRUD
- **创建**: 支持表单填写和JSON导入
- **读取**: 支持列表查看和详情页
- **更新**: 支持编辑和版本控制
- **删除**: 软删除，保留审计日志

### 4.2 智能检索
- **关键词检索**: 全文搜索案例名称、描述
- **标签筛选**: 多标签组合筛选
- **相似案例**: 基于创始人画像推荐相似案例
- **模糊匹配**: 支持"芯片行业早期项目"这类自然语言查询

### 4.3 相似度算法
基于以下维度计算案例相似度：

```python
similarity_score = (
    industry_match * 0.3 +      # 行业匹配度 30%
    stage_match * 0.2 +         # 阶段匹配度 20%
    partner_type_match * 0.2 +  # 合伙人类型 20%
    founder_gap_match * 0.15 +  # 创始人能力缺口 15%
    outcome_match * 0.15        # 结果参考 15%
)
```

### 4.4 复盘模板生成
- **自动复盘**: 根据案例数据自动生成复盘报告
- **模板库**: 提供成功/失败/边界案例的不同模板
- **导出功能**: 支持Markdown、PDF导出

### 4.5 数据看板
- **案例统计**: 总数、行业分布、成功率
- **趋势分析**: 月度新增案例、成功率趋势
- **标签云**: 高频标签可视化

---

## 5. 技术需求规格

### 5.1 技术栈建议
- **后端**: Python (FastAPI) + SQLAlchemy
- **数据库**: PostgreSQL (主存储) + Redis (缓存)
- **搜索**: Elasticsearch 或 PostgreSQL全文搜索
- **前端**: 可选（CLI版本优先，Web版本后续）

### 5.2 CLI优先设计
初期以命令行工具为主：

```bash
# 创建案例
$ case-repo create --template partner-matching

# 搜索案例
$ case-repo search --industry "AI芯片" --stage "初创期"

# 相似案例推荐
$ case-repo similar --case CASE-001 --top 5

# 生成复盘报告
$ case-repo report --case CASE-001 --format markdown

# 数据看板
$ case-repo dashboard
```

### 5.3 数据存储
- 本地JSON文件（初期，支持版本控制）
- 可选：云数据库（后期扩展）

---

## 6. 与合伙人匹配引擎的集成

### 6.1 数据流向
```
案例库(case-repository) 
    ↓ 提供训练数据
合伙人匹配引擎(partner-matching-engine)
    ↓ 输出匹配结果
新案例(case-repository)
```

### 6.2 API接口
案例库需要提供给匹配引擎的接口：

```python
# 获取相似案例
def get_similar_cases(founder_profile: dict, top_k: int = 5) -> list:
    """
    根据创始人画像返回相似案例
    """
    pass

# 获取行业基准
def get_industry_benchmark(industry: str) -> dict:
    """
    获取某行业的合伙人匹配基准数据
    """
    pass

# 记录匹配结果
def record_matching_result(case_data: dict) -> str:
    """
    将新的匹配结果记录为案例
    """
    pass
```

---

## 7. 验收标准

### 7.1 功能验收
- [ ] 能创建、读取、更新、删除案例
- [ ] 能通过标签筛选案例
- [ ] 能推荐相似案例
- [ ] 能生成复盘报告

### 7.2 数据验收
- [ ] 能存储30个案例无性能问题
- [ ] 搜索响应时间 < 1秒
- [ ] 相似度计算准确率 > 80%

### 7.3 质量验收
- [ ] 代码测试覆盖率 > 80%
- [ ] 提供CLI使用文档
- [ ] 提供数据结构说明

---

## 8. 合作模式

### 8.1 期望交付物
1. 可运行的案例库CLI工具
2. 源码 + 测试
3. 使用文档
4. 示例数据（10个案例）

### 8.2 时间节点
- 需求确认：3天
- 开发周期：3-4周
- 测试验收：1周
- 总计：5-6周

---

## 9. 案例数据样本

### 样本案例1：成功案例
```json
{
  "case_id": "CASE-001",
  "case_name": "深圳AI芯片项目合伙人匹配",
  "industry": "AI芯片",
  "stage": "天使轮",
  "founder_profile": {
    "background": "技术",
    "core_tech": "存算一体架构",
    "main_strength": "技术领先",
    "main_weakness": "商业渠道"
  },
  "partner_type": "商业合伙人",
  "outcome": "成功",
  "success_factors": [
    "候选人具备华为渠道资源",
    "技术互补性好",
    "价值观一致"
  ],
  "tags": ["AI芯片", "天使轮", "商业合伙人", "渠道资源"]
}
```

---

## 10. CLI命令详细设计 (新增)

### 10.1 命令体系

```bash
# 案例管理
case-repo create              # 创建新案例
case-repo list                # 列出所有案例
case-repo get <case-id>       # 查看案例详情
case-repo update <case-id>    # 更新案例
case-repo delete <case-id>    # 删除案例

# 智能检索
case-repo search <keyword>    # 关键词搜索
case-repo similar <case-id>   # 查找相似案例
case-repo filter --industry AI芯片 --stage 天使轮  # 多维度筛选

# 分析与报告
case-repo analyze --industry <industry>  # 行业分析
case-repo report <case-id>    # 生成复盘报告
case-repo dashboard           # 数据看板

# 知识图谱操作 (新增)
case-repo graph build         # 构建知识图谱
case-repo graph query "AI芯片合伙人需求"  # 图谱查询
case-repo similarity-matrix   # 生成案例相似度矩阵
```

### 10.2 SECI流程支持命令

```bash
# 社会化阶段 - 访谈记录
case-repo interview start <founder-name>    # 开始访谈
case-repo interview record --audio <file>   # 录音存档
case-repo interview notes <text>            # 记录笔记

# 外显化阶段 - 结构化录入
case-repo externalize <case-id>             # 外显化处理
                              # 自动提取关键决策逻辑
                              # 强制填写结构化字段

# 组合化阶段 - 知识整合
case-repo combine --cases CASE-001,CASE-002 # 交叉分析多个案例
case-repo pattern-extract                   # 提取共性模式

# 内隐化阶段 - 学习辅助
case-repo learn <case-id>                   # 沉浸式案例学习
case-repo quiz <case-id>                    # 生成学习测验
```

---

## 11. 联系方式

**需求方**: Egbertie (满意解研究所创始人)  
**技术对接**: 满意姐 (AI助手，OpenClaw环境)  
**审核方**: 蓝军 (独立审计AI)

---

*文档版本: v1.1 (已补充SECI模型、知识图谱、CLI详细设计)*
