---
# 知识元数据 (5标准化)
knowledge_id: W13-616F43
title: Finishing a Development Branch Reference
category: 11_Skill文档
source: skills/.archive_satisficing-dev-workflow/references/finishing-branch.md
ingested_at: 2026-03-27 17:59:30
word_count: 2297
week: 13
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Finishing a Development Branch Reference

> **知识ID**: W13-616F43  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_satisficing-dev-workflow/references/finishing-branch.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Finishing a Development Branch Reference

Source: satisficing-dev-workflow | obra/superpowers adaptation

---

## Overview

Verify tests → Present options → Execute choice.

Announce at start: "Using the finishing-a-development-branch skill to complete this work."

---

## Step 1: Verify Tests

Run the project's test suite. If tests fail — stop. Do not proceed.

```bash
# Python
pytest -q

# Node/TS
pnpm test

# Rust
cargo test

# Go
go test ./...
```

Show failures clearly. Cannot merge/PR until tests pass.

---

## Step 2: Determine Base Branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
git branch --show-current
```

Or ask: "This branch split from main — is that correct?"

---

## Step 3: Present Options

Present exactly these 4 options — no extra explanation:

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

---

## Step 4: Execute Choice

### Option 1: Merge Locally

```bash
git checkout <base-branch>
git pull
git merge <feature-branch>
<run tests>
git branch -d <feature-branch>
```

### Option 2: Push + PR

```bash
git push -u origin <feature-branch>
gh pr create --title "<title>" --body "## Summary
- <bullet 1>
- <bullet 2>

## Test Plan
- [ ] <verification step>"
```

### Option 3: Keep As-Is

Report: "Keeping branch `<name>`. You can return to it later."

### Option 4: Discard

**Confirm first:**
```
This will permanently delete:
- Branch <name>
- All commits since <base-branch>

Type 'discard' to confirm.
```

Wait for exact word "discard". Then:
```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

---

## Quick Reference

| Option | Merge | Push | Keep Branch | Delete Branch |
|--------|-------|------|-------------|---------------|
| 1. Merge locally | ✓ | — | — | ✓ |
| 2. Create PR | — | ✓ | ✓ | — |
| 3. Keep as-is | — | — | ✓ | — |
| 4. Discard | — | — | — | ✓ (force) |

---

## Common Mistakes

- Skipping test verification before offering options → always verify first
- Merging without pulling latest base → always `git pull` before merge
- Deleting branch before confirming PR merged → wait for merge confirmation
