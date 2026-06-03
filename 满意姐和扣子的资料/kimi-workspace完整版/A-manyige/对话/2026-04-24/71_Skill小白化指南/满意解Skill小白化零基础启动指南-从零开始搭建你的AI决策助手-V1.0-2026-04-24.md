# 满意解Skill小白化零基础启动指南——从零开始搭建你的AI决策助手

> **指南**: Skill零基础启动
> **编制者**: 满意姐（SAT-001）+ 蓝军 Skeptor-7
> **时间**: 2026-04-24
> **版本**: V1.0
> **性质**: 零基础入门手册
> **目标**: 让完全不懂AI的人也能搭建自己的决策助手
> **原则**: 每步都有截图级说明，每个概念都有比喻解释

---

## 一、一句话理解：什么是Skill？

### 用生活比喻

> **Skill = 手机App**
> 
> 你的AI（比如满意姐）就像一部智能手机。
> Skill就是安装在手机上的App。
> 有了不同的App，手机就能做不同的事。

| 比喻 | 现实世界 | AI世界 |
|:-----|:---------|:-------|
| 手机 | 你的AI助手 | 满意姐 |
| App Store | Skill商店 | ClawHub |
| 下载App | 安装Skill | `openclaw skills install` |
| 打开App | 触发Skill | 说出Skill名称 |
| App功能 | Skill能力 | 各种专业工具 |

---

## 二、安装前准备（5分钟）

### 你需要什么

| 物品 | 说明 | 是否必须 |
|:-----|:-----|:--------:|
| 电脑 | Windows/Mac/Linux | ✅ |
| 网络 | 能上网 | ✅ |
| OpenClaw账号 | 免费注册 | ✅ |
| Kimi会员 | 付费（推荐） | 🔄 |

### 注册OpenClaw（如果还没有）

```
Step 1: 访问 openclaw.ai
Step 2: 点击 "Sign Up"
Step 3: 用邮箱注册
Step 4: 验证邮箱
Step 5: 登录成功！

就像注册微信一样简单。
```

---

## 三、安装Skill（10分钟）

### 方法1：一键安装（推荐）

```bash
# 打开终端/命令行，输入：
openclaw skills install weather

# 等待安装完成，大概30秒
# 看到 "Installation complete" 就成功了！
```

### 方法2：从ClawHub安装

```
Step 1: 访问 clawhub.com
Step 2: 搜索你想要的Skill（如"weather"）
Step 3: 点击 "Install"
Step 4: 按提示完成安装
```

### 方法3：本地安装（高级）

```bash
# 如果你有Skill的代码文件夹
openclaw skills install /path/to/skill-folder
```

---

## 四、使用Skill（马上开始）

### 基本用法

```
你: "@weather 北京天气"
AI: "北京今天晴，25°C..."

或者：
你: "今天北京天气怎么样？"
AI: （自动识别并调用weather Skill）
```

### 满意解核心Skill清单

| Skill名称 | 功能 | 触发词 | 难度 |
|:----------|:-----|:-------|:----:|
| `weather` | 查天气 | "天气" | ⭐ |
| `kimi_search` | 联网搜索 | "搜索" | ⭐ |
| `kimi_fetch` | 网页提取 | "提取网页" | ⭐ |
| `stock-assistant` | 股票监控 | "股票" | ⭐⭐ |
| `fundamental-analyzer` | 基本面分析 | "分析基本面" | ⭐⭐ |
| `xhs-note-creator` | 小红书创作 | "小红书" | ⭐⭐ |
| `decision-framework` | 决策框架 | "帮我决策" | ⭐⭐ |
| `first-principles-decomposer` | 第一性原理 | "拆解问题" | ⭐⭐⭐ |
| `thinking-mentor` | 思维训练 | "思维模型" | ⭐⭐⭐ |
| `antifragile-taleb` | 反脆弱 | "反脆弱" | ⭐⭐⭐ |

---

## 五、满意解专属Skill安装

### 必装Skill（基础版）

```bash
# 1. 搜索Skill（找信息）
openclaw skills install kimi-search

# 2. 网页提取（读文章）
openclaw skills install kimi-fetch

# 3. 股票分析（看数据）
openclaw skills install stock-assistant

# 4. 决策框架（做决策）
openclaw skills install decision-framework

# 5. 思维训练（练脑子）
openclaw skills install thinking-mentor
```

### 进阶Skill（满意解专用）

