#!/usr/bin/env python3
"""
知识地图生成器 · knowledge-flywheel-guide
用途: 阶段1自动生成知识资产总览地图
"""

import os
import sys
from pathlib import Path

def scan_directory(root_path, max_depth=3):
    """扫描目录结构，生成树状地图"""
    root = Path(root_path)
    if not root.exists():
        print(f"❌ 路径不存在: {root_path}")
        sys.exit(1)
    
    map_lines = []
    map_lines.append(f"# 知识资产总览地图\n")
    map_lines.append(f"> 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    map_lines.append(f"> 扫描路径: {root.absolute()}\n")
    map_lines.append(f"> 文件总数: {sum(1 for _ in root.rglob('*') if _.is_file())}\n\n")
    
    for item in sorted(root.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            map_lines.append(f"## 📁 {item.name}\n")
            
            # 统计
            files = list(item.rglob('*'))
            file_count = sum(1 for f in files if f.is_file())
            subdirs = [d for d in files if d.is_dir()]
            
            map_lines.append(f"- 文件数: {file_count} | 子文件夹: {len(subdirs)}\n")
            
            # 列出前5个文件作为示例
            sample_files = [f for f in files if f.is_file()][:5]
            if sample_files:
                map_lines.append("- 示例文件:\n")
                for f in sample_files:
                    rel = f.relative_to(item)
                    size = f.stat().st_size
                    size_str = f"{size/1024:.1f}KB" if size > 1024 else f"{size}B"
                    map_lines.append(f"  - `{rel}` ({size_str})\n")
            
            # 引导填写
            map_lines.append("- 这里是: [请用1句话描述这个分类的内容]\n")
            map_lines.append("- 紧急时我来这里找: [请填写1个场景]\n")
            map_lines.append("- 我猜最精华的子文件夹: [请填写]\n\n")
    
    return "".join(map_lines)

def generate_lifebuoy_template():
    """生成救生圈清单模板"""
    return """# 紧急救生圈清单

> 填写说明: 列出5个"如果Egbertie突然问，我必须能立即找到"的场景

| 场景 | Egbertie可能问 | 我知道去哪里找 | 实际路径 |
|:-----|:---------------|:---------------|:---------|
| 战略方向 | "我们现在走到哪？" | [填写] | [填写] |
| 产品内容 | "课程大纲给我" | [填写] | [填写] |
| 运营方法 | "小红书怎么发？" | [填写] | [填写] |
| 身份定义 | "我们的共同禁令是什么？" | [填写] | [填写] |
| 错误教训 | "上次危机怎么处理？" | [填写] | [填写] |

## 额外场景（可选）
| 场景 | Egbertie可能问 | 我知道去哪里找 | 实际路径 |
|:-----|:---------------|:---------------|:---------|
| [自定义] | [填写] | [填写] | [填写] |
| [自定义] | [填写] | [填写] | [填写] |

"""

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 knowledge-map.py <path-to-assets> [output-dir]")
        print("Example: python3 knowledge-map.py ./A-manyige/对话/契晋纪·托付全档/ ./docs/")
        sys.exit(1)
    
    root_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./"
    
    # 生成地图
    map_content = scan_directory(root_path)
    map_file = os.path.join(output_dir, "知识资产总览地图.md")
    
    os.makedirs(output_dir, exist_ok=True)
    with open(map_file, "w", encoding="utf-8") as f:
        f.write(map_content)
    
    print(f"✅ 知识地图已生成: {map_file}")
    
    # 生成救生圈模板
    lifebuoy_content = generate_lifebuoy_template()
    lifebuoy_file = os.path.join(output_dir, "紧急救生圈清单.md")
    
    with open(lifebuoy_file, "w", encoding="utf-8") as f:
        f.write(lifebuoy_content)
    
    print(f"✅ 救生圈清单已生成: {lifebuoy_file}")
    print(f"\n下一步: 打开这两个文件，填写[]中的内容。")

if __name__ == "__main__":
    main()
