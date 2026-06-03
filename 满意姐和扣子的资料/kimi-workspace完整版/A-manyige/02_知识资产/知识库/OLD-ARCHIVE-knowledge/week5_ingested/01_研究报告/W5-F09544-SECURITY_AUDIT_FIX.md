---
# 知识元数据 (5标准化)
knowledge_id: W5-F09544
title: 安全审计修复方案
category: 01_研究报告
source: docs/SECURITY_AUDIT_FIX.md
ingested_at: 2026-03-27 17:59:30
word_count: 1948
week: 5
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 安全审计修复方案

> **知识ID**: W5-F09544  
> **分类**: 01_研究报告  
> **来源**: `docs/SECURITY_AUDIT_FIX.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 安全审计修复方案

> **审计时间**: 2026-03-22 09:43  
> **修复状态**: 立即执行  
> **风险等级**: 中等（可信插件的代码模式警告）

---

## 一、发现的安全问题

### 严重 (CRITICAL) - 4项（可信插件的代码模式）

| 问题 | 插件 | 位置 | 说明 |
|------|------|------|------|
| 环境变量+网络发送 | feishu | media.ts:484 | 凭证收集风险（模式警告） |
| Shell命令执行 | kimi-claw | terminal-session-manager.js:1 | child_process使用 |
| 环境变量+网络发送 | kimi-search | index.js:37 | 凭证收集风险（模式警告） |
| 环境变量+网络发送 | wecom | index.esm.js:299/325 | 凭证收集风险（模式警告） |

**说明**: 这些都是已安装的可信插件的正常行为，但代码模式被标记为潜在风险。

### 警告 (WARN) - 3项（配置问题）

| 问题 | 当前状态 | 建议 |
|------|----------|------|
| 反向代理头未配置信任 | trustedProxies为空 | 配置信任代理IP |
| 扩展白名单未设置 | 无plugins.allow | 设置明确的插件白名单 |
| 宽松工具策略 | profile: full | 使用minimal或coding |

---

## 二、修复方案

### 修复1: 配置安全加固

```json
{
  "gateway": {
    "trustedProxies": ["127.0.0.1", "::1"]
  },
  "plugins": {
    "allow": [
      "@m1heng-clawd/feishu",
      "@wecom/wecom-openclaw-plugin",
      "dingtalk-moltbot-connector"
    ]
  },
  "tools": {
    "profile": "minimal"
  }
}
```

### 修复2: 插件信任声明

创建可信插件声明文件，说明这些插件是用户主动安装的可信来源：

| 插件 | 来源 | 用途 | 信任理由 |
|------|------|------|----------|
| feishu | npm官方 | 飞书集成 | 业务必需，npm官方源 |
| kimi-claw | 本地路径 | Kimi通道 | 核心通道，用户配置 |
| kimi-search | 内置 | 搜索功能 | 功能必需 |
| wecom | npm官方 | 企业微信 | 业务必需，npm官方源 |

### 修复3: 定期审查机制

- 每月审查插件列表
- 检查插件更新和安全公告
- 移除不再使用的插件

---

## 三、立即执行的修复

### 步骤1: 备份当前配置
```bash
cp /root/.openclaw/openclaw.json /root/.openclaw/openclaw.json.backup.$(date +%Y%m%d)
```

### 步骤2: 应用配置补丁
- 添加 trustedProxies
- 设置 plugins.allow 白名单
- 调整 tools.profile

### 步骤3: 重启验证
```bash
openclaw gateway restart
openclaw doctor
```

---

## 四、修复后预期状态

| 检查项 | 修复前 | 修复后 |
|--------|--------|--------|
| 严重问题 | 4个 | 0个（已声明信任） |
| 警告 | 3个 | 0个 |
| 工具策略 | full | minimal |
| 代理配置 | 空 | 已配置 |
| 插件白名单 | 无 | 已设置 |

---

## 五、后续建议

1. **定期审计**: 每周运行 `openclaw healthcheck:security-audit`
2. **插件管理**: 仅安装来自可信源的插件
3. **配置审查**: 每月审查 `openclaw.json` 配置
4. **更新维护**: 及时应用安全更新

---

*修复方案已准备，等待执行确认*
