#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出打包器 (Package Builder)
将质量转化包组装为标准传承包

用法:
    python3 package-builder.py --input ./tsunami-output/07_质量转化包/ --output ./08_标准传承包/
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

def create_directory_structure(output_path):
    """创建标准传承包目录结构"""
    dirs = [
        '00_导览总纲',
        '01_P0核心层',
        '02_P1支撑层',
        '03_P2背景层',
        '04_隐性知识',
        '05_原始文件索引',
        '06_检验清单',
        '07_附录'
    ]
    
    for d in dirs:
        (output_path / d).mkdir(parents=True, exist_ok=True)
    
    print(f"  ✅ 目录结构创建完成")

def copy_transformed_files(input_path, output_path):
    """复制质量转化后的文件"""
    print("\n📦 复制转化后的文件...")
    
    copied = 0
    for item in input_path.iterdir():
        if item.is_dir() and item.name in ['00_导览总纲', '01_P0核心层', '02_P1支撑层', '03_P2背景层']:
            target_dir = output_path / item.name
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.copytree(item, target_dir)
            
            # 统计复制的文件数
            files_count = sum(1 for _ in item.rglob('*') if _.is_file())
            copied += files_count
            print(f"  ✅ {item.name}: {files_count} 个文件")
    
    return copied

def generate_original_index(input_base_path, output_path):
    """生成原始文件索引"""
    print("\n📋 生成原始文件索引...")
    
    # 尝试读取初始索引
    index_path = input_base_path / '01_初始索引.json'
    if not index_path.exists():
        print("  ⚠️ 找不到初始索引，跳过")
        return
    
    with open(index_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    files = data.get('files', [])
    
    # 生成Markdown索引
    md_path = output_path / '05_原始文件索引' / '00_全量文件索引.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# 全量文件索引\n\n")
        f.write("> **原始文件总数**: {}\n\n".format(len(files)))
        f.write("| 序号 | 文件名 | 类型 | 大小 | 优先级 | 路径 |\n")
        f.write("|:-----|:-------|:-----|:-----|:-------|:-----|\n")
        
        for file_info in files:
            priority = file_info.get('classification', {}).get('priority', '未分类')
            f.write(f"| {file_info['id']} | {file_info['filename']} | {file_info['file_type']} | {file_info['size_readable']} | {priority} | {file_info['path']} |\n")
    
    # 生成CSV索引
    import csv
    csv_path = output_path / '05_原始文件索引' / '00_全量文件索引.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        if files:
            writer = csv.DictWriter(f, fieldnames=files[0].keys())
            writer.writeheader()
            writer.writerows(files)
    
    print(f"  ✅ 原始文件索引已生成")

def generate_checklists(output_path):
    """生成检验清单"""
    print("\n✅ 生成检验清单...")
    
    # 传者自检清单
    sender_check = """# 传者自检清单

> **用途**: 传者在交付前自检
> **时间**: 约30分钟

---

## 核心知识确认

- [ ] 我确认了核心知识清单（≤5项）
- [ ] 我补充了遗漏的核心知识（如有）
- [ ] 我删除了不重要的"伪核心"（如有）
- [ ] 我能用1句话解释每项核心知识

## 隐性知识提取

- [ ] 我检查了隐性知识候选清单
- [ ] 我对每个有效候选使用了"隐性知识表达模板"
- [ ] 我标记了"无隐性知识"的候选（移出）
- [ ] 我确认了至少3项隐性知识已提取

## P0/P1/P2确认

- [ ] 我检查了所有P0文件，确认"没有它系统会崩溃"
- [ ] 我检查了所有P1文件，确认"没有它效率降低"
- [ ] 我将部分P2升级为P1（如有）
- [ ] 我删除了所有P3文件（或移至归档）

## 质量检查

- [ ] 我检查了5个随机文件的"阅读指引"，确认合理
- [ ] 我检查了5个随机文件的"五维映射"，确认恰当
- [ ] 我修正了不准确的自动生成的内容
- [ ] 我确认了"开篇语"中的描述准确

## 传承准备

- [ ] 我准备了"传承启动握手"清单
- [ ] 我约定了双周对账时间
- [ ] 我明确了验收日期和标准
- [ ] 我确认了承者已收到传承包

---

**自检结果**: □ 全部通过，可以交付 / □ 有未通过项，需修正

*传者自检清单: V1.0*
"""
    
    sender_path = output_path / '06_检验清单' / '传者自检清单.md'
    with open(sender_path, 'w', encoding='utf-8') as f:
        f.write(sender_check)
    print(f"  ✅ 传者自检清单")
    
    # 承者自检清单
    receiver_check = """# 承者自检清单

> **用途**: 承者在接收后自检
> **时间**: 约20分钟

---

## 接收确认

- [ ] 我收到了完整的传承包（所有文件夹都存在）
- [ ] 我打开了"00_开篇语.md"并阅读
- [ ] 我找到了"00_导览总纲"并了解结构
- [ ] 我确认了P0/P1/P2标记

## 启动检查

- [ ] 我创建了"阅读日志"
- [ ] 我确认了第1个P0文件
- [ ] 我阅读了第1个P0文件的"阅读指引"
- [ ] 我理解了"困惑信号"机制

## 阅读验证

- [ ] 我完成了第1个P0文件的阅读
- [ ] 我执行了"理解验证三问"（能解释？能举例？能执行？）
- [ ] 我记录了"同步写入"笔记
- [ ] 我标记了困惑（如有）

## 对账准备

- [ ] 我准备了双周对账的汇报内容
- [ ] 我列出了需要传者解答的问题
- [ ] 我确认了下次对账时间

---

**自检结果**: □ 全部通过，可以开始传承 / □ 有未通过项，需解决

*承者自检清单: V1.0*
"""
    
    receiver_path = output_path / '06_检验清单' / '承者自检清单.md'
    with open(receiver_path, 'w', encoding='utf-8') as f:
        f.write(receiver_check)
    print(f"  ✅ 承者自检清单")
    
    # 传承验收清单
    acceptance = """# 传承验收清单

> **用途**: 传承完成后的验收
> **标准**: 三层验证（信息→理解→能力）

---

## 第一层：信息传递验证

- [ ] 承者收到了所有P0文件
- [ ] 承者知道P0/P1/P2的优先级
- [ ] 承者能说出每个P0文件的核心主题（用自己的话）
- [ ] 承者知道在哪里找到补充信息

**结果**: □ 通过（100%） / □ 未通过

## 第二层：理解达成验证

- [ ] 承者能解释"核心知识"是什么（不是背诵，是解释）
- [ ] 承者能举出1个自己遇到的例子，并用传者的框架分析
- [ ] 承者能指出"这里我理解不了"（诚实说出困惑）
- [ ] 承者能区分"我知道"和"我理解了"

**结果**: □ 通过（≥80%） / □ 未通过

## 第三层：能力迁移验证

- [ ] 承者能在不看传者文件的情况下，执行核心任务
- [ ] 承者的执行结果与传者的预期一致（或差异在可接受范围）
- [ ] 承者能处理"没见过的情况"（用传者的判断逻辑）
- [ ] 承者能发现传者的遗漏/错误（反哺传者）

**结果**: □ 通过（≥60%） / □ 未通过

## 总体结论

- [ ] 三层全部通过 → 传承成功
- [ ] 通过第一层+第二层，第三层待续 → 部分成功
- [ ] 第一层或第二层未通过 → 需要重新执行

## 签字

- 传者: ____________ 日期: ____________
- 承者: ____________ 日期: ____________

---

*传承验收清单: V1.0*
"""
    
    acceptance_path = output_path / '06_检验清单' / '传承验收清单.md'
    with open(acceptance_path, 'w', encoding='utf-8') as f:
        f.write(acceptance)
    print(f"  ✅ 传承验收清单")

def generate_appendix(input_base_path, output_path):
    """生成附录"""
    print("\n📎 生成附录...")
    
    # 处理日志
    log_content = f"""# 处理日志

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **处理工具**: 知识海啸处理器 V1.0

---

## 处理步骤

1. **海啸导入** (tsunami-ingest.py)
   - 扫描原始文件
   - 生成初始索引
   - 状态: ✅ 完成

2. **智能分类** (smart-triage.py)
   - 自动分类和标记P0/P1/P2/P3
   - 生成阅读顺序
   - 状态: ✅ 完成
   - 注意: ⚠️ 需人工确认P0/P1/P2

3. **核心萃取** (core-extractor.py)
   - 提取核心知识候选
   - 识别隐性知识候选
   - 状态: ✅ 完成
   - 注意: ⚠️ 需人工确认核心知识

4. **质量转化** (quality-transform.py)
   - 生成阅读指引
   - 生成五维映射
   - 生成导览总纲
   - 状态: ✅ 完成
   - 注意: ⚠️ 需人工评分五维映射

5. **输出打包** (package-builder.py)
   - 组装标准传承包
   - 生成检验清单
   - 状态: ✅ 完成

## 人工确认清单

- [ ] P0/P1/P2标记确认（传者，2小时）
- [ ] 核心知识清单确认（传者，1小时）
- [ ] 隐性知识提取（传者，2小时）
- [ ] 五维映射评分（传者，1小时）
- [ ] 阅读指引修正（传者，1小时）

## 版本信息

- 机器处理版本: V1.0
- 人工确认后版本: V1.1（待更新）
- 传承启动后版本: V2.0（待更新）

---

*处理日志: V1.0*
"""
    
    log_path = output_path / '07_附录' / '01_处理日志.md'
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(log_content)
    print(f"  ✅ 处理日志")
    
    # 统计报告
    stats_content = f"""# 统计报告

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 文件统计

| 指标 | 数值 |
|:-----|:-----|
| 原始文件总数 | [从初始索引读取] |
| 处理后保留 | [P0+P1+P2] |
| 归档/删除 | [P3] |

## 类型分布

| 类型 | 数量 | 占比 |
|:-----|:-----|:-----|
| [类型1] | [数量] | [占比] |

## 优先级分布

| 优先级 | 数量 | 占比 |
|:-----|:-----|:-----|
| P0 | [数量] | [占比] |
| P1 | [数量] | [占比] |
| P2 | [数量] | [占比] |
| P3 | [数量] | [占比] |

## 时间分布

| 时间段 | 数量 | 占比 |
|:-------|:-----|:-----|
| [时间段1] | [数量] | [占比] |

---

*统计报告: V1.0*
"""
    
    stats_path = output_path / '07_附录' / '02_统计报告.md'
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write(stats_content)
    print(f"  ✅ 统计报告")

def generate_final_readme(output_path):
    """生成最终的README"""
    print("\n📄 生成最终README...")
    
    readme = f"""# 标准传承包

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **处理工具**: 知识海啸处理器 V1.0
> **质量等级**: 机器处理80% + 人工确认后95%
> **状态**: 待人工确认

---

## 快速开始

### 如果你是传者（3步）

1. **确认P0/P1/P2**（2小时）
   - 打开 `06_检验清单/传者自检清单.md`
   - 检查所有P0文件是否真的是核心
   - 修正错误的标记

2. **补充隐性知识**（2小时）
   - 打开 `04_隐性知识/00_隐性知识清单.md`
   - 对候选文件使用"隐性知识表达模板"
   - 补充你自己的"说不出但很重要"的经验

3. **修正自动生成内容**（1小时）
   - 检查5个随机文件的"阅读指引"
   - 检查5个随机文件的"五维映射"
   - 修正不准确的内容

### 如果你是承者（3步）

1. **了解全貌**（15分钟）
   - 阅读 `00_开篇语.md`
   - 浏览 `00_导览总纲/01_人类视角导览.md`

2. **准备阅读**（10分钟）
   - 创建"阅读日志"
   - 确认第1个P0文件
   - 阅读该文件的"阅读指引"

3. **开始阅读**（按节奏）
   - 每次阅读不超过2小时
   - 每读完一个文件执行"理解验证三问"
   - 记录困惑信号

## 包结构

```
00_开篇语.md              ← 先读这个
00_导览总纲/              ← 然后读这个
  ├── 01_人类视角导览.md
  ├── 02_AI视角导览.md
  └── 03_五维决策底层逻辑.md
01_P0核心层/              ← 核心知识在这里
02_P1支撑层/              ← 支撑知识在这里
03_P2背景层/              ← 背景知识在这里
04_隐性知识/              ← 最难传的知识在这里
05_原始文件索引/          ← 全部原始文件索引
06_检验清单/              ← 自检和验收工具
07_附录/                  ← 处理日志和统计
```

## 重要提醒

⚠️ **这是机器自动生成的传承包，需要人工确认后才能交付**

- P0/P1/P2标记准确率约70-80%
- 核心知识清单需要传者确认
- 隐性知识需要传者手动提取
- 五维映射需要传者评分

## 联系方式

如有问题，请联系：
- 传承问题: [传者联系方式]
- 技术问题: [技术支持联系方式]

---

*标准传承包: V1.0*
*来源: 满意解研究所 · 知识海啸处理器*
"""
    
    readme_path = output_path / 'README.md'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme)
    print(f"  ✅ README.md")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='输出打包器')
    parser.add_argument('--input', '-i', required=True, help='质量转化包路径')
    parser.add_argument('--output', '-o', required=True, help='标准传承包输出路径')
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("📦 知识海啸处理器 - 输出打包器")
    print("="*60)
    
    # 创建目录结构
    print("\n📁 创建标准传承包目录结构...")
    create_directory_structure(output_path)
    
    # 复制转化后的文件
    copied = copy_transformed_files(input_path, output_path)
    
    # 生成原始文件索引
    input_base = input_path.parent
    generate_original_index(input_base, output_path)
    
    # 生成检验清单
    generate_checklists(output_path)
    
    # 生成附录
    generate_appendix(input_base, output_path)
    
    # 生成最终README
    generate_final_readme(output_path)
    
    print(f"\n📊 打包结果:")
    print(f"  已复制文件: {copied}")
    print(f"  生成导览: 3个")
    print(f"  生成检验清单: 3个")
    print(f"  生成附录: 2个")
    print(f"  生成README: 1个")
    
    print(f"\n✅ 标准传承包已生成: {output_path}")
    print("\n⚠️  下一步: 传者人工确认P0/P1/P2标记")
    print("="*60)

if __name__ == '__main__':
    main()
