---
# 知识元数据 (5标准化)
knowledge_id: W16-343CA1
title: Git Auto-Commit Skill
category: 11_Skill文档
source: skills/git-auto-commit/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 4344
week: 16
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Git Auto-Commit Skill

> **知识ID**: W16-343CA1  
> **分类**: 11_Skill文档  
> **来源**: `skills/git-auto-commit/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Git Auto-Commit Skill

## Overview
Git自动提交系统——基于780未提交变更的教训，建立永久自动化的代码保护机制。

## S1: Global Consideration (全局考虑)

### 1.1 人 (People)
| 角色 | 行为模式 | 风险点 |
|------|----------|--------|
| 开发者 | 专注编码，忘记提交 | 数据丢失 |
| AI助手 | 批量修改文件 | 累积大量变更 |
| 系统 | 定时触发 | 冲突处理 |

### 1.2 事 (Tasks)
- 变更检测（每2小时）
- 自动暂存与提交
- 推送重试与失败处理
- 冲突检测与告警

### 1.3 物 (Resources)
- Git仓库（本地+远程）
- 提交日志
- 锁文件（防止并发）
- 配置文件

### 1.4 环境 (Environment)
- 网络可用/不可用
- 远程仓库可访问/不可访问
- 工作时段/非工作时段

### 1.5 外部集成 (External)
- GitHub/GitLab API
- 飞书/企微通知
- Cron调度器

### 1.6 边界情况 (Edge Cases)
- 空提交（无变更）
- 合并冲突
- 超大变更集（>1000文件）
- 网络瞬时中断
- Git锁竞争

## S2: System Closed Loop (系统闭环)

### 2.1 输入
```
时间触发(每2小时) 或 文件变更>50
  ↓
检测工作区状态
```

### 2.2 处理
```
变更检测 → 统计变更 → 自动暂存 → 生成提交信息 → 本地提交 → 尝试推送
```

### 2.3 输出
```
提交结果 + 推送结果 + 日志记录
```

### 2.4 反馈
```
推送失败 → 记录待推送 → 下次重试
冲突检测 → 暂停自动提交 → 告警人工
```

### 2.5 故障处理
| 故障 | 检测 | 自动处理 | 告警 |
|------|------|----------|------|
| 推送失败 | exit code | 记录重试队列 | 2次失败后 |
| 合并冲突 | git status | 暂停自动提交 | 立即 |
| 网络中断 | timeout | 仅本地提交 | 不告警 |
| 锁竞争 | lock file | 退出等待下次 | 不告警 |

## S3: Observable Outputs (可观测输出)

### 3.1 量化指标
| 指标 | 目标 | 测量 |
|------|------|------|
| 提交频率 | 每2小时 | Cron执行记录 |
| 推送成功率 | >95% | 推送日志 |
| 平均变更文件数 | <100 | 提交统计 |
| 未推送积压 | 0 | 重试队列 |

### 3.2 结构化日志
```json
{
  "timestamp": "2026-03-25T20:35:00+08:00",
  "type": "auto_commit",
  "files_changed": 837,
  "insertions": 41874,
  "deletions": 114,
  "commit_hash": "11e49ce",
  "push_status": "local_only",
  "push_attempts": 1,
  "next_retry": "2026-03-25T22:35:00+08:00"
}
```

### 3.3 状态报告
```
📊 Git自动提交状态 (2026-03-25 20:35)
━━━━━━━━━━━━━━━━━━━━━━━━━━
上次提交: 11e49ce (2分钟前)
变更文件: 837个
推送状态: ⏳ 本地已提交，推送待认证
重试队列: 1个提交待推送
━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## S4: Automated Integration (自动化集成)

### 4.1 Cron配置
```yaml
jobs:
  - name: auto-git-commit
    schedule: "0 */2 * * *"  # 每2小时
    script: disaster-recovery/auto-git-commit.sh
    timeout: 300
  
  - name: push-retry
    schedule: "*/30 * * * *"  # 每30分钟检查推送
    script: disaster-recovery/push_retry.sh
```

### 4.2 触发条件
- 定时：每2小时
- 事件：文件变更>50个
- 手动：用户执行脚本

