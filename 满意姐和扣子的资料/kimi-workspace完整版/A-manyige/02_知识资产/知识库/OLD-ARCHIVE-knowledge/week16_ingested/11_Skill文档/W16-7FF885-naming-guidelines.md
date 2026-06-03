---
# 知识元数据 (5标准化)
knowledge_id: W16-7FF885
title: 命名规范指南
category: 11_Skill文档
source: skills/namespace-enforcement/docs/naming-guidelines.md
ingested_at: 2026-03-27 17:59:30
word_count: 4312
week: 16
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 命名规范指南

> **知识ID**: W16-7FF885  
> **分类**: 11_Skill文档  
> **来源**: `skills/namespace-enforcement/docs/naming-guidelines.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 命名规范指南

## 概述

本文档定义了 Workspace 文件命名规范，旨在提升文件检索效率、可维护性和协作体验。

## 核心原则

### 1. 机器优先 (Machine-First)

文件名首先应该是机器友好的，其次才是人类可读。

**为什么？**
- Shell 命令中的自动补全
- 脚本中的模式匹配
- 版本控制系统的兼容性

### 2. 一致性优先 (Consistency-First)

统一的命名风格比"最优"的单个文件名更重要。

**为什么？**
- 降低认知负担
- 支持批量操作
- 便于自动化处理

### 3. 描述性优先 (Descriptive-First)

文件名应该清晰表达内容，而非使用缩写或代号。

**为什么？**
- 减少打开文件确认内容的需要
- 支持模糊搜索
- 便于新成员理解

## 命名格式规范

### 标准格式

```
{type}-{name}(-{qualifier}).{ext}
```

### 组件说明

| 组件 | 必需 | 格式 | 示例 |
|------|------|------|------|
| type | 是 | 小写字母 | `skill`, `doc`, `script`, `config` |
| name | 是 | 小写+连字符 | `namespace-enforcement`, `daily-report` |
| qualifier | 否 | 见下文 | `v2`, `20250327`, `draft` |
| ext | 是 | 标准扩展名 | `.md`, `.py`, `.json` |

### 类型标识 (Type)

| 类型 | 用途 | 适用目录 |
|------|------|----------|
| `skill` | 技能文档 | `skills/` |
| `doc` | 一般文档 | `docs/`, `skills/*/docs/` |
| `script` | 可执行脚本 | `scripts/`, `skills/*/scripts/` |
| `config` | 配置文件 | `config/`, 任意目录 |
| `test` | 测试文件 | `tests/`, `skills/*/tests/` |
| `report` | 报告文件 | `reports/` |

### 限定符 (Qualifier)

#### 版本号格式

```
v{major}           # v1, v2, v3
v{major}.{minor}   # v1.0, v2.5
```

**不要：**
- `version-1`, `ver1`, `V1` — 不统一
- `final`, `latest`, `new` — 时间相关，会过期

#### 日期格式

```
YYYYMMDD           # 20250327
```

**不要：**
- `2025-03-27` — 文件名中避免多余连字符
- `Mar-27-2025` — 包含大写字母和符号

#### 状态标识

```
draft              # 草稿
beta               # 测试版
rc                 # 候选版
```

## 字符规范

### 允许字符

- 小写字母: `a-z`
- 数字: `0-9`
- 连字符: `-` (单词分隔)
- 下划线: `_` (仅在测试文件名中使用)
- 点: `.` (扩展名分隔)

### 禁止字符

所有以下字符都**禁止**出现在文件名中：

```
! @ # $ % ^ & * ( ) = + [ ] { } | ; : ' " < > ? / \ 
```

以及**空格**。

### 大小写规范

**全部小写**。没有任何例外。

```
# ✅ 正确
skill-namespace-enforcement.md
namespace-checker.py

# ❌ 错误
Skill-Namespace-Enforcement.md
NamespaceChecker.py
namespaceChecker.py
NAMESPACE-ENFORCEMENT.md
```

### 连字符使用

使用连字符 `-` 分隔单词：

```
# ✅ 正确
daily-report.md
namespace-enforcement
pre-market-sentiment

# ❌ 错误
daily_report.md     # 下划线
dailyReport.md      # 驼峰
daily report.md     # 空格
```

## 长度规范

- **最小长度**: 3 字符（不含扩展名）
- **最大长度**: 100 字符（含扩展名）
- **建议长度**: 20-50 字符

```
# ✅ 正确
skill-namespace-enforcement.md          # 30字符
script-auto-check-on-create.py          # 28字符

# ❌ 错误
a.md                                    # 太短
this-is-a-very-long-file-name-that-exceeds-the-recommended-length-and-should-be-shortened.md  # 太长
```

## 目录特定规范

### skills/ 目录

```
skill-{name}.md                    # 主技能文档
skill-{name}-{qualifier}.md        # 版本/限定
```

### scripts/ 目录

```
{name}.py                          # Python脚本
{name}.sh                          # Shell脚本
{name}.js                          # JavaScript脚本
test_{name}.py                     # Python测试
```

### docs/ 目录

```
doc-{topic}.md                     # 一般文档
guide-{topic}.md                   # 指南文档
report-{date}.md                   # 报告（带日期）
```

## 常见错误

### 错误1: 使用驼峰命名

```
# ❌ 错误
namespaceChecker.py
dailyReport.md
preMarketSentiment.py

# ✅ 正确
namespace-checker.py
daily-report.md
pre-market-sentiment.py
```

### 错误2: 使用空格

```
# ❌ 错误
daily report.md
namespace enforcement.md

# ✅ 正确
daily-report.md
namespace-enforcement.md
```

### 错误3: 缺少类型前缀

```
# ❌ 错误 (在skills/目录下)
enforcement.md
namespace-rules.md

# ✅ 正确
skill-enforcement.md
skill-namespace-rules.md
```

### 错误4: 版本号格式混乱

```
# ❌ 错误
skill-v1.md
skill-1.0.md
skill-final.md
skill-latest.md

# ✅ 建议
skill-v1.md
skill-v2.md
skill-v2-draft.md
```

### 错误5: 特殊字符

```
# ❌ 错误
skill@namespace.md
report#2025.md
config$test.json

# ✅ 正确
skill-namespace.md
report-20250327.md
config-test.json
```

## 自动化检查

使用命名空间检查器自动验证：

```bash
# 检查单个文件
python3 scripts/namespace-checker.py -f my-file.md

# 检查整个目录
python3 scripts/namespace-checker.py -s ~/.openclaw/workspace

# 生成报告
python3 scripts/namespace-checker.py -s ~/.openclaw/workspace --report

# 预览修复
python3 scripts/namespace-auto-fix.py -s ~/.openclaw/workspace --dry-run

# 应用修复
python3 scripts/namespace-auto-fix.py -s ~/.openclaw/workspace --apply
```

## S6 认知谦逊: 存量文件处理

### 原则

存量文件（创建时间早于规则实施的文件）**不强制迁移**。

### 理由

1. **避免破坏现有链接**: 其他文档可能引用了这些文件
2. **减少变更噪音**: 大量重命名会污染版本历史
3. **尊重历史**: 文件创建时的上下文可能不同

### 建议策略

- **渐进式迁移**: 每周处理 5-10 个存量文件
- **按需迁移**: 当需要修改某个存量文件时，顺便重命名
- **新文件必须合规**: 严格执行，防止问题累积

## 参考

- [Namespace Enforcement Skill](../SKILL.md)
- [迁移指南](migration-guide.md)
