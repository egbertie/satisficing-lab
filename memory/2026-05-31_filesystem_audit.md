# 文件体系健康审计 · 2026-05-31

## 一、诊断结果

### 严重度：🔴 P0

| 问题 | 现状 | 影响 |
|------|------|------|
| 根目录碎片化 | 258 HTML + 6 JSON + 5 JS + 9 MD + 3 TXT + 4 BAK = **285 文件** | 找不到东西、Git 混乱、Pages 部署冲突 |
| site/ 子模块混乱 | 子模块与主仓库指向同一 repo，根目录 HTML 与 site/ 内容重复 | Pages 部署旧版本、版本同步失败 |
| memory/ 结构杂乱 | 22 .md + 6 .json + 1 .jsonl 混居，无清晰分层 | 难以检索、数据饥渴诊断困难 |
| 对话/ 报告严重缺失 | 5/30 仅2篇报告，5/31 零报告 | 大量工作无留痕，知识遗产流失 |
| 根目录与 site/ 内容重叠 | admin-windows.html/file-browser.html 等在两个位置都有 | 哪个是权威？冲突 |
| .bak 文件散布 | 根目录 4 .bak + memory/_backups + .bak/ 目录 | 备份策略混乱 |

### 关键指标

| 指标 | 当前值 | 目标 |
|------|--------|------|
| 根目录文件数 | 285 | ≤15 |
| HTML 权威副本数 | 2 (root + site/) | 1 |
| 对话报告覆盖率 | ~15% (5/29后) | 85%+ |
| 子模块健康 | ❌ 破环 | ✅ 正常 |
| .gitignore 有效性 | ⚠️ 部分失效 | ✅ 严格 |

---

## 二、整改方案

### 2.1 根目录清理

```
workspace/
├── AGENTS.md          Keep (系统文件)
├── SOUL.md            Keep (系统文件)
├── MEMORY.md          Keep (系统文件)
├── IDENTITY.md        Keep (系统文件)
├── USER.md            Keep (系统文件)
├── TOOLS.md           Keep (系统文件)
├── HEARTBEAT.md       Keep (系统文件)
├── README.md          Keep
├── CHANGELOG.md       Keep
├── start-fb.sh        Keep (工具脚本)
├── file-browser.py    Keep (本地服务)
├── memory/            Keep (数据中心)
├── 对话/              Keep (报告归档)
├── site/              Fix (子模块修复)
├── Projects/          Keep
├── Resources/         Keep
├── 项目/              Keep
├── miniapp/           Keep
├── 扣子资料_*/        Keep (归档)
├── 蓝军Skeptor-7/     Keep
├── 替身/              Keep
├── skills/            Keep
├── scripts/           Keep
└── satisficing-lab/   Keep
```

**需要移动/删除的 (约 270+ 文件):**
- 258 HTML → 全部移至 `site/` 或 `Archives/html-legacy/`
- 6 JSON → 移至 `memory/_data/` 对应位置
- 5 JS → 移至 `scripts/` 或删除（中间开发文件）
- 3 TXT → 评估后归档
- 4 BAK → 移至 memory/_backups/

### 2.2 site/ 子模块修复

**问题**: site/ 子模块与主仓库指向同一 repo → Pages 部署混乱

**方案A (推荐)**: site/ 去子模块化
1. 将 site/.git 改名 site/_.git（保留历史）
2. site/ 变成主仓库普通目录
3. 根目录 HTML 文件 → 只保留在 site/（权威副本）
4. .gitignore 保留 site/_.git

**方案B**: 保持子模块但规范管理
1. 建立 .gitmodules
2. 另建独立 repo 用于 site/
3. 主仓库不再维护 HTML 副本

### 2.3 memory/ 分层重组织

```
memory/
├── _data/              ← 18 结构化数据文件 (JSON/JSONL)
├── _scripts/           ← 16 控制论脚本 (Python)
├── _backups/           ← 所有 .bak 归档
├── daily/              ← YYYY-MM-DD.md 每日日志
├── reports/            ← YYYY-MM-DD_主题.md 专项报告
├── INDEX.md            ← 总索引
├── MEMORY.md           → root/MEMORY.md (符号链接或软链)
└── expert_team_*.md    ← 专家团队文件
```

### 2.4 对话文件夹规范

```
对话/
├── YYYY-MM-DD/
│   ├── 主题分类/
│   │   └── YYYY-MM-DD_HHMM_主题_状态.md
│   └── YYYY-MM-DD_每日摘要.md
├── INDEX.md
└── 归档/
```

**每个报告必含字段:**
- 时间戳 (YYYY-MM-DD HH:MM)
- 背景/动机
- 过程
- 成果 (文件·行数·数据)
- 架构决策 (ADR编号)
- 教训/反模式

### 2.5 新增 .gitignore 规则

```gitignore
# 系统
.DS_Store
__pycache__/
*.pyc
.fb-launchd.log
.fb-pid
.fb-log

# 历史归档
.bak/
Archives/
*_历史归档/
扣子资料_*/

# 备份
*.bak
memory/_backups/

# 废弃开发文件
*.txt  (除 README/CHANGELOG)
admin-v3-*.js
admin-v3-*.txt
```

---

## 三、执行优先级

| 优先级 | 任务 | 预计工作量 | 风险 |
|--------|------|-----------|------|
| P0 | 根目录 HTML 归类整理 | 30min | 低（只移不删） |
| P0 | site/ 子模块修复 | 15min | 中（影响 Pages） |
| P1 | memory/ 分层重组 | 20min | 低 |
| P1 | 对话报告补全 | 已在执行 | 无 |
| P2 | .gitignore 完善 | 5min | 低 |

---

## 四、质量门禁

- [ ] 根目录文件数 ≤ 15
- [ ] site/ pages 路径统一且已部署最新版
- [ ] 对话报告覆盖率 85%+
- [ ] memory/ 子目录清晰可索引
- [ ] 零 `.bak` 文件散落
- [ ] git status 干净
