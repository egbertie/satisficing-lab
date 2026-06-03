#!/usr/bin/env python3
"""
Skill虚报状态扫描器 - R4整改通道
全面扫描所有Skill，识别虚报状态
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

WORKSPACE_ROOT = "/root/.openclaw/workspace"
SKILLS_DIR = f"{WORKSPACE_ROOT}/skills"

@dataclass
class SkillAuditResult:
    name: str
    path: str
    has_skill_md: bool
    has_python_code: bool
    has_test_file: bool
    skill_md_lines: int
    code_lines: int
    test_lines: int
    is_placeholder_heavy: bool  # 代码中是否有大量TODO/pass
    test_quality: str  # high/medium/low/none
    claimed_status: str  # 声称的状态
    actual_status: str  # 实际状态
    fraud_type: str  # 虚报类型
    correction_needed: bool
    correction_action: str

class SkillFraudScanner:
    def __init__(self):
        self.results: List[SkillAuditResult] = []
        self.fraud_count = 0
        
    def scan_all_skills(self) -> List[SkillAuditResult]:
        """扫描所有Skill"""
        skills_path = Path(SKILLS_DIR)
        
        # 扫描主skills目录
        for skill_dir in skills_path.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('.') and not skill_dir.name.startswith('z_'):
                result = self._audit_skill(skill_dir)
                if result:
                    self.results.append(result)
        
        return self.results
    
    def _audit_skill(self, skill_dir: Path) -> SkillAuditResult:
        """审计单个Skill"""
        name = skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        
        # 检查基本文件
        has_skill_md = skill_md.exists()
        skill_md_lines = 0
        claimed_status = "UNKNOWN"
        
        if has_skill_md:
            try:
                content = skill_md.read_text(encoding='utf-8')
                skill_md_lines = len(content.split('\n'))
                # 解析声称的状态
                claimed_status = self._parse_claimed_status(content)
            except:
                pass
        
        # 检查Python代码
        python_files = list(skill_dir.glob("*.py"))
        has_python_code = len(python_files) > 0
        code_lines = 0
        is_placeholder_heavy = False
        
        if has_python_code:
            for py_file in python_files:
                try:
                    content = py_file.read_text(encoding='utf-8')
                    lines = len(content.split('\n'))
                    code_lines += lines
                    # 检查是否是空壳代码
                    if 'TODO' in content or content.count('pass') > 3:
                        is_placeholder_heavy = True
                except:
                    pass
        
        # 检查测试文件
        test_files = list(skill_dir.glob("test_*.py")) + list(skill_dir.glob("*_test.py"))
        has_test_file = len(test_files) > 0
        test_lines = 0
        test_quality = "none"
        
        if has_test_file:
            for test_file in test_files:
                try:
                    content = test_file.read_text(encoding='utf-8')
                    test_lines += len(content.split('\n'))
                    # 评估测试质量
                    assert_count = content.count('assert')
                    if assert_count >= 10:
                        test_quality = "high"
                    elif assert_count >= 5:
                        test_quality = "medium"
                    elif assert_count >= 1:
                        test_quality = "low"
                except:
                    pass
        
        # 确定实际状态
        actual_status = self._determine_actual_status(
            has_skill_md, skill_md_lines,
            has_python_code, code_lines,
            has_test_file, test_quality,
            is_placeholder_heavy
        )
        
        # 判断是否虚报
        fraud_type, correction_needed, correction_action = self._detect_fraud(
            claimed_status, actual_status, is_placeholder_heavy, test_quality
        )
        
        if fraud_type != "NONE":
            self.fraud_count += 1
        
        return SkillAuditResult(
            name=name,
            path=str(skill_dir),
            has_skill_md=has_skill_md,
            has_python_code=has_python_code,
            has_test_file=has_test_file,
            skill_md_lines=skill_md_lines,
            code_lines=code_lines,
            test_lines=test_lines,
            is_placeholder_heavy=is_placeholder_heavy,
            test_quality=test_quality,
            claimed_status=claimed_status,
            actual_status=actual_status,
            fraud_type=fraud_type,
            correction_needed=correction_needed,
            correction_action=correction_action
        )
    
    def _parse_claimed_status(self, content: str) -> str:
        """解析SKILL.md中声称的状态"""
        content_lower = content.lower()
        
        # 检查是否有完成标记
        if '运行中' in content or '✅' in content or 'completed' in content_lower:
            return "FIN"
        elif 'wip' in content_lower or '进行中' in content or '🔄' in content:
            return "WIP"
        elif 'todo' in content_lower or '待开始' in content:
            return "TODO"
        
        # 检查是否有版本号（通常表示完成）
        if 'version' in content_lower or 'v1.' in content_lower or 'v2.' in content_lower:
            return "FIN"
        
        # 检查是否声称5标准化完成
        if '5标准' in content or 's1' in content_lower and 's2' in content_lower:
            return "FIN"
        
        return "UNKNOWN"
    
    def _determine_actual_status(self, has_md, md_lines, has_code, code_lines, 
                                  has_test, test_quality, is_placeholder) -> str:
        """确定实际完成状态"""
        if not has_md:
            return "EMPTY"
        
        if md_lines < 10:
            return "SHELL_ONLY"  # 只有空壳
        
        if not has_code:
            if md_lines > 50:
                return "DOC_ONLY"  # 只有文档
            return "SKEL"
        
        if code_lines < 50:
            return "MINIMAL_CODE"
        
        if is_placeholder:
            if has_test and test_quality in ['medium', 'high']:
                return "PARTIAL_WITH_TEST"
            return "PLACEHOLDER_HEAVY"
        
        if not has_test:
            return "NO_TEST"
        
        if test_quality == "low":
            return "LOW_TEST"
        
        if test_quality == "medium":
            return "MEDIUM_TEST"
        
        return "COMPLETE"
    
    def _detect_fraud(self, claimed, actual, is_placeholder, test_quality) -> Tuple[str, bool, str]:
        """检测虚报"""
        if claimed == "FIN":
            if actual in ["EMPTY", "SHELL_ONLY", "SKEL"]:
                return "CRITICAL_FRAUD", True, "删除FIN标记，改为TODO"
            elif actual in ["DOC_ONLY", "MINIMAL_CODE"]:
                return "MAJOR_FRAUD", True, "删除FIN标记，改为WIP"
            elif actual in ["PLACEHOLDER_HEAVY", "NO_TEST", "LOW_TEST"]:
                return "MODERATE_FRAUD", True, "删除FIN标记，改为WIP，补充测试"
            elif is_placeholder and test_quality != "high":
                return "MINOR_FRAUD", True, "完善代码实现，移除TODO/pass"
        
        elif claimed == "WIP":
            if actual in ["EMPTY", "SHELL_ONLY"]:
                return "MISLEADING", True, "改为TODO状态"
        
        return "NONE", False, "无需修正"
    
    def generate_report(self) -> Dict:
        """生成审计报告"""
        total = len(self.results)
        fraud_results = [r for r in self.results if r.fraud_type != "NONE"]
        
        # 按严重程度分类
        critical = [r for r in fraud_results if r.fraud_type == "CRITICAL_FRAUD"]
        major = [r for r in fraud_results if r.fraud_type == "MAJOR_FRAUD"]
        moderate = [r for r in fraud_results if r.fraud_type == "MODERATE_FRAUD"]
        minor = [r for r in fraud_results if r.fraud_type == "MINOR_FRAUD"]
        
        # 超级系统框架Skill
        super_systems = ['backup-suite', 'token-suite', 'quality-suite', 'automation-suite',
                        'content-suite', 'expert-suite', 'feishu-suite', 'file-suite',
                        'governance-suite', 'knowledge-suite']
        super_system_results = [r for r in self.results if r.name in super_systems]
        super_system_fraud = [r for r in super_system_results if r.fraud_type != "NONE"]
        
        return {
            "summary": {
                "total_skills": total,
                "fraud_count": len(fraud_results),
                "fraud_rate": f"{len(fraud_results)/total*100:.1f}%" if total > 0 else "0%",
                "critical": len(critical),
                "major": len(major),
                "moderate": len(moderate),
                "minor": len(minor),
                "super_system_total": len(super_system_results),
                "super_system_fraud": len(super_system_fraud)
            },
            "fraud_by_severity": {
                "CRITICAL": [asdict(r) for r in critical],
                "MAJOR": [asdict(r) for r in major],
                "MODERATE": [asdict(r) for r in moderate],
                "MINOR": [asdict(r) for r in minor]
            },
            "super_system_analysis": [asdict(r) for r in super_system_results],
            "all_results": [asdict(r) for r in self.results]
        }

def main():
    scanner = SkillFraudScanner()
    print("🔍 开始扫描所有Skill...")
    
    results = scanner.scan_all_skills()
    report = scanner.generate_report()
    
    # 输出摘要
    summary = report["summary"]
    print(f"\n{'='*60}")
    print("📊 Skill虚报状态扫描报告")
    print(f"{'='*60}")
    print(f"总Skill数: {summary['total_skills']}")
    print(f"虚报数量: {summary['fraud_count']}")
    print(f"虚报率: {summary['fraud_rate']}")
    print(f"\n严重级别分布:")
    print(f"  🔴 CRITICAL: {summary['critical']}")
    print(f"  🟠 MAJOR: {summary['major']}")
    print(f"  🟡 MODERATE: {summary['moderate']}")
    print(f"  🟢 MINOR: {summary['minor']}")
    print(f"\n超级系统框架:")
    print(f"  总数: {summary['super_system_total']}")
    print(f"  虚报: {summary['super_system_fraud']}")
    
    # 保存报告
    report_path = f"{WORKSPACE_ROOT}/SKILL_FRAUD_SCAN_REPORT.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 详细报告已保存: {report_path}")
    
    return report

if __name__ == "__main__":
    main()
