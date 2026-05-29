#!/usr/bin/env python3
"""
质量门禁基础检查脚本
功能：自动化执行基础质量检查，减少Token消耗
作者：满意解研究所
版本：1.0.0
"""

import os
import sys
import re
import yaml
from pathlib import Path
from typing import List, Tuple, Dict

class QualityGateChecker:
    """质量门禁检查器"""
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.issues = []
        self.warnings = []
        
    def check_file_exists(self) -> bool:
        """S1: 检查SKILL.md是否存在"""
        skill_file = self.skill_path / "SKILL.md"
        if not skill_file.exists():
            self.issues.append("❌ SKILL.md 不存在")
            return False
        return True
    
    def check_frontmatter(self, content: str) -> bool:
        """S2: 检查YAML frontmatter"""
        # 检查是否有frontmatter分隔符
        if not content.startswith('---'):
            self.issues.append("❌ 缺少YAML frontmatter起始标记")
            return False
        
        # 提取frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            self.issues.append("❌ YAML frontmatter格式错误")
            return False
        
        try:
            frontmatter = yaml.safe_load(parts[1])
        except yaml.YAMLError as e:
            self.issues.append(f"❌ YAML解析错误: {e}")
            return False
        
        # 检查必需字段
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in frontmatter:
                self.issues.append(f"❌ 缺少必需字段: {field}")
        
        # 检查name格式（kebab-case）
        if 'name' in frontmatter:
            name = frontmatter['name']
            if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
                self.warnings.append(f"⚠️ name建议用kebab-case: {name}")
        
        return len(self.issues) == 0
    
    def check_sections(self, content: str) -> bool:
        """S3: 检查必需章节"""
        required_sections = [
            ('# ', '标题'),  # H1标题
            ('## Inputs', 'Inputs'),
            ('## Output', 'Output'),
            ('## Process', 'Process'),
        ]
        
        for pattern, name in required_sections:
            if pattern not in content:
                self.issues.append(f"❌ 缺少必需章节: {name}")
        
        # 推荐章节检查（只警告）
        recommended_sections = [
            ('## Examples', 'Examples'),
            ('## Troubleshooting', 'Troubleshooting'),
        ]
        
        for pattern, name in recommended_sections:
            if pattern not in content:
                self.warnings.append(f"⚠️ 建议添加章节: {name}")
        
        return len([i for i in self.issues if i.startswith('❌')]) == 0
    
    def check_line_count(self, content: str) -> bool:
        """S4: 检查行数"""
        lines = content.split('\n')
        if len(lines) > 500:
            self.warnings.append(f"⚠️ SKILL.md超过500行({len(lines)}行)，建议精简或拆分")
        return True
    
    def check_description_format(self, content: str) -> bool:
        """S5: 检查description格式"""
        # 提取description
        match = re.search(r'description:\s*\|\s*\n?\s*([^\n]+(?:\n\s+[^\n]+)*)', content)
        if match:
            desc = match.group(1).strip()
            # 检查是否包含关键要素
            if 'Use when' not in desc and 'use when' not in desc.lower():
                self.warnings.append("⚠️ description建议包含触发短语(Use when...)")
        return True
    
    def check_scripts_folder(self) -> bool:
        """S6: 检查scripts文件夹"""
        scripts_dir = self.skill_path / "scripts"
        skill_md = self.skill_path / "SKILL.md"
        
        if scripts_dir.exists():
            scripts = list(scripts_dir.glob('*'))
            if scripts:
                # 检查SKILL.md是否引用了scripts
                content = skill_md.read_text(encoding='utf-8')
                for script in scripts:
                    if script.name not in content:
                        self.warnings.append(f"⚠️ scripts/{script.name} 在SKILL.md中未被引用")
        return True
    
    def run_all_checks(self) -> Tuple[bool, List[str], List[str]]:
        """运行所有检查"""
        skill_file = self.skill_path / "SKILL.md"
        
        # 基础检查
        if not self.check_file_exists():
            return False, self.issues, self.warnings
        
        content = skill_file.read_text(encoding='utf-8')
        
        # 执行所有检查
        self.check_frontmatter(content)
        self.check_sections(content)
        self.check_line_count(content)
        self.check_description_format(content)
        self.check_scripts_folder()
        
        # 判断是否通过
        critical_issues = [i for i in self.issues if i.startswith('❌')]
        passed = len(critical_issues) == 0
        
        return passed, self.issues, self.warnings


def check_all_skills(skills_dir: str = "/root/.openclaw/workspace/skills") -> Dict:
    """检查所有Skill"""
    skills_path = Path(skills_dir)
    results = {
        'passed': [],
        'failed': [],
        'total': 0
    }
    
    # 排除归档文件夹
    exclude_prefixes = ('.', '_', 'archive')
    
    for skill_dir in skills_path.iterdir():
        if not skill_dir.is_dir():
            continue
        if skill_dir.name.startswith(exclude_prefixes):
            continue
        
        results['total'] += 1
        checker = QualityGateChecker(str(skill_dir))
        passed, issues, warnings = checker.run_all_checks()
        
        if passed:
            results['passed'].append({
                'name': skill_dir.name,
                'warnings': warnings
            })
        else:
            results['failed'].append({
                'name': skill_dir.name,
                'issues': issues,
                'warnings': warnings
            })
    
    return results


def print_report(results: Dict):
    """打印检查报告"""
    print("=" * 60)
    print("质量门禁检查报告")
    print("=" * 60)
    print(f"\n总计检查: {results['total']} 个Skill")
    print(f"通过: {len(results['passed'])} 个")
    print(f"失败: {len(results['failed'])} 个")
    
    if results['failed']:
        print("\n" + "-" * 60)
        print("失败的Skill:")
        print("-" * 60)
        for item in results['failed']:
            print(f"\n📁 {item['name']}")
            for issue in item['issues']:
                print(f"   {issue}")
            for warning in item['warnings']:
                print(f"   {warning}")
    
    if results['passed']:
        print("\n" + "-" * 60)
        print("通过的Skill:")
        print("-" * 60)
        for item in results['passed']:
            print(f"\n✅ {item['name']}")
            for warning in item['warnings']:
                print(f"   {warning}")
    
    print("\n" + "=" * 60)
    if results['failed']:
        print("结果: ❌ 未通过门禁")
        sys.exit(1)
    else:
        print("结果: ✅ 通过门禁")
        sys.exit(0)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='质量门禁检查工具')
    parser.add_argument('--skill', '-s', help='检查指定Skill路径')
    parser.add_argument('--all', '-a', action='store_true', help='检查所有Skill')
    parser.add_argument('--strict', action='store_true', help='严格模式（警告视为失败）')
    
    args = parser.parse_args()
    
    if args.all:
        results = check_all_skills()
        print_report(results)
    elif args.skill:
        checker = QualityGateChecker(args.skill)
        passed, issues, warnings = checker.run_all_checks()
        
        print(f"\n检查Skill: {args.skill}")
        print("=" * 60)
        
        for issue in issues:
            print(issue)
        for warning in warnings:
            print(warning)
        
        if passed:
            print("\n✅ 通过门禁")
            sys.exit(0)
        else:
            print("\n❌ 未通过门禁")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
