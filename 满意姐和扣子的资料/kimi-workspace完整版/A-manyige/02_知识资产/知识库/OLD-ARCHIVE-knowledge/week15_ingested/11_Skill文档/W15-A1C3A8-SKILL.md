---
# 知识元数据 (5标准化)
knowledge_id: W15-A1C3A8
title: 飞书云盘自服务上传 Skill
category: 11_Skill文档
source: skills/feishu-drive-self-upload/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 4742
week: 15
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# 飞书云盘自服务上传 Skill

> **知识ID**: W15-A1C3A8  
> **分类**: 11_Skill文档  
> **来源**: `skills/feishu-drive-self-upload/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# 飞书云盘自服务上传 Skill

> **Skill ID**: `feishu-drive-self-upload`  
> **版本**: v1.0 FIN  
> **创建时间**: 2026-03-26  
> **核心机制**: 用户分享云盘链接 → AI自调试 → 完成上传

---

## 1. 问题背景 (S1 - 输入)

### 1.1 场景描述
- 默认飞书插件工具无法直接上传文件到云盘
- 需要自定义Python插件调用飞书Drive API
- 每次调试上传都需要用户手动干预

### 1.2 解决目标
建立**自服务上传机制**：用户提供云盘分享链接，AI自动完成调试并上传测试文件，验证通路后深度记忆配置。

---

## 2. 解决方案 (S2 - 处理)

### 2.1 核心组件

| 组件 | 路径 | 功能 |
|------|------|------|
| **上传器** | `plugins/feishu_drive_uploader.py` | 完整的云盘上传CLI工具 |
| **测试文件** | `/tmp/test_upload_<timestamp>.txt` | 自动生成的验证文件 |
| **配置存储** | 环境变量 + 硬编码回退 | APP_ID / APP_SECRET |

### 2.2 工作流程

```
用户分享链接
     ↓
AI读取当前插件状态
     ↓
生成测试文件
     ↓
执行上传命令
     ↓
验证上传结果
     ↓
深度记忆成功配置
```

### 2.3 关键命令

```bash
# 1. 列出云盘文件（验证连通性）
cd /root/.openclaw/workspace/plugins && python3 feishu_drive_uploader.py list

# 2. 上传文件
python3 feishu_drive_uploader.py upload <file_path> [folder_token]

# 3. 上传并指定文件夹
python3 feishu_drive_uploader.py upload <file_path> <folder_token>
```

---

## 3. 使用方式 (S3 - 输出)

### 3.1 用户触发指令

用户说类似以下内容时触发本Skill：
- "飞书云盘上传不了"
- "帮我调一下飞书云盘"
- "昨天飞书云盘调通了，今天再看看"
- "分享链接给你，自己调试上传"

### 3.2 标准响应流程

**Step 1**: 检查现有插件
```bash
ls -la /root/.openclaw/workspace/plugins/ | grep feishu_drive
```

**Step 2**: 测试列表API（验证token有效）
```bash
cd /root/.openclaw/workspace/plugins && python3 feishu_drive_uploader.py list
```

**Step 3**: 生成测试文件
```bash
echo "测试文件内容 - $(date)" > /tmp/test_upload.txt
```

**Step 4**: 执行上传
```bash
python3 feishu_drive_uploader.py upload /tmp/test_upload.txt
```

**Step 5**: 报告结果并更新MEMORY.md

---

## 4. 自动化集成 (S4 - 自动化)

### 4.1 每日备份Cron

```bash
# 每天03:00执行云盘备份
0 3 * * * cd /root/.openclaw/workspace && python3 plugins/feishu_drive_uploader.py upload memory/backup.zip
```

### 4.2 配置固化

成功配置后，在以下位置记录：
- `MEMORY.md` → 飞书云盘上传 ✅ 已调通
- `TOOLS.md` → 插件路径和命令速查
- 本Skill文档 → 永久保存流程

---

## 5. 验证清单 (S5 - 验证)

### 5.1 功能验证
- [ ] `list` 命令返回文件列表
- [ ] `upload` 命令成功上传
- [ ] 大文件自动压缩（>20MB）
- [ ] 指定文件夹上传正常

### 5.2 当前状态 (2026-03-26)

| 检查项 | 状态 | 备注 |
|--------|------|------|
| 插件存在 | ✅ | `feishu_drive_uploader.py` |
| Token有效 | ✅ | 已获取tenant_access_token |
| 列表API | ✅ | 返回3个文件 |
| 上传API | ✅ | 测试文件上传成功 |
| 权限范围 | ✅ | drive:drive, drive:file |

---

## 6. 局限与边界 (S6 - 认知谦逊)

### 6.1 已知局限
1. **文件大小限制**: 单次上传最大20MB，超大文件自动压缩为ZIP
2. **Token有效期**: tenant_access_token 有效期2小时，自动刷新
3. **文件夹权限**: 需要用户提前创建文件夹并获取folder_token
4. **依赖系统命令**: 压缩功能依赖系统 `zip` 命令

### 6.2 不支持的场景
- 断点续传
- 多线程并行上传
- 文件夹递归上传
- 实时同步（双向）

---

## 7. 对抗测试 (S7 - 鲁棒性)

### 7.1 故障场景测试

| 场景 | 预期行为 | 实际结果 |
|------|----------|----------|
| Token过期 | 自动刷新并重试 | 已实现 |
| 文件不存在 | 返回清晰错误 | 已实现 |
| 网络中断 | 抛出异常 | 已实现 |
| 文件夹token无效 | API返回错误 | 待测试 |
| 超大文件(>100MB) | 压缩后上传 | 待测试 |

### 7.2 恢复机制

如果插件失效：
1. 检查 `plugins/feishu_drive_uploader.py` 是否存在
2. 检查APP_ID/APP_SECRET是否有效
3. 重新执行完整调试流程

---

## 附录：速查命令

```bash
# 快速测试连通性
cd /root/.openclaw/workspace/plugins && python3 feishu_drive_uploader.py list

