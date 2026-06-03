---
# 知识元数据 (5标准化)
knowledge_id: W8-5E3857
title: API Configuration Manager Skill
category: 11_Skill文档
source: skills/.archive_api-configuration-manager/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 437
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# API Configuration Manager Skill

> **知识ID**: W8-5E3857  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_api-configuration-manager/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# API Configuration Manager Skill

## Purpose
管理所有第三方API的配置、注册和状态监控

## 5-Standard Compliance

| Standard | Implementation |
|----------|----------------|
| 全局考虑 | 覆盖GitHub Models/Perplexity/Jina AI/Excalidraw等 |
| 系统考虑 | 注册→配置→验证→监控→更新闭环 |
| 迭代机制 | 定期检查配置有效性，自动更新失效配置 |
| Skill化 | 标准化接口：register/configure/verify/monitor |
| 自动化 | 自动检测未配置API，自动触发注册流程 |

## APIs Managed
- GitHub Models
- Perplexity
- Jina AI
- Excalidraw
- Claude (备用)
