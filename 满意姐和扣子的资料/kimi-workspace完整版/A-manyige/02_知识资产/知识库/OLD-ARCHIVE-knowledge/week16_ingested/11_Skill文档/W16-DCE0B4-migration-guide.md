---
# 知识元数据 (5标准化)
knowledge_id: W16-DCE0B4
title: 迁移指南
category: 11_Skill文档
source: skills/namespace-enforcement/docs/migration-guide.md
ingested_at: 2026-03-27 17:59:30
word_count: 3545
week: 16
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 迁移指南

> **知识ID**: W16-DCE0B4  
> **分类**: 11_Skill文档  
> **来源**: `skills/namespace-enforcement/docs/migration-guide.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 迁移指南

## 概述

本文档指导如何将现有文件迁移到新的命名规范。

## 迁移原则

### S6 认知谦逊

> **存量文件不强制迁移。**

这不是技术限制，而是有意识的决策：

1. **风险最小化**: 避免破坏现有引用和链接
2. **成本优化**: 不是所有文件都值得迁移
3. **渐进改进**: 逐步提升而非一次性颠覆

## 迁移策略

### 策略1: 新文件严格合规（必须）

所有新创建的文件**必须**符合命名规范。

```
# ✅ 正确 - 新文件
skill-new-feature.md
script-helper.py

# ❌ 错误 - 新文件使用旧命名
NewFeature.md
helper_script.py
```

### 策略2: 按需迁移（推荐）

当你需要修改一个存量文件时，顺便将其重命名。

```
# 场景: 需要更新 OldFeature.md

步骤1: 重命名文件
OldFeature.md → skill-old-feature.md

步骤2: 更新内容
步骤3: 更新引用该文件的其他文档
```

### 策略3: 批量迁移（谨慎）

适用于目录结构混乱、需要整体重构的场景。

**步骤:**

1. 使用 `--dry-run` 预览变更
2. 备份重要文件
3. 分批次执行迁移
4. 更新所有相关引用

```bash
# 1. 预览
python3 scripts/namespace-auto-fix.py -s skills/old-skill --dry-run

# 2. 备份
cp -r skills/old-skill skills/old-skill-backup-$(date +%Y%m%d)

# 3. 分批迁移（每次5-10个文件）
python3 scripts/namespace-auto-fix.py -s skills/old-skill --apply --yes

# 4. 检查引用
grep -r "old-skill" . --include="*.md" --include="*.py"
```

## 迁移优先级

### P0: 立即迁移

- 即将被修改的文件
- 被频繁引用的文件
- 名称冲突风险高的文件

### P1: 近期迁移

- 活跃度高的目录
- 新成员可能接触的文件
- 自动化工具生成的文件

### P2: 择机迁移

- 很少访问的旧文档
- 归档性质的文件
- 即将废弃的功能相关文件

### P3: 不迁移

- 第三方代码/库
- 外部引用的资源
- 明确标记为"遗留"的文件

## 迁移检查清单

迁移前：
- [ ] 确定迁移范围
- [ ] 备份重要文件
- [ ] 预览变更 (`--dry-run`)
- [ ] 通知团队成员

迁移中：
- [ ] 小批量执行
- [ ] 验证每个变更
- [ ] 记录变更日志

迁移后：
- [ ] 更新内部引用
- [ ] 运行测试确保功能正常
- [ ] 通知团队成员变更完成
- [ ] 更新相关文档

## 常见场景

### 场景1: 技能文档迁移

```bash
# 旧命名
daily-report/              # 目录名正确
  DailyReport.md           # ❌ 需要修复
  helper.py                # ❌ 需要添加前缀

# 迁移后
daily-report/
  skill-daily-report.md    # ✅ 添加skill-前缀，全小写
  script-helper.py         # ✅ 添加script-前缀
```

### 场景2: 配置文件迁移

```bash
# 旧命名
config.yaml                # ❌ 缺少描述性名称
OldConfig.json             # ❌ 大写，不描述内容

# 迁移后
config-namespace-rules.yaml    # ✅
config-legacy-migration.json   # ✅
```

### 场景3: 测试文件迁移

```bash
# 旧命名
test-namespace.py          # ❌ 缺少被测对象信息
NamespaceTest.py           # ❌ 大写，无下划线

# 迁移后
test_namespace_checker.py      # ✅ 标准测试命名
test_conflict_scenarios.py     # ✅ 描述性名称
```

## 工具使用

### 检查当前状态

```bash
# 生成合规报告
python3 scripts/namespace-metrics.py -s ~/.openclaw/workspace --save

# 查看趋势
python3 scripts/namespace-metrics.py -s ~/.openclaw/workspace --trend
```

### 自动修复

```bash
# 预览修复
python3 scripts/namespace-auto-fix.py -s skills/my-skill --dry-run

# 应用修复
python3 scripts/namespace-auto-fix.py -s skills/my-skill --apply

# 包含存量文件（谨慎使用）
python3 scripts/namespace-auto-fix.py -s skills/my-skill --apply --include-legacy
```

### 生成报告

```bash
# Markdown报告
python3 scripts/namespace-metrics.py -s ~/.openclaw/workspace --markdown reports/compliance-report.md

# JSON报告
python3 scripts/namespace-metrics.py -s ~/.openclaw/workspace --json reports/compliance-report.json
```

## 故障排除

### 问题: 修复后链接断裂

**原因**: 其他文件引用了旧文件名

**解决**: 使用 grep 查找引用并更新

```bash
grep -r "old-filename" . --include="*.md" --include="*.py"
```

### 问题: 同名文件冲突

**原因**: 目标文件名已存在

**解决**: 手动处理冲突，添加限定符区分

```
skill-helper.md        # 已存在
skill-helper-v2.md     # 新文件使用版本号
```

### 问题: 版本历史丢失

**原因**: Git 将重识别视为删除+创建

**解决**: 使用 `git mv` 保留历史

```bash
git mv OldFile.md new-file.md
git commit -m "refactor: rename OldFile.md to new-file.md per naming convention"
```

## 附录: 迁移进度追踪

```markdown
## Namespace Migration Progress

### 已迁移 ✅
- [x] skills/namespace-enforcement/ (2025-03-27)
- [x] skills/daily-report/ (2025-03-28)

### 进行中 🔄
- [ ] skills/stock-assistant/
- [ ] skills/token-optimizer/

### 待迁移 ⏳
- [ ] skills/weather/
- [ ] skills/rss-ai-reader/

### 不迁移 🚫
- external/ (第三方代码)
- archive/ (归档文件)
```

---

**记住**: 迁移是手段，不是目的。目标是提升可维护性，而非追求完美合规。
