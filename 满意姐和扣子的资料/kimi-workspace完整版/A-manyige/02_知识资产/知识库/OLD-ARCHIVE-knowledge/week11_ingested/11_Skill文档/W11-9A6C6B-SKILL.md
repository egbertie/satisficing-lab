---
# 知识元数据 (5标准化)
knowledge_id: W11-9A6C6B
title: SKILL
category: 11_Skill文档
source: skills/.archive_management-rules/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 7471
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# SKILL

> **知识ID**: W11-9A6C6B  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_management-rules/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

---
name: management-rules
version: 2.0.0
description: |
  管理规则手册 - 沟通规则、任务管理、报告机制、记忆更新、安全规则：
  1. 全局考虑：覆盖人/事/物/环境/外部集成/边界情况
  2. 系统考虑：规则定义→执行→监督→改进完整闭环
  3. 迭代机制：PDCA循环，版本历史，反馈收集
  4. Skill化：标准SKILL.md格式，可安装可调用
  5. 自动化：自动合规检查+cron监控+报告生成
author: Satisficing Institute
tags:
  - management
  - rules
  - compliance
  - governance
requires:
  - model: "kimi-coding/k2p5"
  - local_tools: ["python3"]
---

# 管理规则手册 Skill V2.0.0

## S1: 全局考虑 (Global Coverage)

### 1.1 人 - 规则适用对象

| 角色 | 规则重点 | 权限 | 边界情况 |
|------|----------|------|----------|
| Director(人类) | 战略决策、规则制定 | 最高权限 | 规则豁免权 |
| Captain(AI) | 任务管理、资源协调 | 执行权 | 紧急情况处置 |
| Specialist(AI) | 专业执行、质量交付 | 操作权 | 专业判断优先 |
| Auditor(AI) | 合规检查、监督 | 审计权 | 强制阻断权 |
| 外部用户 | 服务使用 | 受限权限 | 请求权 |

### 1.2 事 - 五大规则体系

```yaml
rule_systems:
  communication_rules:
    description: "沟通规则"
    components:
      - 汇报层级: "按角色分级汇报"
      - 沟通准则: "清晰、及时、完整"
      - 响应时效: "P0立即，P1 1h，P2 4h，P3 24h"
    escalation: "超时自动升级"
    
  task_management:
    description: "任务管理"
    components:
      - 生命周期: "创建→分配→执行→检查→关闭"
      - 优先级: "P0/P1/P2/P3四级"
      - 截止日期: "必设，可调整"
    tracking: "全程跟踪"
    
  reporting_mechanism:
    description: "报告机制"
    components:
      - 晨报: "每日09:00"
      - 日报: "每日23:59"
      - 周报: "每周日"
      - 里程碑: "达成时"
    automation: "自动生成"
    
  memory_update:
    description: "记忆更新"
    components:
      - MEMORY.md: "长期记忆"
      - memory/YYYYMMDD.md: "每日日志"
      - 决策记录: "带[RULE]标签"
      - 截止日期: "同步记录"
    frequency: "每日更新"
    
  security_rules:
    description: "安全规则"
    components:
      - 权限分级: "按角色分配"
      - 敏感操作: "需二次确认"
      - 数据安全: "加密+备份"
    enforcement: "强制执行"
```

### 1.3 物 - 规则管理资源

| 资源类型 | 管理规则 | 监控 | 边界处理 |
|----------|----------|------|----------|
| 规则文档 | 版本控制 | 变更审计 | 冲突检测 |
| 合规数据 | 定期采集 | 实时分析 | 缺失告警 |
| 报告模板 | 标准化 | 格式检查 | 自动修正 |
| 记忆文件 | 完整性 | 更新频率 | 自动提醒 |

### 1.4 环境 - 规则运行上下文

| 环境因素 | 规则调整 | 验证 |
|----------|----------|------|
| 紧急程度 | P0简化流程 | 事后审计 |
| 时间约束 | 截止临近加速 | 质量检查 |
| 资源可用 | 资源不足降级 | 影响评估 |
| 外部变化 | 合规要求更新 | 审查 |

### 1.5 外部集成

