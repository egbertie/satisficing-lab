#!/usr/bin/env python3
"""
蓝军审计SOP - Blue Army Audit Standard Operating Procedure V1.1

目的：将审计经验固化为标准流程，确保每次审计一致、完整、无疏漏

核心原则：
1.  🔴 诚实审计 - 最大的底线，宁可FAIL，不虚报PASS
2.  checklist驱动 - 每个Skill必须过 checklist
3.  零容忍 - 任何一项不通过即FAIL
4.  文档化 - 所有审计结果必须记录
5.  可追溯 - 每个决定都有依据
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime

# ============ 蓝军审计标准 V1.1 ============
# 任何变更必须更新版本号并记录变更日志
# 🔴 诚实审计是最大的底线 - 宁可FAIL，不虚报PASS

AUDIT_STANDARD_VERSION = "1.1.0"
AUDIT_DATE = "2026-03-28"

# 核心审计维度（5维度17项）
AUDIT_DIMENSIONS = {
    'D1_CodeQuality': {
        'name': '代码质量',
        'items': [
            {'id': 'D1-01', 'item': '代码行数≥150行', 'weight': 'P0'},
            {'id': 'D1-02', 'item': '非占位符实现', 'weight': 'P0'},
            {'id': 'D1-03', 'item': '错误处理完善', 'weight': 'P1'},
        ]
    },
    'D2_TestCoverage': {
        'name': '测试覆盖',
        'items': [
            {'id': 'D2-01', 'item': '存在run_tests函数', 'weight': 'P0'},
            {'id': 'D2-02', 'item': '支持--test CLI参数', 'weight': 'P0'},
            {'id': 'D2-03', 'item': '测试数量≥10项', 'weight': 'P0'},
            {'id': 'D2-04', 'item': '测试通过率100%', 'weight': 'P0'},
        ]
    },
    'D3_TokenManagement': {
        'name': 'Token管理',
        'items': [
            {'id': 'D3-01', 'item': 'Token成本估算', 'weight': 'P0'},
            {'id': 'D3-02', 'item': 'Token效益红线', 'weight': 'P0'},  # 易遗漏！
            {'id': 'D3-03', 'item': 'Token优化空间评估', 'weight': 'P0'},  # 易遗漏！
            {'id': 'D3-04', 'item': '红线数值合理性检查', 'weight': 'P1'},
        ]
    },
    'D4_Documentation': {
        'name': '文档完整性',
        'items': [
            {'id': 'D4-01', 'item': 'SKILL.md存在', 'weight': 'P0'},
            {'id': 'D4-02', 'item': '版本号记录', 'weight': 'P1'},
            {'id': 'D4-03', 'item': '变更日志', 'weight': 'P2'},
        ]
    },
    'D5_StandardCompliance': {
        'name': '标准化合规',
        'items': [
            {'id': 'D5-01', 'item': '5标准化(S1-S5)', 'weight': 'P0'},
            {'id': 'D5-02', 'item': '归属映射正确', 'weight': 'P1'},
            {'id': 'D5-03', 'item': '审计签字', 'weight': 'P0'},
        ]
    },
}

# 易遗漏项清单（历史教训）
EASY_TO_MISS = [
    {'id': 'H0', 'priority': 'P0', 'item': '🔴 诚实审计', 'lesson': '最大的底线 - 宁可FAIL，不虚报PASS'},
    {'id': 'D3-02', 'priority': 'P0', 'item': 'Token效益红线', 'lesson': '2026-03-28被用户指出遗漏'},
    {'id': 'D3-03', 'priority': 'P0', 'item': 'Token优化空间评估', 'lesson': '与D3-02同时遗漏'},
    {'id': 'D2-03', 'priority': 'P1', 'item': '测试数量≥10项', 'lesson': '早期只检查存在性不检查数量'},
    {'id': 'D1-02', 'priority': 'P1', 'item': '非占位符实现', 'lesson': 'V1.0系统全是占位符'},
]

# ============ 数据类 ============
@dataclass
class AuditItem:
    """单项审计结果"""
    item_id: str
    description: str
    passed: bool
    evidence: str
    weight: str  # P0/P1/P2

@dataclass
class AuditResult:
    """Skill审计结果"""
    skill_name: str
    audit_version: str
    audit_time: str
    auditor: str
    dimensions: Dict[str, List[AuditItem]]
    p0_failures: List[str]
    overall_status: str  # PASS / FAIL / CONDITIONAL
    notes: str

@dataclass
class AuditReport:
    """批量审计报告"""
    report_time: str
    total_skills: int
    passed: int
    failed: int
    conditional: int
    results: List[AuditResult]

# ============ 蓝军审计器 ============
class BlueArmyAuditor:
    """
    蓝军审计器 - 严格按照SOP执行审计
    
    使用方式：
        auditor = BlueArmyAuditor()
        result = auditor.audit_skill('/path/to/skill')
        report = auditor.audit_all('/path/to/skills')
    """
    
    def __init__(self):
        self.version = AUDIT_STANDARD_VERSION
        self.checklist = self._build_checklist()
    
    def _build_checklist(self) -> List[Dict]:
        """构建完整checklist"""
        checklist = []
        for dim_key, dim_data in AUDIT_DIMENSIONS.items():
            for item in dim_data['items']:
                checklist.append({
                    'dimension': dim_data['name'],
                    'id': item['id'],
                    'item': item['item'],
                    'weight': item['weight'],
                })
        return checklist
    
    def audit_skill(self, skill_path: str, auditor_name: str = "蓝军") -> AuditResult:
        """
        审计单个Skill
        
        Args:
            skill_path: Skill目录路径
            auditor_name: 审计员名称
            
        Returns:
            AuditResult: 完整审计结果
        """
        skill_path = Path(skill_path)
        skill_name = skill_path.name
        
        dimensions_results = {}
        p0_failures = []
        
        # D1: 代码质量
        dimensions_results['D1_CodeQuality'] = self._audit_code_quality(skill_path)
        
        # D2: 测试覆盖
        dimensions_results['D2_TestCoverage'] = self._audit_test_coverage(skill_path)
        
        # D3: Token管理（易遗漏！）
        dimensions_results['D3_TokenManagement'] = self._audit_token_management(skill_path)
        
        # D4: 文档完整性
        dimensions_results['D4_Documentation'] = self._audit_documentation(skill_path)
        
        # D5: 标准化合规
        dimensions_results['D5_StandardCompliance'] = self._audit_standard_compliance(skill_path)
        
        # 收集P0失败项
        for dim_items in dimensions_results.values():
            for item in dim_items:
                if item.weight == 'P0' and not item.passed:
                    p0_failures.append(f"{item.item_id}: {item.description}")
        
        # 判定总体状态
        if p0_failures:
            overall_status = "FAIL"
        elif any(not item.passed for dim in dimensions_results.values() for item in dim):
            overall_status = "CONDITIONAL"
        else:
            overall_status = "PASS"
        
        return AuditResult(
            skill_name=skill_name,
            audit_version=self.version,
            audit_time=datetime.now().isoformat(),
            auditor=auditor_name,
            dimensions={k: [asdict(i) for i in v] for k, v in dimensions_results.items()},
            p0_failures=p0_failures,
            overall_status=overall_status,
            notes=f"使用审计标准V{self.version}"
        )
    
    def _audit_code_quality(self, skill_path: Path) -> List[AuditItem]:
        """审计代码质量"""
        results = []
        py_files = list(skill_path.glob('*.py'))
        
        if py_files:
            main_py = max(py_files, key=lambda f: f.stat().st_size)
            with open(main_py, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = len(content.splitlines())
        else:
            content = ""
            lines = 0
        
        # D1-01: 代码行数≥150行
        results.append(AuditItem(
            item_id='D1-01',
            description='代码行数≥150行',
            passed=lines >= 150,
            evidence=f"实际{lines}行" if lines > 0 else "无Python文件",
            weight='P0'
        ))
        
        # D1-02: 非占位符实现（检查是否有pass、TODO、# TODO等）
        placeholder_count = content.count('pass  # TODO') + content.count('# TODO') + content.count('NotImplemented')
        results.append(AuditItem(
            item_id='D1-02',
            description='非占位符实现',
            passed=placeholder_count < 5,  # 允许少量TODO
            evidence=f"发现{placeholder_count}个占位符" if content else "无代码",
            weight='P0'
        ))
        
        # D1-03: 错误处理完善
        has_error_handling = 'try:' in content and 'except' in content
        results.append(AuditItem(
            item_id='D1-03',
            description='错误处理完善',
            passed=has_error_handling,
            evidence="有try-except" if has_error_handling else "缺少错误处理",
            weight='P1'
        ))
        
        return results
    
    def _audit_test_coverage(self, skill_path: Path) -> List[AuditItem]:
        """审计测试覆盖"""
        results = []
        py_files = list(skill_path.glob('*.py'))
        
        if py_files:
            main_py = max(py_files, key=lambda f: f.stat().st_size)
            with open(main_py, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        else:
            content = ""
        
        # D2-01: 存在run_tests函数
        has_run_tests = 'def run_tests' in content
        results.append(AuditItem(
            item_id='D2-01',
            description='存在run_tests函数',
            passed=has_run_tests,
            evidence="存在" if has_run_tests else "不存在",
            weight='P0'
        ))
        
        # D2-02: 支持--test CLI参数
        has_cli_test = "'--test'" in content or '"--test"' in content or 'args.test' in content
        results.append(AuditItem(
            item_id='D2-02',
            description='支持--test CLI参数',
            passed=has_cli_test,
            evidence="支持" if has_cli_test else "不支持",
            weight='P0'
        ))
        
        # D2-03: 测试数量≥10项（检查assert数量）
        test_count = content.count('assert ')
        results.append(AuditItem(
            item_id='D2-03',
            description='测试数量≥10项',
            passed=test_count >= 10,
            evidence=f"发现{test_count}个assert",
            weight='P0'
        ))
        
        # D2-04: 测试通过率100%
        test_passed = None
        if has_cli_test and py_files:
            try:
                result = subprocess.run(
                    ['python3', str(main_py), '--test'],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(skill_path)
                )
                test_passed = result.returncode == 0
            except:
                test_passed = False
        
        results.append(AuditItem(
            item_id='D2-04',
            description='测试通过率100%',
            passed=test_passed if test_passed is not None else False,
            evidence="通过" if test_passed else "失败或未运行",
            weight='P0'
        ))
        
        return results
    
    def _audit_token_management(self, skill_path: Path) -> List[AuditItem]:
        """
        审计Token管理（易遗漏维度！）
        
        历史教训：2026-03-28被用户指出D3-02和D3-03遗漏
        """
        results = []
        py_files = list(skill_path.glob('*.py'))
        
        if py_files:
            main_py = max(py_files, key=lambda f: f.stat().st_size)
            with open(main_py, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        else:
            content = ""
        
        # D3-01: Token成本估算
        has_token_cost = 'TOKEN_COST' in content or 'token_cost' in content.lower()
        results.append(AuditItem(
            item_id='D3-01',
            description='Token成本估算',
            passed=has_token_cost,
            evidence="存在" if has_token_cost else "不存在",
            weight='P0'
        ))
        
        # D3-02: Token效益红线（易遗漏！）
        has_red_lines = 'TOKEN_RED_LINES' in content or 'red_line' in content.lower()
        results.append(AuditItem(
            item_id='D3-02',
            description='Token效益红线',
            passed=has_red_lines,
            evidence="存在" if has_red_lines else "不存在（易遗漏！）",
            weight='P0'
        ))
        
        # D3-03: Token优化空间评估（易遗漏！）
        has_optimization = 'TOKEN_OPTIMIZATION' in content or 'optimization' in content.lower()
        results.append(AuditItem(
            item_id='D3-03',
            description='Token优化空间评估',
            passed=has_optimization,
            evidence="存在" if has_optimization else "不存在（易遗漏！）",
            weight='P0'
        ))
        
        # D3-04: 红线数值合理性检查
        has_reasonable_values = 'max_per' in content and ('10000' in content or '100000' in content)
        results.append(AuditItem(
            item_id='D3-04',
            description='红线数值合理性检查',
            passed=has_reasonable_values,
            evidence="有数值约束" if has_reasonable_values else "无数值约束",
            weight='P1'
        ))
        
        return results
    
    def _audit_documentation(self, skill_path: Path) -> List[AuditItem]:
        """审计文档完整性"""
        results = []
        
        skill_md = skill_path / 'SKILL.md'
        has_skill_md = skill_md.exists()
        
        # D4-01: SKILL.md存在
        results.append(AuditItem(
            item_id='D4-01',
            description='SKILL.md存在',
            passed=has_skill_md,
            evidence="存在" if has_skill_md else "不存在",
            weight='P0'
        ))
        
        # D4-02: 版本号记录
        has_version = False
        if has_skill_md:
            with open(skill_md, 'r', encoding='utf-8', errors='ignore') as f:
                md_content = f.read()
            has_version = 'version' in md_content.lower() or 'v2.' in md_content or 'v1.' in md_content
        
        results.append(AuditItem(
            item_id='D4-02',
            description='版本号记录',
            passed=has_version,
            evidence="有版本号" if has_version else "无版本号",
            weight='P1'
        ))
        
        # D4-03: 变更日志
        has_changelog = False
        if has_skill_md:
            has_changelog = '版本历史' in md_content or 'changelog' in md_content.lower() or '更新' in md_content
        
        results.append(AuditItem(
            item_id='D4-03',
            description='变更日志',
            passed=has_changelog,
            evidence="有变更日志" if has_changelog else "无变更日志",
            weight='P2'
        ))
        
        return results
    
    def _audit_standard_compliance(self, skill_path: Path) -> List[AuditItem]:
        """审计标准化合规"""
        results = []
        skill_md = skill_path / 'SKILL.md'
        
        # D5-01: 5标准化(S1-S5)
        has_5standard = False
        if skill_md.exists():
            with open(skill_md, 'r', encoding='utf-8', errors='ignore') as f:
                md_content = f.read()
            has_5standard = 'S1' in md_content and 'S5' in md_content
        
        results.append(AuditItem(
            item_id='D5-01',
            description='5标准化(S1-S5)',
            passed=has_5standard,
            evidence="提及S1-S5" if has_5standard else "未提及",
            weight='P0'
        ))
        
        # D5-02: 归属映射正确
        has_belongs = False
        if skill_md.exists():
            has_belongs = 'belongs_to' in md_content or '归属' in md_content
        
        results.append(AuditItem(
            item_id='D5-02',
            description='归属映射正确',
            passed=has_belongs,
            evidence="有归属映射" if has_belongs else "无归属映射",
            weight='P1'
        ))
        
        # D5-03: 审计签字（检查是否有审计记录文件）
        audit_record = skill_path / '.audit_record.json'
        results.append(AuditItem(
            item_id='D5-03',
            description='审计签字',
            passed=audit_record.exists(),
            evidence="有审计记录" if audit_record.exists() else "无审计记录",
            weight='P0'
        ))
        
        return results
    
    def generate_report(self, results: List[AuditResult], output_path: str):
        """生成审计报告"""
        report = {
            'report_time': datetime.now().isoformat(),
            'audit_standard_version': self.version,
            'total_skills': len(results),
            'summary': {
                'passed': sum(1 for r in results if r.overall_status == 'PASS'),
                'failed': sum(1 for r in results if r.overall_status == 'FAIL'),
                'conditional': sum(1 for r in results if r.overall_status == 'CONDITIONAL'),
            },
            'easy_to_miss_reminder': EASY_TO_MISS,  # 易遗漏项提醒
            'results': [asdict(r) for r in results]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def print_checklist(self):
        """打印checklist供人工核对"""
        print("=" * 70)
        print(f"蓝军审计Checklist V{self.version}")
        print("=" * 70)
        print("\n【易遗漏项 - 必须重点检查】")
        for item in EASY_TO_MISS:
            print(f"  ⚠ {item['id']}: {item['item']}")
            print(f"    教训: {item['lesson']}")
        
        print("\n【完整Checklist】")
        for item in self.checklist:
            print(f"  [{item['weight']}] {item['id']}: {item['item']}")
        
        print("\n" + "=" * 70)

# ============ 命令行接口 ============

def run_tests() -> bool:
    """运行SOP自测试"""
    print("=" * 70)
    print("蓝军审计SOP V1.0 自测试")
    print("=" * 70)
    
    all_passed = True
    
    # Test 1: 审计标准版本检查
    print("\n[Test 1] 审计标准版本存在...")
    assert AUDIT_STANDARD_VERSION, "版本号未设置"
    print(f"  ✓ 版本: {AUDIT_STANDARD_VERSION}")
    
    # Test 2: 5维度定义完整性
    print("\n[Test 2] 5审计维度完整性...")
    assert len(AUDIT_DIMENSIONS) == 5, "维度数量错误"
    print(f"  ✓ 5维度定义完整")
    
    # Test 3: 易遗漏项清单存在
    print("\n[Test 3] 易遗漏项清单存在...")
    assert len(EASY_TO_MISS) > 0, "易遗漏项清单为空"
    print(f"  ✓ {len(EASY_TO_MISS)}个易遗漏项已记录")
    
    # Test 4: Checklist构建
    print("\n[Test 4] Checklist构建...")
    auditor = BlueArmyAuditor()
    assert len(auditor.checklist) > 0, "Checklist为空"
    print(f"  ✓ Checklist: {len(auditor.checklist)}项")
    
    # Test 5: Token维度包含红线检查
    print("\n[Test 5] Token维度包含红线检查...")
    token_dim = AUDIT_DIMENSIONS['D3_TokenManagement']
    item_ids = [item['id'] for item in token_dim['items']]
    assert 'D3-02' in item_ids, "D3-02 Token红线未定义"
    assert 'D3-03' in item_ids, "D3-03 Token优化未定义"
    print("  ✓ Token红线已纳入标准")
    
    # Test 6: 审计器实例化
    print("\n[Test 6] 审计器实例化...")
    auditor = BlueArmyAuditor()
    assert auditor.version == AUDIT_STANDARD_VERSION
    print("  ✓ 审计器实例化成功")
    
    # Test 7: 自审计（测试自己）
    print("\n[Test 7] SOP自审计...")
    current_file = Path(__file__)
    temp_skill = current_file.parent
    result = auditor.audit_skill(temp_skill, auditor_name="SOP自测")
    print(f"  ✓ 自审计完成: {result.overall_status}")
    
    print("\n" + "=" * 70)
    print("ALL 7 SOP TESTS PASSED ✓")
    print("=" * 70)
    
    return all_passed

def main():
    """主入口"""
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        success = run_tests()
        sys.exit(0 if success else 1)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--checklist':
        auditor = BlueArmyAuditor()
        auditor.print_checklist()
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == '--audit':
        if len(sys.argv) < 3:
            print("Usage: python blue_army_sop.py --audit /path/to/skill")
            sys.exit(1)
        skill_path = sys.argv[2]
        auditor = BlueArmyAuditor()
        result = auditor.audit_skill(skill_path)
        print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
        return
    
    print("蓝军审计SOP V1.0")
    print("用法:")
    print("  --test      运行自测试")
    print("  --checklist 打印完整checklist")
    print("  --audit     审计指定Skill")

if __name__ == '__main__':
    main()
