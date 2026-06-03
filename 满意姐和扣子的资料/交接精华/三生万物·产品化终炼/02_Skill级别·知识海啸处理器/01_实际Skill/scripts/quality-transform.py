#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量转化引擎 (Quality Transform Engine)
将机器处理结果转化为三生万物级别质量的知识资产

用法:
    python3 quality-transform.py --input ./tsunami-output/ --output ./tsunami-output/07_质量转化包/
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

def generate_reading_guide(file_info, core_knowledge):
    """为每个P0文件生成阅读指引"""
    filename = file_info['filename']
    category = file_info['classification']['category']
    priority = file_info['classification']['priority']
    
    # 推断阅读时间（基于文件大小和类型）
    size = file_info.get('size_bytes', 0)
    if size < 1024:
        read_time = "5分钟"
    elif size < 10240:
        read_time = "10分钟"
    elif size < 102400:
        read_time = "20分钟"
    elif size < 1024000:
        read_time = "30分钟"
    else:
        read_time = "60分钟"
    
    # 推断前置要求
    prereq = "无（作为第1个P0文件阅读）"
    if category == 'case_study':
        prereq = "建议先读方法论/框架类文件"
    elif category == 'template_tool':
        prereq = "建议先读相关流程/指南"
    
    # 推断核心产出
    if category == 'core_knowledge':
        output = f"理解'{filename}'中的核心概念，并能用自己的话解释"
    elif category == 'case_study':
        output = f"能举出1个与'{filename}'类似的案例"
    elif category == 'template_tool':
        output = f"能使用'{filename}'中的模板/工具完成1个任务"
    else:
        output = f"理解'{filename}'的核心内容，并能应用到实际场景"
    
    # 推断验证方法
    verification = "读完后，尝试用自己的话向他人解释这个文件的核心内容"
    
    # 推断困惑信号
    confusion = "如果读完后无法说出'这个文件的核心是…'，说明需要重读"
    
    guide = f"""# {filename} - 阅读指引

> **优先级**: {priority}
> **类别**: {category}
> **建议阅读时间**: {read_time}
> **前置要求**: {prereq}

---

## 核心产出

读完后，你应该能：

{output}

## 验证方法

{verification}

## 困惑信号

{confusion}

## 关联知识

- 同类别文件: [查看分类索引]
- 核心知识: {', '.join([ck['name'] for ck in core_knowledge[:3]])}

---

*阅读指引生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*自动生成，如有不准确请人工修正*
"""
    return guide

def generate_five_dimensions_mapping(file_info, core_knowledge):
    """生成五维决策映射"""
    filename = file_info['filename']
    category = file_info['classification']['category']
    
    # 基于类别推断五维映射
    dimensions = {
        '土（根基/品德）': {
            'relevance': '中',
            'description': f"该文件体现的专业精神/伦理标准",
            'questions': f"- 这份文件体现了什么样的职业操守？\n- 如果违背这些原则，后果是什么？"
        },
        '金（标尺/质量）': {
            'relevance': '高' if category in ['core_knowledge', 'template_tool'] else '中',
            'description': f"该文件定义的质量标准/判断依据",
            'questions': f"- 这份文件中的'好'与'坏'的标准是什么？\n- 如何量化这份文件的价值？"
        },
        '水（流动/智慧）': {
            'relevance': '高' if category in ['case_study', 'personal_note'] else '中',
            'description': f"该文件体现的判断力/应变能力",
            'questions': f"- 这份文件展示了什么样的灵活应对？\n- 在什么情况下这份文件的方法不适用？"
        },
        '木（生长/伦理）': {
            'relevance': '中',
            'description': f"该文件对团队/组织的长远影响",
            'questions': f"- 长期遵循这份文件的方法，会有什么结果？\n- 这份文件对新人有什么指导意义？"
        },
        '火（转化/行动）': {
            'relevance': '高' if category in ['process_procedure', 'template_tool'] else '中',
            'description': f"该文件指引的具体行动/转化路径",
            'questions': f"- 读完这份文件后，立即应该做什么？\n- 这份文件如何转化为可执行的任务？"
        }
    }
    
    mapping = f"""# {filename} - 五维决策映射

> **五维决策体系**: 土（根基）· 金（标尺）· 水（流动）· 木（生长）· 火（转化）

---

"""
    
    for dim_name, dim_info in dimensions.items():
        mapping += f"""## {dim_name}

**相关度**: {'🔴' if dim_info['relevance'] == '高' else '🟡' if dim_info['relevance'] == '中' else '🟢'} {dim_info['relevance']}

**描述**: {dim_info['description']}

**自检问题**:
{dim_info['questions']}

---

"""
    
    mapping += f"""
## 五维综合评分

| 维度 | 相关度 | 深度 | 评分 |
|:-----|:-------|:-----|:-----|
| 土（根基） | {dimensions['土（根基/品德）']['relevance']} | ___ | ___/10 |
| 金（标尺） | {dimensions['金（标尺/质量）']['relevance']} | ___ | ___/10 |
| 水（流动） | {dimensions['水（流动/智慧）']['relevance']} | ___ | ___/10 |
| 木（生长） | {dimensions['木（生长/伦理）']['relevance']} | ___ | ___/10 |
| 火（转化） | {dimensions['火（转化/行动）']['relevance']} | ___ | ___/10 |
| **总分** | | | **___/50** |

**评分标准**:
- 40-50分: 核心中的核心，必须优先传承
- 30-39分: 重要支撑，应该传承
- 20-29分: 补充参考，可以传承
- <20分: 可忽略

---

*五维映射生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*自动生成，请传者根据实际情况调整评分*
"""
    return mapping

