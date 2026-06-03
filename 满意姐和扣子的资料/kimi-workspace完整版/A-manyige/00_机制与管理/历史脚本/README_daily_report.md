# 每日晨报生成脚本 - 使用说明

## 📋 脚本简介

`daily_morning_report_generator.py` 是一个自动化脚本，用于每日晨报的自动生成。它从多个数据源收集信息，分析任务状态，生成格式化的晨报文本，可直接复制到飞书/微信发送。

### 核心功能

- ✅ 自动读取 MEMORY.md 中的待办事项
- ✅ 自动读取每日日志中的任务状态
- ✅ 自动读取 Skill 进化追踪器状态
- ✅ 自动识别今日到期任务
- ✅ 自动识别 P0/P1 优先级任务
- ✅ 自动计算任务完成率
- ✅ 自动检测阻塞任务
- ✅ 根据任务量生成时间分配建议
- ✅ 长期目标倒计时提醒

### 自动化程度

| 功能 | 自动化程度 | 人工干预 |
|------|----------|----------|
| 数据收集 | 100% 自动 | 无需 |
| 优先级识别 | 100% 自动 | 无需 |
| 完成率计算 | 100% 自动 | 无需 |
| 时间建议 | 90% 自动 | 可微调 |
| 长期提醒 | 100% 自动 | 配置日期 |
| 格式化输出 | 100% 自动 | 无需 |

**综合自动化程度：95%**

### 节省时间

- **传统方式**：人工整理 15-20 分钟/天
- **脚本方式**：运行脚本 2-3 分钟/天
- **节省时间**：约 13-17 分钟/天，月度节省 6-8 小时

---

## 🚀 快速开始

### 1. 安装要求

```bash
# 确保使用 Python 3.7+
python3 --version

# 无需额外依赖，纯标准库实现
```

### 2. 首次运行

```bash
cd /root/.openclaw/workspace/scripts

# 生成今日晨报
python3 daily_morning_report_generator.py --print

# 保存配置模板（可选）
python3 daily_morning_report_generator.py --save-config
```

### 3. 查看输出

生成的晨报保存在：
```
/root/.openclaw/workspace/A满意哥专属文件夹/01_🔥今日重点/晨报_YYYY-MM-DD.md
```

---

## 📖 使用方式

### 基本用法

```bash
# 生成今日晨报
python3 daily_morning_report_generator.py

# 生成指定日期的晨报
python3 daily_morning_report_generator.py --date 2026-03-16

# 打印到控制台（不保存）
python3 daily_morning_report_generator.py --print

# 指定输出文件
python3 daily_morning_report_generator.py -o /path/to/output.md

# 指定配置文件
python3 daily_morning_report_generator.py -c /path/to/config.json
```

### 定时自动运行（推荐）

添加 cron 任务，每天早上 9:00 自动生成：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天 9:00 运行）
0 9 * * * cd /root/.openclaw/workspace/scripts && python3 daily_morning_report_generator.py

# 或使用更推荐的方式：错峰到 9:07
7 9 * * * cd /root/.openclaw/workspace/scripts && python3 daily_morning_report_generator.py
```

---

## ⚙️ 配置文件说明

配置文件 `morning_report_config.json` 控制脚本行为：

### 主要配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `workspace_path` | 工作空间路径 | `/root/.openclaw/workspace` |
| `output_path` | 晨报输出目录 | `A满意哥专属文件夹/01_🔥今日重点` |
| `long_term_goals.官宣日期` | 里程碑日期 | `2026-03-25` |
| `greetings` | 星期问候语 | 见配置 |
| `time_allocation_rules` | 时间分配规则 | 按P0任务数 |
| `priority_emojis` | 优先级图标 | 🔥⭐📌💭 |

### 自定义时间分配规则

```json
{
  "time_allocation_rules": {
    "P0任务数>=3": {
      "深度工作": "4小时",
      "沟通协作": "1小时",
      "学习研究": "0.5小时"
    },
    "P0任务数=2": {
      "深度工作": "3小时",
      "沟通协作": "1小时",
      "学习研究": "1小时"
    }
  }
}
```

### 数据源配置

```json
{
  "data_sources": {
    "memory_md": {
      "enabled": true,
      "path": "MEMORY.md"
    },
    "daily_logs": {
      "enabled": true,
      "path": "memory/YYYY-MM-DD.md"
    },
    "skill_tracker": {
      "enabled": true,
      "path": "skill.json"
    }
  }
}
```

---

## 📊 数据源说明

脚本从以下数据源自动收集信息：

### 1. MEMORY.md（主记忆文件）

- 解析 `- [ ] 待办任务` 格式
- 识别 `P0/P1/P2/P3` 优先级标记
- 提取 `(2026-03-25)` 截止日期

**示例格式**：
```markdown
- [ ] P0: 完成Pitch Deck第3-5页
- [ ] P1: 更新案例库（CASE-016）
- [x] P0: 发送黎红雷教授邮件 (2026-03-14)
```

### 2. memory/YYYY-MM-DD.md（每日日志）

- 读取当天的日志文件
- 提取其中的任务列表
- 合并到今日任务池

### 3. skill.json（Skill 进化追踪器）

- 统计活跃 Skill 数量
- 显示系统运行状态
- 可选：追踪 Skill 使用频率

---

## 📝 输出格式示例

```markdown
🌅 满意解晨报 · 2026-03-16 周一

