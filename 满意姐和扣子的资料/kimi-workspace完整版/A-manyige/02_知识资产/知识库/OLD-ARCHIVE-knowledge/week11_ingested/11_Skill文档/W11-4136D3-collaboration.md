---
# 知识元数据 (5标准化)
knowledge_id: W11-4136D3
title: Collaboration Traps
category: 11_Skill文档
source: skills/.archive_git/collaboration.md
ingested_at: 2026-03-27 17:59:30
word_count: 1388
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Collaboration Traps

> **知识ID**: W11-4136D3  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_git/collaboration.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Collaboration Traps

## Push/Pull

- `git pull` = fetch + merge — can create unexpected merge commits
- `git pull --rebase` avoids merge commits but can have conflicts
- Push rejected for non-fast-forward ≠ you need force — pull first
- `--force` overwrites others' history — `--force-with-lease` is safer

## Force Push

- `--force` ignores others' changes — coworkers' commits lost
- `--force-with-lease` fails if remote changed — safer but not foolproof
- Force push to main/master = broken CI/CD references, failed deploys
- Branch protection on GitHub/GitLab prevents force push — always configure

## Remote Branches

- `git fetch` doesn't update working directory — only refs
- Branch tracking doesn't update automatically if remote renames
- `origin` is convention, not requirement — other remotes can exist
- `git remote prune origin` cleans refs but not local branches

## Code Review

- Push during review = new commits not necessarily reviewed
- Force push during review = diff changes, comments may become obsolete
- Approve before CI complete = bugs merged
- Squash merge loses individual commit history

## Team Coordination

- Multiple people on same branch = constant conflicts
- No branch naming convention = chaos in long-running projects
- Forgetting to pull before starting work = divergent history
- Rebasing shared branch without warning = teammates' work broken
