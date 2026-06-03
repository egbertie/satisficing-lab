> 生成时间: 2026-04-05 08:19+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# skill-usage-tracker - Skill使用追踪器

## 描述
追踪OpenClaw Skill使用频率、检测手工操作绕过、生成使用率报告，并通过强制使用提醒培养正确使用习惯。

## 触发条件
- 用户要求"查看Skill使用情况"、"为什么不用Skill"
- 发现手工操作绕过标准Skill路径
- 需要生成周期性Skill使用报告

## 功能
- **使用频率追踪**：记录每次Skill调用，统计日/周/月使用率
- **手工绕过检测**：通过文件修改时间、命令历史等信号检测疑似手工操作
- **报告生成**：输出Markdown格式的使用报告与改进建议
- **强制提醒**：对低频或未使用的高价值Skill生成提醒
- **习惯培养**：追踪连续使用天数，鼓励 Skill-First 工作方式

## 核心事件类型
- `SKILL_USED` - 正确使用Skill
- `MANUAL_WORKAROUND` - 疑似手工绕过
- `DIRECT_EDIT` - 直接编辑文件（未通过Skill）

## 使用方法
```bash
cd skills/skill-usage-tracker/scripts
python3 skill_usage_tracker.py --help
python3 main.py
```

## 数据存储
- 本地JSON：`~/.openclaw/skill_usage/`
- 事件日志按日期滚动存储
- 支持加密哈希校验防篡改

## 依赖
- Python 3.10+
- 标准库（json, os, re, hashlib, subprocess）

## 版本
- 1.0.0-real
- 作者：满意妞（蓝军监督）
