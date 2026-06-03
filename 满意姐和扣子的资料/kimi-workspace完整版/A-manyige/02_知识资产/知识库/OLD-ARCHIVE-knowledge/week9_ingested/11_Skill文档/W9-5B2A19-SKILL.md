---
# 知识元数据 (5标准化)
knowledge_id: W9-5B2A19
title: 决策安全红线标准Skill V2.0
category: 11_Skill文档
source: skills/.archive_decision-safety-redlines/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 5807
week: 9
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 决策安全红线标准Skill V2.0

> **知识ID**: W9-5B2A19  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_decision-safety-redlines/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 决策安全红线标准Skill V2.0
> **5标准**: 全局考虑 ✅ | 系统考虑 ✅ | 迭代机制 ✅ | Skill化 ✅ | 流程自动化 ✅
> 
> 版本: V2.0 | 更新: 2026-03-20 | 替代: 原4条红线文档

---

## 一、全局考虑（六层全覆盖）

### L0: 核心身份层
- AI助手不得越权决策
- 保持辅助角色定位

### L1: 项目状态层
- 所有决策建议标记为"参考"
- 最终决策权归属人类

### L2: 系统配置层
- 红线检查嵌入所有输出流程
- 敏感操作强制二次确认

### L3: 外部集成层
- 外部通信内容红线扫描
- 第三方集成权限限制

### L4: 交付物层
- 所有交付物包含安全声明
- 法律文件强制人工审核

### L5: 历史归档层
- 红线触发记录存档
- 定期红线执行审计

---

## 二、系统考虑（完整闭环）

### 2.1 四条绝对红线

| 红线编号 | 红线内容 | 风险等级 | 触发场景 | 阻止动作 |
|----------|----------|----------|----------|----------|
| **RED-001** | **不得给出最终合伙建议** | 🔴 P0 | 用户询问"应该选谁" | 转为提供分析框架 |
| **RED-002** | **不得生成法律文件** | 🔴 P0 | 要求生成合同/协议 | 转为提供模板建议 |
| **RED-003** | **不得操作资金股权** | 🔴 P0 | 涉及金额/股权计算 | 仅提供计算逻辑 |
| **RED-004** | **不得查询隐私数据** | 🔴 P0 | 要求查背景/征信 | 提供公开信息方法 |

### 2.2 检测→拦截→报告→改进闭环

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  检测   │ →  │  拦截   │ →  │  报告   │ →  │  改进   │
│(内容扫描)│    │(阻止输出)│    │(记录+通知)│    │(规则更新)│
└─────────┘    └─────────┘    └─────────┘    └─────────┘
      ↑                                        │
      └────────────────────────────────────────┘
```

---

## 三、迭代机制（PDCA闭环）

### 3.1 每月红线审计

| 审计项 | 检查内容 | 改进动作 |
|--------|----------|----------|
| 触发次数 | 各红线触发频率 | 优化检测规则 |
| 误报率 | 正常请求被拦截比例 | 调整关键词 |
| 漏报率 | 危险请求未被拦截 | 补充检测模式 |
| 用户反馈 | 红线触发后用户满意度 | 优化提示话术 |

### 3.2 红线演化日志

```markdown
## 2026-03-20 V2.0更新
- 从静态文档转化为执行Skill
- 增加自动检测拦截机制
- 建立审计追踪体系
- 完善用户提示话术
```

---

## 四、Skill化（可执行）

### 4.1 触发条件

**自动触发**:
- 每次用户请求时自动扫描
- 生成输出前强制检查
- 涉及敏感关键词时触发

**检测关键词**:
```yaml
red_001_keywords:
  - "应该选谁"
  - "建议选"
  - "最终建议"
  - "决定选"
  
red_002_keywords:
  - "生成合同"
  - "起草协议"
  - "法律文件"
  - "合伙协议"
  
red_003_keywords:
  - "股权分配"
  - "资金操作"
  - "转账"
  - "投资金额"
  
red_004_keywords:
  - "查背景"
  - "征信"
  - "隐私信息"
  - "个人调查"
```

### 4.2 执行流程

```python
def check_decision_safety_red_lines(user_input, ai_output):
    """
    决策安全红线检查
    返回: (is_safe, triggered_reds, safe_output)
    """
    triggered_reds = []
    
    # RED-001: 不得给出最终合伙建议
    if contains_keywords(user_input, red_001_keywords):
        triggered_reds.append("RED-001")
        ai_output = add_safety_disclaimer(ai_output, "RED-001")
    
    # RED-002: 不得生成法律文件
    if contains_keywords(user_input, red_002_keywords):
        triggered_reds.append("RED-002")
        ai_output = block_legal_content(ai_output)
    
    # RED-003: 不得操作资金股权
    if contains_keywords(user_input, red_003_keywords):
        triggered_reds.append("RED-003")
        ai_output = convert_to_calculation_logic(ai_output)
    
    # RED-004: 不得查询隐私数据
    if contains_keywords(user_input, red_004_keywords):
        triggered_reds.append("RED-004")
        ai_output = suggest_public_sources(ai_output)
    
    is_safe = len(triggered_reds) == 0
    
    # 记录触发日志
    if triggered_reds:
        log_red_line_trigger(triggered_reds, user_input)
    
    return is_safe, triggered_reds, ai_output
