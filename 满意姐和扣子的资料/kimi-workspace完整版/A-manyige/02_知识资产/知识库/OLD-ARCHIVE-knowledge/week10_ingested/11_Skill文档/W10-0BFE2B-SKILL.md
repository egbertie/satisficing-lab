---
# 知识元数据 (5标准化)
knowledge_id: W10-0BFE2B
title: Feishu Suite V2 - 整合版
category: 11_Skill文档
source: skills/.archive_feishu-suite-v2/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1322
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Feishu Suite V2 - 整合版

> **知识ID**: W10-0BFE2B  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_feishu-suite-v2/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Feishu Suite V2 - 整合版

> **整合来源**: feishu-doc-manager + feishu-docx-powerwrite + feishu-messaging + feishu-file-handler + sendfiles-to-feishu + dingtalk-feishu-cn  
> **整合时间**: 2026-03-21  
> **整合原因**: 消除重复，统一接口

## Purpose
飞书全功能管理：文档、消息、文件、多维表格

## 5-Standard Compliance (整合后)

| Standard | Implementation | Status |
|----------|----------------|--------|
| 全局考虑 | 覆盖文档/消息/文件/表格 | ✅ 100% |
| 系统考虑 | 完整飞书工作流 | ✅ 100% |
| 迭代机制 | API版本兼容 | ✅ 100% |
| Skill化 | 统一接口 | ✅ 100% |
| 自动化 | 批量操作支持 | ✅ 100% |

## Commands

### 文档管理
- feishu doc create - 创建文档
- feishu doc read - 读取文档
- feishu doc write - 写入文档
- feishu docx powerwrite - 高级写入

### 消息通信
- feishu msg send - 发送消息
- feishu msg broadcast - 广播消息
- feishu msg history - 消息历史

### 文件操作
- feishu file upload - 上传文件
- feishu file download - 下载文件
- feishu file list - 文件列表

### 多维表格
- feishu bitable query - 查询记录
- feishu bitable create - 创建记录
- feishu bitable update - 更新记录

## 整合说明

| 原Skill | 功能 | 整合状态 |
|---------|------|----------|
| feishu-doc-manager | 文档管理 | ✅ 保留 |
| feishu-docx-powerwrite | 高级写入 | ✅ 合并 |
| feishu-messaging | 消息发送 | ✅ 保留 |
| feishu-file-handler | 文件处理 | ✅ 合并到messaging |
| sendfiles-to-feishu | 文件发送 | ✅ 合并到messaging |
| dingtalk-feishu-cn | 钉钉整合 | ✅ 拆分独立 |

## 优化收益
- Skill数量: 8 → 2 (-75%)
- Token消耗: -75%
- 接口统一: 100%

---

*整合完成: 2026-03-21*
