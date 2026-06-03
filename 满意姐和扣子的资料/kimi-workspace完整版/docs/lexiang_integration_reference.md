---
kia-version: 1.0
tier: T0
title: 腾讯乐享知识库集成参考文档
source: docs/lexiang_integration_reference.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchD-docs-04]
---

# 腾讯乐享知识库集成参考文档

> 来源：用户提供的4个关键网址 + 网络搜索补充
> 整理时间：2026-04-08
> 整理者：蓝军 Skeptor-7
> 状态：已内化，待凭证补齐后完全闭环

---

## 一、原始参考链接

| # | URL | 内容性质 | 访问状态 |
|---|-----|----------|----------|
| 1 | https://lexiangla.com/wiki/api/?company_from=e3a24a342f8311f185d7c6b1c633a73b | 乐享开放接口文档首页 | ✅ 无需登录，为 OAuth2 概述页 |
| 2 | https://docs.qq.com/doc/DUWNWVERyZUdkbEZx | 腾讯乐享管理员使用手册 | 🔒 腾讯文档，需登录后查看 |
| 3 | https://lexiangla.com/guide?company_from=e3a24a342f8311f185d7c6b1c633a73b | 乐享帮助中心 | ✅ 公开访问，含管理员手册入口 |
| 4 | https://lexiang.tencent.com/wiki/api/50001.html | 乐享AI助手 × 企微机器人配置 | ✅ 需登录企微后台配合配置 |

---

## 二、核心发现：如何获取 AppKey / AppSecret

### 2.1 官方路径（来自 lexiang.tencent.com 官方文档）

1. **登录乐享知识库**，以**管理员身份**进入企业管理后台
2. 进入 **【开发】-【接口凭证管理】**
3. 点击 **添加凭证**
4. 弹窗中输入接口凭证名称并确认
5. **初始化成功后会显示 AppSecret**
   - ⚠️ **切勿泄漏**
   - ⚠️ **关闭弹框后不再显示 AppSecret**，务必立即复制保存

### 2.2 权限分配（两步不可或缺的配置）

**第一步：分配接口权限**
- 创建凭证后，点击「修改权限」
- 勾选当前 AKSK 允许调用的接口并保存

**第二步：设置知识授权范围**
- 默认选择「公司内所有知识」
- 若指定团队，则团队管理、知识库管理、AI 助手等接口的读写实体范围都将受限制

### 2.3 获取 Staff ID（写操作必需）

- 在乐享个人资料页查看**员工编号**
- 部分组织也可能使用企业微信的 `userid` 作为 `staff_id`
- 不确定时，可调用只读接口 `list-teams` 不传 `staff_id` 进行测试

---

## 三、技术规范

### 3.1 认证方式
- **OAuth2 客户端授权模式**（`client_credentials`）
- 对客户端持**完全信任原则**，赋予所有接口权限（但需第二步勾选）

### 3.2 Token 机制
| 项目 | 说明 |
|------|------|
| 有效期 | 2 小时（7200 秒） |
| 频率限制 | 20 次 / 10 分钟 |
| 缓存建议 | **必须缓存**，避免频繁调用被拦截 |
| 失败返回 | `401 Unauthorized` / `429 Too Many Requests` |

### 3.3 请求头规范
```http
# 读操作
Authorization: Bearer {access_token}
Content-Type: application/json; charset=utf-8

# 写操作（额外需要）
x-staff-id: {staff_id}
```

---

## 四、与当前系统的对接状态

### 4.1 已落地资产
- `lexiang_bridge.py`（workspace 根目录）
  - 自动读取 `.env.lexiang`
  - 自动获取并缓存 access_token（2 小时）
  - 封装 `list-teams`、`list-spaces`、`list-entries`、`create-entry`
- `.env.lexiang`（workspace 根目录，chmod 600 安全文件）
  - 当前为空，待用户填入凭证

### 4.2 待补齐条件
- [ ] `LEXIANG_APP_KEY`
- [ ] `LEXIANG_APP_SECRET`
- [ ] `LEXIANG_STAFF_ID`

### 4.3 闭环验证计划
用户补齐上述三个值后，执行：
```bash
cd /root/.openclaw/workspace && python3 lexiang_bridge.py list-teams
```
若成功返回团队列表，则乐享知识库接口彻底闭环。

---

## 五、业务价值判断

| 能力 | 与满意解研究所的关联 |
|------|----------------------|
| 知识库沉淀 | 五路图腾方法论 / 儒商伦理 / 合伙人匹配案例库 |
| 企微机器人 | 未来可将「合伙人匹配决策教练」发布为企微智能助手 |
| 文件上传 | 对话归档、案例库附件、研究报告自动入库 |

---

## 六、相关文件索引

- 桥接器：`/root/.openclaw/workspace/lexiang_bridge.py`
- 凭证文件：`/root/.openclaw/workspace/.env.lexiang`
- Skill 安装路径：`/root/.openclaw/workspace/skills/lexiang-skill/`
- 本参考文档：`/root/.openclaw/workspace/docs/lexiang_integration_reference.md`
