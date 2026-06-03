#!/usr/bin/env python3
"""
满意解知识管理系统 - 同步脚本
从Core定义自动生成Working文档

使用方式:
  python3 scripts/sync_from_core.py

功能:
  1. 读取core/*.yaml定义
  2. 生成/更新working/*.md文档
  3. 确保全局一致性
"""

import yaml
import re
from datetime import datetime
from pathlib import Path

# 路径配置
CORE_DIR = Path("core")
WORKING_DIR = Path("A满意哥专属文件夹/02_✅成果交付")
BACKUP_DIR = Path("A满意哥专属文件夹/03_📋历史版本")

class KnowledgeSync:
    def __init__(self):
        self.core_data = {}
        self.changes = []
        
    def load_core(self):
        """加载所有Core定义文件"""
        print("📚 加载Core定义...")
        
        for yaml_file in CORE_DIR.glob("*.yaml"):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                self.core_data[yaml_file.stem] = yaml.safe_load(f)
                print(f"  ✅ 加载: {yaml_file.name}")
                
    def sync_v13(self):
        """同步V1.3完全版本"""
        print("\n🔄 同步V1.3完全版本...")
        
        target = WORKING_DIR / "满意解研究所_V1.3_完全版本.md"
        
        if not target.exists():
            print(f"  ⚠️ 目标文件不存在: {target}")
            return
            
        # 读取原文件
        with open(target, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 备份原文件
        backup_name = f"满意解研究所_V1.3_完全版本_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        backup_path = BACKUP_DIR / backup_name
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  💾 已备份: {backup_name}")
        
        # 同步五路图腾表格
        wulu = self.core_data.get('五路图腾', {}).get('五路图腾', {})
        
        # 构建新表格
        new_table = """| 图腾 | 五行 | 核心精神 | 决策维度 | 代表人物 |
|------|------|----------|----------|----------|
"""
        for key in ['LIU', 'SIMON', 'GUANYIN', 'CONFUCIUS', 'HUINENG']:
            item = wulu.get(key, {})
            new_table += f"| **{key}（{key}）** | {item.get('五行', '')} | {item.get('核心精神', '')} | {item.get('决策维度', '')} | {item.get('代表人物', '')} |\n"
            
        # 替换表格（使用正则匹配表格区域）
        table_pattern = r'\| 图腾 \| 五行 \| 核心精神 \| 决策维度 \| 代表人物 \|[\s\S]*?(?=#### 3\.3|## |$)'
        if re.search(table_pattern, content):
            content = re.sub(table_pattern, new_table + "\n", content)
            self.changes.append("V1.3: 五路图腾表格已同步")
            
        # 同步CONFUCIUS章节
        confucius = wulu.get('CONFUCIUS', {})
        new_section = f"""##### CONFUCIUS（孔子）——木

**核心精神**：{confucius.get('核心精神', '仁义礼智信')}

**决策维度**：
- 合伙人伦理：合伙关系中的仁义礼智信
- 信任治理：建立和维护合伙人之间的信任机制
- 伦理边界：商业决策中的儒家伦理底线

**应用场景**：
如何在合伙人关系中践行"仁"（相互扶持）？如何建立"义"（规则契约）？如何在利益冲突时守住"礼智信"的伦理底线？
"""
        
        # 替换CONFUCIUS章节
        confucius_pattern = r'##### CONFUCIUS（.*?）——木[\s\S]*?(?=##### HUINENG|#### |## |$)'
        if re.search(confucius_pattern, content):
            content = re.sub(confucius_pattern, new_section + "\n\n", content)
            self.changes.append("V1.3: CONFUCIUS章节已同步")
            
        # 同步相生关系
        xiangsheng = self.core_data.get('五路图腾', {}).get('相生关系', {})
        logic = xiangsheng.get('逻辑', [])
        
        new_xiangsheng = """**相生逻辑**：
"""
        for line in logic:
            new_xiangsheng += f"- {line}\n"
            
        xiangsheng_pattern = r'\*\*相生逻辑\*\*：[\s\S]*?(?=---|## |$)'
        if re.search(xiangsheng_pattern, content):
            content = re.sub(xiangsheng_pattern, new_xiangsheng, content)
            self.changes.append("V1.3: 相生关系已同步")
            
        # 保存更新后的文件
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"  ✅ V1.3同步完成")
        
    def sync_strategy(self):
        """同步战略定位1.1版本"""
        print("\n🔄 同步战略定位1.1版本...")
        
        target = WORKING_DIR / "战略定位1.1版本_满意解研究所.md"
        
        if not target.exists():
            print(f"  ⚠️ 目标文件不存在: {target}")
            return
            
        with open(target, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 备份
        backup_name = f"战略定位1.1版本_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        backup_path = BACKUP_DIR / backup_name
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # 同步五路图腾表格
        wulu = self.core_data.get('五路图腾', {}).get('五路图腾', {})
        confucius = wulu.get('CONFUCIUS', {})
        
        # 替换方法护城河表格中的CONFUCIUS行
        old_line = r'\| CONFUCIUS \| 木 \|.*?\|.*?\|'
        new_line = f"| CONFUCIUS | 木 | {confucius.get('决策维度', '合伙人伦理与信任治理')} | 黎红雷企业儒学 |"
        
        if re.search(old_line, content):
            content = re.sub(old_line, new_line, content)
            self.changes.append("战略定位1.1: 五路图腾表格已同步")
            
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"  ✅ 战略定位1.1同步完成")
        
    def sync_v2_package(self):
        """同步V2.0下载包"""
        print("\n🔄 同步V2.0下载包...")
        
        # 复制更新后的文件到下载包
        import shutil
        
        source_files = [
            WORKING_DIR / "满意解研究所_V1.3_完全版本.md",
            WORKING_DIR / "战略定位1.1版本_满意解研究所.md"
        ]
        
        target_dir = Path("A满意哥专属文件夹/99_📦完整下载包/V2.0_技术跃升成果集")
        
        for source in source_files:
            if source.exists():
                target = target_dir / source.name
                shutil.copy2(source, target)
                self.changes.append(f"V2.0: {source.name}已更新")
                
        print(f"  ✅ V2.0下载包同步完成")
        
    def generate_report(self):
        """生成同步报告"""
        print("\n" + "="*50)
        print("📊 同步报告")
        print("="*50)
        
        if self.changes:
            print("\n✅ 已完成的变更:")
            for change in self.changes:
                print(f"  • {change}")
        else:
            print("\n✅ 所有文档已是最新，无变更")
            
        print(f"\n📁 Core定义文件: {len(self.core_data)}个")
        print("  • 五路图腾.yaml")
        print("  • 专家网络.yaml")
        print("  • 品牌资产.yaml")
        print("  • 产品体系.yaml")
        
        print("\n💡 使用提示:")
        print("  1. 修改core/*.yaml文件")
        print("  2. 运行: python3 scripts/sync_from_core.py")
        print("  3. 所有工作文档自动同步")
        
    def run(self):
        """运行完整同步流程"""
        print("="*50)
        print("🚀 满意解知识管理系统 - 同步引擎")
        print("="*50)
        
        self.load_core()
        self.sync_v13()
        self.sync_strategy()
        self.sync_v2_package()
        self.generate_report()
        
        print("\n✨ 同步完成!")

if __name__ == "__main__":
    sync = KnowledgeSync()
    sync.run()