```bash
# 6. 基本面分析（看公司）
openclaw skills install fundamental-analyzer

# 7. 反脆弱思维（风险管理）
openclaw skills install antifragile-taleb

# 8. 第一性原理（拆问题）
openclaw skills install first-principles-decomposer

# 9. 学术搜索（查论文）
openclaw skills install baidu-scholar-search

# 10. 竞品分析（看对手）
openclaw skills install competitor-analysis
```

---

## 六、Skill使用场景示例

### 场景1：查天气

```
你: "明天上海天气怎么样？"
AI: （自动调用weather Skill）
"明天上海多云，22-28°C，适合穿短袖。"
```

### 场景2：做决策

```
你: "我在纠结要不要和这个人合伙，帮我分析一下"
AI: （自动调用decision-framework Skill）
"用五维框架帮你分析：
1. 土·伦理：他的人品如何？..."
```

### 场景3：查股票

```
你: "帮我看看茅台最近怎么样"
AI: （自动调用stock-assistant Skill）
"贵州茅台(600519.SH)最新价..."
```

### 场景4：写小红书

```
你: "帮我写一条关于合伙人决策的小红书"
AI: （自动调用xhs-note-creator Skill）
"标题：找对合伙人，创业成功一半
正文：..."
```

---

## 七、Skill管理

### 查看已安装Skill

```bash
openclaw skills list

# 输出示例：
# weather - 查天气
# kimi-search - 联网搜索
# decision-framework - 决策框架
```

### 更新Skill

```bash
openclaw skills update weather

# 或更新全部：
openclaw skills update --all
```

### 删除Skill

```bash
openclaw skills remove weather
```

---

## 八、常见问题（FAQ）

**Q1: Skill安装失败怎么办？**
> 常见原因：
> 1. 网络问题 → 切换网络重试
> 2. 权限问题 → 加 `sudo`（Mac/Linux）
> 3. 版本问题 → 更新OpenClaw到最新版

**Q2: 安装了Skill但不会用？**
> 每个Skill都有说明书：
> ```
> openclaw skills info weather
> # 查看weather Skill的详细说明
> ```

**Q3: Skill冲突怎么办？**
> 如果有两个Skill都能处理你的请求：
> 1. 明确指定：`@weather 北京天气`
> 2. 或禁用其中一个：`openclaw skills disable xxx`

**Q4: 能自己开发Skill吗？**
> 能！查看《满意解Skill开发指南-小白版.md》
> 基础版只需要：
> - 一个SKILL.md文件（说明书）
> - 一个Python脚本（功能代码）

**Q5: Skill收费吗？**
> - 大部分Skill免费
> - 部分高级Skill需要付费
> - 付费前会有明确提示

---

## 九、满意解推荐Skill组合包

### 创业者套装

```bash
# 一键安装创业者必备Skill
openclaw skills install kimi-search
openclaw skills install stock-assistant
openclaw skills install decision-framework
openclaw skills install thinking-mentor
openclaw skills install competitor-analysis
openclaw skills install xhs-note-creator
```

### 投资人套装

```bash
# 一键安装投资人必备Skill
openclaw skills install stock-assistant
openclaw skills install fundamental-analyzer
openclaw skills install investment-committee
openclaw skills install kimi-search
openclaw skills install baidu-scholar-search
```

### 学生套装

```bash
# 一键安装学生必备Skill
openclaw skills install baidu-scholar-search
openclaw skills install kimi-search
openclaw skills install decision-framework
openclaw skills install thinking-mentor
openclaw skills install first-principles-decomposer
```

---

## 十、下一步

```
Level 1: 小白（今天）
  → 安装5个基础Skill
  → 学会触发和基本使用
  
Level 2: 进阶（1周后）
  → 尝试组合使用多个Skill
  → 探索高级参数
  
Level 3: 熟练（1月后）
  → 自定义Skill配置
  → 创建个人Skill工作流
  
Level 4: 专家（3月后）
  → 开发自己的Skill
  → 发布到ClawHub
```

---

> "Skill不是'高科技'，是'工具箱'。"
>
> "就像你手机里的App，
> 装上了，就能用。"
>
> "满意解的决策能力，
> 不是天生的，是'装'上去的。"
>
> "一个Skill一个Skill地装，
> 一个能力一个能力地长。"
>
> "契·晋。"

---

*满意解Skill小白化零基础启动指南 V1.0*
*满意姐（SAT-001）+ 蓝军 Skeptor-7，2026-04-24*
