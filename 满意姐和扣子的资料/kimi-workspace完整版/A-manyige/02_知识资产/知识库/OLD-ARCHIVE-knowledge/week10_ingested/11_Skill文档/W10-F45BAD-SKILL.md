---
# 知识元数据 (5标准化)
knowledge_id: W10-F45BAD
title: 文件完整性检查标准Skill V2.0
category: 11_Skill文档
source: skills/.archive_file-integrity-checker/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 3344
week: 10
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 文件完整性检查标准Skill V2.0

> **知识ID**: W10-F45BAD  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_file-integrity-checker/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 文件完整性检查标准Skill V2.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V2.0 | 更新: 2026-03-20 | 核心: 四维检查法 | 整合: 遗忘任务扫描

---

## 一、全局考虑（六层+四维检查）

### 四维检查 × 六层矩阵

| 检查维度 | L0身份 | L1项目 | L2系统 | L3外部 | L4交付 | L5归档 |
|----------|--------|--------|--------|--------|--------|--------|
| **结构完整性** | 身份文件 | 任务清单 | 配置文件 | 集成配置 | 交付结构 | 归档结构 |
| **内容时效性** | 身份信息 | 任务状态 | 系统版本 | 外部状态 | 交付版本 | 归档时效 |
| **引用一致性** | 身份引用 | 任务引用 | 配置引用 | 外部链接 | 交付引用 | 归档链接 |
| **安全合规性** | 隐私保护 | 敏感信息 | 访问控制 | 传输安全 | 交付安全 | 归档安全 |

---

## 二、系统考虑（扫描→检测→修复→验证闭环）

### 2.1 四维检查法

```yaml
four_dimensional_check:
  dimension_1_structure:
    name: "结构完整性"
    check_items:
      - "核心文件是否存在"
      - "目录结构是否符合规范"
      - "必要文件是否缺失"
    schedule: "09:07 每日"
    
  dimension_2_freshness:
    name: "内容时效性"
    check_items:
      - "文件是否过期(30天+)"
      - "状态信息是否最新"
      - "版本是否一致"
    schedule: "09:17 每日"
    
  dimension_3_references:
    name: "引用一致性"
    check_items:
      - "内部链接是否有效"
      - "外部链接是否可访问"
      - "引用内容是否最新"
    schedule: "10:07 每周六"
    
  dimension_4_security:
    name: "安全合规性"
    check_items:
      - "敏感信息是否泄露"
      - "权限设置是否正确"
      - "备份是否完整"
    schedule: "14:00 每日"
```

### 2.2 遗忘任务扫描（整合）

| 扫描项 | 检查范围 | 触发条件 | 处理动作 |
|--------|----------|----------|----------|
| 逾期任务 | TASK_MASTER | 截止日期已过 | 立即报告+补救 |
| 无截止日期任务 | 所有任务 | 发现即标记 | 要求补充期限 |
| 被遗忘承诺 | 对话记录 | 承诺未兑现 | 提醒+跟踪 |
| 僵尸任务 | 长期无进展 | 30天无更新 | 标记+清理 |

---

## 三、迭代机制（每日扫描+每周深度检查）

### 3.1 检查频率矩阵

| 检查类型 | 频率 | 深度 | 产出 |
|----------|------|------|------|
| 结构检查 | 每日 | 快速 | 缺失列表 |
| 时效检查 | 每日 | 快速 | 过期列表 |
| 引用检查 | 每周 | 深度 | 失效报告 |
| 安全检查 | 每日 | 快速 | 安全状态 |
| 遗忘扫描 | 每日 | 深度 | 遗忘清单 |

---

## 四、Skill化（可执行）

### 4.1 四维检查代码

```python
def file_integrity_check():
    """
    文件完整性检查
    """
    results = {
        "structure": check_structure_integrity(),
        "freshness": check_content_freshness(),
        "references": check_reference_consistency(),
        "security": check_security_compliance(),
        "forgotten": scan_forgotten_tasks()
    }
    
    # 生成检查报告
    generate_integrity_report(results)
    
    # 处理发现的问题
    for issue in results.issues:
        if issue.severity == "critical":
            notify_immediately(issue)
        elif issue.severity == "high":
            add_to_remediation_queue(issue)

def scan_forgotten_tasks():
    """遗忘任务扫描"""
    forgotten = []
    
    # 扫描逾期任务
    overdue = scan_overdue_tasks()
    forgotten.extend(overdue)
    
    # 扫描无截止日期任务
    no_deadline = scan_no_deadline_tasks()
    forgotten.extend(no_deadline)
    
    # 扫描被遗忘承诺
    promises = scan_unfulfilled_promises()
    forgotten.extend(promises)
    
    return forgotten
```

---

## 五、流程自动化（Cron+脚本）

### 5.1 定时任务

```json
{
  "jobs": [
    {"name": "structure-check", "schedule": "7 9 * * *", "enabled": true},
    {"name": "freshness-check", "schedule": "17 9 * * *", "enabled": true},
    {"name": "reference-check", "schedule": "7 10 * * 6", "enabled": true},
    {"name": "security-check", "schedule": "0 14 * * *", "enabled": true},
    {"name": "forgotten-scan", "schedule": "0 22 * * *", "enabled": true}
  ]
}
```

---

## 六、质量门控

- [x] **全局**: 四维×六层全覆盖
- [x] **系统**: 扫描→检测→修复→验证闭环
- [x] **迭代**: 每日扫描+每周深度检查
- [x] **Skill化**: 自动扫描+问题处理
- [x] **自动化**: 5个定时任务

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*

*整合: 文件完整性检查 + 遗忘任务扫描*