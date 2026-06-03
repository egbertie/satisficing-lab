---
# 知识元数据 (5标准化)
knowledge_id: W17-8F856F
title: daily-report
category: 11_Skill文档
source: skills/task-manager/templates/daily-report.md
ingested_at: 2026-03-27 17:59:30
word_count: 607
week: 17
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# daily-report

> **知识ID**: W17-8F856F  
> **分类**: 11_Skill文档  
> **来源**: `skills/task-manager/templates/daily-report.md`  
> **入库时间**: 2026-03-27

---

## 正文

## 晨报 - {{DATE}}

### 📅 日期信息
**报告日期**: {{DATE}}  
**星期**: {{WEEKDAY}}  
**距离官宣**: {{DAYS_TO_LAUNCH}}天

---

### 🎯 今日重点（Top 3）
{{TODAY_TOP3}}

---

### ✅ 昨日完成
{{YESTERDAY_COMPLETED}}

---

### 🔄 进行中
{{IN_PROGRESS}}

---

### ⏰ 即将到期提醒
{{UPCOMING_REMINDERS}}

---

### ⚠️ 风险/阻塞
{{BLOCKERS}}

---

### ❓ 需要决策
{{DECISIONS_NEEDED}}

---

### 📊 今日数据
| 指标 | 数值 |
|------|------|
| 今日截止 | {{TODAY_COUNT}} |
| 进行中 | {{WIP_COUNT}} |
| 即将到期(3天内) | {{UPCOMING_COUNT}} |
| 逾期 | {{OVERDUE_COUNT}} |

---

### 📝 备注
{{NOTES}}

---

*晨报生成时间: {{GENERATED_AT}}*  
*生成者: 满意妞（主控AI）*  
*数据来源: TASK_MASTER.md + memory/{{DATE}}.md*
