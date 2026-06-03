---
# 知识元数据 (5标准化)
knowledge_id: W13-1DB64B
title: Skill分级策略标准Skill V2.0
category: 11_Skill文档
source: skills/.archive_skill-classification/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1561
week: 13
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Skill分级策略标准Skill V2.0

> **知识ID**: W13-1DB64B  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_skill-classification/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Skill分级策略标准Skill V2.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V2.0 | 更新: 2026-03-20 | 分级: 核心/扩展/实验

---

## 一、全局考虑（六层+三级Skill）

### Skill分级 × 六层矩阵

| 分级 | 标准 | L0身份 | L1项目 | L2系统 | L3外部 | L4交付 | L5归档 |
|------|------|--------|--------|--------|--------|--------|--------|
| **核心** | 5标准+高频 | 核心能力 | 高频使用 | 系统必备 | 稳定集成 | 高质量 | 标准归档 |
| **扩展** | 5标准+中频 | 扩展能力 | 按需使用 | 可选安装 | 外部集成 | 可用 | 归档 |
| **实验** | 部分标准 | 实验能力 | 测试使用 | 不稳定 | 不集成 | 开发中 | 草稿 |

---

## 二、系统考虑（分级→管理→升级→淘汰闭环）

### 2.1 分级标准

| 维度 | 核心 | 扩展 | 实验 |
|------|------|------|------|
| 5标准 | 全部满足 | 全部满足 | 部分满足 |
| 使用频率 | 每日+ | 每周+ | 按需 |
| 稳定性 | 生产级 | 可用 | 测试 |
| 支持级别 | 全力维护 | 尽力维护 | 无承诺 |

---

## 三、迭代机制（每月分级评审）

---

## 四、Skill化（自动分级）

```python
def auto_classify_skill(skill_path):
    """自动评估Skill分级"""
    score = {
        "global_coverage": check_global_coverage(skill_path),
        "systematic": check_systematic(skill_path),
        "iterative": check_iterative(skill_path),
        "skillized": check_skillized(skill_path),
        "automated": check_automated(skill_path)
    }
    
    if all(score.values()):
        return "CORE"
    elif score["skillized"] and score["automated"]:
        return "EXTENSION"
    else:
        return "EXPERIMENTAL"
```

---

## 五、流程自动化（每月评审）

```json
{
  "job": {
    "name": "skill-classification-review",
    "schedule": "0 9 1 * *"
  }
}
```

---

## 六、质量门控

- [x] **全局**: 三级×六层
- [x] **系统**: 分级→管理→升级闭环
- [x] **迭代**: 每月评审
- [x] **Skill化**: 自动分级
- [x] **自动化**: 定期评审

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*