---
# 知识元数据 (5标准化)
knowledge_id: W8-98A1A3
title: SKILL
category: 11_Skill文档
source: skills/.archive_archive-handler/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 2501
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W8-98A1A3  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_archive-handler/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: archive-handler
version: 1.0.0
description: 安全通用的压缩文件处理工具。支持 ZIP/RAR/7z/TAR/TAR.GZ 格式的解压、内容预览和文件提取，无网络依赖，本地安全处理。
author: Satisficing Institute (Custom)
tags:
  - archive
  - zip
  - unzip
  - compression
  - file-management
  - security
requires:
  - binary: "python3"
  - binary: "unzip"
  - binary: "tar"
  optional:
    - binary: "unrar"
    - binary: "7z"
---

# Archive Handler Skill

安全、通用的压缩文件处理工具。专为满意解研究所定制，满足日常文件交互需求，同时保持完全自主可控。

## 核心原则

1. **本地处理** — 无网络调用，不上传任何数据
2. **安全第一** — 解压前扫描，限制敏感路径写入
3. **格式全覆盖** — ZIP/RAR/7z/TAR/TAR.GZ/BZ2/XZ
4. **只读优先** — 默认预览内容，显式确认后才解压

## 使用方式

### 1. 安全预览（推荐）

先查看压缩包内容，不实际解压：

```bash
python3 /root/.openclaw/workspace/skills/archive-handler/archive_handler.py preview <压缩包路径>
```

返回内容：
- 文件列表（含路径、大小、类型）
- 压缩格式识别
- 安全风险评估（是否有可执行文件、隐藏文件等）

### 2. 智能解压

解压到指定目录（默认为 `./extracted_<文件名>/`）：

```bash
python3 /root/.openclaw/workspace/skills/archive-handler/archive_handler.py extract <压缩包路径> [目标目录]
```

安全特性：
- 自动检测路径遍历攻击（`../` 等）
- 限制单文件最大解压尺寸（默认 100MB）
- 限制总解压尺寸（默认 1GB）
- 禁止写入系统敏感路径

### 3. 指定文件提取

只提取需要的文件：

```bash
python3 /root/.openclaw/workspace/skills/archive-handler/archive_handler.py extract-single <压缩包路径> <包内文件路径> [目标目录]
```

### 4. 批量处理

处理目录下的所有压缩包：

```bash
python3 /root/.openclaw/workspace/skills/archive-handler/archive_handler.py batch <目录路径> [目标目录]
```

## 安全策略

### 自动阻止的行为

- 路径遍历（`../../../etc/passwd` 等）
- 绝对路径写入（`/etc/`、`C:\Windows` 等）
- 符号链接指向外部路径
- 单文件超过 100MB
- 总解压超过 1GB
- 可执行文件（.exe/.bat/.sh 等）需二次确认

### 支持的格式

| 格式 | 扩展名 | 需要工具 |
|------|--------|----------|
| ZIP | .zip | unzip (内置) |
| RAR | .rar | unrar (需安装) |
| 7z | .7z, .7zip | 7z/p7zip (需安装) |
| TAR | .tar | tar (内置) |
| Gzip | .tar.gz, .tgz | tar (内置) |
| Bzip2 | .tar.bz2, .tbz2 | tar (内置) |
| XZ | .tar.xz, .txz | tar (内置) |

## 安装依赖（可选）

```bash
# Ubuntu/Debian
sudo apt-get install unrar p7zip-full

# CentOS/RHEL
sudo yum install unrar p7zip

# macOS
brew install unrar p7zip
```

## 与 Agent 协作

当我（Kimi Claw）收到压缩包时，会：

1. **安全扫描** — 用 `preview` 检查内容
2. **风险评估** — 识别可疑文件
3. **向你报告** — 告诉你里面有什么
4. **等你确认** — 你说解压才解压，说忽略就忽略

## 自建理由

为什么不直接用 zipcracker 或其他外部 skill？

| 维度 | 外部 Skill | 自建 archive-handler |
|------|-----------|---------------------|
| 代码可控 | ❌ 不可审计 | ✅ 完全透明 |
| 功能精准 | ❌ 破解密码为主 | ✅ 日常解压为主 |
| 安全边界 | ❌ 依赖外部逻辑 | ✅ 内置安全策略 |
| 维护成本 | ❌ 受制于人 | ✅ 自主迭代 |
| 信任基础 | ❌ 第三方作者 | ✅ 满意解研究所 |

## 版本历史

- **v1.0.0** (2026-03-14): 初始版本，支持主流格式，基础安全策略

## 未来迭代

- [ ] 压缩功能（创建压缩包）
- [ ] 密码保护 ZIP 支持（合法场景）
- [ ] 增量解压（只解压变更文件）
- [ ] 云存储集成（可选，本地优先）