# 快速上传文件
python3 feishu_drive_uploader.py upload /path/to/file

# 上传到指定文件夹
python3 feishu_drive_uploader.py upload /path/to/file <folder_token>
```

---

**最后验证**: 2026-03-26 10:11  
**验证结果**: ✅ 测试文件上传成功 (Token: HL7TbrBHDotaQxxzV2rceVd9ngg)  
**状态**: 已深度记忆，下次自动响应


## S1: 全局考虑

### 人
- **操作者**: AI助手（满意妞）
- **使用者**: Egbertie（最终用户）
- **维护者**: AI自我维护

### 事
- **核心功能**: [根据Skill具体功能描述]
- **边界场景**: 异常情况处理、降级策略
- **异常处理**: 错误捕获、重试机制、告警通知

### 物
- **输入资源**: 用户指令、配置文件、环境变量
- **输出产物**: 执行结果、日志文件、状态报告
- **依赖工具**: OpenClaw框架、系统工具、外部API

### 环境
- **运行环境**: Linux系统、OpenClaw运行时
- **配置要求**: 环境变量、权限设置
- **权限需求**: 文件读写、网络访问、进程管理

### 外部
- **第三方依赖**: 根据Skill具体依赖
- **API限制**: 速率限制、配额管理
- **网络要求**: 互联网连接（如需要）

### 边界
- **功能边界**: 明确Skill能力范围
- **性能边界**: 响应时间、资源消耗上限
- **安全边界**: 权限最小化、敏感信息保护


## S2: 系统闭环

### 输入
- **输入格式**: 明确参数格式、类型要求
- **参数校验**: 前置验证、默认值处理
- **默认值**: 合理的默认配置

### 处理
- **核心逻辑**: Skill主要功能实现
- **错误处理**: 异常捕获、优雅降级
- **日志记录**: 操作日志、错误日志、审计日志

### 输出
- **输出格式**: 标准化输出结构
- **状态码**: 成功/失败状态标识
- **错误信息**: 清晰的错误描述和解决方案

### 反馈
- **执行结果**: 任务完成状态
- **状态报告**: 当前系统状态汇总
- **异常告警**: 异常情况及时通知


## S3: 可观测输出

### 指标
- **执行次数**: 任务执行计数
- **成功率**: 成功执行比例
- **耗时**: 平均执行时间
- **Token消耗**: 本Skill的Token使用情况

### 日志
- **操作日志**: `/tmp/[skill-name].log`
- **错误日志**: 异常详情记录
- **审计日志**: 关键操作追踪

### 报告
- **执行报告**: 单次执行详情
- **状态报告**: 定期状态汇总
- **统计报告**: 周期性能统计


## S4: 自动化执行

### 触发
- **Cron定时**: 根据需求配置定时任务
- **事件触发**: 文件变更、状态变化
- **手动触发**: 用户主动调用

### 脚本
- **自动化脚本**: `scripts/[skill-name].sh`
- **批处理**: 批量任务处理
- **流水线**: CI/CD集成（如适用）

### 监控
- **自动监控**: 进程监控、资源监控
- **自动告警**: 异常自动通知
- **自动恢复**: 故障自动重启/修复


## S5: 自验证机制

### 测试
- **单元测试**: 核心功能独立测试
- **集成测试**: 与其他组件集成验证
- **端到端测试**: 完整流程验证

### 检查清单
- **前置检查**: 环境、依赖、权限验证
- **执行检查**: 中间状态确认
- **后置检查**: 结果验证、清理确认

### 质量门禁
- **通过率阈值**: 测试通过率≥90%
- **质量标准**: 代码规范、文档完整
- **失败处理**: 失败重试、降级方案、告警通知