### 4.3 脚本清单
| 脚本 | 功能 | 调用 |
|------|------|------|
| auto-git-commit.sh | 主提交逻辑 | Cron/手动 |
| push_retry.sh | 推送重试 | Cron |
| commit_stats.py | 提交统计 | 手动 |

## S5: Self-Validation (自我验证)

### 5.1 自动检查
- [ ] Git仓库存在且可写
- [ ] 用户配置（name/email）
- [ ] 远程仓库配置
- [ ] 上次提交时间
- [ ] 未推送提交数

### 5.2 测试用例
```bash
# 测试空变更
cd /tmp && mkdir test_git_auto && cd test_git_auto && git init
cp /root/.openclaw/workspace/disaster-recovery/auto-git-commit.sh .
bash auto-git-commit.sh
# 期望: "工作区干净，无需提交"

# 测试正常提交
echo "test" > test.txt
bash auto-git-commit.sh
# 期望: 提交成功，日志记录
```

### 5.3 健康检查
```bash
# 检查Git状态
git status --short | wc -l
# 应返回0（无未提交变更）

# 检查未推送提交
git log origin/main..HEAD --oneline | wc -l
# 应监控此数值
```

## S6: Cognitive Humility (认知谦逊)

### 6.1 能力边界
1. **无法解决合并冲突**：需人工介入
2. **无法强制推送**：需认证，需用户授权
3. **无法处理二进制大文件**：需Git LFS
4. **无法保证网络可用**：依赖外部条件

### 6.2 不确定性标注
- 提交信息标注[AUTO]以区分手动提交
- 推送状态标注[待重试]或[失败]
- 变更统计基于git diff，可能包含未跟踪文件

### 6.3 已知问题
- 首次推送需认证（GitHub Token）
- 大文件提交可能超时
- 锁文件可能残留（需清理）

## S7: Adversarial Testing (对抗测试)

### 7.1 测试场景

#### 场景1: 无变更
```
状态: 工作区干净
触发: 自动提交
预期: 检测无变更，正常退出，无空提交
```

#### 场景2: 单文件变更
```
操作: 修改1个文件
触发: 自动提交
预期: 正确提交，信息包含文件数
```

#### 场景3: 大量变更
```
操作: 批量创建1000个文件
触发: 自动提交
预期: 提交成功，可能耗时较长，日志记录
```

#### 场景4: 推送失败重试
```
操作: 断开网络
触发: 提交+推送
预期: 本地提交成功，推送失败，加入重试队列
恢复: 网络恢复后，push_retry.sh自动推送
```

#### 场景5: 合并冲突
```
操作: 远程有新提交，本地修改同一文件
触发: 自动提交后推送
预期: 推送失败，检测到冲突，暂停自动提交，告警
```

#### 场景6: 锁竞争
```
操作: 同时运行两个实例
触发: 自动提交
预期: 第二个实例检测到锁，退出等待
```

#### 场景7: 超大文件
```
操作: 创建200MB文件
触发: 自动提交
预期: 提交失败（或极慢），告警，跳过
```

## Usage

### 手动执行
```bash
# 立即执行自动提交
bash disaster-recovery/auto-git-commit.sh

# 查看提交日志
tail -f /tmp/auto-git-commit.log

# 查看统计
python3 disaster-recovery/commit_stats.py
```

### 配置
```bash
# 设置Git用户信息（必须）
git config user.name "Auto Committer"
git config user.email "auto@example.com"

# 配置远程仓库
git remote add origin https://github.com/user/repo.git
```

## Files

| 文件 | 路径 | 说明 |
|------|------|------|
| 主脚本 | disaster-recovery/auto-git-commit.sh | 自动提交 |
| 日志 | /tmp/auto-git-commit.log | 执行记录 |
| 锁文件 | /tmp/auto-git-commit.lock | 并发控制 |

## Version
- **Version**: V1.0
- **Status**: FIN (7-standard complete)
- **Created**: 2026-03-25
- **Trigger**: 780-uncommitted-incident
- **Standard**: S1-S7 full compliance
