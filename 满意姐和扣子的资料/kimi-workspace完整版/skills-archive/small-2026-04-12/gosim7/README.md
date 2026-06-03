# 劳大 skill

> "Hard truth first. Then hard work."

把科比公开采访、演讲、写作和 Mamba Mentality 材料蒸馏成一个可复用的 AI Skill。  
让 Codex 用高标准、重执行、少废话的方式跟你对话。  
像一个冷静、直接、压强很高的教练，而不是一个只会喊口号的 motivational bot。

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Codex Skill](https://img.shields.io/badge/Codex-Skill-black.svg)
![AgentSkills](https://img.shields.io/badge/AgentSkills-Compatible-green.svg)

提供公开语料和场景化模板  
生成一个真正能拿来对话的 劳大 skill  
用高标准、冷处理、重 reps 的方式回复你

⚠️ 本项目用于自我管理、行动辅导、复盘和决策支持，不用于骚扰、PUA、威胁、羞辱或危险操控。

安装 · 使用 · 效果示例 · 功能特性

* * *

## 安装

### Codex

> 重要：请把 skill 放进 Codex 可发现的 skills 目录。

```powershell
git clone https://github.com/GoSim7/laoda-skill.git "$HOME\\.codex\\skills\\laoda-skill"
```

### 本机当前路径

```powershell
C:\Users\Administrator\.codex\skills\laoda-skill
```

### 依赖（可选）

如果你要继续扩充语料、抓网页和 YouTube 字幕，可以安装：

```powershell
pip install yt-dlp youtube-transcript-api
```

* * *

## 环境要求

- Codex 或兼容 Agent Skills 的环境
- Python 3.9+
- 不需要 GPU
- 不需要本地模型
- 不需要 Docker
- 如需扩充公开视频字幕，建议安装 `yt-dlp`

* * *

## 使用

在 Codex 中直接告诉它使用 `laoda-skill`：

```text
Use laoda-skill and review my plan.
Use laoda-skill. Be harsher.
Use laoda-skill in 劳大模式.
Use laoda-skill to help me recover after failure.
```

如果你想让它更狠一点，可以显式说：

```text
劳大模式
go harder
be harsher
上强度
狠一点
```

### 常见调用场景

命令/提示 说明
`Use laoda-skill and review my routine.` 检查习惯、节奏、执行漏洞
`Use laoda-skill to coach this decision.` 做高标准决策拆解
`Use laoda-skill in 劳大模式.` 启动最强硬但安全的回复风格
`Use laoda-skill after I failed.` 做失败复盘和 24 小时重启方案

* * *

## 效果示例

> 输入：`我知道该做什么，但我就是拖延，想让你狠一点。`

场景一：拖延

```text
用户        ❯ 我总是拖到最后才开始

劳大 skill ❯ Truth: 你不是不知道做什么，你是不肯按标准执行。
             Gap: 你一直在等感觉到位，没在按计划开工。
             Order: 现在开始，不要再谈状态。
             Rep today: 45 分钟，单任务，手机拿远，做完再说。
```

场景二：害怕发布作品

```text
用户        ❯ 我怕发出去别人会觉得很烂

劳大 skill ❯ Truth: 怕，说明这次出手有分量。
             Gap: 你在保护舒适区，不是在建立证据。
             Order: 今天发。
             Rep today: 发布，记录反馈，明天优化下一版。
```

场景三：失败后想躺平

```text
用户        ❯ 我这次又失败了，感觉废了

劳大 skill ❯ What happened: 你输了这一回合。
             What it exposed: 准备、执行、复盘里至少有一块是软的。
             What changes today: 别自怜，先看录像。
             Next rep: 写出 3 个错误，今天修 1 个，24 小时内再打一次。
```

场景四：想要纯高压模式

```text
用户        ❯ 开劳大模式，别安慰我

劳大 skill ❯ Truth: 那就别再给我讲潜力，给我看 reps。
             Gap: 你的标准比你的习惯响，问题就在这。
             Order: 切掉借口，排出时间块，天天重复。
             Rep today: 90 分钟深度工作，记产出，报结果。
```

* * *

## 功能特性

### 语气模式

模式 说明
`film-room` 冷静、分析型、像赛后看录像
`locker-room` 强压、直接、催执行
`late-night reset` 稳住情绪，但马上转行动
`laoda` 最强硬的安全模式，也就是劳大模式，短句、压强大、只认 reps

### 内置能力

能力 内容
决策系统 10 条 Mamba 风格决策原则
语气模板 高压开场、中段施压、结尾命令
few-shot 示例 拖延、失败、发布恐惧、创业选择等真实场景
安全边界 不冒充真人，不做侮辱性输出，不支持危险用途

### 资料工程

文件/脚本 作用
`SKILL.md` skill 主定义
`references/decision-system.md` 决策系统蒸馏
`references/voice-templates.md` 语气模板
`references/few-shot-dialogues.md` 对话样例
`references/source-manifest.json` 来源清单
`references/collected-sources.json` 已抓取语料
`scripts/harvest_public_sources.py` 批量抓网页和字幕
`scripts/discover_youtube_sources.py` 自动发现嵌入 YouTube 源

运行逻辑：

`收到用户问题 -> 判断目标和软点 -> 按高标准拆出下一 rep -> 用劳大风格输出`

* * *

## 边界说明

- 不冒充 Kobe Bryant 本人
- 不伪造私密记忆、经历或真人细节
- 不输出侮辱、威胁、羞辱式内容
- 当用户处于危险、自伤、违法等场景时，自动退出高压风格，切回安全回答

* * *

## 仓库

GitHub：

[https://github.com/GoSim7/laoda-skill](https://github.com/GoSim7/laoda-skill)
