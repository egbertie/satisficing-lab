#!/usr/bin/env python3
"""
蓝军深度洞察审计模块
检查每个产出是否有完整的L1-L5深度洞察

来源: 第六类任务整改 - Skill闭环升级
创建时间: 2026-03-31
"""

import sys
import re
from pathlib import Path

class DeepInsightAuditor:
    """深度洞察审计器"""
    
    def __init__(self):
        self.required_sections = ["L1", "L2", "L3", "L4", "L5"]
        self.errors = []
    
    def audit_file(self, filepath):
        """审计单个文件"""
        path = Path(filepath)
        
        if not path.exists():
            self.errors.append(f"❌ 文件不存在: {filepath}")
            return False
        
        content = path.read_text(encoding='utf-8')
        
        # 检查是否有深度洞察部分
        if "深度洞察" not in content and "五层深挖" not in content:
            self.errors.append(f"❌ {filepath}: 缺少深度洞察部分")
            return False
        
        # 检查L1-L5完整性
        missing_sections = []
        for section in self.required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            self.errors.append(f"⚠️ {filepath}: 缺少 {', '.join(missing_sections)}")
            return False
        
        # 检查L3是否深挖到根因
        l3_content = self._extract_section(content, "L3")
        if l3_content and not self._has_root_cause_depth(l3_content):
            self.errors.append(f"⚠️ {filepath}: L3未深挖到根因（缺乏'根因'/'人性'/'认知'关键词）")
            return False
        
        # 检查L5是否有可执行指导
        l5_content = self._extract_section(content, "L5")
        if l5_content and not self._has_executable_guidance(l5_content):
            self.errors.append(f"⚠️ {filepath}: L5缺乏可执行指导（无具体步骤/方案）")
            return False
        
        print(f"✅ {filepath}: 深度洞察完整")
        return True
    
    def _extract_section(self, content, section_name):
        """提取特定章节内容"""
        pattern = rf"### {section_name}.*?(?=###|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(0) if match else ""
    
    def _has_root_cause_depth(self, content):
        """检查是否深挖到根因"""
        root_cause_keywords = ["根因", "人性", "认知", "本质", "深层"]
        return any(kw in content for kw in root_cause_keywords)
    
    def _has_executable_guidance(self, content):
        """检查是否有可执行指导"""
        executable_keywords = ["步骤", "方案", "原则", "执行", "可执行"]
        return any(kw in content for kw in executable_keywords)
    
    def audit_directory(self, directory, pattern="*.md"):
        """审计整个目录"""
        path = Path(directory)
        files = list(path.rglob(pattern))
        
        print(f"🔍 审计目录: {directory}")
        print(f"   找到 {len(files)} 个文件")
        print()
        
        passed = 0
        failed = 0
        
        for file in files:
            # 跳过某些目录
            if "z_archive" in str(file) or "__pycache__" in str(file):
                continue
            
            if self.audit_file(file):
                passed += 1
            else:
                failed += 1
        
        print()
        print("=" * 50)
        print(f"审计结果: 通过 {passed}, 失败 {failed}, 总计 {passed + failed}")
        
        if self.errors:
            print("\n❌ 错误详情:")
            for error in self.errors:
                print(f"   {error}")
        
        return failed == 0

# 使用示例
if __name__ == "__main__":
    auditor = DeepInsightAuditor()
    
    # 审计skills目录
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "/root/.openclaw/workspace/skills"
    
    success = auditor.audit_directory(target, "SKILL.md")
    
    if not success:
        print("\n🔴 深度洞察审计未通过，请修复以上问题")
        sys.exit(1)
    else:
        print("\n✅ 深度洞察审计通过")
        sys.exit(0)
