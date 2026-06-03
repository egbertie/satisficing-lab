---
# 知识元数据 (5标准化)
knowledge_id: W15-E0712B
title: Dialogue Token Optimizer Skill
category: 11_Skill文档
source: skills/dialogue-token-optimizer/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 4314
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Dialogue Token Optimizer Skill

> **知识ID**: W15-E0712B  
> **分类**: 11_Skill文档  
> **来源**: `skills/dialogue-token-optimizer/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Dialogue Token Optimizer Skill

## Overview
智能对话Token优化系统，通过时段控制、深度标记、上下文管理三重机制，实现对话Token消耗的最优化。

## S1: Global Consideration (全局考虑)

### 1.1 人 (People)
| 角色 | 需求 | 影响 |
|------|------|------|
| 用户(Egbertie) | 高效获取信息，控制成本 | 需要快速识别模式 |
| AI助手(满意妞) | 平衡服务质量与资源消耗 | 需要智能判断 |
| 系统管理员 | 监控整体Token使用 | 需要透明数据 |

### 1.2 事 (Tasks)
- 自动时段模式切换
- 深度标记识别与响应
- 上下文压缩建议
- Token使用实时监控

### 1.3 物 (Resources)
- Token预算池
- 对话上下文存储
- 配置文件
- 日志记录

### 1.4 环境 (Environment)
- 工作时间vs非工作时间
- 核心任务vs闲聊场景
- 紧急需求vs常规查询

### 1.5 外部集成 (External)
- Cron定时任务
- 基线检查系统
- Token监控仪表板

### 1.6 边界情况 (Edge Cases)
- 深夜紧急请求（应覆盖时段限制）
- 连续深度标记冲突（取最后一个）
- Token即将耗尽时的强制处理

## S2: System Closed Loop (系统闭环)

### 2.1 输入
```
用户输入 → 深度标记检测 → 时段模式检测 → Token状态检测
```

### 2.2 处理
```
标记识别 → 配置匹配 → 响应策略选择 → 执行优化
```

### 2.3 输出
```
优化响应 + Token使用报告 + 压缩建议
```

### 2.4 反馈
```
实际Token消耗 → 策略效果评估 → 配置微调
```

### 2.5 故障处理
| 故障场景 | 处理策略 | 降级方案 |
|----------|----------|----------|
| 标记识别失败 | 使用默认模式 | 标准响应 |
| 配置读取失败 | 使用硬编码默认值 | 保守模式 |
| 状态检测超时 | 跳过优化 | 正常响应 |

## S3: Observable Outputs (可观测输出)

### 3.1 量化指标
| 指标 | 采集方式 | 目标值 |
|------|----------|--------|
| 日Token消耗 | 自动统计 | <8000 |
| 深度标记使用率 | 日志分析 | >50% |
| 时段模式匹配度 | 对比分析 | >90% |
| 压缩建议采纳率 | 用户反馈 | >30% |

### 3.2 结构化输出
```json
{
  "optimization_applied": true,
  "mode": "core|light|hibernate",
  "marker_detected": "[快速]",
  "token_saved": 450,
  "guidance": "一句话回答，最多10个字。"
}
```

### 3.3 可视化报告
- 每日Token消耗曲线
- 时段模式分布饼图
- 深度标记使用频率
- 优化效果对比

## S4: Automated Integration (自动化集成)

### 4.1 Cron配置
```yaml
jobs:
  - name: token-mode-controller
    schedule: "0 * * * *"  # 每小时检查时段
    script: scripts/token_mode_controller.sh
  
  - name: conversation-optimizer-report
    schedule: "0 9,18 * * *"  # 早晚报告
    script: scripts/conversation_optimizer.py
```

### 4.2 触发器
- 会话启动时：检测当前时段模式
- 用户输入时：检测深度标记
- Token达70%：主动推送压缩建议
- Token达85%：强制推荐/compaction

### 4.3 脚本清单
| 脚本 | 功能 | 调用方式 |
|------|------|----------|
| token_mode_controller.sh | 时段模式控制 | Cron每小时 |
| depth_marker_processor.py | 深度标记处理 | 实时调用 |
| conversation_optimizer.py | 对话优化建议 | 实时+定时 |

## S5: Self-Validation (自我验证)

### 5.1 自动检查清单
- [ ] 时段模式切换正确性
- [ ] 深度标记识别准确率
- [ ] Token计算准确性
- [ ] 配置文件格式有效性

### 5.2 测试用例
```bash
# 测试深度标记识别
echo "[快速] 今天天气如何" | python3 scripts/depth_marker_processor.py
# 期望: minimal模式，max_tokens=200

