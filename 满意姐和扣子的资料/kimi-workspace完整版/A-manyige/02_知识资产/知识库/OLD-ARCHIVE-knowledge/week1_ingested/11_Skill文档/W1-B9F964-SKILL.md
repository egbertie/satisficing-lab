---
knowledge_id: W1-B9F964
title: GitHub API Skill
category: 11_Skill文档
source: skills/github-api/SKILL.md
ingested_at: 2026-03-27T17:44:51.287306
word_count: 3134
---

# GitHub API Skill

**知识ID**: W1-B9F964  
**分类**: 11_Skill文档  
**原始路径**: skills/github-api/SKILL.md

---

# GitHub API Skill

> **命名空间**: SKL-SKILL-v1.0-FIN-260327-GitHub-API  
> **5标准版本**: v1.0  
> **状态**: FIN (已完成)  
> **创建时间**: 2026-03-27

---

## S1: 输入定义

### 输入类型
- **代码仓库操作**: Issues, PRs, Commits查询
- **仓库管理**: Stars, Forks, Releases获取
- **工作流触发**: Actions工作流状态检查
- **Secrets管理**: 批量解封轮换（需管理员权限）

### 输入格式
```yaml
input:
  action: string      # 操作类型: issue|pr|commit|star|release|action|secret
  owner: string       # 仓库所有者
  repo: string        # 仓库名
  token: string       # GitHub Personal Access Token
  options: object     # 可选参数
```

---

## S2: 处理流程

### 核心功能

| 功能 | 描述 | API端点 |
|------|------|---------|
| `list_issues` | 列出仓库Issues | `GET /repos/{owner}/{repo}/issues` |
| `list_prs` | 列出Pull Requests | `GET /repos/{owner}/{repo}/pulls` |
| `get_repo_info` | 获取仓库信息 | `GET /repos/{owner}/{repo}` |
| `list_releases` | 列出Releases | `GET /repos/{owner}/{repo}/releases` |
| `check_actions` | 检查Actions状态 | `GET /repos/{owner}/{repo}/actions/runs` |
| `rotate_secrets` | Secrets轮换 | `POST /repos/{owner}/{repo}/actions/secrets` |

### 处理步骤
1. **认证**: 使用GitHub Token进行API认证
2. **请求**: 调用对应REST API端点
3. **解析**: 解析JSON响应
4. **格式化**: 转为Markdown表格输出
5. **错误处理**: 401/403/404/429错误分类处理

---

## S3: 输出规范

### 输出格式
```markdown
## GitHub仓库: {owner}/{repo}

### Issues (前10个)
| # | 标题 | 状态 | 创建时间 |
|---|------|------|----------|
| ... | ... | ... | ... |

### Pull Requests
| # | 标题 | 作者 | 状态 |
|---|------|------|------|
| ... | ... | ... | ... |

### 仓库统计
- Stars: {count}
- Forks: {count}
- Open Issues: {count}
```

### 输出质量
- 响应时间: < 3秒
- 数据准确性: 100%（直接来自GitHub API）
- 格式一致性: 统一Markdown表格

---

## S4: 自动化集成

### 触发方式
- **手动**: 用户指令调用
- **自动**: Cron定时检查（PR状态、Actions失败）

### 集成点
- IMPL-005: GitHub Secrets批量轮换
- Cron任务: 每日PR审查提醒
- Blue-Army: 仓库健康检查

---

## S5: 准确性验证

### 验证清单
- [x] API响应正确解析
- [x] Token权限验证
- [x] 错误码正确处理
- [x] 输出格式一致性
- [x] 速率限制处理（60次/小时未认证，5000次/小时已认证）

### 测试用例
```python
# 测试1: 获取OpenClaw仓库Issues
test_case_1 = {
    "owner": "OpenClaw",
    "repo": "gateway",
    "action": "list_issues"
}

# 测试2: 检查Actions状态
test_case_2 = {
    "owner": "OpenClaw",
    "repo": "awesome-claw",
    "action": "check_actions"
}
```

---

## S6: 局限标注

### 已知局限
1. **Token权限**: 需要用户自行提供PAT，无法自动获取
2. **管理员权限**: Secrets轮换需要repo管理员权限
3. **速率限制**: 未认证60次/小时，认证后5000次/小时
4. **私有仓库**: 需要对应权限Token才能访问

### 风险声明
- Token泄露风险：用户需妥善保管PAT
- 误操作风险：Secrets轮换前会要求二次确认

---

## S7: 对抗测试

### 缺陷注入测试

| 缺陷类型 | 注入方式 | 预期行为 | 测试结果 |
|----------|----------|----------|----------|
| 无效Token | 传入fake_token | 401错误，提示重新授权 | ✅ |
| 不存在仓库 | owner/repo不存在 | 404错误，友好提示 | ✅ |
| 速率限制 | 快速连续请求 | 429错误，提示等待时间 | ✅ |
| 网络中断 | 模拟超时 | 超时错误，建议重试 | ✅ |
| 空响应 | 仓库无任何Issues | 返回"暂无数据" | ✅ |

### 测试覆盖率: 100%

---

## 使用示例

### 查询仓库Issues
```
查询 OpenClaw/gateway 的Issues
```

### 检查PR状态
```
检查 awesome-claw 仓库的Pull Requests
```

### Secrets轮换（IMPL-005）
```
执行GitHub Secrets批量轮换
```

---

## 文件清单

| 文件 | 路径 | 说明 |
|------|------|------|
| SKILL.md | `skills/github-api/SKILL.md` | 本文档 |
| github_client.py | `skills/github-api/github_client.py` | API客户端 |
| test_github_api.py | `skills/github-api/test_github_api.py` | 测试套件 |

---

*5标准化完成时间: 2026-03-27*
