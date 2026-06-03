---
# 知识元数据 (5标准化)
knowledge_id: W12-BE1F44
title: Permission Auditor Skill
category: 11_Skill文档
source: skills/.archive_permission-auditor/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 394
week: 12
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Permission Auditor Skill

> **知识ID**: W12-BE1F44  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_permission-auditor/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Permission Auditor Skill

## Purpose
审计和管理所有第三方服务权限

## 5-Standard Compliance

| Standard | Implementation |
|----------|----------------|
| 全局考虑 | 覆盖所有服务的权限清单管理 |
| 系统考虑 | 需求识别→权限申请→验证→使用→定期复核闭环 |
| 迭代机制 | 权限变更自动记录，定期复核必要性 |
| Skill化 | 标准化接口：audit/request/verify/renew |
| 自动化 | 每周检查权限完整度，到期前预警 |

## Commands
- `audit` - 审计当前权限
- `request` - 申请新权限
- `verify` - 验证权限有效性
- `renew` - 续期即将到期权限
