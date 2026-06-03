---
# 知识元数据 (5标准化)
knowledge_id: W15-7A9890
title: task_failure
category: 11_Skill文档
source: skills/disaster-recovery-wecom/templates/task_failure.md
ingested_at: 2026-03-27 17:59:30
word_count: 347
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# task_failure

> **知识ID**: W15-7A9890  
> **分类**: 11_Skill文档  
> **来源**: `skills/disaster-recovery-wecom/templates/task_failure.md`  
> **入库时间**: 2026-03-27

---

## 正文

<font color="#FF0000">**[P0 - 紧急]**</font>

**❌ 任务执行失败**

**失败时间:** {{TIMESTAMP}}
**任务名称:** {{TASK_NAME}}
**任务ID:** {{TASK_ID}}

---

**失败原因:**

```
{{ERROR_MESSAGE}}
```

**任务信息:**
- 开始时间: {{START_TIME}}
- 执行时长: {{DURATION}}
- 重试次数: {{RETRY_COUNT}}

**处理建议:**
1. 查看详细日志
2. 检查依赖服务
3. 手动重新执行
4. 更新任务配置

---

<font color="gray">{{TIMESTAMP}}</font>
