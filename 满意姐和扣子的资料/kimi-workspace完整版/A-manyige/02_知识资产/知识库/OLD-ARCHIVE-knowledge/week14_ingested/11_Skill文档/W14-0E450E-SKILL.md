---
# 知识元数据 (5标准化)
knowledge_id: W14-0E450E
title: Workspace Health Scanner Skill
category: 11_Skill文档
source: skills/.archive_workspace-health-scanner/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 843
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Workspace Health Scanner Skill

> **知识ID**: W14-0E450E  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_workspace-health-scanner/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Workspace Health Scanner Skill

## 功能概述
自动扫描工作空间健康状态，从四个维度评估系统健康度，生成健康报告并提供优化建议。

## 扫描维度
1. **结构健康度** (25%) - 核心文件、目录结构、重复文件
2. **时效健康度** (25%) - 文档更新、Skill使用、任务逾期
3. **引用健康度** (25%) - 死链检测、循环引用、孤儿文档
4. **安全健康度** (25%) - 文件权限、敏感信息、备份验证

## 使用方法

### 命令
```bash
# 每日扫描
openclaw agent --skill workspace-health-scanner --task daily-scan

# 深度扫描
openclaw agent --skill workspace-health-scanner --task deep-scan

# 指定维度扫描
openclaw agent --skill workspace-health-scanner --task scan --dimension structure
```

### Python调用
```python
from skills.workspace_health_scanner import HealthScanner

scanner = HealthScanner()
result = scanner.scan()
print(f"健康度评分: {result['total_score']}")
```

## 输出格式
- 健康度评分: 0-100分
- 维度评分: 四个维度分别评分
- 问题清单: 分级问题列表
- 优化建议: 可执行建议

## 配置
见 `config/scanner-config.json`

## 作者
满意解研究所 - 持续优化系统

## 版本
v1.0.0 - 2026-03-15
