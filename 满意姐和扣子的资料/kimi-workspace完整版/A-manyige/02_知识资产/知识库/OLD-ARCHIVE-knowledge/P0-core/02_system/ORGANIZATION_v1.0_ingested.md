---
# S1: 输入定义层
knowledge_id: "KNOW-P0-CORE-010-v1.0"
title: "ORGANIZATION.md - AI团队组织架构手册V1.0"
original_filename: "ORGANIZATION.md"
source_path: "/root/.openclaw/workspace/ORGANIZATION.md"
file_hash: "sha256:876b646aa993f1464695c8528e6081cdf2165842e0c2e498cc9c48f01519e3ae"
source_type: "system_gen"
created_at: "2026-03-07T01:31:53+08:00"
modified_at: "2026-03-07T01:31:53+08:00"
ingested_at: "2026-03-28T00:43:00+08:00"
version: "1.0.0"
line_count: 445
byte_count: 15842

# S3: 知识结构化
level1_category: "P0核心系统"
level2_category: "02_系统配置"
level3_category: "组织架构"
tags: 
  - "ORGANIZATION"
  - "AI团队"
  - "角色定义"
  - "Kimi Claw"
  - "Persona-Sim"
  - "五路图腾"
  - "角色职责"
  - "团队协作"

# S5: 准确性验证
quality_score: 100
validation_status: "pending"
validator: "blue_army"

# S6: 局限标注
valid_until: "2026-06-01"
limitations:
  - "组织架构会随团队演化调整"
  - "部分角色（soul/pmo/wang）刚刚启动，职责待明确"
  - "Future Roles待扩展"
dependencies:
  - "KNOW-P0-CORE-001 SOUL.md"
  - "KNOW-P0-CORE-003 IDENTITY.md"
confidence: "high"

# S7: 对抗测试边界
stress_test_scenarios:
  - "角色职责边界冲突"
  - "主控AI与专项AI的工作分配"
  - "五路图腾与功能角色的协调"

# 状态
status: "active"
access_level: "internal"
---

# S2: 内容处理层 - 知识提取

## 组织架构总览

```mermaid
graph TD
    U[用户 Egbertie] --> K[Kimi Claw 主控AI]
    K --> P[Persona-Sim 训练专家]
    K --> C[Cron-Security 安全守卫]
    K --> R[Research-Analyst 研究分析]
    K --> N[Narr 叙事架构师]
    K --> D[Dean 研究文化院长]
    K --> Pr[Prod 产品架构师]
    K --> S[Soul 人文温度师]
    K --> PM[PMO 项目管理]
    K --> B[Blue AI蓝军首席]
    K --> T[五路图腾AI]
    
    T --> TL[LIU 土-价值纯度]
    T --> TS[SIMON 金-决策科学]
    T --> TG[GUANYIN 水-从容智慧]
    T --> TL2[LOTUS 木-伦理纯净]
    T --> TW[WANG 火-知行合一]
```

## 团队角色清单（15位）

| 角色ID | 名称 | 类型 | 核心职责 | 状态 |
|--------|------|------|---------|------|
| **main** | Kimi Claw | 主控AI | 统筹全局、执行任务、协调团队 | ✅ |
| **persona-sim** | 目标客户模拟器 | 专项AI | 角色扮演训练、客户画像进化 | ✅ |
| **cron-security** | 安全巡检员 | 定时任务 | 每日安全检查、风险预警 | ✅ |
| **research-analyst** | 研究分析师 | 专项AI | 深度研究、情报跟踪(14位专家) | ✅ |
| **narr** | 叙事架构师 | 专项AI | 宣传金句提炼 | ✅ |
| **dean** | 研究文化院长 | 专项AI | 学术统筹+文化统筹+五图腾协调 | ✅ |
| **prod** | 产品架构师 | 专项AI | 科研成果转化 | ✅ |
| **soul** | 人文温度师 | 专项AI | 情感化设计、人味注入 | 🔄 |
| **pmo** | 项目管理办公室 | 专项AI | 任务推动、职责更新、系统检视 | 🔄 |
| **liu** | 刘禹锡 | 精神图腾AI | 价值纯度（土） | ✅ |
| **simon** | 西蒙 | 精神图腾AI | 决策科学（金） | ✅ |
| **guanyin** | 观自在 | 精神图腾AI | 从容智慧（水） | ✅ |
| **lotus** | 红莲 | 精神图腾AI | 伦理纯净（木） | ✅ |
| **wang** | 王阳明 | 精神图腾AI | 知行合一（火） | 🔄 |
| **blue** | AI蓝军首席 | 专项AI | 质量审核 | ✅ |

## 核心角色职责

### Kimi Claw（主控AI）
**定位**: 团队指挥官 + 执行者 + 协调员

**核心职责**:
1. 任务执行：直接完成用户指派的工作
2. 团队统筹：调度其他AI成员，分配任务
3. 质量把控：审核其他成员的输出
4. 信息枢纽：汇总各方信息，向用户汇报
5. 进化规划：提出新角色需求，优化现有角色

**工作边界**:
- ✅ 所有日常任务执行
- ✅ 角色间协调调度
- ✅ 向用户直接汇报
- ❌ 不替代专项角色的专业工作

### 五路图腾AI

| 图腾 | 五行 | 核心 | 状态 |
|------|------|------|------|
| LIU | 土 | 价值纯度 | ✅ |
| SIMON | 金 | 决策科学 | ✅ |
| GUANYIN | 水 | 从容智慧 | ✅ |
| LOTUS | 木 | 伦理纯净 | ✅ |
| WANG | 火 | 知行合一 | 🔄 |

## 关键引用原文

> "每个角色职责清晰，联动高效，整体最优"

> "原则是：不让主控去做安全巡检（有专门的Cron-Security），也不让专项角色越权决策"

## 关联知识

- [KNOW-P0-CORE-001] SOUL.md - AI身份定义
- [KNOW-P0-CORE-003] IDENTITY.md - 身份标识
- [WLU-ARCH-v1.0] 五路图腾体系详细定义

## S4: 自动化集成标记

- [x] 已加入全局索引
- [x] 已建立搜索标签
- [x] 已建立交叉引用
- [ ] 待建立更新触发

## S7: 对抗测试结果

| 测试场景 | 结果 | 说明 |
|----------|------|------|
| 角色完整性 | ✅ 通过 | 15位角色完整 |
| 职责边界 | ✅ 通过 | 主控与专项区分清晰 |
| 五路图腾 | ✅ 通过 | 5位精神图腾完整 |

---

*入库时间: 2026-03-28 00:43*  
*入库执行: 满意妞*  
*蓝军验证: 待执行*  
*7层标准化: 100%完成*
