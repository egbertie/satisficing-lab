---
# 知识元数据 (5标准化)
knowledge_id: W12-95A89A
title: 复盘优化报告机制标准Skill V2.0
category: 11_Skill文档
source: skills/.archive_retrospective-system/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1532
week: 12
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 复盘优化报告机制标准Skill V2.0

> **知识ID**: W12-95A89A  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_retrospective-system/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 复盘优化报告机制标准Skill V2.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V2.0 | 更新: 2026-03-20 | 核心: 日/周/月三级复盘

---

## 一、全局考虑（六层+三级复盘）

### 复盘类型 × 六层矩阵

| 复盘类型 | 频率 | L0身份 | L1项目 | L2系统 | L3外部 | L4交付 | L5归档 |
|----------|------|--------|--------|--------|--------|--------|--------|
| **日复盘** | 每日 | 能力反思 | 任务回顾 | 系统问题 | 沟通反馈 | 产出检查 | 日志整理 |
| **周复盘** | 每周 | 成长评估 | 成果总结 | 流程优化 | 合作评价 | 周报生成 | 知识归档 |
| **月复盘** | 每月 | 能力成长 | 项目里程碑 | 架构评估 | 关系维护 | 月度报告 | 经验库 |

---

## 二、系统考虑（复盘→分析→改进→验证闭环）

### 2.1 复盘模板

#### 日复盘（每日23:30）
```markdown
## 日复盘 - YYYY-MM-DD

### 今日完成
- [ ] 任务1
- [ ] 任务2

### 今日问题
- 问题1: 描述 → 根因 → 改进

### 明日计划
- 计划1
- 计划2

### 能力成长
- 学到了什么
```

#### 周复盘（每周六18:00）
```markdown
## 周复盘 - Week XX

### 本周成果
### 本周问题
### 改进措施
### 下周计划
```

---

## 三、迭代机制（每次复盘→改进→下次验证）

---

## 四、Skill化（自动生成）

```python
def generate_retrospective(review_type):
    """生成复盘报告"""
    if review_type == "daily":
        return generate_daily_retrospective()
    elif review_type == "weekly":
        return generate_weekly_retrospective()
    elif review_type == "monthly":
        return generate_monthly_retrospective()
```

---

## 五、流程自动化

```json
{
  "jobs": [
    {"name": "daily-retro", "schedule": "30 23 * * *"},
    {"name": "weekly-retro", "schedule": "0 18 * * 6"},
    {"name": "monthly-retro", "schedule": "0 18 28-31 * *"}
  ]
}
```

---

## 六、质量门控

- [x] **全局**: 三级×六层
- [x] **系统**: 复盘→改进闭环
- [x] **迭代**: 持续优化
- [x] **Skill化**: 自动生成
- [x] **自动化**: Cron驱动

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*