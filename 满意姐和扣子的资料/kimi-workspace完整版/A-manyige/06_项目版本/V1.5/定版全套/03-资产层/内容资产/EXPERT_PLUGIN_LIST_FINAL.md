---
kia-version: 1.0
tier: T1
title: 专家插件清单（最终版）
source: A-satisficing-v27/03-资产层/内容资产/EXPERT_PLUGIN_LIST_FINAL.md
ingested: 2026-04-16
tags: [auto-kia, v27, batch-2026-04-16]
---

# 专家插件清单（最终版）

> **实施时间**: 2026-03-31 09:20  
> **架构**: 6 Worker + 12专家插件（7真实专家+5图腾）  
> **状态**: ✅ 已实施

---

## 专家插件清单

### 真实专家插件（7个）

| 插件ID | 专家姓名 | 领域 | 对应Worker | 知识库路径 | 状态 |
|--------|----------|------|------------|------------|------|
| **EXPERT-LIU** | 黎红雷教授 | 儒商哲学/企业伦理 | Supervisor-Biz | `knowledge/experts/li_honglei/` | ✅ 已创建 |
| **EXPERT-LUO** | 罗汉教授 | 数学/软件工程 | Supervisor-Tech | `knowledge/experts/luo_han/` | ⏳ 待创建 |
| **EXPERT-XIE** | 谢宝剑研究员 | 深港战略/地理经济 | Worker-Analysis | `knowledge/experts/xie_baojian/` | ⏳ 待创建 |
| **EXPERT-XU** | XU先生 | AI/压力测试 | Worker-Execution | `knowledge/experts/xu/` | ⏳ 待创建 |
| **EXPERT-FANG** | 方翊沣博士 | 脑科学/BCI/神经反馈 | Worker-Creative | `knowledge/experts/fang_yifeng/` | ⏳ 待创建 |
| **EXPERT-CHEN** | 陈国祥博士 | 神经科/能量治疗 | Worker-Creative | `knowledge/experts/chen_guoxiang/` | ⏳ 待创建 |
| **EXPERT-LI** | 李泽湘教授 | 硬科技孵化/机器人 | Meta-Strategist | `knowledge/experts/li_zexiang/` | ⏳ 待创建 |

### 图腾插件（5个）

| 插件ID | 图腾 | 五行 | 对应Worker | 知识库路径 | 状态 |
|--------|------|------|------------|------------|------|
| **TOTEM-LIU** | 刘禹锡(LIU) | 土 | Worker-Execution | `knowledge/totems/liu_yuxi/` | ✅ 已创建 |
| **TOTEM-SIMON** | 司马贺(SIMON) | 金 | Meta-Strategist | `knowledge/totems/simon/` | ⏳ 待创建 |
| **TOTEM-GUANYIN** | 观自在(GUANYIN) | 水 | Worker-Analysis | `knowledge/totems/guanyin/` | ⏳ 待创建 |
| **TOTEM-CONFUCIUS** | 孔子(CONFUCIUS) | 木 | Supervisor-Biz | `knowledge/totems/confucius/` | ⏳ 待创建 |
| **TOTEM-HUINENG** | 六祖慧能(HUINENG) | 火 | Worker-Creative | `knowledge/totems/huineng/` | ⏳ 待创建 |

---

## 已完成内容

### 黎红雷专家插件（EXPERT-LIU）✅
- [x] 知识库目录创建
- [x] 核心知识文档（biography.md）
- [x] 文章入库（xiumius.cn文章）
- [x] 索引文件（index.json）

### LIU图腾插件（TOTEM-LIU）✅
- [x] 知识库目录创建
- [x] 方法论文档（methodology.md）
- [x] 索引文件（index.json）

---

## 专家独立发表意见机制

### 触发条件

专家插件在以下场景**必须**独立发表意见：

1. **合伙伦理决策** → LIU专家+CONFUCIUS图腾双重校验
2. **技术架构决策** → 罗汉教授插件技术评估
3. **战略方向决策** → SIMON图腾+李泽湘专家联合评估
4. **创新方案评估** → HUINENG图腾+方翊沣专家直觉校验
5. **风险预警** → GUANYIN图腾独立扫描
6. **执行方案** → LIU图腾执行监督

### 意见发表格式

```markdown
## [专家/图腾名称] 独立意见

**任务ID**: [任务标识]
**决策场景**: [具体场景]
**我的立场**: [支持/反对/保留/补充]

**核心观点**:
1. [观点1]
2. [观点2]
3. [观点3]

**参考依据**:
- [知识库链接1]
- [知识库链接2]

---
**发表时间**: YYYY-MM-DD HH:MM
**独立度**: 100%（非Worker推导，基于自身知识库）
```

---

## 知识库自动迭代机制

### 持续学习源

| 专家/图腾 | 自动迭代源 | 更新频率 |
|-----------|------------|----------|
| 黎红雷 | 儒商文化期刊、儒商大会 | 每周 |
| 罗汉 | 数学/软件工程顶会 | 每日 |
| 谢宝剑 | 深港政策、区域经济报告 | 每周 |
| 方翊沣 | 脑科学期刊、BCI会议 | 每周 |
| SIMON | 决策科学、满意解理论 | 每周 |

### 新知识点入库流程

```
发现新知识点
    ↓
自动抓取 → 元数据提取 → 主题分类
    ↓
匹配专家插件 → 知识库写入
    ↓
专家插件"学习"完成
    ↓
下次决策时可引用
```

---

## 新增知识链接处理

**链接**: https://c.xiumius.cn/board/v5/5q79C/691433112
**内容**: 黎红雷《企业儒学：中国管理哲学的自主知识体系》
**处理状态**: ✅ 已入库
**入库位置**: `knowledge/experts/li_honglei/updates/2026-03-31-xiumius-article.md`
**专家关联**: EXPERT-LIU（黎红雷专家）+ TOTEM-LIU（刘禹锡图腾）
**后续**: 自动触发LIU图腾知识更新，参与未来儒商决策

---

*专家插件清单 - 持续迭代*
