---
# 知识元数据 (5标准化)
knowledge_id: W10-3C6D39
title: Skill: Economic Intelligence
category: 11_Skill文档
source: skills/.archive_economic-intelligence/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2479
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Skill: Economic Intelligence

> **知识ID**: W10-3C6D39  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_economic-intelligence/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Skill: Economic Intelligence

## 简介

经济环境研究体系Skill - 基于深圳南山定位的宏观/微观经济环境监测与分析工具。

> **核心原理**：深圳南山的硬科技企业家，其决策受特定时空约束。

## 能力

- 宏观环境监测（政策/资本/供应链/国际形势）
- 中观环境洞察（产业集群/区域生态）
- 微观环境跟踪（企业动态/人才流动）
- 环境-策略映射
- 研究输出生成

## 使用方式

### 环境监测

```bash
# 生成今日环境日报
econ-intel daily-report

# 生成本周环境周报
econ-intel weekly-report

# 生成环境月报
econ-intel monthly-report
```

### 特定领域监测

```bash
# 政策监测
econ-intel policy --level [national|provincial|city|district]

# 融资监测
econ-intel funding --sector [AI|semiconductor|biotech|new-energy]

# 供应链监测
econ-intel supply-chain --category [chip|material|equipment|software]
```

### 客户情境匹配

```bash
# 根据当前环境为客户提供策略建议
econ-intel strategy --customer <customer-id> --stage [seed|angel|A|B]

# 查看当前环境周期判断
econ-intel cycle-status
```

### 预警系统

```bash
# 查看风险预警
econ-intel alerts

# 设置特定客户预警
econ-intel watch --customer <id> --type [funding|team|risk]
```

## 输入

- 监测类型（daily/weekly/monthly）
- 关注领域（policy/funding/supply/international）
- 客户信息（用于情境匹配）
- 预警条件

## 输出

- 环境日报/周报/月报
- 政策解读
- 风险提示
- 策略建议
- 预警通知

## 示例

### 示例1：生成环境日报

```
启动：econ-intel daily-report

输出：
━━━━━━━━━━━━━━━━━━━━
硬科技环境日报 | 202X年XX月XX日
━━━━━━━━━━━━━━━━━━━━

【政策动态】
• 工信部发布《XX产业发展指南》
• 深圳市启动新一轮人才计划申报

【融资事件】
• AI领域：XX公司完成A轮5000万融资
• 半导体：XX芯片企业获战略投资

【供应链动态】
• 芯片交期缩短至16周
• 某材料价格环比下降5%

【国际形势】
• 美方更新实体清单
• 人民币汇率波动

【今日关注】
⚠️ 风险提示：实体清单更新涉及硬科技领域
💡 机会提示：人才计划申报窗口开启
```

### 示例2：客户情境匹配

```
> 客户：AI芯片公司，A轮阶段
> 当前环境：调整期

启动：econ-intel strategy --customer "AI芯片-A轮" --stage A

输出：
【环境判断】
当前处于：调整期
特征：融资难度增加、估值回调、人才市场松动

【合伙人策略建议】
1. 人才策略：精兵简政，保留核心
2. 股权策略：向核心人才倾斜
3. 扩张节奏：聚焦核心，暂缓多元化
4. 风险提示：关注现金流，避免核心流失

【话术建议】
"市场进入调整期，融资更注重基本面。建议优化团队结构，
把资源集中在最核心的人才上。这是一个去泡沫、练内功的好时机。"
```

### 示例3：风险预警

```
启动：econ-intel alerts

输出：
🔴 红色预警
• 客户X：核心高管离职（CTO）
• 行业：某AI公司合伙人纠纷曝光

🟡 黄色预警
• 政策：补贴申报窗口即将关闭
• 市场：某细分领域融资热度下降

建议行动：
1. 联系客户X，评估合伙人稳定性
2. 通知相关客户抓紧申报补贴
```

## 监测数据源

### 官方渠道
- 国务院/科技部/工信部官网
- 广东省/深圳市/南山区政府网站

### 数据平台
- IT桔子、企名片、企查查
- Wind、同花顺
- 36氪、投中网

### 行业垂直
- 半导体行业观察、芯智讯
- 新材料在线、甲子光年

### 国际源
- Reuters、Bloomberg
- Nature、Science

## 自动化配置

### Cron任务

```bash
# 每日经济环境监测（09:17）
0 9 * * * openclaw agent --skill economic-intelligence --task daily-report

# 每周环境周报（周五17:17）
0 17 * * 5 openclaw agent --skill economic-intelligence --task weekly-report

# 每月环境月报（次月3日09:17）
0 9 3 * * openclaw agent --skill economic-intelligence --task monthly-report
```

## 相关文档

- [经济环境研究体系_V1.1.md](/root/.openclaw/workspace/经济环境研究体系_V1.1.md)

## 元数据

- 版本：V1.1
- 作者：满意解研究所
- 更新日期：2026-03-15
- 适用范围：深圳南山硬科技企业
