---
# 知识元数据 (5标准化)
knowledge_id: W12-200F8C
title: 感知力训练体系标准Skill V2.0
category: 11_Skill文档
source: skills/.archive_perception-training-system/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1592
week: 12
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 感知力训练体系标准Skill V2.0

> **知识ID**: W12-200F8C  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_perception-training-system/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 感知力训练体系标准Skill V2.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V2.0 | 更新: 2026-03-20 | 核心: 五路图腾感知力训练

---

## 一、全局考虑（六层+五维感知）

### 感知维度 × 六层矩阵

| 维度 | 对应图腾 | 训练内容 | L0身份 | L1项目 | L2系统 | L3外部 | L4交付 | L5归档 |
|------|----------|----------|--------|--------|--------|--------|--------|--------|
| **土-经验** | CONFUCIUS | 历史案例分析 | 经验积累 | 案例复盘 | 模式库 | 外部经验 | 分析报告 | 经验库 |
| **水-趋势** | GUANYIN | 环境变化感知 | 敏感度 | 趋势跟踪 | 数据监控 | 行业动态 | 预警报告 | 趋势库 |
| **木-生长** | 生长图腾 | 潜力评估 | 成长型思维 | 潜力识别 | 成长追踪 | 外部学习 | 成长计划 | 学习档案 |
| **金-逻辑** | SIMON | 结构化分析 | 逻辑思维 | 分析框架 | 算法支持 | 外部验证 | 分析报告 | 方法库 |
| **火-压力** | 压力图腾 | 压力测试 | 抗压能力 | 场景模拟 | 测试框架 | 蓝军挑战 | 测试报告 | 测试档案 |

---

## 二、系统考虑（评估→训练→反馈→提升闭环）

### 2.1 训练体系

#### 基础训练（每日10分钟）
- 冥想/正念练习
- 案例分析阅读
- 决策日志记录

#### 进阶训练（每周30分钟）
- 模拟决策演练
- 专家咨询对话
- 复盘反思写作

#### 高阶训练（每月2小时）
- 真实场景决策
- 压力环境测试
- 跨维度综合应用

---

## 三、迭代机制（每日/每周/每月）

---

## 四、Skill化（训练指导）

```python
def generate_perception_training(level, dimension):
    """生成感知力训练内容"""
    if dimension == "earth":
        return generate_historical_case_training(level)
    elif dimension == "water":
        return generate_trend_perception_training(level)
    # ... 其他维度
```

---

## 五、流程自动化

```json
{
  "jobs": [
    {"name": "daily-perception", "schedule": "0 7 * * *"},
    {"name": "weekly-perception", "schedule": "0 10 * * 0"},
    {"name": "monthly-perception", "schedule": "0 9 1 * *"}
  ]
}
```

---

## 六、质量门控

- [x] **全局**: 五维×六层
- [x] **系统**: 评估→训练→反馈→提升
- [x] **迭代**: 三级训练频率
- [x] **Skill化**: 训练指导生成
- [x] **自动化**: 定时提醒

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*