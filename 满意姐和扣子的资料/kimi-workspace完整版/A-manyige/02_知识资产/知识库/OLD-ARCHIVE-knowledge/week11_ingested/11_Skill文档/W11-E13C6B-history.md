---
# 知识元数据 (5标准化)
knowledge_id: W11-E13C6B
title: History Traps
category: 11_Skill文档
source: skills/.archive_git/history.md
ingested_at: 2026-03-27 17:59:30
word_count: 1471
week: 11
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# History Traps

> **知识ID**: W11-E13C6B  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_git/history.md`  
> **入库时间**: 2026-03-27

---

## 正文

# History Traps

## Reset

- `git reset --hard` loses uncommitted changes PERMANENTLY — no undo
- `--hard` vs `--soft` vs `--mixed` — each moves different things
- Reset of pushed commit = history diverges — you need force push
- Reset with untracked files = untracked survive — can surprise you

## Revert

- Revert creates NEW commit — doesn't delete the original
- Revert of merge commit needs `-m 1` or `-m 2` — without it, error
- Revert of revert = re-applies changes — confusing history
- Revert of old commit can conflict with later commits

## Amend

- `--amend` changes SHA — amended commit is DIFFERENT commit
- Amend of pushed commit = same problems as rebase
- `--amend` without staging = only changes message
- Accidental amend on wrong commit = use reflog to recover

## Reflog

- Reflog is LOCAL — doesn't sync with remote
- Reflog expires (default 90 days) — old commits lost
- `git gc` can clean unreachable commits before expiration
- Reflog of deleted branch is in HEAD reflog, not branch reflog

## Cherry-pick

- Cherry-pick creates new commit with different SHA
- Cherry-picking then merging = duplicate commits in history
- Cherry-pick of merge commit needs `-m` flag
- Conflicts in cherry-pick = resolve same as rebase

## Blame

- `git blame` shows last change, not original author
- Blame ignores whitespace changes with `-w`
- `git log -p filename` shows full history of changes
- Blame on moved code: use `git log --follow` for renamed files