```yaml
integrations:
  role_federation:
    type: 角色管理
    data_flow: "规则 → 角色权限"
    action: "角色行为约束"
  
  quality_gate_system:
    type: 合规检查
    data_flow: "执行数据 → 合规审计"
    action: "违规行为标记"
  
  worry_list_manager:
    type: 风险监控
    data_flow: "规则违反 → 担忧清单"
    action: "合规风险预警"
  
  feishu_messaging:
    type: 通知推送
    data_flow: "规则提醒 → 消息通知"
    action: "定时规则提醒"
  
  calendar_system:
    type: 截止管理
    data_flow: "日历事件 → 规则触发"
    action: "截止前规则检查"
```

### 1.6 边界情况处理

| 边界场景 | 检测 | 处理 |
|----------|------|------|
| 规则冲突 | 一致性检查 | 优先级仲裁 |
| 规则缺失 | 场景未覆盖 | 标记待补充 |
| 例外请求 | 人工申请 | 审计追踪+授权 |
| 规则过时 | 定期审查 | 更新标记 |
| 执行异常 | 监控告警 | 人工介入 |

---

## S2: 系统考虑 (Systematic)

### 2.1 规则管理闭环

```
规则定义 → 发布生效 → 执行监控 → 合规检查 → {合规?}
  ├─ 是 → 效果评估 → 持续运行
  └─ 否 → 违规处理 → 整改跟踪
       ↓
  规则优化 ← 反馈收集 ← 定期复盘
```

### 2.2 输入处理

| 输入类型 | 验证 | 转换 |
|----------|------|------|
| 规则变更 | 权限+格式 | 版本更新 |
| 执行数据 | 完整性 | 合规指标 |
| 反馈建议 | 来源验证 | 改进项 |
| 外部要求 | 影响评估 | 规则补充 |

### 2.3 规则引擎

```yaml
rule_engine:
  parser:
    - 规则语法解析
    - 依赖关系分析
    - 冲突检测
  
  validator:
    - 权限验证
    - 条件匹配
    - 动作执行
  
  monitor:
    - 执行跟踪
    - 违规检测
    - 效果测量
```

### 2.4 输出规范

| 输出类型 | 格式 | 内容 |
|----------|------|------|
| 规则文档 | Markdown | 结构化规则 |
| 合规报告 | 表格 | 合规率+问题列表 |
| 违规通知 | 消息 | 违规详情+整改要求 |
| 改进建议 | 列表 | 优先级+建议 |

### 2.5 反馈闭环

| 反馈 | 来源 | 应用 |
|------|------|------|
| 执行问题 | 角色反馈 | 规则细化 |
| 合规数据 | 自动检查 | 规则效果评估 |
| 改进建议 | 复盘会议 | 规则更新 |
| 外部要求 | 合规审计 | 规则补充 |

### 2.6 故障处理

| 故障 | 检测 | 响应 |
|------|------|------|
| 规则解析错误 | 语法检查 | 回滚+告警 |
| 规则冲突 | 一致性检查 | 禁用冲突规则 |
| 监控失效 | 心跳检测 | 降级模式 |
| 数据丢失 | 校验失败 | 备份恢复 |

---

## S3: 迭代机制 (Iterative)

### 3.1 PDCA循环

```yaml
Plan(计划):
  - 每月制定规则优化计划
  5. automation
  - 规划规则更新

Do(执行):
  - 执行规则监控
  - 收集合规数据
  - 记录执行情况

Check(检查):
  - 统计合规率
  - 分析违规模式
  - 评估规则效果

Act(改进):
  - 更新规则内容
  - 优化执行流程
  - 完善监控指标
```

### 3.2 版本历史

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| v2.0.0 | 2026-03-21 | 5标准全覆盖 | 满意解研究所 |
| v1.1.0 | 2026-03-18 | 增加安全规则 | 满意解研究所 |
| v1.0.0 | 2026-03-15 | 初始版本 | 满意解研究所 |

### 3.3 反馈收集

| 源 | 频率 | 用途 |
|----|------|------|
| 执行日志 | 实时 | 规则效果 |
| 合规检查 | 每日 | 违规统计 |
| 角色反馈 | 实时 | 规则改进 |
| 外部审计 | 每月 | 体系完善 |

