# 已归档旧版本目录

> **位置**: `/root/.openclaw/workspace/archive/deprecated/`  
> **归档时间**: 2026-04-04  
> **归档原因**: 版本升级与代码治理，避免旧版本与新版本共存造成混淆

---

## 一、已归档文件清单

| 旧版本文件 | 原始功能 | 替代版本 | 归档原因 |
|------------|----------|----------|----------|
| `skill_conditioning.py` | Skill条件反射训练 | `skill_conditioning_v2.py` | 重构为基于组件库的版本 |
| `decision_solidifier.py` | 决策即时固化 | `decision_solidifier_v2.py` | 重构为基于组件库的版本 |
| `unified_defense_system.py` | 统一防御系统V1.0 | `unified_defense_system_v4.py` | 已被V2/V3/V4迭代替代 |
| `unified_defense_system_v2.py` | 统一防御系统V2.0 | `unified_defense_system_v4.py` | 已被V3/V4迭代替代 |
| `unified_defense_system_v3.py` | 统一防御系统V3.0 | `unified_defense_system_v4.py` | 已被V4迭代替代 |
| `totem_quantifier.py` | 五路图腾量化评分 | `totem_multi_agent_council.py` | 功能被审议机制替代 |

---

## 二、为什么不直接删除

1. **灾备需要**: 这些代码是历史迭代的真实交付物，保留可快速回滚
2. **审计需要**: 蓝军审计和基线检查可能需要追溯历史版本
3. **知识连续性**: 部分文档可能仍有历史参考价值

---

## 三、使用规则

**禁止事项**:
- ❌ 不要再引用或导入这些旧版本文件
- ❌ 不要再在文档中推荐这些旧版本的运行命令
- ❌ 不要将其移回 workspace 根目录

**例外情况**:
- 只有在做历史对比分析或灾难恢复时，经蓝军审计同意后方可临时读取

---

## 四、文档引用清理状态

| 文档 | 清理状态 | 更新时间 |
|------|----------|----------|
| `docs/Skill盘点与记忆系统-技术迭代条件记录.md` | ✅ 已更新 | 2026-04-04 |
| `docs/Skill盘点与记忆系统-技术迭代条件记录-V2.0.md` | ✅ 已更新 | 2026-04-04 |

---

*归档完成 | 满意姐 | 2026-04-04*
