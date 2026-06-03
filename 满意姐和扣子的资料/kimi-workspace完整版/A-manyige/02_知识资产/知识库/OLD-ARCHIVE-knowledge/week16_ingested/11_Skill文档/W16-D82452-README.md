---
# 知识元数据 (5标准化)
knowledge_id: W16-D82452
title: 📡 信息采集与质量控制体系 V2.0
category: 11_Skill文档
source: skills/info-collection-quality/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 2290
week: 16
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 📡 信息采集与质量控制体系 V2.0

> **知识ID**: W16-D82452  
> **分类**: 11_Skill文档  
> **来源**: `skills/info-collection-quality/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 📡 信息采集与质量控制体系 V2.0

> **5-Standard Skill** | 7标准全流程质量管控

## 快速开始

```bash
# 检查系统状态
python3 scripts/info-collection-quality-runner.py status

# 检查单个数据源
python3 scripts/info-collection-quality-runner.py check --input examples/sample-high-quality.json

# 批量检查
python3 scripts/info-collection-quality-runner.py batch --dir examples/

# 运行对抗测试
python3 scripts/info-collection-quality-runner.py adversarial-test
```

## 7标准实现

| 标准 | 说明 | 实现 |
|------|------|------|
| **S1** | 输入信息源/采集任务 | ✅ 四级来源分级标准 |
| **S2** | 质量检查四级链 | ✅ 完整性→准确性→时效性→一致性 |
| **S3** | 质量报告+改进建议 | ✅ 结构化JSON报告 |
| **S4** | Pipeline自动集成 | ✅ config/pipeline.json |
| **S5** | 质量指标量化 | ✅ 0-100分，A+到C等级 |
| **S6** | 局限标注 | ✅ 认知谦逊声明 |
| **S7** | 对抗测试 | ✅ 红队测试套件 |

## 质量评分示例

```
📊 质量评估结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
任务: ICQ-20260321-001
总分: 94.0 / 100
等级: A
状态: PASSED

维度得分:
  完整性   ████████░░ 100% (权重35%)
  准确性   ████████░░ 100% (权重30%)
  时效性   █████░░░░░  70% (权重20%)
  一致性   ████████░░ 100% (权重15%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 文件结构

```
info-collection-quality/
├── SKILL.md                    # 技能定义文档
├── README.md                   # 本文件
├── cron.json                   # 定时任务配置
├── config/
│   └── pipeline.json           # Pipeline钩子配置
├── scripts/
│   ├── __init__.py
│   ├── main.py                 # 入口文件
│   └── info-collection-quality-runner.py  # 主程序
├── examples/
│   ├── sample-high-quality.json   # 高质量示例
│   ├── sample-low-quality.json    # 低质量示例
│   └── sample-bad.json            # 异常数据示例
├── logs/                       # 运行日志
└── reports/                    # 质量报告输出
```

## 质量等级说明

| 等级 | 分数 | 使用建议 |
|------|------|----------|
| A+ | 95-100 | 可直接使用，无需修改 |
| A | 85-94 | 建议使用，小瑕疵可忽略 |
| B+ | 75-84 | 有条件使用，需标注局限性 |
| B | 65-74 | 谨慎使用，需人工复核 |
| C | <65 | 不建议使用，需重新采集 |

## Python API

```python
from scripts.info_collection_quality_runner import QualityChecker

checker = QualityChecker()
report = checker.check(data_source)

print(f"质量分: {report.overall_score}")
print(f"等级: {report.grade}")
print(f"建议: {report.recommendations}")
```

## 5-Standard 验收

- ✅ **全局**: 覆盖采集全流程质量管控
- ✅ **系统**: S1→S2→S3→S4→S5→S6→S7闭环
- ✅ **迭代**: 对抗测试驱动持续改进
- ✅ **Skill化**: 标准化API接口
- ✅ **自动化**: Pipeline自动触发，100%自动化

## 版本

- **Version**: 2.0.0
- **Date**: 2026-03-21
- **Status**: 5-Standard 达标 ✅
