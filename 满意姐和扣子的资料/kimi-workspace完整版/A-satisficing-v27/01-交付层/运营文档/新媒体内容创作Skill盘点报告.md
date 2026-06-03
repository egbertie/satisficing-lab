---
kia-version: 1.0
tier: T0
title: 🎯 满意解研究所新媒体内容创作Skill盘点报告
source: A-satisficing-v27/01-交付层/运营文档/新媒体内容创作Skill盘点报告.md
ingested: 2026-04-16
tags: [auto-kia, v27, batch-2026-04-16]
---

---
title: 满意解研究所新媒体内容创作Skill盘点报告
date: 2026-04-02
author: 满意姐
---

# 🎯 满意解研究所新媒体内容创作Skill盘点报告

> **盘点原则**: 宝刀入库，不用生锈。梳理现有Skill，建立调用体系，提升内容生产效率。

---

## 一、核心Skill总览

| Skill名称 | 核心功能 | 适用平台 | 状态 | 优先级 |
|-----------|----------|----------|------|--------|
| **copywriting-zh-pro** | 中文文案大师 | 全平台 | ✅ 可用 | P0 |
| **marketing-content-generator** | 统一营销内容套件 | 全平台 | ✅ 可用 | P0 |
| **channel-script-generator** | 渠道话术生成器 | 私域/商业 | ✅ 可用 | P1 |
| **content-distribution-engine** | 内容分发引擎 | 公域多平台 | ✅ 可用 | P1 |
| **auto-redbook-skills** | 小红书自动内容 | 小红书 | ✅ 可用 | P1 |
| **multi-format-output-evolution** | 多元输出生成 | 全格式 | ✅ 可用 | P2 |
| **ai-social-media-content** | AI社交媒体内容 | 视频/图片 | ✅ 可用 | P2 |

---

## 二、Skill详细解析

### 2.1 copywriting-zh-pro（中文文案大师）

**定位**: 最全面的中文文案创作Skill

**核心能力**:
- **多平台适配**: 小红书、公众号、朋友圈、抖音、电商详情页
- **文案框架**: AIDA、PAS、FAB、BAB、4P等8种框架
- **标题生成**: 7种黄金标题公式
- **CTA优化**: 高转化行动号召文案
- **情感触发**: 恐惧、紧迫、便捷、身份、安全等8种情绪

**五大专用模式**:

| 模式 | 用途 | 输出 |
|------|------|------|
| **Mode A** | 品牌文案 | Slogan×10、Key Message×3、Hero Copy×3 |
| **Mode B** | 电商转化 | 主标题×5、卖点×5-8、详情页结构、FAQ |
| **Mode C** | 社媒传播 | 小红书/抖音/朋友圈/公众号定制化内容 |
| **Mode D** | 老板交付 | 可直接提交的方案（推荐版/稳妥版/测试版） |
| **Mode E** | 跨境营销 | 中英双语、Amazon/Shopify/独立站适配 |

**平台语调默认设置**:
- 小红书: personal, experiential, useful, lightly emotional
- 朋友圈: concise, social, trust-based, less salesy
- 公众号: structured, informative, readable
- 抖音: immediate hook, spoken rhythm, short beats
- 电商详情页: benefit-forward, objection-aware, skimmable

**使用建议**:
```
# 生成小红书种草文案
copywriting-zh-pro --mode C --platform xiaohongshu --topic "合伙人选择" --style 种草

# 生成公众号深度文章
copywriting-zh-pro --mode C --platform wechat --topic "张雪机车案例分析" --length long

# 生成品牌Slogan
copywriting-zh-pro --mode A --type slogan --theme "满意解合伙人决策"
```

---

### 2.2 marketing-content-generator（统一营销内容套件）

**定位**: 替代adwords+copywriting+copywriting-zh-pro的整合方案

**核心模块**:

| 模块 | 命令 | 功能 |
|------|------|------|
| 广告文案 | `mcg ad` | Google/Facebook/TikTok/百度广告 |
| 落地页 | `mcg landing` | Landing Page/销售页完整文案 |
| 社媒内容 | `mcg social` | 小红书/公众号/抖音/朋友圈 |
| 电商文案 | `mcg ecommerce` | Amazon/Shopify/淘宝/京东/拼多多 |
| 邮件营销 | `mcg email` | 邮件序列/营销邮件/自动化邮件 |
| A/B测试 | `mcg abtest` | 多版本文案生成与测试建议 |

