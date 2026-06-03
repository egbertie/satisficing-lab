# OpenClaw Skill 治理与获取协议 V1.0

> **来源**：基于 AGENTS.md 双经济要求、费用红线规则，以及 awesome-openclaw-skills 安全警告（供应链攻击风险）综合制定  
> **状态**：立即生效，血液化执行  
> **监督者**：蓝军 Skeptor-7

---

## 一、核心原则

**禁止「见到就装」。**

任何 Skill 的获取都必须经过治理流程。安装不是目的，**提升创始人可用性**才是。我们拒绝为了「整理 skill」而「向内集邮」。

---

## 二、SAP-7 协议（Skill Acquisition Protocol - 7 Steps）

### S1 | Scan（发现）
- 来源：研究资料、微信文章、用户推荐、ClawHub 搜索
- 动作：记录 Skill 名称 + 来源链接 + 发现时间
- 输出：`memory/skill-candidate-pool.json`

### S2 | Assess（评估）
用双经济过滤器快速筛选：
- **效益经济学**：是否直接服务于满意解研究所当前里程碑（V1.6 案例库完善、合伙人决策产品化）？
- **Token 经济学**：是否免费？调用频率如何？是否存在隐性的高 Token 消耗或 API 费用？
- **创始人 5 分钟可用性**：Egbertie 能否在 5 分钟内理解它的用途和边界？
- **判定标准**：三者均「是」才进入 S3；任一「否」直接归档为「暂不处理」，不加队列。

### S3 | Vet（安全审查）
- **信源审查**：GitHub Stars、维护者活跃度、社区使用信号（Highlighted / downloads）
- **权限审查**：是否读写本地文件？是否执行命令？是否访问网络？是否索要敏感凭据？
- **风险评级**：
  - 🟢 低风险：纯文本处理、无外部网络、无文件写入
  - 🟡 中风险：读写本地文件 / 访问公开 API（需最小权限 token）
  - 🔴 高风险：执行系统命令 / 索要主账号密码或私钥 / 来源不明
- **红线条款**：🔴 高风险 Skill **禁止安装**，除非经 Blue Army 特批且 Egbertie 书面确认。

### S4 | Approve（人工确认）
- 若 Skill 涉及**任何费用**（付费 API、订阅、超出免费额度），必须逐项经 Egbertie 人工独立确认（费用红线规则）。
- 若 Skill 为 🟡 中风险，需向 Egbertie 简要报告权限范围，获得口头确认后方可进入 S5。
- 若 Skill 为 🟢 低风险，可由 Blue Army 自主批准，事后报备。

### S5 | Install & Test（安装与沙盒测试）
- 优先在 isolated session 或 temp workspace 中安装测试。
- 测试内容：基本功能跑通、权限边界验证、与现有 Skill 冲突检查。
- 测试不通过 → 退回 S3 或永久放弃。

### S6 | Register（注册入档）
- 写入 `memory/skill-registry.json`，字段包括：
  - `skill_name`, `source_url`, `install_date`, `risk_level`, `purpose`, `approved_by`, `test_status`, `last_used`, `notes`
- 同时更新 `TOOLS.md` 中的本地使用备注（如 API key 配置、别名等）。

### S7 | Integrate（整合与机制化）
- 若该 Skill 成为标准工作流的一部分，更新 `AGENTS.md` 或相关 SKILL.md 的引用。
- 若该 Skill 与现有能力重叠，评估是否替换旧 Skill，避免冗余。

---

## 三、特别禁令

1. **禁止在繁忙任务中并行安装新 Skill**，避免注意力漂移和上下文中毒。
2. **禁止安装来源不明的第三方中转 API Skill**，防范供应链攻击。
3. **禁止为了「可能以后会用到」而安装 Skill**，必须对应一个当前或近期的具体任务。

---

## 四、当前候选池（示例）

| Skill 来源 | 用途预判 | 风险评级 | 状态 |
|-----------|---------|---------|------|
| `agent-reach`（资料中提及） | 全网搜索、阅读多平台内容 | 🟡 | 待评估 S2 |
| `autoglm-toolkit`（资料中提及） | 浏览器自动化、网页抓取 | 🟡 | 待评估 S2 |
| `academic-deep-research`（已有） | 深度学术调研 | 🟢 | 已注册 |

---

*本协议由 Blue Army 制定，满意姐执行，违规即告警。*