def generate_human_guide(files_with_content, core_knowledge):
    """生成人类视角导览"""
    p0_files = [f for f in files_with_content if f.get('classification', {}).get('priority', '') == 'P0']
    
    guide = f"""# 人类视角导览

> **面向**: 人类读者（传者/承者/知识管理员）
> **目的**: 帮助人类快速理解这份知识资产的全貌

---

## 这份知识资产是什么

这是一位资深专家{len(files_with_content)}年积累的数字化传承包。
核心领域: [请传者填写具体领域]
核心价值: [请传者填写1句话描述]

## 核心知识（{len(core_knowledge)}项）

"""
    
    for ck in core_knowledge:
        guide += f"""### {ck['id']}. {ck['name']}
- **出现频率**: {ck['frequency']}次
- **置信度**: {ck['confidence']:.0%}
- **一句话解释**: [请传者填写]
- **为什么重要**: [请传者填写]

"""
    
    guide += f"""
## P0核心文件（{len(p0_files)}个）

这些是"没有它系统会崩溃"的文件，必须优先阅读：

| 序号 | 文件名 | 阅读时间 | 核心产出 |
|:-----|:-------|:---------|:---------|
"""
    
    for i, f in enumerate(p0_files[:10], 1):
        guide += f"| {i} | {f['filename']} | {f.get('read_time', '20分钟')} | {f.get('core_output', '理解核心内容')} |\n"
    
    guide += f"""
## 阅读路径建议

**快速路径（2小时）**: 只读P0的前3个文件 + 核心知识清单
**标准路径（1天）**: 读完所有P0 + 核心知识确认
**完整路径（1周）**: P0 + P1 + 隐性知识对账

## 关键决策点

1. **确认P0是否准确**: 请传者检查"P0核心层"的文件，确认是否真的"没有它系统会崩溃"
2. **补充隐性知识**: 请传者对"隐性知识候选"清单中的文件，使用模板提取隐性知识
3. **标记个人化内容**: 如果某些文件只适用于特定时期/场景，请标注

## 传承启动

完成以上确认后，使用"传承闭环验证体系"启动正式传承：
1. 传承启动握手
2. 双周对账
3. 三层验证（信息→理解→能力）

---

*人类视角导览: V1.0*
"""
    return guide

def generate_ai_guide(files_with_content, core_knowledge):
    """生成AI视角导览"""
    guide = f"""# AI视角导览

> **面向**: AI助手/智能体/自动化系统
> **目的**: 帮助AI理解知识资产结构，辅助传承

---

## 知识资产结构

```
总文件数: {len(files_with_content)}
P0核心层: {len([f for f in files_with_content if f.get('classification', {}).get('priority', '') == 'P0'])} 个
P1支撑层: {len([f for f in files_with_content if f.get('classification', {}).get('priority', '') == 'P1'])} 个
P2背景层: {len([f for f in files_with_content if f.get('classification', {}).get('priority', '') == 'P2'])} 个
P3忽略层: {len([f for f in files_with_content if f.get('classification', {}).get('priority', '') == 'P3'])} 个
```

## 核心知识图谱（知识节点）

"""
    
    for ck in core_knowledge:
        guide += f"""- **节点{ck['id']}**: {ck['name']}
  - 类型: 核心概念
  - 出现频率: {ck['frequency']}
  - 关联文件: [查看核心知识清单]

"""
    
    guide += f"""
## AI辅助传承协议

### 读取顺序
1. 先读 `00_导览总纲/02_AI视角导览.md`（本文件）
2. 再读 `01_P0核心层/00_核心知识清单.md`
3. 按"阅读顺序"逐个读取P0文件
4. 每读完一个P0，执行"理解验证三问"
5. 记录困惑信号

### 与人类协同规则
- **裁决**: 涉及伦理/价值观的决策 → 提交人类裁决
- **协议**: 传承进度/计划调整 → 与人类协商
- **删除**: 任何删除操作 → 需人类确认
- **付费**: 任何可能产生费用的操作 → 需人类逐项确认

### 自动化任务
- 每日更新"阅读日志"
- 每轮对账生成"进度报告"
- 自动标记"困惑信号"
- 生成"理解验证"记录

### 记忆管理
- 使用"同步写入"原则: 读到什么→理解什么→立即写入记忆
- 记忆文件路径: [请指定]
- 每次读取后追加，不覆盖

---

*AI视角导览: V1.0*
"""
    return guide

