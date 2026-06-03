---
# 知识元数据 (5标准化)
knowledge_id: W15-1883B5
title: backup_failure
category: 11_Skill文档
source: skills/disaster-recovery-wecom/templates/backup_failure.md
ingested_at: 2026-03-27 17:59:30
word_count: 341
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# backup_failure

> **知识ID**: W15-1883B5  
> **分类**: 11_Skill文档  
> **来源**: `skills/disaster-recovery-wecom/templates/backup_failure.md`  
> **入库时间**: 2026-03-27

---

## 正文

<font color="#FF0000">**[P0 - 紧急]**</font>

**💥 备份任务失败**

**失败时间:** {{TIMESTAMP}}
**备份类型:** {{BACKUP_TYPE}}
**失败主机:** {{HOSTNAME}}

---

**失败详情:**

```
{{ERROR_MESSAGE}}
```

**影响:**
- 上次成功备份: {{LAST_SUCCESS}}
- 数据丢失风险: {{RISK_LEVEL}}

**恢复步骤:**
1. 检查磁盘空间
2. 检查网络连接
3. 手动执行备份脚本
4. 验证备份完整性

---

@所有人

<font color="gray">{{TIMESTAMP}}</font>