# 测试时段判断
date -d '02:00 +8 hours' +%H | xargs -I {} scripts/token_mode_controller.sh
# 期望: hibernate模式
```

### 5.3 健康检查
```bash
python3 scripts/conversation_optimizer.py 1000 10000
# 应返回status=normal

python3 scripts/conversation_optimizer.py 9000 10000
# 应返回status=critical，action=suggest_compact
```

## S6: Cognitive Humility (认知谦逊)

### 6.1 能力边界
1. **无法预测用户真实意图**：只能根据标记推断，可能误判
2. **无法精确计算Token**：基于字符估算，非精确值
3. **时段模式过于简化**：仅按小时划分，未考虑具体日程
4. **无法强制用户采纳建议**：只能推送，不能阻止高消耗行为

### 6.2 不确定性标注
- Token估算标注[估算值]，非精确值
- 优化建议标注[建议]，非强制
- 模式判断标注[自动判断]，可手动覆盖

### 6.3 置信度声明
| 功能 | 置信度 | 依据 |
|------|--------|------|
| 深度标记识别 | 95% | 明确的字符串匹配 |
| 时段判断 | 90% | 基于时间规则 |
| Token估算 | 70% | 基于字符数近似 |
| 优化效果预测 | 60% | 依赖用户行为 |

## S7: Adversarial Testing (对抗测试)

### 7.1 测试场景

#### 场景1: 冲突标记
```
输入: "[快速][详细] 问题"
预期: 识别最后一个标记[详细]
```

#### 场景2: 深夜紧急请求
```
时间: 03:00
输入: "[战略] 重要决策"
预期: 覆盖时段限制，提供深度分析
```

#### 场景3: Token临界值
```
上下文: 9900/10000
新输入: 长文本
预期: 立即触发强制压缩建议
```

#### 场景4: 配置损坏
```
操作: 删除配置文件
输入: 任意
预期: 使用硬编码默认值，服务不中断
```

#### 场景5: 极端深度标记
```
输入: "[快速][简要][标准][详细][深度][战略]"
预期: 仅识别最后一个[战略]，其余忽略
```

#### 场景6: 空输入
```
输入: ""
预期: 返回默认配置，不报错
```

#### 场景7: 超大Token预算
```
预算: 999999999
输入: 长文本
预期: 正常处理，无溢出
```

## Usage

### 深度标记使用指南

| 标记 | 场景 | 示例 |
|------|------|------|
| [快速] | 确认简单事实 | "[快速] 今天几号" |
| [简要] | 获取要点 | "[简要] 今日待办" |
| [标准] | 正常对话 | "[标准] 分析一下" |
| [详细] | 需要细节 | "[详细] 解释原理" |
| [深度] | 复杂分析 | "[深度] 竞品对比" |
| [战略] | 框架设计 | "[战略] 产品规划" |

### 时段模式说明

| 时段 | 模式 | 策略 |
|------|------|------|
| 00:00-08:00 | 休眠 | 极简响应，紧急情况可覆盖 |
| 09:00-18:00 | 核心 | 全力服务，深度支持 |
| 18:00-24:00 | 轻度 | 平衡模式，预防性压缩 |

## Files

| 文件 | 路径 | 说明 |
|------|------|------|
| 时段控制器 | scripts/token_mode_controller.sh | Cron调用 |
| 标记处理器 | scripts/depth_marker_processor.py | 实时调用 |
| 对话优化器 | scripts/conversation_optimizer.py | 实时+定时 |
| 配置 | config/token_mode_config.json | 模式配置 |

## Version
- **Version**: V1.0
- **Status**: FIN (7-standard complete)
- **Created**: 2026-03-25
- **Standard**: S1-S7 full compliance