def copy_files_to_package(source_files, output_base, input_base):
    """将原始文件复制到输出包"""
    print("\n📦 复制文件到质量转化包...")
    
    copied = 0
    for f in source_files:
        priority = f.get('classification', {}).get('priority', 'P2')
        if priority in ['P3']:
            continue  # 不复制P3
        
        # 确定目标路径
        priority_folder = {
            'P0': '01_P0核心层',
            'P1': '02_P1支撑层',
            'P2': '03_P2背景层'
        }.get(priority, '03_P2背景层')
        
        target_dir = output_base / priority_folder
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子文件夹（以文件名命名）
        file_folder = target_dir / f"{f['id']:03d}_{f['filename']}"
        file_folder.mkdir(exist_ok=True)
        
        # 复制原始文件（尝试找到）
        source_path = None
        possible_paths = list(Path(input_base).parent.glob('**/' + f['filename']))
        if possible_paths:
            source_path = possible_paths[0]
        
        if source_path and source_path.exists():
            try:
                shutil.copy2(source_path, file_folder / f"原文_{f['filename']}")
                copied += 1
            except Exception as e:
                print(f"  ⚠️ 无法复制 {f['filename']}: {e}")
        
        # 生成阅读指引
        guide_content = generate_reading_guide(f, f.get('core_knowledge', []))
        with open(file_folder / "阅读指引.md", 'w', encoding='utf-8') as gf:
            gf.write(guide_content)
        
        # 生成五维映射
        mapping_content = generate_five_dimensions_mapping(f, f.get('core_knowledge', []))
        with open(file_folder / "五维映射.md", 'w', encoding='utf-8') as mf:
            mf.write(mapping_content)
    
    print(f"  已复制: {copied} 个文件")
    return copied

