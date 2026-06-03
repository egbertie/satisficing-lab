# 知识库条目: NEW-MEDIA-INTELLIGENCE-OFFICER-76

## 元数据
- **Entry_ID**: NEW-MEDIA-INTELLIGENCE-OFFICER-76
- **Topic**: 新媒体情报员_v1.0——普通Kimi Claw的Token高效信息收集方案
- **Source**: 新媒体情报员_v1.0.docx
- **File_Size**: 约9KB
- **Word_Count**: 约8,857字
- **Import_Date**: 2026-04-02
- **Expert_ID**: INFORMATION-ARCHITECT
- **Totem**: 03_观自在 + 05_六祖慧能
- **Status**: 完整入库/Token优化方案/18轮深度挖掘成果

---

## 核心内容摘要

**问题定义**: 普通Kimi Claw用户希望深挖微信、小红书、B站、抖音等新媒体平台+学术研究资源，但只有普通Claw版本  
**解决方案**: "信息雷达系统"（Information Radar System）——Skill组合 + 工具链 + 记忆架构三层设计  
**核心原则**: Token最优、一看就会、自动执行、持续迭代  
**技术基础**: 18轮深度架构挖掘

---

## 5次深度洞察产出

---

### 第1次深度洞察：结构解构——信息雷达系统的三层架构

**系统架构总览**:
```
┌─────────────────────────────────────────────────────────────────┐
│                  INFORMATION RADAR SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: Skill组合层（核心能力封装）                             │
│  ├─ 新媒体情报员（Social Media Scout）                           │
│  ├─ 学术快讯（Academic Briefing）                               │
│  └─ 财经科技晨读（TechFinance Digest）                          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: 工具链层（零Token外部扩展）                             │
│  ├─ RSS-Bridge（GitHub Actions免费版）                          │
│  ├─ 轻量级爬虫（Python+BeautifulSoup）                          │
│  └─ 知识库自动同步（Obsidian + Git）                            │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: 记忆架构层（三层信息金字塔）                            │
│  ├─ L1: 轻量级索引（MEMORY.md）                                  │
│  ├─ L2: 每日简报（Topic Files）                                  │
│  └─ L3: 原始数据（Raw Storage）                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### 第2次深度洞察：演化轨迹——从单次搜索到自动化情报系统

**演化路径**:

| 阶段 | 特征 | 代表方案 |
|------|------|----------|
| **手动搜索** | 人工逐平台查询 | 无Skill |
| **单Skill** | 单平台监控 | 新媒体情报员/学术快讯 |
| **Skill组合** | 多平台聚合 | 信息雷达系统 |
| **自动化** | KAIROS Daemon定时触发 | 晨间自动简报 |
| **智能代理** | 主动推送关键信息 | Month 2目标 |

**18轮深度挖掘轨迹**:
```
第1-6轮: 平台覆盖（微信/小红书/B站/抖音/arXiv/36氪）
第7-12轮: Token优化（摘要而非全文/站点内搜索/差异对比）
第13-18轮: 自动化架构（GitHub Actions/Obsidian集成/KAIROS）
```

---

### 第3次深度洞察：模式识别——信息收集的6大核心算法

**算法1: Token约束搜索**
| 约束 | 实现方式 | 节省效果 |
|------|----------|----------|
| 数量限制 | 只抓取前3条最相关 | -70% |
| 时间窗口 | 仅最近7天 | -50% |
| 内容类型 | 禁止视频/图片，仅文本元数据 | -80% |
| 字数截断 | 摘要≤150字 | -60% |

**算法2: 热度分级系统**
| 标记 | 热度 | 处理策略 |
|------|------|----------|
| 🔥🔥🔥 | 极高 | 立即推送到主对话 |
| 🔥🔥 | 高 | 存入每日简报 |
| 🔥 | 中 | 存档备查 |
| 无标记 | 低 | 仅索引记录 |

**算法3: 信息源矩阵（P0/P1分级）**
| 优先级 | 中文源 | 英文源 |
|--------|--------|--------|
| **P0必读** | 36氪/虎嗅/财新 | TechCrunch/The Information |
| **P1选读** | Product Hunt/GitHub Trending | Hacker News |

**算法4: 三层信息金字塔**
```
L1 轻量级索引 (常驻上下文)
  └─ 格式: 日期|平台|标题|标签|路径
  └─ Token: <150字符/行

L2 每日简报 (按需加载)
  └─ 格式: 3-5条精选+AI洞察
  └─ Token: ≤500字/篇

L3 原始数据 (冷存储)
  └─ 格式: JSON/Markdown
  └─ 检索: Bash grep（不进入上下文）
  └─ 生命周期: 30天后归档
```

**算法5: 差异对比更新**
- 不抓取全库，只抓取"今日新增"
- 与昨日简报对比，提取新增内容
- **节省95%重复Token**

**算法6: Code Mode大数据处理**
- 大数据用Python脚本处理
- 只传结果给Claw
- **减少65%上下文消耗**

---

### 第4次深度洞察：决策考古学——18轮深度挖掘的用户需求轨迹

**第1-6轮: 平台覆盖**
- **用户需求**: 覆盖微信、小红书、B站、抖音、Facebook等多平台
- **考古发现**: 用户要的不是"全"，而是"精"——Token有限，必须筛选

**第7-12轮: Token优化**
- **用户需求**: 普通Claw版本，Token受限
- **考古发现**: 引入"站点内搜索"（site:）而非通用搜索，大幅减少无效结果

**第13-18轮: 自动化架构**
- **用户需求**: 一看就会，自动执行
- **考古发现**: GitHub Actions免费额度 + KAIROS Daemon = 零成本自动化

**Egbertie的深层需求** (推断):
> 要在Token受限的普通Claw上，实现"7×24小时信息雷达"，且配置简单到"复制粘贴即可运行"

---

### 第5次深度洞察：内化沉淀——信息雷达系统的7大可执行资产

**资产1: 新媒体情报员Skill模板**
```yaml
# SKILL: 新媒体情报员_v1.0
约束条件:
  - 每次只抓取前3条最相关内容
  - 仅最近7天
  - 禁止视频/图片，仅文本元数据
