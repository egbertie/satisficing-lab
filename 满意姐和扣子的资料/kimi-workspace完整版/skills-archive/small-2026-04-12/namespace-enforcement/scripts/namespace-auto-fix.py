#!/usr/bin/env python3
"""
Namespace Auto-Fix - 自动修复脚本
S4: 自动化集成 - 自动修复建议
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any

# 导入检查器
sys.path.insert(0, str(Path(__file__).parent))

import importlib.util
spec = importlib.util.spec_from_file_location("namespace_checker", str(Path(__file__).parent / "namespace-checker.py"))
namespace_checker_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(namespace_checker_module)
NamespaceChecker = namespace_checker_module.NamespaceChecker
ViolationType = namespace_checker_module.ViolationType


class NamespaceAutoFix:
    """自动修复器"""
    
    def __init__(self, checker: NamespaceChecker):
        self.checker = checker
        self.fixes_applied: List[Dict[str, Any]] = []
        self.fixes_skipped: List[Dict[str, Any]] = []
    
    def generate_fix(self, violation) -> Optional[str]:
        """
        为违规生成修复后的文件名
        
        修复规则:
        1. 大写 → 小写
        2. 空格 → 连字符
        3. 非法字符 → 移除
        4. 添加类型前缀
        """
        path = Path(violation.file_path)
        filename = path.name
        stem = path.stem
        suffix = path.suffix
        
        new_stem = stem
        
        # 处理大写
        if violation.violation_type == ViolationType.UPPERCASE:
            new_stem = new_stem.lower()
        
        # 处理空格
        if violation.violation_type == ViolationType.SPACES:
            new_stem = new_stem.replace(' ', '-')
        
        # 处理非法字符
        if violation.violation_type == ViolationType.INVALID_CHARS:
            forbidden = self.checker.rules.get("rules", {}).get("characters", {}).get("forbidden", "")
            for char in forbidden:
                new_stem = new_stem.replace(char, '')
            # 特殊处理
            new_stem = new_stem.replace('_', '-')
        
        # 处理缺失类型前缀
        if violation.violation_type == ViolationType.MISSING_TYPE:
            if suffix == '.md':
                if 'skills/' in str(path):
                    new_stem = f"skill-{new_stem.lower()}"
                elif 'docs/' in str(path):
                    new_stem = f"doc-{new_stem.lower()}"
                elif 'scripts/' in str(path):
                    new_stem = f"script-{new_stem.lower()}"
        
        # 处理多种违规的组合
        # 先统一转为小写
        new_stem = new_stem.lower()
        # 替换空格为连字符
        new_stem = new_stem.replace(' ', '-')
        # 移除非法字符
        allowed = set('abcdefghijklmnopqrstuvwxyz0123456789-.')
        new_stem = ''.join(c for c in new_stem if c in allowed)
        # 移除连续的连字符
        while '--' in new_stem:
            new_stem = new_stem.replace('--', '-')
        # 移除首尾连字符
        new_stem = new_stem.strip('-')
        
        new_filename = f"{new_stem}{suffix}"
        
        # 如果新名称与旧名称相同，返回None
        return new_filename if new_filename != filename else None
    
    def preview_fixes(self, directory: str) -> List[Dict[str, Any]]:
        """
        预览所有可修复的文件（dry-run模式）
        
        返回修复建议列表
        """
        # 扫描目录获取违规
        result = self.checker.scan_directory(directory)
        
        suggestions = []
        for violation in result.violations:
            if not violation.auto_fixable:
                self.fixes_skipped.append({
                    "file": violation.file_path,
                    "reason": "无法自动修复",
                    "violation": violation.violation_type.value
                })
                continue
            
            # S6: 存量文件不强制迁移
            if violation.legacy_file:
                enforcement = self.checker.rules.get("enforcement", {})
                if not enforcement.get("strict_mode", False):
                    self.fixes_skipped.append({
                        "file": violation.file_path,
                        "reason": "存量文件，不强制迁移 (S6认知谦逊)",
                        "violation": violation.violation_type.value,
                        "legacy": True
                    })
                    continue
            
            fixed_name = self.generate_fix(violation)
            if fixed_name:
                path = Path(violation.file_path)
                new_path = path.parent / fixed_name
                
                suggestions.append({
                    "original": violation.file_path,
                    "original_name": path.name,
                    "suggested": str(new_path),
                    "suggested_name": fixed_name,
                    "violation_type": violation.violation_type.value,
                    "message": violation.message,
                    "legacy": violation.legacy_file
                })
        
        return suggestions
    
    def apply_fixes(self, suggestions: List[Dict[str, Any]], confirm: bool = True) -> bool:
        """
        应用修复
        
        Args:
            suggestions: 修复建议列表
            confirm: 是否要求确认
        
        Returns:
            是否成功
        """
        if not suggestions:
            print("没有需要修复的文件")
            return True
        
        print(f"\n准备修复 {len(suggestions)} 个文件:")
        print("-" * 60)
        
        for i, sugg in enumerate(suggestions, 1):
            legacy_marker = " [存量]" if sugg.get("legacy") else ""
            print(f"\n{i}.{legacy_marker}")
            print(f"  原文件名: {sugg['original_name']}")
            print(f"  新文件名: {sugg['suggested_name']}")
            print(f"  违规类型: {sugg['violation_type']}")
        
        print("-" * 60)
        
        if confirm:
            response = input("\n确认应用以上修复? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("已取消")
                return False
        
        # 执行修复
        applied = 0
        failed = 0
        
        for sugg in suggestions:
            try:
                old_path = Path(sugg['original'])
                new_path = Path(sugg['suggested'])
                
                # 检查目标是否已存在
                if new_path.exists():
                    print(f"⚠️  跳过: 目标文件已存在 {new_path}")
                    self.fixes_skipped.append({
                        "file": sugg['original'],
                        "reason": "目标文件已存在"
                    })
                    failed += 1
                    continue
                
                # 执行重命名
                old_path.rename(new_path)
                
                self.fixes_applied.append({
                    "original": str(old_path),
                    "new": str(new_path),
                    "violation_type": sugg['violation_type']
                })
                
                print(f"✅ 已修复: {sugg['original_name']} → {sugg['suggested_name']}")
                applied += 1
                
            except Exception as e:
                print(f"❌ 失败: {sugg['original']} - {e}")
                self.fixes_skipped.append({
                    "file": sugg['original'],
                    "reason": str(e)
                })
                failed += 1
        
        print(f"\n修复完成: 成功 {applied} 个, 失败 {failed} 个")
        return failed == 0
    
    def generate_fix_report(self, output_path: Optional[str] = None) -> str:
        """生成修复报告"""
        report = {
            "fixes_applied": self.fixes_applied,
            "fixes_skipped": self.fixes_skipped,
            "total_applied": len(self.fixes_applied),
            "total_skipped": len(self.fixes_skipped),
            "s6_notice": "存量文件遵循S6认知谦逊原则，不强制迁移"
        }
        
        report_json = json.dumps(report, indent=2, ensure_ascii=False)
        
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_json)
            print(f"修复报告已保存: {output_path}")
        
        return report_json


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="Namespace Auto-Fix - 自动修复工具")
    parser.add_argument("--scan", "-s", required=True, help="扫描目录路径")
    parser.add_argument("--dry-run", "-d", help="仅预览修复，不实际应用", action="store_true")
    parser.add_argument("--apply", "-a", help="应用修复", action="store_true")
    parser.add_argument("--yes", "-y", help="自动确认，不提示", action="store_true")
    parser.add_argument("--output", "-o", help="报告输出路径")
    parser.add_argument("--rules", help="自定义规则文件路径")
    parser.add_argument("--include-legacy", help="包含存量文件（默认跳过）", action="store_true")
    
    args = parser.parse_args()
    
    # 初始化
    checker = NamespaceChecker(rules_path=args.rules)
    
    # 如果指定了包含存量文件，临时修改规则
    if args.include_legacy:
        checker.rules["enforcement"]["strict_mode"] = True
    
    auto_fix = NamespaceAutoFix(checker)
    
    # 预览修复
    print("正在分析修复建议...")
    suggestions = auto_fix.preview_fixes(args.scan)
    
    if not suggestions:
        print("\n没有可自动修复的文件")
        if auto_fix.fixes_skipped:
            print(f"\n跳过的文件 ({len(auto_fix.fixes_skipped)} 个):")
            for skip in auto_fix.fixes_skipped[:10]:
                print(f"  - {skip['file']}: {skip['reason']}")
        return
    
    print(f"\n发现 {len(suggestions)} 个可修复的文件")
    
    # 仅预览模式
    if args.dry_run or not args.apply:
        print("\n修复建议预览 (dry-run模式):")
        print("=" * 60)
        
        for i, sugg in enumerate(suggestions, 1):
            legacy_marker = " [存量]" if sugg.get("legacy") else ""
            print(f"\n{i}.{legacy_marker}")
            print(f"  违规: {sugg['message']}")
            print(f"  {sugg['original_name']}")
            print(f"  → {sugg['suggested_name']}")
        
        if not args.apply:
            print("\n" + "=" * 60)
            print("使用 --apply 应用修复")
            print("使用 --apply --yes 自动确认应用")
        
        # 保存预览报告
        if args.output:
            preview_report = {
                "mode": "dry-run",
                "suggestions": suggestions,
                "skipped": auto_fix.fixes_skipped
            }
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(preview_report, f, indent=2, ensure_ascii=False)
            print(f"\n预览报告已保存: {args.output}")
    
    # 应用修复
    if args.apply:
        success = auto_fix.apply_fixes(suggestions, confirm=not args.yes)
        
        if args.output:
            auto_fix.generate_fix_report(args.output)
        
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
