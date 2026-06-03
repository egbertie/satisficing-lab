# 飞书授权流程知识库

> **知识ID**: FEISHU-AUTH-001  
> **主题**: 飞书设备配对授权流程  
> **更新日期**: 2026-03-27

---

## 问题现象

**用户反馈**:
- 收到配对码: `79QBYJS4`
- 收到OpenID: `ou_b83233d8ba6d296ca68df803cd2fb61f`
- 提示: "OpenClaw: access not configured"
- 疑问: 以前是直接给链接点击授权，现在为什么变了？

---

## 原因分析

**授权方式变更**:

| 方式 | 旧流程 | 新流程 |
|------|--------|--------|
| **OAuth** | 直接点击链接授权 | 仍可用，但需要用户主动发起 |
| **设备配对** | 自动完成 | 需要显式批准（安全增强） |

**安全策略升级**:
- OpenClaw增强了飞书渠道的安全验证
- 新用户/设备首次连接时需要**显式配对批准**
- 防止未经授权的设备接入

---

## 解决方案

### 管理员操作（AI执行）

```bash
# 批准飞书配对请求
openclaw pairing approve feishu <PAIRING_CODE>

# 示例
openclaw pairing approve feishu 79QBYJS4
```

**执行结果**:
```
Approved feishu sender ou_b83233d8ba6d296ca68df803cd2fb61f
```

### 用户操作

**无需操作** - 配对批准后自动生效。

如需日历OAuth授权（独立流程）:
1. 在飞书中发送 "授权日历"
2. 点击返回的OAuth链接
3. 同意授权即可

---

## 权限验证

### 设备配对验证
```python
# 验证sender是否已批准
feishu_im_user_get_messages()  # 应能正常获取消息
```

### 日历权限验证
```python
# 验证日历权限
feishu_calendar_calendar(action="primary")  # 应返回主日历信息
```

---

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| "access not configured" | 设备未配对 | 执行pairing approve |
| "need_user_authorization" | OAuth未授权 | 用户点击OAuth链接 |
| "invalid pairing code" | 配对码过期 | 重新生成配对码 |

---

## 历史记录

- **2026-03-27**: 批准用户 `ou_b83233d8ba6d296ca68df803cd2fb61f` 配对请求，代码 `79QBYJS4`

---

## 关联知识

- AIRES-002: WorkBuddy微信直连研究
- IMPL-004: 每日晨报Cron任务（依赖日历授权）

---

*知识入库时间: 2026-03-27*
