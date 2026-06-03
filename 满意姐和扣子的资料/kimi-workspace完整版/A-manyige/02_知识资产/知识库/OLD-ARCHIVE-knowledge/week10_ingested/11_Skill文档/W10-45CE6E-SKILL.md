---
# 知识元数据 (5标准化)
knowledge_id: W10-45CE6E
title: SKILL
category: 11_Skill文档
source: skills/.archive_docker-workflow-automation/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2014
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W10-45CE6E  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_docker-workflow-automation/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: docker-workflow-automation
version: 1.0.0
description: |
  Docker工作流自动化 - 容器生命周期管理的标准工作流：
  1. 全局考虑：覆盖开发、测试、部署全流程
  2. 系统考虑：构建→测试→推送→部署→监控闭环
  3. 迭代机制：根据运行状况优化镜像和配置
  4. Skill化：标准接口，可嵌入CI/CD流程
  5. 流程自动化：自动执行容器管理工作流
author: Satisficing Institute
tags:
  - docker
  - workflow
  - automation
  - devops
requires:
  - model: "kimi-coding/k2p5"
---

# Docker工作流自动化标准Skill V1.0.0

## 标准1: 全局考虑（Global Coverage）

### 1.1 工作流阶段

| 阶段 | 动作 | 检查点 |
|------|------|--------|
| **构建** | docker build | 镜像大小 |
| **测试** | 容器测试 | 健康检查 |
| **推送** | docker push | 标签规范 |
| **部署** | 更新服务 | 零停机 |
| **监控** | 日志/指标 | 运行状态 |

### 1.2 常用工作流

| 工作流 | 场景 |
|--------|------|
| 开发环境 | 本地开发容器 |
| 测试环境 | 自动化测试 |
| 生产部署 | 蓝绿/滚动部署 |
| 数据库 | 数据迁移/备份 |

---

## 标准2: 系统考虑（Systematic）

### 2.1 自动化流程

```
代码变更 → 自动构建 → 健康检查 → 推送镜像 → 更新服务 → 监控验证
```

---

## 标准3: 迭代机制（Iterative）

根据运行状况优化镜像大小、构建时间和配置。

---

## 标准4: Skill化（Skill-ified）

### 4.1 目录结构

```
docker-workflow-automation/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── build_image.py          # 镜像构建
│   ├── run_container.py        # 容器运行
│   ├── deploy_service.py       # 服务部署
│   └── monitor_logs.py         # 日志监控
└── templates/
    └── dockerfile_templates/
```

### 4.2 调用接口

```python
from docker_workflow_automation import DockerWorkflow

workflow = DockerWorkflow()

# 执行部署工作流
workflow.deploy(
    image="myapp:latest",
    environment="production"
)
```

---

## 标准5: 流程自动化（Fully Automated）

### 5.1 使用方法

```bash
# 构建镜像
openclaw skill run docker-workflow-automation build \
  --dockerfile Dockerfile \
  --tag myapp:latest

# 部署服务
openclaw skill run docker-workflow-automation deploy \
  --image myapp:latest \
  --env production
```

---

## 5标准验证清单

| 标准 | 验证项 | 状态 |
|------|--------|------|
| **1. 全局** | 全流程覆盖 | ✅ |
| **2. 系统** | 构建→部署→监控闭环 | ✅ |
| **3. 迭代** | 优化机制 | ✅ |
| **4. Skill化** | 标准目录 + 调用接口 | ✅ |
| **5. 自动化** | 自动执行工作流 | ✅ |

---

*版本: v1.0.0*  
*来源: docker-essentials散落机制提取*  
*创建: 2026-03-20*
