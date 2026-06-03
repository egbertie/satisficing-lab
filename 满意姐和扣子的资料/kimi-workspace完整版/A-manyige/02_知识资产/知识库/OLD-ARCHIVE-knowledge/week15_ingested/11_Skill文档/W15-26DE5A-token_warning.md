---
# 知识元数据 (5标准化)
knowledge_id: W15-26DE5A
title: token_warning
category: 11_Skill文档
source: skills/disaster-recovery-wecom/templates/token_warning.md
ingested_at: 2026-03-27 17:59:30
word_count: 337
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# token_warning

> **知识ID**: W15-26DE5A  
> **分类**: 11_Skill文档  
> **来源**: `skills/disaster-recovery-wecom/templates/token_warning.md`  
> **入库时间**: 2026-03-27

---

## 正文

<font color="#FF8C00">**[P1 - 高优先级]**</font>

**⚠️ Token 消耗预警**

**预警时间:** {{TIMESTAMP}}
**当前使用率:** {{USAGE_PERCENT}}%
**剩余 Token:** {{TOKENS_REMAINING}}

---

**使用统计:**
- 今日已用: {{TOKENS_TODAY}}
- 本周已用: {{TOKENS_WEEK}}
- 月度预算: {{TOKENS_BUDGET}}

**建议:**
1. 检查高消耗任务
2. 考虑启用节流策略
3. 评估是否需要增加预算

---

<font color="gray">{{TIMESTAMP}}</font>
