# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## API配置信息

### GitHub Models (GPT-4o)

| 项目 | 值 |
|------|-----|
| **状态** | ✅ 已验证可用 (2026-03-21) |
| **API Base** | `https://models.inference.ai.azure.com` |
| **认证** | GitHub Token (Fine-grained) |
| **可用模型** | gpt-4o (50次/天), gpt-4o-mini (150次/天) |

**环境变量**:
```bash
export GITHUB_TOKEN="ghp_***"  # 已配置
export GITHUB_MODELS_BASE_URL="https://models.inference.ai.azure.com"
```

**使用示例**:
```bash
curl -X POST "https://models.inference.ai.azure.com/chat/completions" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

---

### Kimi Search (联网搜索)

| 项目 | 值 |
|------|-----|
| **状态** | ✅ 可用 |
| **用途** | 实时联网搜索、信息检索 |
| **访问方式** | 已集成到OpenClaw (`kimi_search` 工具) |

**使用示例**:
```python
# 在OpenClaw中直接调用
kimi_search(query="搜索内容", limit=5)
```

**特点**:
- 中文搜索优化
- 国内直接访问
- 多源引用支持

---

### Jina AI Reader (网页提取)

| 项目 | 值 |
|------|-----|
| **状态** | ✅ 可用 |
| **功能** | URL → Markdown 转换 |
| **免费额度** | 1000万 tokens |

**使用示例**:
```bash
# 无需API Key
curl "https://r.jina.ai/http://example.com"

# 带API Key（更高限额）
curl -H "Authorization: Bearer $JINA_API_KEY" \
  "https://r.jina.ai/http://example.com"
```

---

### Perplexity API

| 项目 | 值 |
|------|-----|
| **状态** | ❌ 暂不可用 |
| **原因** | 网络受限，官网无法访问 |
| **替代方案** | Kimi Search |

**备注**: 如未来网络条件允许，可重新评估。

---

## 更新记录

| 日期 | 更新内容 |
|------|----------|
| 2026-03-21 | 添加API配置信息 (GitHub Models, Kimi Search, Jina AI, Perplexity) |
| 2026-04-04 | 添加Kimi Claw能力参考 (AI诊断、Memory插件、Skillhub) |

---

## Kimi Claw 能力备忘

### 官方Wiki（定期查询）
- **更新日志**: https://kimiclaw.feishu.cn/wiki/AkVew49UBiYcaWkK9FpcPqxcn5I
- **功能文档**: https://kimiclaw.feishu.cn/wiki/W2o6wf94ViOrLnklVsvcCB2CnPd

### 核心能力（2026.4.3更新）

| 能力 | 状态 | 使用场景 |
|------|------|----------|
| **AI问题诊断** | ✅ 可用 | 断连/不回消息/定时任务失败/终端连接失败 |
| **Memory插件** | ✅ 可用 | 记忆力优化（比MEMORY.md更强） |
| **Skillhub** | ✅ 无限制 | 技能搜索，随时可用 |
| **新建Agent优化** | ✅ 可用 | 直接指定名字/人设/技能 |

### 重要提醒
- **我们是Kimi付费用户** - 可直接使用kimi_search/kimi_fetch，无需额外API Key
- **每周查询更新** - 保持对最新功能的了解
- **详细档案**: `docs/KIMI_CLAW_UPDATES.md`

---

## 飞书授权状态备忘（2026-04-10 更新）

| 操作类型 | 状态 | 备注 |
|----------|------|------|
| 用户身份读取 | ✅ 已授权 | `feishu_get_user` 正常 |
| 云盘（Drive）读取 | ✅ 已授权 | `feishu_drive_file` 正常，`weekly-cloud-backup` 已恢复 |
| 文档/Wiki 搜索 | ✅ 已授权 | `feishu_search_doc_wiki` 正常 |
| 日历读取 | ✅ 已授权 | `feishu_calendar_calendar` 正常，可读取主日历 |
| 任务清单读取 | ✅ 已授权 | `feishu_task_tasklist` 正常 |
| 日历写操作（创建/修改日程） | 🟡 待触发 | 若调用写接口，将自动发送授权卡片到飞书对话，需用户点击确认 |
| 任务写操作（创建/修改任务） | 🟡 待触发 | 同上 |

**授权模式**: 系统发起授权请求卡片 → 用户在飞书端点击链接确认 → OpenClaw 刷新 token 后生效。

---

## 用户通信与渠道偏好备忘（2026-04-10 更新）

| 偏好 | 规则 |
|------|------|
| **主对话框** | **Kimi 网页端/APP 为主**，所有核心交互、决策确认、日常提醒默认在此进行 |
| **飞书** | 仅作为：① 授权触发通道 ② P0 紧急异常告警备用通道 |
| **周期性报告** | 不发飞书，统一生成文件到 `A-manyige/汇报/日报/`（或对应子目录），仅在 Kimi 轻量提醒 |
| **Token 策略** | 非紧急事项不通过 message 主动推送任何渠道 |

---

Add whatever helps you do your job. This is your cheat sheet.
