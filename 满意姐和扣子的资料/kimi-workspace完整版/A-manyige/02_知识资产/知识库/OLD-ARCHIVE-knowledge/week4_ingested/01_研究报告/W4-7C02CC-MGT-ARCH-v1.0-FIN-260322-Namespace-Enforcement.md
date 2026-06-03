---
# 知识元数据 (5标准化)
knowledge_id: W4-7C02CC
title: 命名空间强制化协议 V1.0
category: 01_研究报告
source: docs/MGT-ARCH-v1.0-FIN-260322-Namespace-Enforcement.md
ingested_at: 2026-03-27 17:59:30
word_count: 4452
week: 4
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 命名空间强制化协议 V1.0

> **知识ID**: W4-7C02CC  
> **分类**: 01_研究报告  
> **来源**: `docs/MGT-ARCH-v1.0-FIN-260322-Namespace-Enforcement.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 命名空间强制化协议 V1.0

> **协议性质**: 强制执行标准  
> **生效时间**: 2026-03-22  
> **适用范围**: 所有新文件 + 存量文件逐步迁移

---

## 一、命名空间格式（强制）

```
[ProjectCode]-[Type]-[Version]-[Status]-[Date]-[Description]
```

### 1.1 ProjectCode（项目代码）

| 代码 | 项目名称 | 说明 |
|------|----------|------|
| NGT | Negentropy Claw | 数字生命体构建 |
| WLU | 五路图腾 | 专家体系与部落符号 |
| PHX | 凤凰涅槃 | 系统重构与升级 |
| SKL | Skill体系 | 所有Skill相关 |
| DR | 灾备系统 | 备份与恢复 |
| MGT | 管理机制 | Token/质量/承诺等 |

### 1.2 Type（类型）

| 代码 | 类型 | 示例 |
|------|------|------|
| ARCH | 架构文档 | 系统设计、协议定义 |
| IMPL | 实施方案 | 执行计划、操作手册 |
| RSCH | 研究报告 | 深度研究、分析报告 |
| SKILL | Skill文档 | SKILL.md及配套文件 |
| RPT | 报告 | 周报、日报、复盘 |
| CFG | 配置 | 配置文件、脚本 |

### 1.3 Version（版本）

格式: `Major.Minor`
- Major: 重大变更 +1
- Minor: 小修改 +0.1

示例: `v1.0`, `v1.1`, `v2.0`

### 1.4 Status（状态）

| 代码 | 状态 | 说明 |
|------|------|------|
| WIP | 进行中 | Work In Progress |
| FIN | 已完成 | Final |
| REV | 审核中 | Under Review |
| ARC | 已归档 | Archived |
| DEP | 已废弃 | Deprecated |

### 1.5 Date（日期）

格式: `YYMMDD`

示例: `260322` (2026-03-22)

### 1.6 Description（描述）

- 简短描述文件内容
- 使用英文或拼音
- 单词间用连字符 `-` 连接

---

## 二、应用示例

### 正确命名

```
NGT-ARCH-v1.0-FIN-260322-Digital-Life-Protocol
SKL-SKILL-v2.1-WIP-260322-Token-Budget-Enforcer
WLU-RPT-v1.0-FIN-260322-Totem-System-Fusion
PHX-IMPL-v1.2-REV-260322-Knowledge-Graph-Setup
```

### 错误命名

```
❌ 数字生命体协议.md                # 无命名空间
❌ NGT-数字生命体.md                 # 中文描述
❌ NGT-ARCH-v1-FIN-2026-03-22.md     # 版本格式错误，日期格式错误
❌ ARCH-NGT-v1.0.md                  # 顺序错误
```

---

## 三、存量文件迁移计划

### 3.1 高优先级迁移（立即）

| 原文件 | 新命名空间 | 状态 |
|--------|------------|------|
| `NGT_CLAW_FUSION_DESIGN.md` | `NGT-ARCH-v1.0-FIN-260322-Fusion-Design` | ✅ 已重命名 |
| `TOTEM_SYSTEM_NGT_FUSION.md` | `WLU-ARCH-v1.0-FIN-260322-Totem-System` | ✅ 已重命名 |
| `LEAN_7_WASTES_TRACKING.md` | `NGT-IMPL-v1.0-FIN-260322-Lean-Waste-Track` | ✅ 已重命名 |

### 3.2 中优先级迁移（本周）

| 原文件路径 | 目标命名空间 |
|------------|--------------|
| `docs/DISASTER_RECOVERY_V1.1.md` | `DR-ARCH-v1.1-FIN-260321-Disaster-Recovery` |
| `docs/SYMBIOTIC_CONTRACT.md` | `MGT-ARCH-v1.0-FIN-260320-Symbiotic-Contract` |
| `docs/TEN_IRON_RULES.md` | `MGT-ARCH-v1.0-FIN-260320-Ten-Iron-Rules` |

### 3.3 低优先级迁移（Token恢复后）

- 所有 `skills/` 下的 SKILL.md
- 所有 `memory/` 下的日志文件
- 所有 `scripts/` 下的脚本文件

---

## 四、强制执行规则

### 4.1 创建新文件时必须

```yaml
creation_checklist:
  - "确认 ProjectCode 存在"
  - "选择正确的 Type"
  - "版本从 v1.0 开始"
  - "状态设为 WIP（完成后改 FIN）"
  - "日期使用 YYMMDD"
  - "描述简洁明了"
  - "在 MEMORY.md 中添加索引"
