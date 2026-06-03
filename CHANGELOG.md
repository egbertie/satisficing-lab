# CHANGELOG

## [W22] - 2026-05-28 ~ 2026-06-03

### 产品体系 v5.0 · 十二体系融合
- 🏗️ 架构: 统一产品框架 · 十二体系融合 · product-catalog 用户面向四象限筛选
- 🎭 心理类型: 五类标注(镜子·翻译·地图·解药·灯塔) + 共鸣度评分
- 🧬 双光谱: 左右脑+五维评分体系上线 · 驾驶舱🧠产品大脑
- 🏆 品质体系 v3.0: 四层金字塔 + 12-Gate 全量审计 + 精品飞轮 + BARS v2.0
- 🧪 精品飞轮: 3精评>320基础 · 蒸馏闭环 · LLM认知推理精评

### 驾驶舱 v13 · 全面增强
- 🔄 控制论面板: 四层诊断 + 永续控制 + 诚实评分 + LLM对比
- 🧑‍💻 用户面向: v4.0四象限面板 · 品质金字塔面板
- 📊 v10 精确数据层: 6面板统计卡 · 精准数据+源溯
- 🆘 帮助面板: 五层导航 + 全局搜索 + 产品库搜索

### AI 互动工具
- 🧠 直觉训练场: 10轮3秒直觉决策训练
- 💬 对话桥: 5题合伙人对话引导工具
- 🃏 突破卡: 15张创意激发卡牌
- 🎭 三个有灵魂产品: 照见/今日一得/身体日记
- 🌀 元合伙: 灵魂注入 · 五问对话 · 从表单到对话

### 品牌 & 视觉
- 🎨 VI Logo 全面部署: 火承土印+契+晋+鼎+玉 · 20枚标识全站嵌入
- 📱 响应式: 品牌首页+驾驶舱+产品目录 768px/400px 双断点适配
- 🏠 品牌首页: 重构为客户流视角 · 情况分诊台5种处境入口

### 知识体系 & 自动化
- 🌐 知识图谱: 3126连接 · 3836实体 · 48生物化规则
- ⏳ 时间考古: 731实体 · 38天时间线 · 67事件
- 🛡️ 七层免疫: L0基线+L2先天免疫+L4免疫记忆+L5自愈
- 🏗️ 物理层: 信息架构V2 + 统一实体索引 MDM标准
- 📦 312产品: 全量审核上架 · 精品28 · 线上214 · 资料70

### Admin v3.0
- 🏗️ 架构: 9域36模块 · 二级折叠侧栏 · 三级穿透
- 🎨 四层全覆盖: 物理·化学·生物·心理 100%
- 🔗 驾驶舱协同: 返回链接 · 数据统一源 · 模块间跳转

### 客户 & 生命周期
- 📈 客户生命周期 v5.0: 10阶段(宣发→共契) + 获客引擎 + 6渠道矩阵
- 🤝 产品×客户 v4.0: 四层体系(L0→L3) · 阶段性解锁
- 🩺 客户管理 v3.0: 独立客户流 + 健康评分 + 预警中心

### v7 全站优化
- 🔧 139页Logo + 7页标题 + 4页VI配色 + tab五层重排
- 📝 250+页面title批量修复 + 8残留清理
- 🔗 全站链接闭环: 导航链路修复 · 返回链接补全
- 🐛 QA审核: 9项异常修复 · 全站263页闭环

### 工具 & 基础设施
- 🔧 devserver.py 本地测试服务器 + dev.sh 验收脚本
- 📦 备份镜像Action · stable-2026-05-29 全站248页封装
- 🚀 GitHub Pages 文件浏览器 + portal.html 统一入口

---

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
