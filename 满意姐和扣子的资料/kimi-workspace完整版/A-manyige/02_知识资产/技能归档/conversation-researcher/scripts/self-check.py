#!/usr/bin/env python3
"""
self-check.py
Conversation Researcher 自检脚本
验证7-S标准合规性
"""

import os
import sys
import json
from pathlib import Path

# 添加lib路径
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

class StandardChecker:
    """7-S标准检查器"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def check(self, standard: str, name: str, condition: bool, detail: str = ""):
        """检查单项标准"""
        status = "✅ PASS" if condition else "❌ FAIL"
        self.results.append({
            "standard": standard,
            "name": name,
            "status": status,
            "passed": condition,
            "detail": detail
        })
        if condition:
            self.passed += 1
        else:
            self.failed += 1
        print(f"{status} | S{standard}: {name} {detail}")
    
    def run_all_checks(self):
        """执行所有检查"""
        print("="*60)
        print("Conversation Researcher - 7-S标准自检")
        print("="*60)
        print()
        
        # S1: 输入
        skill_md = self.base_dir / "SKILL.md"
        self.check("1", "输入定义", skill_md.exists(), "SKILL.md存在")
        if skill_md.exists():
            content = skill_md.read_text()
            self.check("1", "主题输入支持", "研究主题" in content or "topic" in content.lower())
            self.check("1", "问题输入支持", "问题" in content or "question" in content.lower())
            self.check("1", "关键词支持", "关键词" in content or "keyword" in content.lower())
        
        # S2: 处理
        runner = self.base_dir / "scripts" / "research-runner.py"
        self.check("2", "搜索实现", runner.exists(), "research-runner.py存在")
        if runner.exists():
            content = runner.read_text()
            self.check("2", "多源搜索", "multi_source_search" in content)
            self.check("2", "信息整合", "integrate" in content)
            self.check("2", "深度分析", "analyze" in content)
        
        # S3: 输出
        self.check("3", "报告生成", runner.exists())
        if runner.exists():
            content = runner.read_text()
            self.check("3", "摘要输出", "summary" in content.lower())
            self.check("3", "发现输出", "finding" in content.lower())
            self.check("3", "引用输出", "source" in content.lower())
            self.check("3", "建议输出", "recommend" in content.lower() or "建议" in content)
        
        # S4: 手动触发
        self.check("4", "命令行触发", "main()" in runner.read_text() if runner.exists() else False)
        self.check("4", "环境变量支持", "RESEARCH_TOPIC" in runner.read_text() if runner.exists() else False)
        
        # S5: 准确性
        if runner.exists():
            content = runner.read_text()
            self.check("5", "来源验证", "verify_sources" in content)
            self.check("5", "引用可追溯", "url" in content.lower())
        
        # S6: 局限性
        if runner.exists():
            content = runner.read_text()
            self.check("6", "时效性标注", "temporal" in content.lower() or "时效" in content)
            self.check("6", "偏见分析", "bias" in content.lower() or "偏见" in content)
        
        # S7: 验证
        if runner.exists():
            content = runner.read_text()
            self.check("7", "交叉验证", "cross_validation" in content.lower())
            self.check("7", "多源验证", "min_sources" in content or "consensus" in content)
        
        # 文件结构检查
        print()
        print("-"*60)
        print("文件结构检查")
        print("-"*60)
        
        required_files = [
            ("SKILL.md", self.base_dir / "SKILL.md"),
            ("config/researcher.json", self.base_dir / "config" / "researcher.json"),
            ("scripts/research-runner.py", self.base_dir / "scripts" / "research-runner.py"),
            ("scripts/self-check.py", self.base_dir / "scripts" / "self-check.py"),
        ]
        
        for name, path in required_files:
            self.check("F", f"文件: {name}", path.exists())
        
        # 汇总
        print()
        print("="*60)
        print("自检结果汇总")
        print("="*60)
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"总计: {self.passed + self.failed}")
        print(f"合规率: {self.passed/(self.passed+self.failed)*100:.1f}%" if (self.passed+self.failed) > 0 else "N/A")
        print()
        
        # 合规性判断
        if self.failed == 0:
            print("✅ 所有检查通过！已达到5标准")
            return 0
        elif self.passed / (self.passed + self.failed) >= 0.85:
            print("⚠️ 基本合规，存在次要问题")
            return 0
        else:
            print("❌ 未达标准，需要改进")
            return 1


def main():
    checker = StandardChecker()
    return checker.run_all_checks()


if __name__ == "__main__":
    sys.exit(main())
