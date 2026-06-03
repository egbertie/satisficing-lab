---
# 知识元数据 (5标准化)
knowledge_id: W15-AD013D
title: system_failure
category: 11_Skill文档
source: skills/disaster-recovery-wecom/templates/system_failure.md
ingested_at: 2026-03-27 17:59:30
word_count: 314
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# system_failure

> **知识ID**: W15-AD013D  
> **分类**: 11_Skill文档  
> **来源**: `skills/disaster-recovery-wecom/templates/system_failure.md`  
> **入库时间**: 2026-03-27

---

## 正文

<font color="#{{COLOR}}">**[{{LEVEL}} - {{LEVEL_NAME}}]**</font>

**🚨 系统故障告警**

**故障时间:** {{TIMESTAMP}}
**故障主机:** {{HOSTNAME}}
**告警级别:** {{LEVEL}}

---

**故障详情:**

{{DESCRIPTION}}

---

**影响范围:**
- {{IMPACT}}

**建议处理:**
1. {{ACTION_1}}
2. {{ACTION_2}}
3. {{ACTION_3}}

---

<font color="gray">{{TIMESTAMP}}</font>
