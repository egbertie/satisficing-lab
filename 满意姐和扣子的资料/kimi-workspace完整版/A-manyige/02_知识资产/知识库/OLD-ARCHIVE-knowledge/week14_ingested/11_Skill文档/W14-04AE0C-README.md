---
# 知识元数据 (5标准化)
knowledge_id: W14-04AE0C
title: AI Meeting Notes Scripts
category: 11_Skill文档
source: skills/ai-meeting-notes/scripts/README.md
ingested_at: 2026-03-27 17:59:30
word_count: 1467
week: 14
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# AI Meeting Notes Scripts

> **知识ID**: W14-04AE0C  
> **分类**: 11_Skill文档  
> **来源**: `skills/ai-meeting-notes/scripts/README.md`  
> **入库时间**: 2026-03-27

---

## 正文

# AI Meeting Notes Scripts

## 脚本说明

### ai-meeting-notes.py
AI会议笔记主处理脚本 - Level 5 生产级实现

**功能：**
- **S1 输入标准化**: 支持文本/VTT/录音等多种输入格式
- **S2 处理流程化**: 提取要点→行动项→责任人→截止时间
- **S3 输出结构化**: Markdown/JSON双格式输出
- **S4 触发自动化**: 手动触发 + 自动文件监控

**使用方法：**
```bash
# 处理文件
python3 ai-meeting-notes.py process meeting-notes.txt

# 输出JSON格式
python3 ai-meeting-notes.py process meeting-notes.txt --format json

# 查看系统状态
python3 ai-meeting-notes.py status

# 运行对抗测试
python3 ai-meeting-notes.py test --adversarial
```

### self_check.py
准确性自检模块 - S5标准实现

**功能：**
- 完整性检查（7项检查点）
- 置信度评分
- 改进建议生成

**使用方法：**
```bash
# 检查结果文件
python3 self_check.py result.json

# 在Python中调用
from self_check import SelfCheckEngine
engine = SelfCheckEngine()
report = engine.run_full_check(result_data)
```

### adversarial_test.py
对抗测试模块 - S7标准实现

**功能：**
- 噪声注入测试
- 格式损坏测试  
- 语义混乱测试
- 极端情况测试

**使用方法：**
```bash
# 运行全部对抗测试
python3 adversarial_test.py

# 输出JSON报告
python3 adversarial_test.py --json > adversarial_report.json
```

## 目录结构

```
scripts/
├── ai-meeting-notes.py      # 主处理脚本
├── self_check.py            # 自检模块 (S5)
├── adversarial_test.py      # 对抗测试 (S7)
├── ai-meeting-notes-runner.py  # 旧版运行器
├── main.py                  # 旧版入口
└── utils/                   # 工具函数（预留）
    ├── parser.py
    ├── extractor.py
    └── formatter.py
```

## 依赖安装

```bash
pip install -r ../requirements.txt
```

## 测试

```bash
# 运行测试用例
python3 -m pytest ../tests/

# 运行自检
python3 ai-meeting-notes.py status
```