**社媒内容特化命令**:
```bash
# 小红书种草文案
mcg social xiaohongshu --topic "职场效率工具" --style "种草" --cta "收藏"

# 公众号深度文章
mcg social wechat --topic "AI趋势分析" --length long --tone professional

# 抖音脚本
mcg social douyin --hook "震惊体" --product "护肤产品" --duration 60

# 朋友圈软性文案
mcg social moments --content "产品上新" --tone soft
```

**小红书专用输出结构**:
- 标题×10（带数字、痛点、方法、测评、盘点等角度）
- 开场钩子×5
- 文章结构
- CTA/评论引导×5

**与copywriting-zh-pro的协同**:
- `marketing-content-generator`: 批量生成、快速产出
- `copywriting-zh-pro`: 精细打磨、风格定制
- **建议工作流**: MCG快速生成 → Copywriting-zh-pro精细优化

---

### 2.3 channel-script-generator（渠道话术生成器）

**定位**: 满意解研究所专属，6大渠道定制化话术

**覆盖渠道**:
1. **律所** - 增值服务、客户粘性、风险控制
2. **猎头** - 优质客户、返佣、效率
3. **会所** - 转介价值、专业背书、合规
4. **孵化器** - 服务增值、满意度、入驻体验
5. **家办** - 风险控制、长期价值、回报
6. **科学家** - 信任、专业性、方法论

**话术结构**（每套包含）:
- 开场白（破冰、建立连接）
- 痛点共鸣（挖掘需求）
- 价值展示（解决方案）
- 案例背书（信任建立）
- 合作邀约（下一步行动）

**三种场景版本**:
- 初次接触（电话/微信）
- 深度交流（面谈）
- 合作邀约（正式提案）

**万能模板**:
- 30秒电梯演讲
- 3分钟咖啡聊天版
- 10分钟深度交流版

---

### 2.4 content-distribution-engine（内容分发引擎）

**定位**: 一源多用，将百科全书内容自动重组为不同平台版本

**输出矩阵**:

| 受众 | 文件 | 特点 | 长度 |
|------|------|------|------|
| 商业伙伴 | business-partner.md | 专业、数据、ROI导向 | 2000-3000字 |
| 渠道伙伴 | channel-partner.md | 赋能、返佣、合作模式 | 1500-2500字 |
| 客户 | client.md | 痛点、方案、信任背书 | 2000-3000字 |
| 公众号 | wechat-official.md | 深度、故事、互动引导 | 2000-3000字 |
| 小红书 | xiaohongshu.md | 视觉、金句、种草导向 | 500-800字 |

**内容重组规则示例**:

**公众号版结构**:
1. 钩子标题（痛点/好奇/利益）
2. 故事开场（个人经历引入）
3. 问题放大（共鸣构建）
4. 解决方案（方法论简述）
5. 互动引导（评论/转发/关注）

**小红书版结构**:
1. 封面标题（大字报风格）
2. 痛点金句（3-5个）
3. 解决方案（图示化）
4. 工具推荐（TRL-PFI卡片）
5. CTA（私信/收藏/关注）

---

### 2.5 auto-redbook-skills（小红书自动内容）

**定位**: 小红书专用内容生成Skill

**文件清单**:
- `SKILL.md` - 主Skill文件（adwords基础）
- `tips.md` - 文案技巧指南
- `example.md` - 示例内容
- `content_auto_fit.md` - 内容自动适配

**文案核心法则**:
- AIDA: Attention → Interest → Desire → Action
- PAS: Problem → Agitate → Solution
- BAB: Before → After → Bridge
- 4U: Urgent + Unique + Ultra-specific + Useful

**标题黄金法则**:
- 数字开头转化率更高（奇数优于偶数）
- 长度：中文10-20字
- 包含好处或解决的痛点
- 创造好奇心但不做标题党