```

### 4.3 标准响应模板

**RED-001触发响应**:
```
⚠️ **决策安全提示**

根据我们的决策安全红线，AI不得给出最终合伙建议。

我可以为您提供：
- 合伙人评估框架
- 多维度分析矩阵
- 决策参考信息

最终决策请结合您的实际情况和专业顾问意见。
```

**RED-002触发响应**:
```
⚠️ **法律文件安全提示**

AI生成的法律文件可能存在风险，不建议直接使用。

建议您：
- 咨询专业律师起草正式文件
- 使用我提供的框架与律师沟通
- 参考标准模板但需专业审核
```

**RED-003触发响应**:
```
⚠️ **资金操作安全提示**

AI不提供直接的资金/股权操作服务。

我可以帮您：
- 分析股权分配逻辑
- 计算不同方案的影响
- 提供决策参考数据

具体操作请咨询财务/法务专业人士。
```

**RED-004触发响应**:
```
⚠️ **隐私数据安全提示**

AI不得查询个人隐私数据。

您可以：
- 使用公开渠道自行查询
- 委托第三方背调机构
- 通过正式渠道获取授权信息
```

---

## 五、流程自动化（集成）

### 5.1 自动拦截配置

```yaml
safety_red_lines:
  enabled: true
  auto_check: true
  log_triggers: true
  
  rules:
    - id: RED-001
      name: "no_final_decision"
      action: "disclaimer"
      severity: "high"
      
    - id: RED-002
      name: "no_legal_docs"
      action: "block"
      severity: "critical"
      
    - id: RED-003
      name: "no_financial_ops"
      action: "convert"
      severity: "critical"
      
    - id: RED-004
      name: "no_privacy_queries"
      action: "redirect"
      severity: "high"
```

### 5.2 触发日志自动记录

```bash
#!/bin/bash
# scripts/red-line-logger.sh

log_red_line_trigger() {
    local red_id=$1
    local context=$2
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    echo "[$timestamp] RED_LINE_TRIGGERED: $red_id | Context: $context" >> logs/red-line-triggers.log
    
    # 如果触发RED-002或RED-003，立即通知
    if [[ "$red_id" == "RED-002" || "$red_id" == "RED-003" ]]; then
        echo "🚨 严重红线触发: $red_id" | notify_admin
    fi
}
```

### 5.3 月度审计报告

```bash
#!/bin/bash
# scripts/red-line-monthly-audit.sh

echo "=== 决策安全红线月度审计 ==="
echo "审计时间: $(date)"
echo ""

# 统计各红线触发次数
echo "红线触发统计:"
grep "RED-001" logs/red-line-triggers.log | wc -l
grep "RED-002" logs/red-line-triggers.log | wc -l
grep "RED-003" logs/red-line-triggers.log | wc -l
grep "RED-004" logs/red-line-triggers.log | wc -l

# 生成审计报告
cat > reports/red-line-audit-$(date +%Y-%m).md << EOF
# 决策安全红线审计报告 $(date +%Y-%m)

## 触发统计
$(grep "RED_LINE_TRIGGERED" logs/red-line-triggers.log | cut -d' ' -f3 | sort | uniq -c)

## 改进建议
$(analyze_trigger_patterns)
EOF

echo "审计报告已生成: reports/red-line-audit-$(date +%Y-%m).md"
```

---

## 六、质量门控

### 6.1 5标准自检清单

- [x] **全局考虑**: 6层全覆盖
- [x] **系统考虑**: 检测→拦截→报告→改进闭环
- [x] **迭代机制**: 月度审计+规则优化
- [x] **Skill化**: 自动检测、标准响应、日志记录
- [x] **流程自动化**: 触发记录、月度审计、严重告警

### 6.2 验证测试

```bash
# 测试RED-001
echo "我应该选谁做合伙人？" | test_red_line_check

# 测试RED-002
echo "帮我生成合伙协议" | test_red_line_check

# 测试RED-003
echo "股权怎么分配？" | test_red_line_check

# 测试RED-004
echo "查一下他的背景" | test_red_line_check
```

---

## 七、使用方式

### 7.1 人工检查

```bash
# 查看红线触发历史
tail -50 logs/red-line-triggers.log

# 查看月度审计
ls reports/red-line-audit-*.md

# 手动触发检查
echo "用户输入" | ./scripts/red-line-check.sh
```

### 7.2 集成到对话流程

所有AI输出自动经过 `check_decision_safety_red_lines()` 检查，无需人工干预。

---

*5标准合规: ✅ 全局 | ✅ 系统 | ✅ 迭代 | ✅ Skill化 | ✅ 自动化*

*版本历史: V1.0(4条规则)→V2.0(5标准Skill)*