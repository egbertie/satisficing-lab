#!/usr/bin/env python3
"""
满意解知识管理系统 - 一致性检查脚本
自动检测全局不一致问题

使用方式:
  python3 scripts/consistency_check.py
"""

import re
from pathlib import Path
from colorama import Fore, Style

class ConsistencyChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def check_wulu_totem(self):
        """检查五路图腾定义一致性"""
        print("\n🔍 检查五路图腾定义...")
        
        # 读取core定义
        core_file = Path("core/五路图腾.yaml")
        if core_file.exists():
            with open(core_file, 'r', encoding='utf-8') as f:
                core_content = f.read()
                
            # 检查CONFUCIUS在core中的定义
            if '合伙人伦理与信任治理' in core_content:
                correct_dimension = '合伙人伦理与信任治理'
            else:
                correct_dimension = None
        else:
            self.warnings.append("core/五路图腾.yaml 不存在")
            return
            
        # 检查所有工作文档
        working_docs = [
            "A满意哥专属文件夹/02_✅成果交付/满意解研究所_V1.3_完全版本.md",
            "A满意哥专属文件夹/02_✅成果交付/战略定位1.1版本_满意解研究所.md"
        ]
        
        outdated_patterns = [
            (r'生生不息', 'CONFUCIUS核心精神应为"仁义礼智信"'),
            (r'感知力训练.*直觉', 'CONFUCIUS决策维度应为"合伙人伦理"'),
            (r'孔子/儒商', 'CONFUCIUS名称应为"孔子"（不含儒商）'),
            (r'XU先生', '应改为CONFUCIUS'),
        ]
        
        for doc_path in working_docs:
            doc = Path(doc_path)
            if not doc.exists():
                continue
                
            with open(doc, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern, message in outdated_patterns:
                if re.search(pattern, content):
                    self.errors.append(f"{doc.name}: 发现过时表述 - {message}")
                    
    def check_expert_annotations(self):
        """检查专家标注一致性"""
        print("\n🔍 检查专家标注...")
        
        experts = ['黎红雷', '罗汉', '谢宝剑', '李泽湘', '方翊沣', '陈国祥']
        
        working_docs = [
            "A满意哥专属文件夹/02_✅成果交付/满意解研究所_V1.3_完全版本.md",
            "A满意哥专属文件夹/02_✅成果交付/战略定位1.1版本_满意解研究所.md"
        ]
        
        for doc_path in working_docs:
            doc = Path(doc_path)
            if not doc.exists():
                continue
                
            with open(doc, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for expert in experts:
                # 检查专家名是否出现但未标注（拟邀）
                pattern = rf'{expert}[^（）]*?(?!（拟邀）)[^\n]*?'
                if expert in content and f'{expert}（拟邀）' not in content:
                    # 再精确检查
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if expert in line and '（拟邀）' not in line and '学术顾问团队' not in line:
                            # 排除已经是括号内的情况
                            if not re.search(rf'{re.escape(expert)}.*?[（(]', line):
                                self.errors.append(f"{doc.name}:{line_num} {expert} 缺少'（拟邀）'标注")
                                break
                                
    def check_geographic_terms(self):
        """检查地理定位术语"""
        print("\n🔍 检查地理定位...")
        
        working_docs = [
            "A满意哥专属文件夹/02_✅成果交付/满意解研究所_V1.3_完全版本.md",
            "A满意哥专属文件夹/02_✅成果交付/战略定位1.1版本_满意解研究所.md"
        ]
        
        for doc_path in working_docs:
            doc = Path(doc_path)
            if not doc.exists():
                continue
                
            with open(doc, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查是否错误使用"大湾区"
            if '大湾区' in content and '深港' not in content:
                self.warnings.append(f"{doc.name}: 使用'大湾区'，建议改为'深港'")
                
    def check_file_sync_status(self):
        """检查文件同步状态"""
        print("\n🔍 检查文件同步状态...")
        
        import filecmp
        
        pairs = [
            (
                "A满意哥专属文件夹/02_✅成果交付/满意解研究所_V1.3_完全版本.md",
                "A满意哥专属文件夹/99_📦完整下载包/V2.0_技术跃升成果集/满意解研究所_V1.3_完全版本.md"
            ),
            (
                "A满意哥专属文件夹/02_✅成果交付/战略定位1.1版本_满意解研究所.md",
                "A满意哥专属文件夹/99_📦完整下载包/V2.0_技术跃升成果集/战略定位1.1版本_满意解研究所.md"
            )
        ]
        
        for source, target in pairs:
            source_path = Path(source)
            target_path = Path(target)
            
            if not source_path.exists():
                continue
                
            if not target_path.exists():
                self.warnings.append(f"{target_path.name}: 下载包中不存在")
            elif not filecmp.cmp(source_path, target_path, shallow=False):
                self.errors.append(f"{target_path.name}: 与源文件不一致，需要同步")
                
    def generate_report(self):
        """生成检查报告"""
        print("\n" + "="*60)
        print("📊 一致性检查报告")
        print("="*60)
        
        if self.errors:
            print(f"\n{Fore.RED}❌ 发现 {len(self.errors)} 个错误:{Style.RESET_ALL}")
            for error in self.errors:
                print(f"  • {error}")
        else:
            print(f"\n{Fore.GREEN}✅ 未发现错误{Style.RESET_ALL}")
            
        if self.warnings:
            print(f"\n{Fore.YELLOW}⚠️ 发现 {len(self.warnings)} 个警告:{Style.RESET_ALL}")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        print("\n" + "="*60)
        
        if self.errors:
            print(f"\n{Fore.RED}请运行: python3 scripts/sync_from_core.py 修复{Style.RESET_ALL}")
        elif self.warnings:
            print(f"\n{Fore.YELLOW}建议检查警告项{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.GREEN}✨ 所有检查通过！{Style.RESET_ALL}")
            
    def run(self):
        """运行完整检查流程"""
        print("="*60)
        print("🚀 满意解知识管理系统 - 一致性检查")
        print("="*60)
        
        self.check_wulu_totem()
        self.check_expert_annotations()
        self.check_geographic_terms()
        self.check_file_sync_status()
        self.generate_report()

if __name__ == "__main__":
    checker = ConsistencyChecker()
    checker.run()
