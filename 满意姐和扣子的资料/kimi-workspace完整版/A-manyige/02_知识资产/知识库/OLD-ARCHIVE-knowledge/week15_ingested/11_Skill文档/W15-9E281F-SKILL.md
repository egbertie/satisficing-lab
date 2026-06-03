---
# 知识元数据 (5标准化)
knowledge_id: W15-9E281F
title: citation-consistency-auto-fix Skill V5标准版本
category: 11_Skill文档
source: skills/citation-consistency-auto-fix/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1713
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# citation-consistency-auto-fix Skill V5标准版本

> **知识ID**: W15-9E281F  
> **分类**: 11_Skill文档  
> **来源**: `skills/citation-consistency-auto-fix/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# citation-consistency-auto-fix Skill V5标准版本

## S1: 全局考虑

### 输入
- 工作区文件路径
- 引用模式（内部链接、外部URL）
- 修复策略（自动/人工确认）

### 覆盖维度
| 维度 | 考虑内容 |
|------|----------|
| **人** | 开发者维护文档、用户查阅资料 |
| **事** | 扫描引用、检测失效、自动修复 |
| **物** | Markdown文件、内部链接、外部URL |
| **环境** | 本地文件系统、网络环境 |
| **外部集成** | 外部URL可用性检查 |
| **边界情况** | 循环引用、相对路径、URL临时失效 |

---

## S2: 系统考虑

### 处理流程
```
全量扫描 → 引用提取 → 有效性验证 → 失效标记 → 自动修复 → 报告生成
    ↑                                              ↓
    └──────────── 定时执行 ← 手动触发 ←────────────┘
```

### 故障处理
- **路径不存在**: 标记失效，尝试修复
- **URL超时**: 重试3次，仍失败标记待检查
- **权限不足**: 记录错误，跳过该文件

---

## S3: 输出规范

### 修复报告
```json
{
  "scan_time": "2026-03-22T09:00:00+08:00",
  "files_scanned": 100,
  "citations_found": 250,
  "broken_found": 10,
  "auto_fixed": 8,
  "need_manual": 2,
  "fixes": [
    {
      "file": "docs/guide.md",
      "old_link": "../old/path.md",
      "new_link": "../new/path.md",
      "status": "fixed"
    }
  ]
}
```

---

## S4: 自动化集成

### 自动修复策略
1. **内部链接**: 尝试查找同名文件，自动修正路径
2. **相对路径**: 基于文件位置重新计算
3. **外部URL**: 标记待人工检查（不自动修改）
4. **重复引用**: 合并重复项

### 执行频率
- 每周六10:07自动执行
- 支持手动触发
- P1问题立即通知

---

## S5: 自我验证

### 质量指标
- 扫描覆盖率: 100%
- 误修复率: <1%
- 修复准确率: >95%

### 测试用例
1. 正常引用 → 验证通过
2. 路径变更 → 自动修复
3. 文件删除 → 标记失效
4. 循环引用 → 检测并报告

---

## S6: 认知谦逊

### 局限
- 无法判断内容相关性（只能检查存在性）
- 外部URL可用性可能临时变化
- 复杂相对路径可能计算错误
- 不处理内容变更导致的语义失效

---

## S7: 对抗测试

| 场景 | 预期行为 |
|------|----------|
| 大量文件（>1000） | 分批处理，避免内存溢出 |
| 循环引用 | 检测并中断，报告循环链 |
| 权限拒绝 | 跳过该文件，继续扫描 |
| 磁盘空间不足 | 提前检查，失败报错 |
| 并发修改 | 文件锁或重试机制 |

---

## 使用说明

```bash
# 自动扫描并修复
python3 scripts/citation_fixer.py --auto-fix

# 仅扫描，不修复
python3 scripts/citation_fixer.py --scan-only

# 生成报告
python3 scripts/citation_fixer.py --report
```