工具调用:
  - site:mp.weixin.qq.com [关键词] 2026-04
  - site:xiaohongshu.com [关键词] 最近一周
  - site:bilibili.com [关键词] 专栏文章
输出格式:
  | 平台 | 热度 | 标题 | 关键洞察 | 原文链接 |
自动化触发: 每天早上9:00
```

**资产2: 学术快讯Skill模板**
```yaml
# SKILL: 学术快讯_v2.0
Token优化:
  - 使用arXiv RSS API而非网页抓取
  - 只读摘要，不下载PDF
  - LLM自动分类：相关/存疑/无关（减少80%无效输入）
高价值判断:
  - 引用量>100的更新
  - 作者来自Top10机构
  - 包含开源代码链接
输出: 每周趋势雷达图
```

**资产3: GitHub Actions自动化工作流**
```yaml
# .github/workflows/rss-aggregator.yml
on:
  schedule:
    - cron: '0 */6 * * *'  # 每6小时运行一次（免费额度内）
jobs:
  aggregate:
    steps:
      - Fetch WeChat Articles
      - Fetch Academic Papers
      - Commit to Repository
```

**资产4: Token效率配置参数**
| 策略 | 配置命令 | 效果 |
|------|----------|------|
| Prompt缓存 | /config set optimization.prompt_caching=true | -90% |
| 流式截断 | /config set optimization.max_chunk_size=500 | -70% |
| 摘要优先 | /config set optimization.prefer_summaries=true | -80% |
| Code模式 | /config set optimization.code_mode_threshold=1000 | -65% |

**资产5: 一键部署指令**
```bash
# 3分钟完成配置
/mkdir -p .kimi/skills/{social-media,academic,memory}
/write .kimi/skills/social-media/SCOUT.md [粘贴Skill 1]
/write .kimi/skills/academic/BRIEFING.md [粘贴Skill 2]
/config set kairos.enabled=true
/config set info.sources=wechat,xiaohongshu,arxiv,36kr
```

**资产6: 四周迭代路径**
| 周次 | 目标 | 里程碑 |
|------|------|--------|
| Week 1 | 基础搭建 | 每日自动简报，Token<5K/天 |
| Week 2 | 质量调优 | 用户反馈循环，自动调整策略 |
| Week 3 | 知识整合 | 跨平台关联，趋势预测 |
| Week 4 | 生态扩展 | A2A协议，UDS Inbox共享 |
| Month 2 | 智能代理 | 主动推送关键信息 |

**资产7: 首次运行指令模板**
```
"执行完整信息收集流程：
1. 运行/skill:social-media-scout抓取今日微信、小红书内容
2. 运行/skill:academic-briefing获取arXiv今日论文
3. 生成今日综合简报（Markdown，≤1000字）
4. 更新MEMORY.md索引
5. 将高价值内容（🔥≥2）推送到主对话"
```

---

## 与KIMI-CLAW-SKILL-ECOSYSTEM-HANDBOOK-75的关联

| 维度 | Skill生态系统手册 (Entry 75) | 新媒体情报员 (Entry 76) |
|------|---------------------------|------------------------|
| **定位** | Skill生态顶层架构设计 | 具体应用场景实现 |
| **层级** | 5层架构（约束/能力/知识/行为/协作） | 3层架构（Skill/工具链/记忆） |
| **协议** | MCP + A2A | GitHub Actions + RSS |
| **目标用户** | Skill开发者 | 普通Claw终端用户 |
| **Token策略** | Skill组合优化 | 约束搜索+差异对比 |
| **关系** | **基础设施** | **应用实例** |

**协同效应**: 
Entry 76是Entry 75中"Skill生态系统"的具体应用实例——
- 使用Entry 75的Skill模板结构
- 遵循Entry 75的Token优化原则
- 实现Entry 75提出的"KAIROS Daemon"自动化模式

---

## 索引
- **主题**: 信息收集, 新媒体监控, 学术研究, Token优化, 自动化, GitHub Actions
- **核心Skill**: 新媒体情报员/学术快讯/财经科技晨读
- **平台覆盖**: 微信/小红书/B站/抖音/Facebook/arXiv/36氪/虎嗅/财新
- **技术栈**: Python, BeautifulSoup, RSS, GitHub Actions, Obsidian
- **Token优化**: 数量限制/时间窗口/摘要优先/Code模式/差异对比
- **记忆架构**: 三层金字塔（索引/简报/原始数据）
- **自动化**: KAIROS Daemon, 定时触发, 主动推送
- **部署方式**: 一键部署, 3分钟配置, 零额外成本
- **迭代路径**: Week1基础→Week2调优→Week3整合→Week4扩展→Month2智能

---

*5次深度洞察完成 - 2026-04-02*
*Token消耗: ~25K（5次深度洞察+内容解析）*
*版本: 新媒体情报员V1.0*
*适用: 普通Kimi Claw用户*