```

### 4.2 Git提交时必须

```bash
# 提交信息格式
[ProjectCode]-[Type]: [简短描述]

# 示例
git commit -m "NGT-ARCH: Add digital life protocol v1.0"
git commit -m "SKL-SKILL: Update token budget enforcer v2.1"
```

### 4.3 文件头必须包含

```markdown
---
namespace: "[ProjectCode]-[Type]-[Version]-[Status]-[Date]-[Description]"
project: "[ProjectCode]"
type: "[Type]"
version: "[Version]"
status: "[Status]"
date: "[YYYY-MM-DD]"
description: "[Description]"
---
```

---

## 五、索引维护

### 5.1 MEMORY.md 索引格式

```markdown
## 命名空间索引

### NGT (Negentropy Claw)
| 命名空间 | 类型 | 版本 | 状态 | 路径 |
|----------|------|------|------|------|
| NGT-ARCH-v1.0-FIN-260322-Fusion-Design | ARCH | v1.0 | FIN | docs/NGT-ARCH-v1.0-FIN-260322-Fusion-Design.md |
| NGT-IMPL-v1.0-FIN-260322-Lean-Waste-Track | IMPL | v1.0 | FIN | docs/NGT-IMPL-v1.0-FIN-260322-Lean-Waste-Track.md |

### WLU (五路图腾)
| 命名空间 | 类型 | 版本 | 状态 | 路径 |
|----------|------|------|------|------|
| WLU-ARCH-v1.0-FIN-260322-Totem-System | ARCH | v1.0 | FIN | docs/WLU-ARCH-v1.0-FIN-260322-Totem-System.md |
```

### 5.2 自动化检查脚本

```python
#!/usr/bin/env python3
# scripts/namespace-check.py

def check_namespace_compliance():
    """检查命名空间合规性"""
    violations = []
    
    # 检查所有md文件
    for file in list_all_md_files():
        if not has_namespace_header(file):
            violations.append(f"{file}: 缺少命名空间头")
        
        if not in_memory_index(file):
            violations.append(f"{file}: 未在MEMORY.md中索引")
    
    return violations
```

---

## 六、7标准验收

### S1: 全局考虑
- ✅ 人: 用户创建文件时强制遵循
- ✅ 事: 文件创建→命名→索引完整流程
- ✅ 物: 所有项目代码、类型定义完整
- ✅ 环境: Token约束下渐进迁移
- ✅ 外部: 与Git提交规范集成
- ✅ 边界: 存量文件有迁移计划

### S2: 系统闭环
- ✅ 输入: 新文件创建
- ✅ 处理: 命名空间分配 + 索引更新
- ✅ 输出: 合规文件 + 索引记录
- ✅ 反馈: 不合规自动检测

### S3: 可观测输出
- ✅ 索引表格可视化
- ✅ 违规清单自动报告

### S4: 自动化集成 🔄
- ✅ Git提交规范（文档化）
- 🔄 自动化检查脚本（**已设计，待开发部署**）

### S5: 自我验证 🔄
- ✅ 创建检查清单（文档化）
- 🔄 索引完整性验证（**待自动化**）

### S6: 认知谦逊 ✅
- ✅ 存量文件不强制立即迁移
- ✅ 迁移计划分优先级

### S7: 对抗测试 🔄
- 🔄 故意违规命名测试（**待执行**）

**7标准达成度: 75%** (S4/S5/S7文档完成，实施待执行)

---

*命名空间强制化协议已生效*