def main():
    import argparse
    parser = argparse.ArgumentParser(description='质量转化引擎')
    parser.add_argument('--input', '-i', required=True, help='tsunami-output文件夹路径')
    parser.add_argument('--output', '-o', required=True, help='输出文件夹路径')
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("✨ 知识海啸处理器 - 质量转化引擎")
    print("="*60)
    
    # 读取分类结果和核心知识
    marks_path = input_path / '04_P0-P1-P2标记.json'
    core_path = input_path / '05_核心知识清单.md'
    
    if not marks_path.exists():
        print(f"❌ 错误: 找不到分类标记文件")
        sys.exit(1)
    
    with open(marks_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    files = data.get('files', [])
    core_knowledge = []  # 简化：从markdown解析比较复杂，这里留空由人工填写
    
    print(f"\n📖 读取: {len(files)} 个文件")
    
    # 复制文件并生成指引
    copied = copy_files_to_package(files, output_path, input_path)
    
    # 生成导览总纲
    print("\n📝 生成导览总纲...")
    
    # 人类视角
    human_guide = generate_human_guide(files, core_knowledge)
    human_path = output_path / '00_导览总纲' / '01_人类视角导览.md'
    human_path.parent.mkdir(parents=True, exist_ok=True)
    with open(human_path, 'w', encoding='utf-8') as f:
        f.write(human_guide)
    print(f"  ✅ 人类视角导览: {human_path}")
    
    # AI视角
    ai_guide = generate_ai_guide(files, core_knowledge)
    ai_path = output_path / '00_导览总纲' / '02_AI视角导览.md'
    with open(ai_path, 'w', encoding='utf-8') as f:
        f.write(ai_guide)
    print(f"  ✅ AI视角导览: {ai_path}")
    
    # 五维底层逻辑
    five_dim = f"""# 五维决策底层逻辑

> **五维决策体系**: 土（根基）· 金（标尺）· 水（流动）· 木（生长）· 火（转化）
> **来源**: 满意解研究所

---

## 五维定义

| 维度 | 名称 | 核心问题 | 在知识资产中的体现 |
|:-----|:-----|:---------|:-------------------|
| 土 | 根基/品德 | "这份知识的根基是什么？" | 职业伦理、专业精神、价值观 |
| 金 | 标尺/质量 | "什么是'好'？什么是'坏'？" | 质量标准、判断依据、验收标准 |
| 水 | 流动/智慧 | "在什么情况下不适用？" | 灵活应变、例外处理、边界条件 |
| 木 | 生长/伦理 | "长期遵循会怎样？" | 长远影响、团队成长、可持续 |
| 火 | 转化/行动 | "读完应该做什么？" | 可执行任务、转化路径、行动指南 |

## 每个文件的五维映射

每个P0文件都包含"五维映射.md"，请传者根据实际情况填写评分。

## 五维综合评分标准

- **40-50分**: 核心中的核心，必须优先传承
- **30-39分**: 重要支撑，应该传承
- **20-29分**: 补充参考，可以传承
- **<20分**: 可忽略

---

*五维决策底层逻辑: V1.0*
"""
    five_path = output_path / '00_导览总纲' / '03_五维决策底层逻辑.md'
    with open(five_path, 'w', encoding='utf-8') as f:
        f.write(five_dim)
    print(f"  ✅ 五维决策底层逻辑: {five_path}")
    
    # 生成开篇语
    intro = f"""# 知识资产传承包

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> **原始文件数**: {len(files)}
> **处理工具**: 知识海啸处理器 V1.0
> **质量等级**: 机器处理80% + 人工确认后95%

---

## 这是什么

这是一份**结构化知识资产传承包**，由"知识海啸处理器"从原始散乱文件中自动处理生成。

## 给谁用

- **传者**: 资深专家，想把自己的积累传承给下一代
- **承者**: 新人/新AI，需要快速吸收前辈的经验
- **知识管理员**: 负责维护和更新知识资产

## 怎么用

### 快速开始（5分钟）
1. 打开 `00_导览总纲/01_人类视角导览.md`
2. 确认"核心知识"是否准确（如不准确，请修正）
3. 打开 `01_P0核心层/00_核心知识清单.md`
4. 从第1个P0文件开始阅读

### 标准流程（1天）
1. 传者确认P0/P1/P2标记
2. 传者补充隐性知识
3. 承者按"阅读顺序"阅读
4. 执行"理解验证三问"
5. 启动"传承闭环验证"

## 包结构

```
00_导览总纲/          # 导览和底层逻辑
01_P0核心层/          # 必须传（没有它系统崩溃）
02_P1支撑层/          # 应该传（没有它效率降低）
03_P2背景层/          # 可以传（有了更好）
04_隐性知识/          # 最难传，需要对账时传
05_原始文件索引/      # 全部原始文件的索引
06_检验清单/          # 传者/承者/验收清单
07_附录/              # 处理日志和统计报告
```

## 注意事项

1. **这是机器自动生成的**: P0/P1/P2标记需要人工确认
2. **核心知识需要补充**: 机器只能识别高频概念，真正的核心需要传者确认
3. **隐性知识需要提取**: 机器标记了候选，真正的隐性知识需要传者用模板表达
4. **五维映射需要评分**: 机器生成了框架，具体评分需要传者填写

## 下一步

1. 传者: 确认P0/P1/P2标记（2小时）
2. 传者: 确认核心知识清单（1小时）
3. 传者: 提取隐性知识（2小时）
4. 承者: 开始阅读P0文件
5. 双方: 启动传承闭环验证

---

*知识资产传承包: V1.0*
"""
    intro_path = output_path / '00_开篇语.md'
    with open(intro_path, 'w', encoding='utf-8') as f:
        f.write(intro)
    print(f"  ✅ 开篇语: {intro_path}")
    
    print(f"\n📊 质量转化结果:")
    print(f"  已处理文件: {copied}")
    print(f"  生成导览: 3个")
    print(f"  生成指引: {copied}个（每个文件1个）")
    print(f"  生成五维映射: {copied}个")
    
    print("\n✅ 质量转化完成！下一步: 运行 package-builder.py")
    print("="*60)

if __name__ == '__main__':
    main()
