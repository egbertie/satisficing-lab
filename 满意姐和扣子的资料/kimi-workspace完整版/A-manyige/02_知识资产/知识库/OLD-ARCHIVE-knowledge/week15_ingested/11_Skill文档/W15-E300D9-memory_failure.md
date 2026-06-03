---
# 知识元数据 (5标准化)
knowledge_id: W15-E300D9
title: memory_failure
category: 11_Skill文档
source: skills/disaster-recovery-wecom/templates/memory_failure.md
ingested_at: 2026-03-27 17:59:30
word_count: 408
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# memory_failure

> **知识ID**: W15-E300D9  
> **分类**: 11_Skill文档  
> **来源**: `skills/disaster-recovery-wecom/templates/memory_failure.md`  
> **入库时间**: 2026-03-27

---

## 正文

<font color="#FF0000">**[P0 - 紧急]**</font>

**🧠 记忆系统异常**

**异常时间:** {{TIMESTAMP}}
**异常类型:** {{ERROR_TYPE}}
**涉及文件:** {{AFFECTED_FILE}}

---

**异常详情:**

```
{{ERROR_DETAILS}}
```

**⚠️ 数据风险:**
- MEMORY.md 状态: {{MEMORY_STATUS}}
- 今日日志: {{TODAY_LOG_STATUS}}
- 任务看板: {{TASK_BOARD_STATUS}}

**紧急恢复:**
1. 立即停止所有写入操作
2. 从 Git 恢复 MEMORY.md
3. 验证文件完整性
4. 重新生成损坏的日志

---

@所有人

<font color="gray">{{TIMESTAMP}}</font>
