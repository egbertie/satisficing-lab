# 满意解研究所 · 网站复刻手册

> SITE_HANDBOOK.md v1.0 · 2026-06-03
> 如果你正在读这份文件，可能是因为网站挂了、需要迁移、或者你想理解它到底是怎么建的。
> 这份手册的目的：让任何一个懂 HTML/CSS/JS 的人都能在几小时内完整复刻这个网站。

---

## 目录

1. [快速启动：10 分钟复刻](#1-快速启动10-分钟复刻)
2. [网站地图：所有页面](#2-网站地图所有页面)
3. [核心技术架构](#3-核心技术架构)
4. [数据流：entities_index.json 如何驱动一切](#4-数据流-entities_indexjson-如何驱动一切)
5. [产品体系：三类分层](#5-产品体系三类分层)
6. [管理后台：9 域 × 36 子模块](#6-管理后台9-域-×-36-子模块)
7. [VI 视觉识别系统](#7-vi-视觉识别系统)
8. [部署与运维](#8-部署与运维)
9. [故障恢复速查](#9-故障恢复速查)

---

## 1. 快速启动：10 分钟复刻

### 你只需要

1. 一台电脑（Mac / Windows / Linux 都可以）
2. Python 3（macOS 自带）
3. GitHub 账号（如果要部署上线）
4. 这份手册 + 完整代码包

### 本地预览（30 秒）

```bash
cd satisficing-lab
./dev.sh test
# 浏览器打开 http://localhost:8766/index.html
```

### 部署到 GitHub Pages（10 分钟）

```bash
# 1. 创建 GitHub 仓库，例如 yourname/my-site
# 2. 设置仓库为 GitHub Pages (Settings → Pages → Branch: main, root)

cd satisficing-lab
git init
git remote add origin git@github.com:yourname/my-site.git
git add -A && git commit -m "Initial"
git push -u origin main

# 3. 等待 1-2 分钟，访问 https://yourname.github.io/my-site/
```

### 绑定自定义域名

```bash
# 在 DNS 控制台添加 CNAME 记录：
#   www.yourdomain.com → yourname.github.io

# 在 GitHub 仓库 Settings → Pages → Custom domain 输入 www.yourdomain.com
# GitHub 会自动申请 HTTPS 证书
```

---

## 2. 网站地图：所有页面

### 入口页面（面向客户）

| 文件 | 说明 | 重要性 |
|------|------|:---:|
| `index.html` | **品牌首页** · 五维决策框架 · 核心产品 · 工具箱 · 时间线 · 关于我们 | 🔴 P0 |
| `go.html` | **产品导航页** · 五族折叠（章衡镜契觉）+ 45 个链接 | 🔴 P0 |
| `go-gallery.html` | **画廊浏览** · 60+ 产品卡片沉浸式浏览 | 🟡 P1 |
| `product-catalog.html` | **产品目录** · 动态 173+ 产品总表 | 🟡 P1 |
| `about.html` | **关于我们** · 品牌故事 · 团队 · 文化 | 🟡 P1 |

### 后台管理页面

| 文件 | 说明 | 重要性 |
|------|------|:---:|
| `dashboard-v3.html` | **驾驶舱** · 数据总览看板（只读），12 标签页 | 🔴 P0 |
| `admin-windows.html` | **管理后台** · 9 域 × 36 子模块，操作入口 | 🔴 P0 |
| `admin-overview.html` | 管理总览 | 🟡 P1 |
| `admin-tools.html` | 管理工具箱 | 🟡 P1 |

### 五族产品页（go.html 中引用）

**衡 · 标尺与量化**（司马贺·金·可行域）
- `fulldiag.html` · 衡·测渊 · 完整版诊断 28 题
- `rps.html` · 衡·探底 · RPS 风险剖面
- `slicing-pie.html` · 衡·分利 · SlicingPie 贡献记账
- `checklist.html` · 衡·校尺 · 决策前自检清单

**镜 · 照见与状态**（水月观音·水·身心流）
- `knights.html` · 镜·警兆 · 四骑士自检
- `pre0.html` · 镜·回身 · PRE-0 压力锚定
- `knights-cards.html` · 镜·警兆·速查

**觉 · 顿悟与淬炼**（六祖慧能·火·直觉阈）
- `crisis-sim.html` · 觉·淬火 · 危机模拟
- `decision-theatre.html` · 觉·入幕 · 决策剧场 🏆
- `cards-play.html` · 觉·入局 · 卡牌完整案例 🏆
- `quotes.html` · 觉·淬火·金句

**契 · 约定与规则**（孔子·木·信义观）
- `match.html` · 契·择伴 · 合伙人匹配度
- `metapartner.html` · 契·立盟 · 元合伙章程
- `exit-guide.html` · 契·善别 · 退出决策指南

**章 · 根基与传承**（刘禹锡·土·时间轴）
- `creation.html` · 章·创世 · 星月传奇
- `roots.html` · 章·立信 · 寻根手记
- `cases.html` · 章·鉴往 · 84 案例精选
- `deep-gottman.html` · L3·四骑士深度

### 技能/Skill 产品页（35 个）

按前缀 `sk-` 分组，编号 4-35：

| 范围 | 产品 | 数量 |
|------|------|:---:|
| sk-4 | archaeo, firewall, fresh, inherit, revive | 5 |
| sk-5 | 5d.html | 1 |
| sk-9 | deep.html | 1 |
| sk-10-35 | calm, match, negotiate, stress, survey, daily, honesty, protocol, workshop, moon, course, econ, fin, founder, comm, cog, cross, breakpoint, decomp, sync, decision-save, maturity, immunity, interrupt, batch, track, audit-skill, exec | 27 |

另有 `skill-*` 前缀的 6 个版本页：`skill-archaeo, skill-audit, skill-deep, skill-firewall, skill-fresh, skill-revive`

### 案例页（8 个）

`case-68entry`, `case-birui`, `case-dji-2007`, `case-gugao`, `case-haijou`, `case-xhs-zhangxue`, `case-yunjing`, `case-zhangxue`

### 血液产品页（14 个）

`blood-m1` 到 `blood-m14`，与五维框架元素对应

### 飞轮页（12 个）

`fw-m1` 到 `fw-m12`，知识飞轮的模块化组件

### 运营页（26 个）

`ops-accelerator`, `ops-app-prd`, `ops-canvas-physical`, `ops-community`, `ops-compliance`, `ops-content-calendar`, `ops-data-asset`, `ops-digital-transform`, `ops-email-sequence`, `ops-exit-design`, `ops-feedback-system`, `ops-finance-manual`, `ops-gov-relations`, `ops-industry-alliance`, `ops-knowledge-base`, `ops-member-system`, `ops-nps`, `ops-okr-manual`, `ops-pitch-pack`, `ops-podcast-plan`, `ops-prompt-lib`, `ops-publishing`, `ops-social-guide`, `ops-strategy-2026`, `ops-toolkit-governance`, `ops-viral-growth`

### 深度探索页（14 个）

`deep-altman`, `deep-chronicle-v1-4`, `deep-design`, `deep-duke`, `deep-feld`, `deep-gottman`, `deep-lencioni`, `deep-manifesto`, `deep-slicing`, `deep-thiel`, `deep-wasserman`

### 传播媒体页（6 个）

`media-email`, `media-podcast`, `media-ppt`, `media-video`, `media-xiaohongshu`, `media-zhihu`

### 对话页（8 个）

`dialogue-bridge`, `dialogue-full-check`, `dialogue-genesis`, `dialogue-genesis-command`, `dialogue-handover-test`, `dialogue-heritage-gap`, `dialogue-rules-not-run`, `dialogue-tsunami`

### 游戏页（7 个）

`game-conflict`, `game-duo`, `game-fengyun`, `game-journey`, `game-maturity`, `game-quick`, `game-totem`

### 跟踪页（5 个）

`track-battery`, `track-brain`, `track-evtol2`, `track-quantum`, `track-robot2`

### 微信系列（7 个）

`wx-0433`, `wx-awareness`, `wx-cancer`, `wx-ethics`, `wx-intuition`, `wx-scale`, `wx-trust`

### 产品开发页（4 个）

`prod-cards-physical`, `prod-matching-algo`, `prod-video-script`, `prod-web-engine`

### 危机页（3 个）

`crisis-pr`, `crisis-sim`, `crisis-warning-v1`

### 其他独立页

| 文件 | 说明 |
|------|------|
| `guide.html` | 用户引导 |
| `account.html` | 客户中心 |
| `assessment.html` | 综合评估 |
| `certification.html` | 认证引导师 |
| `workshop.html` | 公开课/工作坊 |
| `wizard.html` | 新手向导 |
| `privacy.html` | 隐私政策 |
| `terms.html` | 服务条款 |
| `whitepaper.html` | 白皮书 |
| `portal.html` | 门户入口 |
| `hibernate.html` | 休眠/维护页 |
| `farewell.html` | 告别页 |
| `newcomer.html` | 新手指南 |
| `onboarding.html` | 入职引导 |
| `exit-guide.html` | 退出指南 |
| `partner-protocol.html` | 合伙人协议 |
| `partner-escape.html` | 合伙人退出 |
| `proposal.html` | 方案建议书 |
| `file-browser.html` | 文件浏览器 |

### 废弃/开发版页面（保留在 .bak/ 中）

从根目录移走了 7 个 dashboard 版本（v1/v2/clean/kozi-debug/local/min/vfy），统一在 `.bak/` 归档。

---

## 3. 核心技术架构

### 技术栈

```
前端:   HTML5 + CSS3 + Vanilla JavaScript
         零框架依赖 · 零 NPM 依赖 · 零构建工具
后端:   静态文件（纯前端，无服务器）
数据:   entities_index.json (JSON 文件 · 8.1MB)
托管:   GitHub Pages (免费 · 自动 HTTPS · CDN)
开发:   Python 内置 HTTP Server (devserver.py)
```

### 文件依赖图

```
index.html ─────── sri-design.css          (设计系统)
go.html ───────── sri-design.css
admin-windows.html ─── entities_index.json  (数据驱动)
dashboard-v3.html ─── entities_index.json
所有产品页 ────── sri-design.css
cards-play.html ─── flywheel-engine.js      (飞轮引擎)
admin-tools.html ─── gate-check.js          (质量门禁)
account.html ─── password.js                (密码管理)
```

### 设计系统 (sri-design.css)

**一个 CSS 文件统治全部 265 页。** 基于 CSS 变量体系，零 class 框架依赖。

核心设计原则：
- Hook Model（触发→行动→可变奖励→投入）
- Storytelling Design（叙事引导决策）
- Dieter Rams「少却更好」

### 资源文件 (assets/)

40 个文件，包括 Logo 多尺寸（logo-small.png 等）、五维分标识、Favicon。

### 本地开发工具

| 文件 | 用途 |
|------|------|
| `dev.sh` | 开发工具入口（test/verify/push） |
| `devserver.py` | Python 零依赖本地服务器（端口 8766） |

**验证检查项（`dev.sh verify`，20 项）：**

| # | 类别 | 检查内容 | 发现场景 |
|---|------|----------|----------|
| 1-13 | 后端代码 | Python 语法编译（13个文件） | — |
| 14 | 前端完整性 | `sri-design.css` ≥ 5KB（防止截断） | 2026-06-03：批量注入脚本意外覆盖为 117B |
| 15 | 前端完整性 | `flywheel-engine.js` ≥ 5KB | 2026-06-03：同批被截断 |
| 16 | 前端完整性 | `gate-check.js` ≥ 10KB | 2026-06-03：同批被截断 |
| 17 | 前端完整性 | `sri-track.js` ≥ 2KB | — |
| 18 | 前端完整性 | `sri-api.js` ≥ 2KB | — |
| 19 | 数据 | `entities_index.json` JSON 有效性 | — |
| 20 | 关键页面 | JS 括号平衡检查 | 2026-06-03：残留 `</div>` 导致 JS 语法错误 |
| 21 | 品牌 | 「满意红」品牌名已全部清除 | — |
| 22 | 导航 | 关键页面客户通道入口一致性 | 2026-06-03：go.html 缺少客户通道链接 |
| 23 | 安全 | 驾驶舱无密码泄漏（`PASSCODE`/`123654`） | 2026-06-03：源码含明文密码 `123654` |
| 24 | 安全 | 管理后台无裸 `<h1>admin-windows</h1>` 标题 | 2026-06-03：页面显示 "admin-windows" |
| 25 | HTML | 关键页面 `</html>` 标签完整 | 2026-06-03：admin-windows 缺少 `</body></html>` |
| 26 | 链接 | HTML 页面内部引用有效性（死链检查） | — |
| 27 | API | 后端 Health + Contact API 可用性 | — |

**运行方式**：
```bash
./dev.sh verify
# 应通过 20+/20+ 项检查
```

---

## 4. 数据流：entities_index.json 如何驱动一切

### 数据模型

`entities_index.json` 是网站的**单一数据源**（Single Source of Truth）。

```json
{
  "meta": { "version": "...", "updated": "...", "total_entities": ... },
  "products": 315,       ← 产品索引
  "customers": 5,         ← 客户档案
  "avatars": 22,          ← 替身/角色
  "tasks": 195,           ← 任务
  "documents": 76,        ← 文档
  "decisions": 35,        ← 决策记录
  "milestones": 9,        ← 里程碑
  "connections": 12556,   ← 实体间关联
  "customer_profiles": 31,← 客户画像
  "cities": 31,           ← 城市市场数据
  "knowledge_pipeline": 5,← 知识消化管道
  "crons": 20,            ← Cron 任务
  "living_rules": 48,     ← 活跃规则
  "quality_metrics": 23,  ← 质量指标
  "workflows": 18,        ← 工作流
  "governance_frameworks": 6, ← 治理框架
  "vi_standards": 20,     ← VI 标准
  "lifecycle_stages": 7,  ← 生命周期阶段
  "simulation_scenarios": 16, ← 模拟场景
  "scoring_models": 2,    ← 评分模型
  "content_assets": 0,    ← 内容资产
  "instructions_set": 45, ← 指令集
  "growth_metrics": 10,   ← 增长指标
  "historical_artifacts": 10, ← 历史文物
  "additional_discoveries": 7, ← 发现
  "interactive_avatars": 5    ← 交互替身
}
```

### 数据流向

```
entities_index.json (Cron 每小时自动更新)
  │
  ├─→ admin-windows.html    (fetch JSON → 44 个 viewRenderer 函数 → 动态渲染)
  │     └─ 产品总览 / 客户360 / KPI仪表盘 / 质量中心 / 免疫系统 等
  │
  ├─→ dashboard-v3.html     (fetch JSON → 12 标签页 → 数据看板)
  │     └─ 总览 / 产品 / 客户 / 知识 / 免疫 / 城市 等
  │
  └─→ product-catalog.html  (fetch JSON → 产品列表渲染)
```

### 产品模型字段（products[] 中的每个产品）

```json
{
  "id": "PROD-001",
  "name": "产品名",
  "category": "内容 | 技能/Skill | 运营 | 测评 | 游戏 | 对话 | 产品开发 | 口眼 | 危机",
  "url": "product.html",          ← 有 URL = 线上可访问
  "status": "active | archived | draft",
  "premium": true,                ← 精品标识
  "phase": "概念 | 原型 | 内测 | 打磨 | 精品",
  "description": "...",
  "version": "1.0",
  "related": ["PROD-002", ...]
}
```

- 有 URL + 有文件 = 在线产品（约 173 个）
- 有 URL + 无文件 = 待上线
- 无 URL + 已归档 = 蒸馏归档（75 个，LC-007 状态）
- `premium: true` = 精品 18 件

---

## 5. 产品体系：三类分层

### 三层结构（324 件总产品）

```
精品 18 件 ────────── 深度打磨 · 完整叙事 · 强交互
  │
线上 155 件 ──────── 可访问 · 基础功能完整
  │
资料 67 件 ────────── 内部资料 · 调查 · 文档
  │
已蒸馏归档 75 件 ──── 保留设计思想 · 可反蒸馏恢复
```

### 精品 18 件（可独立体验的核心产品）

| 产品 | 文件 | 说明 |
|------|------|------|
| 决策剧场 | `decision-theatre.html` | 5 幕决策模拟 🏆 |
| 卡牌完整案例 | `cards-play.html` | 52 张卡牌 🏆 |
| 完整版诊断 | `fulldiag.html` | 28 题 8 模块 |
| 四骑士自检 | `knights.html` | 12 题关系诊断 |
| PRE-0 | `pre0.html` | 3 分钟压力锚定 |
| RPS 风险剖面 | `rps.html` | 32 题 4 维 |
| 危机模拟 | `crisis-sim.html` | 3 场景模拟 |
| 合伙人匹配 | `match.html` | 多维匹配度 |
| 元合伙章程 | `metapartner.html` | 协议生成 |
| SlicingPie | `slicing-pie.html` | 贡献记账 |
| 退出指南 | `exit-guide.html` | 决策框架 |
| 决策前清单 | `checklist.html` | 自检流程 |
| ... 等 6 件 |

### 产品形态通用原则

同一底层逻辑 → 不同形态实现 → 触类旁通

- **叙事/内容类** → 反思交互（轻量）
- **技能/工具类** → 标记交互（轻量）
- **单件深度** → 精品 18 件级别

---

## 6. 管理后台：9 域 × 36 子模块

### 架构概述

`admin-windows.html` 是管理操作的核心入口（与只读的 dashboard-v3.html 分工）。

### 9 个管理域（对标 ERP + BSC + PLM + KM）

| 域 ID | 名称 | 子模块 | 说明 |
|------|------|:---:|------|
| `strategy` | 📊 战略仪表盘 | 4 | KPI · 战略地图 · 里程碑 · 风险雷达 |
| `product` | 📦 产品全生命周期 | 5 | 总览 · 双光谱 · 管道 · 质量 · 发布 |
| `customer` | 👤 客户关系 | 4 | 360 档案 · 销售管道 · 交付 · 成功 |
| `finance` | 💰 财务与定价 | 4 | 收入 · 定价 · 成本 · 预算 |
| `knowledge` | 🧬 知识资产 | 4 | 图谱 · 内容 · 术语 · 学习 |
| `ops` | ⚙️ 运营与流程 | 4 | 任务 · 决策 · Cron · 工作流 |
| `governance` | 🛡️ 免疫与治理 | 4 | 免疫 · 规则 · 质量门禁 · 合规 |
| `archaeology` | 🏺 考古与洞察 | 4 | 时间线 · 文物 · 模拟 · 洞察 |
| `people` | 👥 组织与人 | 4 | 替身 · 专家团 · 评议会 · 网络 |

### 44 个 viewRenderer 函数

管理后台通过 `viewRenderers` 对象注册所有视图。每个域的子模块对应一个函数：

```javascript
// 新增视图只需注册一个函数
viewRenderers['product-overview'] = function() {
  // 从 DB (entities_index.json) 中取产品数据
  // 生成 HTML 表格/卡片
  // 返回 HTML 字符串
};
```

**三级穿透标准**：L1 总览卡 → L2 列表视图 → L3 详情

---

## 7. VI 视觉识别系统

### 色彩体系

```css
--sri-red:  #C23B22      /* 主色 · 火承土印 · 满意红 */
--sri-gold:  #8B6914      /* 辅助色 · 鼎玉 · 时间金 */
--sri-bg:    #F5F0E6      /* 背景 · 羊皮纸暖白 */
--text:      #4D4D4D      /* 正文 · 墨色 */
--text-muted:#6E6E6E      /* 次要文本 */
--title:     #2A2A2A      /* 标题 */
--border:    #C5B99A      /* 边框 */
--white:     #ffffff      /* 卡片白 */
--green:     #3D7A4F      /* 成功绿 */
```

### ❌ 严禁事项

- ❌ 使用正红 `#FF0000` 替代 `#C23B22`
- ❌ 拉伸/变形 Logo
- ❌ 给 Logo 加阴影或描边
- ❌ 去除 Logo 的斑驳质感
- ❌ Logo 小于 24px
- ❌ 使用非标准字体

### 字体

- **网页**：`PingFang SC`（macOS 系统字体，无需加载）
- **印刷**：`方正宋刻本秀楷`
- CSS 栈：`-apple-system, "PingFang SC", "Noto Sans SC", sans-serif`

### Logo 体系

| 标识 | 文件 | 用途 |
|------|------|------|
| 主标识（火承土印） | `assets/logo-small.png` | 品牌/关于/管理 |
| 直觉阈 | `assets/guanyin-small.png` | 慧能·火 |
| 可行域 | `assets/kexing-small.png` | 司马贺·金 |
| 时间轴 | `assets/jin-small.png` | 刘禹锡·土 |
| 身心流 | `assets/lianxin-small.png` | 观音·水 |
| 信义观 | `assets/liangyi-small.png` | 孔子·木 |
| 两翼引擎 | `assets/liangyi-small.png` | 概念页 |
| 鼎玉·机构 | `assets/dingyu-small.png` | 合规/账户 |
| 契晋·文化坐标 | `assets/ding-small.png` | 文化概念页 |

---

## 8. 部署与运维

### 完整部署流程

```bash
# Step 0: 准备
cd satisficing-lab
python3 -m http.server 8766    # 本地预览测试

# Step 1: 验收
./dev.sh verify
# 应通过 9/9 项检查

# Step 2: 推送
./dev.sh push
# 自动 git add/commit/push → GitHub Pages 自动部署

# Step 3: 验证上线
# 打开 https://egbertie.github.io/satisficing-lab/
# 检查首页/产品页/驾驶舱是否正常
```

### GitHub 仓库配置

- **主仓库**：`egbertie/satisficing-lab`
- **备份仓库**：`egbertie/satisficing-lab-backup`（自动镜像）
- **GitHub Pages 源**：Branch `main`，根目录 `/`
- **HTTPS**：GitHub 自动提供

### GitHub Actions（自动备份镜像）

`.github/workflows/mirror-backup.yml` — 每次 push 自动同步到备份仓库。需要 `BACKUP_TOKEN` secret。

### 本地备份

```bash
# 打包完整备份
tar czf satisficing-lab-YYYYMMDD.tar.gz \
  satisficing-lab/ memory/ MEMORY.md SOUL.md AGENTS.md USER.md IDENTITY.md TOOLS.md HEARTBEAT.md \
  满意姐和扣子的资料/ 扣子资料_最终整理版/

# 存到另一个硬盘
```

### 数据更新机制

- `entities_index.json` 由 Cron 每小时自动更新
- `open_tasks_audit.json` 任务审计清单
- `file_index.json`（87KB）文件索引

### .gitignore 策略

不跟踪的内容（保护隐私 + 减小仓库体积）：
- 扣子历史资料（含 API Key）
- 嵌套 git 仓库（satisficing-lab/ 子目录）
- 运行时文件（.portal-*, .fb-*）
- 备份文件（*.bak, .bak/）
- 历史归档（*_历史归档/）

---

## 9. 故障恢复速查

### 网站打不开

| 症状 | 可能原因 | 修复 |
|------|------|------|
| 404 | GitHub Pages 未启用 | Settings → Pages → Source: main / root |
| 显示异常 | CSS 缓存 | 硬刷新 Ctrl+Shift+R |
| 页面排版崩溃 | sri-design.css 被截断 | `git show HEAD:sri-design.css > sri-design.css` |
| 数据不显示 | entities_index.json 损坏 | `python3 -c "import json; json.load(open('entities_index.json'))"` |
| 只显示页面标题不渲染 | JS 语法错误（残留HTML标签） | `./dev.sh verify` 检查括号平衡 + 运行 `node --check` |
| 自定义域名失效 | DNS 记录过期 | 检查 CNAME 记录 / GitHub Pages 设置 |
| 仓库被删 | 账号问题 | 从本地备份恢复：`git push --force origin main` |
| JS/CSS 文件变成几字节 | 批量脚本误覆盖非HTML文件 | `git show HEAD:文件名 > 文件名` 逐个恢复 |

### 从零恢复（最坏情况）

```bash
# 你有一个本地备份文件：satisficing-lab-YYYYMMDD.tar.gz
tar xzf satisficing-lab-YYYYMMDD.tar.gz

# 创建新 GitHub 仓库
cd satisficing-lab
git init && git add -A && git commit -m "Recovery"
git remote add origin git@github.com:yourname/new-repo.git
git push -u origin main

# Settings → Pages → Source: main / root
# 等待 1-2 分钟即可访问
```

### 数据修复

```bash
# 如果 entities_index.json 损坏
# 从 memory/_data/entities_index.json 恢复（独立备份）
cp memory/_data/entities_index.json entities_index.json

# 或从 .bak/ 恢复历史版本
cp .bak/entities_index_2026-05-30T*.json entities_index.json
```

---

## 附录

### A. 关键查询

```bash
# 检查产品数量
python3 -c "import json; d=json.load(open('entities_index.json')); print(len(d['products']), 'products')"

# 统计有 URL 的产品
python3 -c "import json; d=json.load(open('entities_index.json')); print(sum(1 for p in d['products'] if p.get('url')), 'online')"

# 验证所有页面引用的文件存在性
for f in $(grep -oh 'href="[^"]*\.html"' *.html | sed 's/href="//;s/"//' | sort -u); do
  [ -f "$f" ] || echo "MISSING: $f"
done
```

### B. 相关文档

- `MEMORY.md` — 项目长时记忆（架构决策、反模式、品牌首页定义）
- `SOUL.md` — 人格设定（企业文化体系、专家团队）
- `memory/VI_视觉识别系统.md` — VI 完整规范
- `.gitignore` — 忽略规则
- `.github/workflows/mirror-backup.yml` — 自动备份

---

> 满意解研究所 · 火承土印 · 光的接力
> 版本: v1.0 · 生成: 2026-06-03
> 问题或更新 → 联系满意红