**正文写作技巧**:
- 第一句话的唯一目的：让人读第二句
- 短句>长句，短段>长段
- 多用"你"，少用"我们"
- 用具体数字代替模糊描述
- 一个段落=一个观点

---

### 2.6 multi-format-output-evolution（多元输出生成）

**定位**: 输出格式技术进化引擎，持续研究新输出技术

**当前能力** (V1.0):
| 输出类型 | 技术方案 | 状态 |
|:---|:---|:---:|
| Markdown文档 | 代码块输出 | ✅ 成熟 |
| 表格预览+CSV | Markdown表格 + CSV代码 | ✅ 成熟 |
| Mermaid图表 | Mermaid代码 | ✅ 可用 |

**在研能力**:
| 输出类型 | 技术方案 | 预计上线 |
|:---|:---|:---:|
| PNG图片直接生成 | 研究中 | 2周内 |
| Excel文件生成 | 研究中 | 1个月内 |
| 数据可视化图表 | ECharts/Plotly | 1个月内 |
| 短视频生成 | Runway/Pika/剪映API | 2个月内 |
| H5互动页面 | 易企秀/MAKA/自主HTML | 3个月内 |
| 在线小游戏 | HTML5 Canvas/Phaser.js | 4个月内 |

**应用场景**:
- 将张雪案例分析转化为Mermaid决策流程图
- 将合伙人评估模型转化为可视化图表
- 将案例库转化为短视频脚本
- 将决策工具转化为H5互动页面

---

### 2.7 ai-social-media-content（AI社交媒体内容）

**定位**: 通过inference.sh CLI生成TikTok/Instagram/YouTube/Twitter内容

**核心能力**:
- 视频生成（Veo/Seedance/OmniHuman）
- 图片生成（FLUX）
- 语音合成（Kokoro TTS）
- 文案生成（Claude）

**平台格式支持**:
| 平台 | 比例 | 时长 | 分辨率 |
|------|------|------|--------|
| TikTok | 9:16 | 15-60s | 1080x1920 |
| Instagram Reels | 9:16 | 15-90s | 1080x1920 |
| YouTube Shorts | 9:16 | <60s | 1080x1920 |
| YouTube Thumbnail | 16:9 | - | 1280x720 |
| Twitter/X | 16:9/1:1 | <140s | 1920x1080 |

**内容工作流**:
1. 用Claude写脚本
2. 用Kokoro TTS生成语音
3. 用OmniHuman生成AI数字人视频
4. 批量生成多平台内容

**使用建议**:
- 适合生成视频/图片类社交媒体内容
- 需要inference.sh账号和API
- 可用于制作合伙人决策科普短视频

---

## 三、去AI化专项能力

### 3.1 去AI化检查清单（来自五路图腾体系V2.1）

```
【去AI化自检】发布前必须检查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ 没有"首先/其次/再次/最后"结构
□ 没有"综上所述/总而言之/值得注意的是"
□ 没有"根据XX显示/从数据可以看出"
□ 没有排比句超过3个
□ 有具体场景，不是抽象概念
□ 有主语，不是被动语态
□ 有情绪词（好/糟/惊讶/郁闷），不是纯中性
□ 允许口语化（行吧/算了/其实/说真的）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 3.2 AI味 vs 人味对比

| AI味 ❌ | 人味 ✅ |
|---------|---------|
| 首先，我们需要分析... | 先看这事儿... |
| 根据数据显示，用户满意度提升 | 用户反馈说，这东西用着舒服多了 |
| 综上所述，建议采用方案A | 说实话，方案A更靠谱 |
| 值得注意的是，该现象背后存在多重因素 | 这事儿有点复杂，几个方面搅在一起 |
| 从多个维度进行综合考量 | 全方位想了想 |

### 3.3 内化要求

**Token红线**: 去AI化不能靠增加废话实现，要在有限Token内做到"像人"

**执行层**: 创意Writer负责最终润色去AI化

**质检**: 蓝军审计每次检查"AI味浓度"

---

## 四、Skill调用体系建议

### 4.1 内容生产工作流

```
┌─────────────────────────────────────────────────────────────┐
│                    内容生产工作流                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: 内容规划                                           │
│  ├── 确定主题（如：张雪机车案例分析）                        │
│  └── 确定平台（公众号+小红书）                               │
│                                                             │
│  Step 2: 核心内容生成                                       │
│  ├── 使用 copywriting-zh-pro --mode D（老板交付模式）        │
│  │   输出：结构化内容框架 + 关键论点                         │
│  └── 或使用 content-distribution-engine                     │
│      输出：多平台适配版本                                    │
│                                                             │
│  Step 3: 平台定制化                                         │
│  ├── 公众号版                                               │
│  │   └── copywriting-zh-pro --platform wechat --length long  │
│  ├── 小红书版                                               │
│  │   ├── auto-redbook-skills 风格检查                        │
│  │   └── copywriting-zh-pro --platform xiaohongshu           │
│  └── 渠道话术版                                             │
│      └── channel-script-generator --channel 律所/猎头/孵化器  │
│                                                             │
│  Step 4: 去AI化处理                                         │
│  ├── 应用去AI化检查清单                                      │
│  ├── 人工润色：添加个人经历、情感表达                        │
│  └── 蓝军审计：检查"AI味浓度"                               │
│                                                             │
│  Step 5: 多媒体增强（可选）                                  │
│  ├── 图表：multi-format-output-evolution（Mermaid）          │
│  ├── 视频：ai-social-media-content                           │
│  └── 图片：ai-social-media-content（FLUX）                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 快速调用命令表

