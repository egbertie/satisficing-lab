---
# 知识元数据 (5标准化)
knowledge_id: W8-D88BEE
title: 自动清理系统标准Skill V2.0
category: 11_Skill文档
source: skills/.archive_auto-cleanup-system/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 1235
week: 8
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 自动清理系统标准Skill V2.0

> **知识ID**: W8-D88BEE  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_auto-cleanup-system/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 自动清理系统标准Skill V2.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V2.0 | 更新: 2026-03-20 | 核心: 分周期自动清理

---

## 一、全局考虑（六层+三层清理）

| 清理类型 | 周期 | L0身份 | L1项目 | L2系统 | L3外部 | L4交付 | L5归档 |
|----------|------|--------|--------|--------|--------|--------|--------|
| **临时文件** | 7天 | 临时数据 | 临时产出 | 临时缓存 | 临时集成 | 临时交付 | 无需归档 |
| **日志归档** | 30天 | 操作日志 | 项目日志 | 系统日志 | 外部日志 | 交付日志 | 归档存储 |
| **备份转存** | 90天 | 身份备份 | 项目备份 | 系统备份 | 外部备份 | 交付备份 | 长期归档 |

---

## 二、系统考虑（扫描→判断→清理→验证闭环）

### 2.1 清理规则

```yaml
cleanup_rules:
  temp_files:
    age: "7 days"
    path: ["/tmp/", "*.tmp", "*.cache"]
    action: "delete"
    
  logs:
    age: "30 days"
    path: ["/var/log/", "logs/"]
    action: "archive"
    archive_path: "/backup/logs/"
    
  backups:
    age: "90 days"
    path: ["/backup/"]
    action: "transfer"
    transfer_path: "/longterm/backup/"
```

---

## 三、迭代机制（每周清理日志检查）

---

## 四、Skill化（自动清理）

```python
def auto_cleanup():
    """自动清理主函数"""
    cleanup_temp_files(age_days=7)
    archive_logs(age_days=30)
    transfer_backups(age_days=90)
```

---

## 五、流程自动化（每日凌晨执行）

```json
{
  "job": {
    "name": "auto-cleanup",
    "schedule": "0 3 * * *"
  }
}
```

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*