### 3.4 优化触发

| 指标 | 阈值 | 动作 |
|------|------|------|
| 合规率 | <90% | 规则重审 |
| 违规频率 | >5/周 | 专项改进 |
| 规则冲突 | >0 | 立即解决 |
| 用户投诉 | >2/月 | 规则优化 |

---

## S4: Skill化 (Skill-ified)

### 4.1 目录结构

```
management-rules/
├── SKILL.md                    # 本文件
├── _meta.json                  # 元数据
├── scripts/
│   ├── rules_runner.py         # 主运行脚本
│   ├── parser.py               # 规则解析
│   ├── validator.py            # 合规验证
│   ├── monitor.py              # 执行监控
│   └── reporter.py             # 报告生成
├── config/
│   ├── rules.yaml              # 规则定义
│   └── thresholds.yaml         # 阈值配置
├── rules/
│   ├── communication.md        # 沟通规则
│   ├── task_management.md      # 任务管理
│   ├── reporting.md            # 报告机制
│   ├── memory.md               # 记忆更新
│   └── security.md             # 安全规则
└── logs/
    └── rules.log               # 运行日志
```

### 4.2 标准化接口

```python
class ManagementRules:
    
    def query_rule(self, rule_type: str, query: str) -> Rule:
        """查询规则"""
        pass
    
    def check_compliance(self, action: str, context: dict) -> ComplianceResult:
        """检查合规性"""
        pass
    
    def update_rule(self, rule_id: str, content: str) -> None:
        """更新规则"""
        pass
    
    def generate_report(self, period: str) -> Report:
        """生成合规报告"""
        pass
    
    def get_template(self, template_type: str) -> str:
        """获取报告模板"""
        pass
```

### 4.3 调用方式

```bash
# 安装Skill
openclaw skill install management-rules

# 查询规则
openclaw skill run management-rules query --type communication

# 检查合规
openclaw skill run management-rules check --action "task_close"

# 生成报告
openclaw skill run management-rules report --period daily

# 获取模板
openclaw skill run management-rules template --type morning
```

---

## S5: 自动化 (Automation)

### 5.1 Cron定时任务

```json
{
  "jobs": [
    {
      "name": "management-rules-compliance-check",
      "schedule": "0 */6 * * *",
      "command": "cd /root/.openclaw/workspace/skills/management-rules && python3 scripts/rules_runner.py check",
      "description": "每6小时执行合规检查"
    },
    {
      "name": "management-rules-daily-report",
      "schedule": "59 23 * * *",
      "command": "cd /root/.openclaw/workspace/skills/management-rules && python3 scripts/rules_runner.py report",
      "description": "每日23:59生成合规日报"
    },
    {
      "name": "management-rules-weekly-review",
      "schedule": "47 22 * * 0",
      "command": "cd /root/.openclaw/workspace/skills/management-rules && python3 scripts/rules_runner.py weekly",
      "description": "每周日22:47生成规则周回顾"
    }
  ]
}
```

### 5.2 自动化脚本

| 脚本 | 功能 | 触发 |
|------|------|------|
| `rules_runner.py` | 主控 | cron/手动 |
| `parser.py` | 规则解析 | 加载时 |
| `validator.py` | 合规验证 | 执行时 |
| `monitor.py` | 执行监控 | 持续 |
| `reporter.py` | 报告 | 定时 |

### 5.3 自动监控

| 监控项 | 阈值 | 告警 |
|--------|------|------|
| 合规率 | <95% | 质量告警 |
| 违规数 | >3/天 | 紧急通知 |
| 规则冲突 | >0 | 立即告警 |
| 更新延迟 | >24h | 提醒 |

---

## 附录：命令参考

| 命令 | 功能 | 示例 |
|------|------|------|
| `query [type]` | 查询规则 | `query communication` |
| `check [action]` | 检查合规 | `check task_close` |
| `report [period]` | 生成报告 | `report daily` |
| `template [type]` | 获取模板 | `template morning` |

---

*版本: v2.0.0*  
*更新日期: 2026-03-21*  
*作者: 满意解研究所*