| 场景 | 推荐Skill | 命令/调用方式 |
|------|-----------|---------------|
| 快速生成多平台内容 | marketing-content-generator | `mcg social [platform] --topic [主题]` |
| 精细打磨文案 | copywriting-zh-pro | 指定Mode C/D + platform |
| 生成渠道话术 | channel-script-generator | 指定渠道类型 + 场景 |
| 一源多用分发 | content-distribution-engine | 输入百科全书内容 |
| 小红书专用 | auto-redbook-skills | 应用tips.md检查清单 |
| 去AI化处理 | 五路图腾V2.1 | 应用8项检查清单 |
| 生成图表 | multi-format-output-evolution | Mermaid代码 |
| 生成视频 | ai-social-media-content | `infsh app run` |

---

## 五、立即行动计划

### 5.1 Skill整理与激活

- [ ] 将关键Skill从OLD-ARCHIVE迁移到工作目录
- [ ] 测试每个Skill的可用性
- [ ] 建立Skill快速调用别名/脚本
- [ ] 制作Skill使用速查卡

### 5.2 内容生产测试

- [ ] 用marketing-content-generator生成1篇公众号+1篇小红书
- [ ] 用copywriting-zh-pro精细优化
- [ ] 应用去AI化检查清单
- [ ] 对比效果，建立最优工作流

### 5.3 知识库建设

- [ ] 将去AI化检查清单固化到AGENTS.md
- [ ] 建立平台语调参考库（公众号/小红书/抖音）
- [ ] 积累优秀文案模板
- [ ] 建立案例库（成功/失败文案对比）

---

## 六、Skill价值评估

| Skill | 使用频率 | 节省时间 | 质量提升 | 综合价值 |
|-------|:--------:|:--------:|:--------:|:--------:|
| copywriting-zh-pro | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| marketing-content-generator | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| content-distribution-engine | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| channel-script-generator | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| auto-redbook-skills | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| multi-format-output-evolution | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| ai-social-media-content | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 七、结语

**宝刀已盘点，只待出鞘时。**

这份报告梳理了满意解研究所现有的7大内容创作Skill，覆盖从文案生成、平台适配、去AI化到多媒体输出的完整工作流。

**核心建议**:
1. **主武器**: copywriting-zh-pro + marketing-content-generator
2. **副武器**: content-distribution-engine + channel-script-generator
3. **必杀技**: 去AI化检查清单（五路图腾V2.1）
4. **未来方向**: multi-format-output-evolution（图表/视频/H5）

下一步行动：整理并激活这些Skill，建立标准化的内容生产工作流，让每个内容输出都达到"专业级品质+人格化温度"。

---

*盘点完成 - 2026-04-02*
*满意解研究所 · 内容创作能力中心*
