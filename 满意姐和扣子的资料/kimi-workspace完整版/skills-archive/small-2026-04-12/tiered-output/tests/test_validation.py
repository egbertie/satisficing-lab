#!/usr/bin/env python3
"""
分级输出系统 - 测试验证脚本
Tiered Output System - Test Validation Script

用于验证三级输出长度机制的正确性和效果
"""

import json
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional


def get_skill_main_file(skill_path: Path):
    """获取Skill的主代码文件"""
    skill_name = skill_path.name.replace('-', '_')
    candidates = [
        skill_path / f"{skill_name}.py",
        skill_path / "__init__.py",
        skill_path / "main.py",
        skill_path / "runner.py",
        skill_path / "skill.py",
    ]
    for c in candidates:
        if c.exists():
            return c
    py_files = list(skill_path.glob("*.py"))
    if py_files:
        return py_files[0]
    return None


@dataclass
class TestResult:
    test_name: str
    tier: str
    token_count: int
    passed: bool
    issues: List[str]
    sample_output: str

class TieredOutputTester:
    def __init__(self, config_path: str = "../config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        self.results: List[TestResult] = []
    
    def count_tokens(self, text: str) -> int:
        """估算token数（中文约1字=1token，英文约1词=1.3tokens）"""
        import re
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        other = len(text) - chinese_chars - sum(len(w) for w in re.findall(r'[a-zA-Z]+', text))
        return int(chinese_chars + english_words * 1.3 + other * 0.5)
    
    def test_tier_limits(self) -> bool:
        """测试各级别Token限制"""
        print("\n[测试] Token限制验证")
        
        # L1测试 - 应<50 tokens
        l1_sample = "✅ 任务已完成。建议：检查邮件确认最终交付。"
        l1_tokens = self.count_tokens(l1_sample)
        l1_pass = l1_tokens <= 50
        self.results.append(TestResult(
            test_name="L1_Token_Limit",
            tier="L1",
            token_count=l1_tokens,
            passed=l1_pass,
            issues=[] if l1_pass else [f"Token数({l1_tokens})超过限制(50)"],
            sample_output=l1_sample
        ))
        print(f"  L1: {l1_tokens} tokens - {'✅ 通过' if l1_pass else '❌ 失败'}")
        
        # L2测试 - 应200-500 tokens
        l2_sample = """## 摘要
完成3个文件审计，发现2个高风险项需立即处理。

## 关键发现
- **文件完整性**: 95%通过，缺失1个配置文件
- **安全风险**: 发现2个硬编码密钥，需轮换
- **性能优化**: 1个查询可优化，预计提升30%效率

## 下一步
1. 立即轮换密钥 - 安全团队/2小时内
2. 补充配置文件 - 开发团队/今日完成
3. 部署查询优化 - 明日上线"""
        l2_tokens = self.count_tokens(l2_sample)
        l2_pass = 100 <= l2_tokens <= 500
        issues = []
        if l2_tokens < 100:
            issues.append(f"Token数({l2_tokens})低于最小值(100)")
        elif l2_tokens > 500:
            issues.append(f"Token数({l2_tokens})超过最大值(500)")
        self.results.append(TestResult(
            test_name="L2_Token_Limit",
            tier="L2",
            token_count=l2_tokens,
            passed=l2_pass,
            issues=issues,
            sample_output=l2_sample[:100] + "..."
        ))
        print(f"  L2: {l2_tokens} tokens - {'✅ 通过' if l2_pass else '❌ 失败'}")
        
        # L3测试 - 应>1000 tokens
        l3_sample = """# 系统健康状态深度分析报告

## 执行摘要
经过对全量系统指标的综合分析，本周系统整体运行状态良好，健康度评分92/100。
主要关注点集中在磁盘存储使用率持续上升趋势，目前已达85%警戒线，
建议在本周末前完成存储清理和扩容评估工作，避免影响核心服务稳定性。

## 背景与上下文
本报告基于过去30天的监控数据分析，涵盖生产环境全部12个服务节点。
分析周期: 2026-03-01 至 2026-03-21
数据来源: Prometheus + Grafana + ELK Stack

## 详细指标分析

### CPU使用率分析
- **平均值**: 45% (较上周下降5%)
- **峰值**: 78% (发生于周二14:00流量高峰时段)
- **趋势**: 整体呈下降趋势，负载均衡效果良好
- **异常检测**: 周三凌晨03:00出现短暂 spike 至85%，持续2分钟，已定位为目标服务定时任务

### 内存使用率分析
- **平均值**: 68%
- **可用内存**: 12GB / 总36GB
- **内存泄漏扫描**: 未发现明显泄漏迹象
- **OOM事件**: 本周0次
- **建议**: 内存使用处于健康水平，继续监控

### 磁盘使用率分析 [重点关注]
- **当前使用率**: 85% (警戒线: 80%)
- **增长趋势**: 每周+2% (线性增长)
- **预计满盘时间**: 约7周后 (2026年5月中旬)
- **主要占用**: 日志文件(40%), 备份数据(30%), 应用数据(20%), 其他(10%)
- **风险等级**: 中高风险

### 网络IO分析
- **入站流量**: 平均 120MB/s, 峰值 350MB/s
- **出站流量**: 平均 85MB/s, 峰值 200MB/s
- **延迟**: P50=15ms, P95=45ms, P99=120ms
- **丢包率**: 0.01% (可接受范围)

### 数据库性能分析
- **查询QPS**: 平均 2,500, 峰值 8,000
- **慢查询**: 本周新增 12 条 (>1s)
- **连接池**: 使用率 65%
- **锁等待**: 最大 200ms

## 警告详情与根因分析

| 级别 | 项目 | 当前值 | 阈值 | 持续时间 | 建议措施 |
|------|------|--------|------|----------|----------|
| 🔴 高 | 磁盘使用 | 85% | 80% | 5天 | 立即清理 + 扩容评估 |
| 🟡 中 | 备份延迟 | 2h | 1h | 3天 | 优化备份脚本 |
| 🟢 低 | SSL证书 | 30天 | 14天 | - | 计划续期 |

### 磁盘使用率根因分析 (5 Whys)
1. **为什么磁盘使用率达85%?** → 日志文件增长过快
2. **为什么日志增长过快?** → 调试级别日志未关闭
3. **为什么调试日志未关闭?** → 上次故障排查后未恢复
4. **为什么未恢复?** → 缺乏配置审查流程
5. **根本原因** → 缺少变更管理和自动化配置检查

## 可选解决方案对比

### 方案A: 日志清理与轮转优化
- **成本**: 低 (人力 4h)
- **效果**: 可释放约20%存储空间
- **实施难度**: 低
- **风险**: 无
- **ROI**: 高

### 方案B: 存储扩容
- **成本**: 中 (硬件/云存储费用)
- **效果**: 增加100%存储容量
- **实施难度**: 中 (需停机窗口)
- **风险**: 中 (数据迁移风险)
- **ROI**: 中

### 方案C: 冷热数据分离
- **成本**: 高 (架构改造)
- **效果**: 长期解决存储问题
- **实施难度**: 高
- **风险**: 高
- **ROI**: 长期高

## 推荐方案
**短期**: 立即执行方案A (本周内)
**中期**: 启动方案B评估 (本月内)
**长期**: 规划方案C架构升级 (下季度)

## 执行计划

| 阶段 | 任务 | 负责人 | 截止时间 | 依赖 | 状态 |
|------|------|--------|----------|------|------|
| 1 | 调整日志级别 | 运维 | 今日 | 无 | ⏳ 待开始 |
| 2 | 清理历史日志 | 运维 | 明日 | 阶段1 | ⏳ 待开始 |
| 3 | 评估扩容方案 | 架构 | 本周五 | 阶段2 | ⏳ 待开始 |
| 4 | 实施扩容 | 运维 | 下周 | 阶段3 | ⏳ 待开始 |

## 附录

### A. 监控图表链接
- [CPU趋势图](https://grafana/d/cpu)
- [内存使用图](https://grafana/d/memory)
- [磁盘分析](https://grafana/d/disk)

### B. 相关文档
- 运维手册 v2.3
- 扩容SOP
- 事件响应流程

---
*报告生成时间: 2026-03-21 19:50*
*下次检查: 2026-03-28*
"""
        l3_tokens = self.count_tokens(l3_sample)
        l3_pass = l3_tokens >= 1000
        self.results.append(TestResult(
            test_name="L3_Token_Limit",
            tier="L3",
            token_count=l3_tokens,
            passed=l3_pass,
            issues=[] if l3_pass else [f"Token数({l3_tokens})低于最小值(1000)"],
            sample_output=l3_sample[:200] + "..."
        ))
        print(f"  L3: {l3_tokens} tokens - {'✅ 通过' if l3_pass else '❌ 失败'}")
        
        return l1_pass and l2_pass and l3_pass
    
    def test_trigger_rules(self) -> bool:
        """测试触发规则"""
        print("\n[测试] 触发规则验证")
        
        commands = self.config['triggers']['user_commands']
        
        # 测试指令映射
        test_cases = [
            ("/brief", "L1"),
            ("/b", "L1"),
            ("/normal", "L2"),
            ("/n", "L2"),
            ("/detail", "L3"),
            ("/d", "L3"),
        ]
        
        passed = True
        for cmd, expected_tier in test_cases:
            actual_tier = None
            for tier, cmd_list in commands.items():
                if cmd in cmd_list:
                    actual_tier = tier
                    break
            
            test_pass = actual_tier == expected_tier
            if not test_pass:
                passed = False
            print(f"  指令 '{cmd}' -> {actual_tier} - {'✅' if test_pass else '❌'}")
        
        return passed
    
    def test_token_savings(self) -> Dict[str, float]:
        """测试Token节省率"""
        print("\n[测试] Token节省率计算")
        
        # 获取各级的token数
        l1_result = next(r for r in self.results if r.test_name == "L1_Token_Limit")
        l2_result = next(r for r in self.results if r.test_name == "L2_Token_Limit")
        l3_result = next(r for r in self.results if r.test_name == "L3_Token_Limit")
        
        l1_tokens = l1_result.token_count
        l2_tokens = l2_result.token_count
        l3_tokens = l3_result.token_count
        
        savings = {
            "L1_vs_L3": round((l3_tokens - l1_tokens) / l3_tokens * 100, 1),
            "L2_vs_L3": round((l3_tokens - l2_tokens) / l3_tokens * 100, 1),
            "L1_vs_L2": round((l2_tokens - l1_tokens) / l2_tokens * 100, 1)
        }
        
        print(f"  L1相比L3节省: {savings['L1_vs_L3']}%")
        print(f"  L2相比L3节省: {savings['L2_vs_L3']}%")
        print(f"  L1相比L2节省: {savings['L1_vs_L2']}%")
        
        return savings
    
    def test_template_structure(self) -> bool:
        """测试模板结构完整性"""
        print("\n[测试] 模板结构验证")
        
        templates = self.config['templates']
        required_templates = ['task_completion', 'problem_diagnosis', 'data_analysis', 'general_response']
        
        passed = True
        for template_name in required_templates:
            if template_name not in templates:
                print(f"  ❌ 缺少模板: {template_name}")
                passed = False
            else:
                template = templates[template_name]
                for tier in ['L1', 'L2', 'L3']:
                    if tier not in template:
                        print(f"  ❌ {template_name} 缺少 {tier} 级别")
                        passed = False
                if passed:
                    print(f"  ✅ {template_name}")
        
        return passed
    
    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        print("=" * 60)
        print("分级输出系统 - 测试验证")
        print("=" * 60)
        
        results = {
            "tier_limits": self.test_tier_limits(),
            "trigger_rules": self.test_trigger_rules(),
            "token_savings": self.test_token_savings(),
            "template_structure": self.test_template_structure(),
        }
        
        # 计算总体通过率
        passed_tests = sum(1 for v in results.values() if isinstance(v, bool) and v)
        total_tests = sum(1 for v in results.values() if isinstance(v, bool))
        
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print(f"通过: {passed_tests}/{total_tests}")
        print(f"Token节省率: L1较L3节省 {results['token_savings']['L1_vs_L3']}%")
        
        return results

def main():
    tester = TieredOutputTester()
    results = tester.run_all_tests()
    
    # 保存详细结果
    output_file = Path("test_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total_tests": len([v for v in results.values() if isinstance(v, bool)]),
                "passed_tests": sum(1 for v in results.values() if isinstance(v, bool) and v),
                "token_savings": results['token_savings']
            },
            "details": [r.__dict__ for r in tester.results]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存至: {output_file}")

if __name__ == "__main__":
    main()
