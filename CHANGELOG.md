# CHANGELOG

## [Admin v3.0] - 2026-05-30

### 管理后台 v3.0 · 体系化重构
- 🏗️ 架构: 9大管理域·36子模块·二级折叠侧栏
- 📊 三级穿透: L1总览卡→L2列表视图→L3四层详情
- 🎨 四层全覆盖: 物理🔩·化学⚗️·生物🧬·心理🧠 100%
- 🔗 驾驶舱协同: 返回链接·数据统一源·模块间跳转
- 📦 312产品·5客户·195任务·48规则·15Cron 全部动态渲染
- 🚫 零硬编码: 所有面板从entities_index.json动态fetch
- ✅ HTML/CSS/JS完全平衡·无语法错误

## 🏷️ stable-2026-05-29 — 全站稳定版本封装

> 2026-05-29 23:42 · **248个HTML文件全量存档** · 39个导航可达页面 · MD5双重验证

### 封装范围
- **site/ 全量**：248 个 HTML 文件，MD5 100% 一致验证通过
- **导航可达页面**：39 个 (从 index.html BFS 遍历完整链接图谱)
- **备份位置**：`site/.bak/stable-2026-05-29-full/` (248 f)
- **Git tag**：`stable-2026-05-29`

### 导航链路图谱 (39页)
```
index.html (入口)
├── about.html        → chemical-report, decision-theatre, go
├── assessment.html    → thermometer, privacy, terms, knights, account
├── cards-play.html    → assessment, thermometer, rps
├── checklist.html     → go
├── chemical-report    → decision-theatre, assessment
├── decision-theatre   → assessment, chemical-report
├── go.html (导航中枢) → guide, account, certification, go-gallery, about,
│                        assessment, thermometer, crisis-sim, knights,
│                        workshop, fulldiag, rps, slicing-pie, checklist,
│                        pre0, knights-cards, quotes, match, metapartner,
│                        exit-guide, creation, roots, cases, deep-gottman,
│                        product-catalog, flywheel, dashboard, privacy
├── privacy/terms/symbols → index, go
├── radar.html         → assessment, chemical-report
├── cases.html         → (案例库, 从零重写)
├── dashboard.html     → index (驾驶舱, sessionStorage密码门)
├── product-catalog    → go (产品目录, 108KB)
├── knights.html       → thermometer, assessment, account
├── fulldiag.html      → assessment
├── match.html         → metapartner, assessment
├── pre0.html          → assessment, crisis-sim
├── crisis-sim.html    → go
├── workshop.html      → go
├── certification.html → go
├── creation.html      → stars
├── stars.html         → creation, roots
├── roots.html         → assessment
├── flywheel.html      → dashboard
├── deep-gottman.html  → go
├── exit-guide.html    → assessment, crisis-sim
├── go-gallery.html    → wizard
├── wizard.html        → go
├── guide.html         → go
├── quotes.html        → go
├── rps.html           → go
├── slicing-pie.html   → go
├── metapartner.html   → go
├── thermometer.html   → knights, account
├── account.html       → go
└── report-demo.html   → chemical-report
```

### 质量门禁
- ✅ 0 个 `event.target`（全站 `this` 参数传递）
- ✅ 0 个 `crypto.subtle` / SHA-256（全站明文）
- ✅ sessionStorage 密码门 + 降级提示
- ✅ 248/248 MD5 备份一致

---

### 早期记录

> 2026-05-29 23:32 · 8个核心页面统一存档（已被上方全量覆盖）

### 封装清单
| 页面 | 大小 | 关键特征 |
|------|------|----------|
| index.html | 13KB | 首页，术语统一，两翼恢复 |
| about.html | 9KB | 关于页，三脉修正 |
| checklist.html | 11KB | 自检清单，VI统一，12源验证 |
| cases.html | 9KB | 案例库，fil+this模式 |
| gate.html | 9KB | 密码门，明文比对 |
| decision-theatre.html | 22KB | 决策剧场，水月观音 |
| product-catalog.html | 108KB | 产品目录 |
| dashboard.html | 50KB | 驾驶舱，sessionStorage密码门+降级提示 |

### 关键决策
- **密码门改用 sessionStorage**：关闭浏览器即清除，每次打开需重新输入，根治跨浏览器缓存不一致
- **降级提示**：检测到 sessionStorage 不可用时（如 Safari 内容拦截器），密码门显示黄色提示
- **0 个 event.target**：全站使用 `this` 参数传递模式
- **0 个 crypto.subtle**：全站明文密码
- **备份位置**：`site/.bak/stable-2026-05-29/`
- **Git tag**：`stable-2026-05-29`

---

## [dashboard] - 2026-05-29

### v4 (23:00) - 恢复稳定版
- 回滚到v2数据版本（飞书数据正常、tab正常）

### v3 (22:30) - 字体修改
- ❌ 全局替换font-size导致布局破坏 → 已回滚

### v2 (21:30) - 数据连接
- ✅ 连接飞书Base：195任务+26客户
- ✅ 明文密码验证
- ✅ this参数模式（无event.target）

### v1 (20:00) - 从零重写
- ✅ 产品库模式（onclick传this）
- ✅ 一个script块
- ✅ 11个tab全部可用

---

## [cases] - 2026-05-29

### v2 (22:38) - 终极重写
- ✅ 用诊断页验证通过的模式完整替换
- ✅ fil(type, btn) + this传参
- ✅ 12个案例数据内嵌

### v1 - 初始版  
- ❌ event.target导致筛选按钮无效

---

## [index] - 2026-05-29

### v2 - 表述统一
- ✅ 决策教练 → 决策外脑
- ✅ 22年 → 11年（银行）
- ✅ 两翼恢复左脑+右脑
- ✅ 3月26日试运营 + 6月21日正式运营

---

## [about] - 2026-05-29

### v2 - 三脉修正
- ✅ 三个11年讲法
- ✅ 五维决策对外
- ✅ 品牌归属精简

---

## [decision-theatre] - 2026-05-29

### v2 - 术语修正
- ✅ 观自在 → 水月观音
- ✅ 四骑士 → 关系危机信号

---

## [checklist] - 2026-05-29

### v2 - VI统一
- ✅ 全面重排排版
- ✅ 12源验证
- ✅ 决策行动分级设计

---

## [gate] - 2026-05-29

### v2 - 密码简化
- ✅ Web Crypto → 明文比对
- ✅ 12345678 / 123654 双密码
