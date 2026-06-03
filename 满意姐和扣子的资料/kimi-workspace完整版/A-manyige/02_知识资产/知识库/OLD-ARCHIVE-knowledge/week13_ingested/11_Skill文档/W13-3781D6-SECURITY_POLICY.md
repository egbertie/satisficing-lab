---
# 知识元数据 (5标准化)
knowledge_id: W13-3781D6
title: 安全策略文档
category: 11_Skill文档
source: skills/.archive_satisficing-web-fetcher/SECURITY_POLICY.md
ingested_at: 2026-03-27 17:59:30
word_count: 2254
week: 13
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 安全策略文档

> **知识ID**: W13-3781D6  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_satisficing-web-fetcher/SECURITY_POLICY.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 安全策略文档

## 1. 安全红线

以下行为**严格禁止**：

1. ❌ **抓取登录后才能访问的内容**
   - 不得使用保存的Cookie/Token访问受保护资源
   - 不得绕过身份验证机制

2. ❌ **抓取个人隐私数据**
   - 身份证号、手机号、银行卡号
   - 家庭住址、个人行程
   - 社交媒体私信内容

3. ❌ **高频/大规模抓取**
   - 速率限制：默认1请求/秒
   - 单域名并发限制：最大2
   - 禁止分布式爬取

4. ❌ **自动绕过验证码**
   - 禁止识别和自动填写验证码
   - 禁止破解图形验证、滑块验证

5. ❌ **使用代理隐藏身份**
   - 禁止通过代理服务器匿名抓取
   - 系统级代理除外（需审批）

以下行为**必须执行**：

1. ✅ **所有请求记录审计日志**
   - URL、时间、结果、错误信息
   - 保留30天

2. ✅ **浏览器进程沙箱隔离**
   - 独立进程运行
   - 内存限制2GB
   - 超时自动终止

3. ✅ **域名白名单校验**
   - 仅允许特定域名
   - 默认拒绝所有

4. ✅ **内容安全检查**
   - PII自动检测和脱敏
   - 敏感内容过滤

## 2. 技术控制措施

### 2.1 沙箱隔离

```python
# 内存限制
with MemoryLimiter(max_mb=2048):
    browser_operation()

# 超时控制
with TimeoutGuard(timeout=30):
    fetch_operation()
```

### 2.2 域名白名单

```python
ALLOWED_DOMAINS = [
    "example.com",
    "api.github.com",
    "*.wikipedia.org",
]

# 默认拒绝所有
if not whitelist.is_allowed(url):
    raise SecurityError(f"Domain not allowed: {url}")
```

### 2.3 审计日志

```python
# 每个请求必须记录
audit_logger.log({
    "timestamp": time.time(),
    "url": url,
    "fetcher_type": "HTTPFetcher",
    "success": True/False,
    "error": error_message,
})
```

### 2.4 PII脱敏

```python
# 自动检测和脱敏
filter = ContentFilter()
clean_content = filter.mask_pii(content)
```

## 3. 审计与监控

### 3.1 审计日志格式

```json
{
  "timestamp": 1710500000,
  "url": "https://example.com/page",
  "fetcher_type": "HTTPFetcher",
  "success": true,
  "error": null,
  "source_ip": "127.0.0.1",
  "duration_ms": 1250
}
```

### 3.2 异常检测规则

| 规则 | 描述 | 响应 |
|------|------|------|
| 高频请求 | 1分钟内>60请求 | 限速警告 |
| 大内容 | 响应>10MB | 截断并记录 |
| PII检测 | 检测到身份证/手机号 | 脱敏并告警 |
| 内存超限 | 进程>2GB | 强制终止 |
| 超时 | 请求>30秒 | 终止并记录 |
| 黑名单域名 | 访问非白名单域名 | 拒绝并告警 |

### 3.3 定期审计

- **每日**：检查异常请求日志
- **每周**：审查白名单变更
- **每月**：完整安全审计

## 4. 应急响应

### 4.1 发现违规使用

1. 立即停止相关请求
2. 隔离相关日志
3. 通知安全团队
4. 评估数据泄露风险

### 4.2 安全事件分级

| 级别 | 描述 | 响应时间 |
|------|------|----------|
| P0 | 数据泄露、恶意爬取 | 立即 |
| P1 | 安全策略绕过 | 1小时 |
| P2 | 配置错误、误告警 | 24小时 |

## 5. 合规要求

### 5.1 法律合规

- 遵守《网络安全法》
- 遵守《数据安全法》
- 遵守《个人信息保护法》
- 遵守目标网站robots.txt

### 5.2 伦理准则

- 不给目标网站造成负担
- 不抓取敏感个人信息
- 尊重知识产权
- 仅用于合法目的

## 6. 责任声明

本工具仅供合法用途使用。使用者需对以下事项负责：

1. 确保抓取行为符合法律法规
2. 确保不侵犯他人权益
3. 确保不违反目标网站服务条款
4. 对使用本工具产生的一切后果负责

---

*文档版本：1.0*
*生效日期：2026-03-15*