*新的一周，元气满满！*

【今日重点】
🔥 P0: 完成Pitch Deck第3-5页
🔥 P0: 发送黎红雷教授邮件
⭐ P1: 更新案例库（CASE-016）
⭐ P1: V1.0蓝军意见整理
📌 P2: 专家网络搭建

【进行中】3项正常推进
【阻塞】0项
【完成率】本周77%

【系统状态】14/14个Skill活跃运行

【时间建议】
- 深度工作：3小时（Pitch Deck）
- 沟通协作：1小时（邮件/电话）
- 学习研究：1小时

💡 长期提醒：距3/25官宣还有9天

---
*满意解研究所 · 晨报生成时间：09:07*
```

---

## 🔧 高级用法

### 集成到 OpenClaw 定时任务

在 OpenClaw 中设置定时任务：

```bash
# 使用 openclaw 命令行设置
cd /root/.openclaw/workspace/scripts
openclaw cron create \
  --name "daily-morning-report" \
  --schedule "0 9 * * *" \
  --command "python3 daily_morning_report_generator.py" \
  --enabled
```

### 作为模块导入

```python
from daily_morning_report_generator import Config, ReportGenerator

# 加载配置
config = Config()

# 生成报告
generator = ReportGenerator(config)
report = generator.generate_report("2026-03-16")

# 自定义处理
print(f"今日重点任务数: {len(report.focus_tasks)}")
print(f"完成率: {report.completion_rate}%")

# 保存报告
output_path = generator.save_report(report)
print(f"报告已保存: {output_path}")
```

### 批量生成历史晨报

```bash
# 生成过去7天的晨报
for i in {1..7}; do
    date=$(date -d "$i days ago" +%Y-%m-%d)
    python3 daily_morning_report_generator.py --date $date
done
```

---

## 🐛 故障排查

### 问题1：找不到任务

**检查**：
1. MEMORY.md 是否存在
2. 任务格式是否正确（`- [ ] 任务内容`）
3. 工作空间路径是否正确

**解决**：
```bash
# 检查文件路径
ls -la /root/.openclaw/workspace/MEMORY.md

# 手动指定路径
python3 daily_morning_report_generator.py -c custom_config.json
```

### 问题2：优先级识别错误

**检查任务格式**：
```markdown
# 正确格式
- [ ] P0: 任务标题
- [ ] P1 任务标题
- [ ] P0-任务标题

# 不支持格式
- [ ] [P0] 任务标题
- [ ] 优先级P0：任务标题
```

### 问题3：输出目录不存在

**解决**：
```python
# 脚本会自动创建目录，如遇权限问题手动创建
mkdir -p "/root/.openclaw/workspace/A满意哥专属文件夹/01_🔥今日重点"
```

---

## 🔄 更新日志

### v1.0.0 (2026-03-15)

- ✅ 初始版本发布
- ✅ 支持多数据源读取
- ✅ 自动优先级识别
- ✅ 时间分配建议
- ✅ 长期目标提醒
- ✅ 纯 Python 标准库实现，无依赖

---

## 💡 使用建议

### 最佳实践

1. **保持任务格式统一**：使用 `- [ ] P0: 任务内容` 格式
2. **每日更新 MEMORY.md**：及时标记完成状态
3. **定期回顾配置**：根据实际工作节奏调整时间分配规则
4. **结合定时任务**：设置每天早上自动生成，形成习惯

### 扩展思路

- 可扩展读取飞书多维表格数据
- 可扩展读取日历 API 获取会议安排
- 可扩展生成图表（完成率趋势图）
- 可扩展发送邮件/飞书消息

---

## 📞 支持

如有问题或建议，请：
1. 检查本说明文档
2. 查看配置文件注释
3. 联系满意解研究所

---

*满意解研究所 · 让每日规划更高效*
