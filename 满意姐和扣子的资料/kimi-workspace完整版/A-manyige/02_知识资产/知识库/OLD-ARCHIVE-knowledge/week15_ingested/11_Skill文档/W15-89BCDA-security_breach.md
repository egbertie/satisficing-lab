---
# 知识元数据 (5标准化)
knowledge_id: W15-89BCDA
title: security_breach
category: 11_Skill文档
source: skills/disaster-recovery-wecom/templates/security_breach.md
ingested_at: 2026-03-27 17:59:30
word_count: 330
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# security_breach

> **知识ID**: W15-89BCDA  
> **分类**: 11_Skill文档  
> **来源**: `skills/disaster-recovery-wecom/templates/security_breach.md`  
> **入库时间**: 2026-03-27

---

## 正文

<font color="#FF0000">**[P0 - 紧急]**</font>

**🔒 安全告警**

**告警时间:** {{TIMESTAMP}}
**告警类型:** {{ALERT_TYPE}}
**严重程度:** 严重

---

**事件详情:**

{{EVENT_DESCRIPTION}}

**涉及资源:**
- {{RESOURCE_1}}
- {{RESOURCE_2}}
- {{RESOURCE_3}}

**立即行动:**
1. 🚨 撤销可疑权限
2. 🚨 检查访问日志
3. 🚨 重置相关凭据
4. 🚨 通知安全团队

---

@所有人

<font color="gray">{{TIMESTAMP}}</font>
