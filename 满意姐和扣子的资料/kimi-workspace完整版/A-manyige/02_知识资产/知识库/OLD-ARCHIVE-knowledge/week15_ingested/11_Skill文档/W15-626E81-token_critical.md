---
# 知识元数据 (5标准化)
knowledge_id: W15-626E81
title: token_critical
category: 11_Skill文档
source: skills/disaster-recovery-wecom/templates/token_critical.md
ingested_at: 2026-03-27 17:59:30
word_count: 352
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# token_critical

> **知识ID**: W15-626E81  
> **分类**: 11_Skill文档  
> **来源**: `skills/disaster-recovery-wecom/templates/token_critical.md`  
> **入库时间**: 2026-03-27

---

## 正文

<font color="#FF0000">**[P0 - 紧急]**</font>

**🔴 Token 即将耗尽**

**告警时间:** {{TIMESTAMP}}
**当前使用率:** {{USAGE_PERCENT}}%
**剩余 Token:** {{TOKENS_REMAINING}}

---

**⚠️ 重要提示**

Token 使用率已超过 95%，即将触发限制。

**立即行动:**
1. ✅ 暂停非关键任务
2. ✅ 检查是否有异常消耗
3. ✅ 联系管理员增加预算
4. ✅ 启用紧急节流模式

**预计耗尽时间:** {{ESTIMATED_DEPLETION}}

---

@所有人

<font color="gray">{{TIMESTAMP}}</font>
