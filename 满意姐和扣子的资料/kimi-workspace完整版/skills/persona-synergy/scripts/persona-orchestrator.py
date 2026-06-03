#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""角色协调器 - 按选定模式执行多角色分析（增强版）

支持三种协同模式：
  A: 顺序协同（先流程后审计）
  B: 并行协同（双视角同时输出）
  C: 蓝军主导（审计优先）

用法: python3 persona-orchestrator.py "任务描述" [A/B/C] [--verbose]
"""
import sys

def mode_a_sequential(task):
    return f"""[模式A: 顺序协同]
━━━━━━━━━━━━━━━━━━━━
Step 1 [满意姐] 流程启动
  → 任务'{task}'已纳入执行队列
  → 评估优先级（P0/P1/P2/P3）
  → 制定执行计划

Step 2 [执行] 任务处理
  → 按满意姐计划执行
  → 同步写入记忆文件
  → 记录进度到追踪文件

Step 3 [蓝军] 输出审计
  → 10项认知审计清单
  → 发现至少1个问题
  → 风险等级: 🔴高危/🟡中危/🟢可控

Step 4 [主控] 整合交付
  → 合并满意姐产出+蓝军审计
  → 如有冲突，提交conflict-resolver.py
  → 最终输出 + Git提交
━━━━━━━━━━━━━━━━━━━━
适用场景: 内容创作、文档整理、常规执行"""

def mode_b_parallel(task):
    return f"""[模式B: 并行协同]
━━━━━━━━━━━━━━━━━━━━
[满意姐] 流程视角（同步输出）
  → 任务'{task}'涉及决策
  → 建议流程: 评估→准备→执行→复盘
  → 优先级标记: P0

[蓝军] 风险视角（同步输出）
  → 建议补充"最坏情况分析"
  → 建议补充"退出机制"
  → 识别潜在认知偏差

[主控] 冲突检测
  → 检测满意姐流程 vs 蓝军要求
  → 如无冲突: 双视角互补，合并执行
  → 如有冲突: 提交conflict-resolver.py裁决

[整合结论]
  → 按满意姐流程执行
  → 蓝军要求的补充分析作为P0子任务并行
  → 双周同步会检查进展
━━━━━━━━━━━━━━━━━━━━
适用场景: 投资决策、合伙人选择、战略方向"""

def mode_c_blue_dominant(task):
    return f"""[模式C: 蓝军主导审计]
━━━━━━━━━━━━━━━━━━━━
[蓝军] 全面审计启动
  1. 认知审计清单10项检查:
     - 信源独立性 ✅/❌
     - 时效性 ✅/❌
     - 因果混淆 ✅/❌
     - 幸存者偏差 ✅/❌
     - 基底率忽视 ✅/❌
     - 锚定效应 ✅/❌
     - 确认偏误 ✅/❌
     - 语言腐败 ✅/❌
     - 数学谬误 ✅/❌
     - 样本偏差 ✅/❌
  2. 发现至少1个问题（禁止"一切正常"）
  3. 输出风险等级和具体指控

[满意姐] 补充关怀视角
  → 审计过程中注意用户状态
  → 如用户疲惫，建议暂停
  → 如用户焦虑，简化输出

[主控] 整合输出
  → 蓝军主导，满意姐辅助
  → 输出审计报告
  → 如需整改，生成整改清单
━━━━━━━━━━━━━━━━━━━━
适用场景: 质量审计、风险排查、合规检查"""

def orchestrate(task, mode='A', verbose=False):
    if mode.upper() == 'C':
        result = mode_c_blue_dominant(task)
    elif mode.upper() == 'B':
        result = mode_b_parallel(task)
    else:
        result = mode_a_sequential(task)
    
    if verbose:
        result += f"""
━━━━━━━━━━━━━━━━━━━━
[执行参数]
任务: {task}
模式: {mode.upper()}
时间戳: {__import__('datetime').datetime.now().isoformat()}
下一步: 按上述步骤执行，完成后Git提交"""
    return result

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        verbose = '--verbose' in sys.argv
        task = sys.argv[1]
        mode = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 'A'
        print(orchestrate(task, mode, verbose))
    else:
        print(__doc__)
