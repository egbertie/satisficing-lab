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

---

Add whatever helps you do your job. This is your cheat sheet.
