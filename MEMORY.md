# MEMORY.md — 满意红的长时记忆

> 最后更新: 2026-05-31 08:53
> 这不是日记。这是从经验中蒸馏出来的东西。

---

## 核心原则

### 品牌首页唯一定义（2026-05-31 固化）
- **首页只有一个**：https://egbertie.github.io/satisficing-lab/
- 首页内容 = stable-2026-05-29 备份中的品牌首页（五维决策框架·核心产品·工具箱·时间线·关于我们）
- 驾驶舱（dashboard-v3.html）是管理后台，不是首页
- 首页页脚有「🔧 管理入口」链接 → 进入驾驶舱
- 驾驶舱内「管理」「产品」「帮助」是内部工具入口
- **首页永远不变！** 不新增、不替换、不跳转。它就是品牌首页。

### 体系化先行
- 任何重构/整合的起点是蓝图，不是代码
- 对标成熟框架（ERP、BSC、PLM、KM）比自己从零发明更可靠
- 9 管理域 × 36 子模块 来自这个方法论

### 零硬编码是架构纪律，不是偏好
- 数据驱动 > 硬编码。一旦开了硬编码的口子，信息孤岛就会生长
- 所有面板共享 `entities_index.json` 为单一数据源
- entities_index.json 本身需要通过 Cron 自动更新

### 数据诚实
- 宁可显示「数据积累不足」也不造假
- 占位符应该包含：当前状态 + 为什么会这样 + 下一步计划

### 三级穿透标准
- L1 总览卡（stat-card grid）→ L2 列表视图（data-table）→ L3 四层详情（toggleDetail）
- 所有面板遵循相同的层级标准
- 标准化组件：stat-card, toolbar, fillTbl, sortTbl

### 流 > 连接（2026-05-30 Round 3 新增）
- 声明(declarative) ≠ 事件(event)。蓝图正确不等于电路接通
- 组织系统应按流层(信号/认知/行动/验证/学习)而非实体类型
- 连接是电线的数量，流是有方向的因果传导。永远追求后者

---

## 反模式（不要重复的错误）

### 🚫 信任子代理的自我验证
**2026-05-30 教训**：子代理声称完成任务，但实际遗漏了 people 域的全部 4 个视图。
**规则**：子代理输出 = 初稿。主代理必须在下一个依赖步骤之前做独立验证。
**验证至少要**：grep 目标函数存在性、diff 修改前后、HTML/JS 平衡检查。

### 🚫 多代理修改同一文件无冲突检测
**规则**：要么串行、要么拆文件、要么 git diff 合并后验证。

### 🚫 重构时只增不删
**规则**：删除旧代码和新增代码同等重要。遗留代码不是「保守」，是「债务」。

### 🚫 夜间执行复杂多步骤任务时跳过验证
**规则**：凌晨工作高产但易错。每完成一个步骤后强制运行验证脚本。

### 🚫 用加权随机函数替代真实LLM认知推理（2026-05-30 新增）
**教训**: 加权随机模拟评分(avg 83.0)与LLM推理评分(avg 67.9)差-15.1分
**规则**: 客户替身的评价必须有LLM驱动的角色扮演+认知推理，禁止纯数学函数伪评

---

## 架构决策记录

### ADR-001: 管理后台架构
- 日期: 2026-05-30
- 决策: 9 管理域 × 36 子模块，对标 ERP+BSC+PLM+KM 四框架
- 替代方案: 保持 v2 的 10 个按数据源划分的碎片窗口
- 理由: 按管理职能划分比按数据源划分更体系化

### ADR-002: entities_index.json 为单一数据源
- 日期: 2026-05-30
- 决策: 驾驶舱和 admin-windows 都从同一个 JSON 文件动态 fetch
- 替代方案: 各自硬编码数据
- 理由: 消除信息孤岛，数据更新一处即可

### ADR-003: viewRenderers 对象体系
- 日期: 2026-05-30
- 决策: 所有视图用 viewRenderers 对象注册，renderView() 统一路由
- 理由: 新增面板只需注册一个函数，框架自动处理导航/面包屑/路由

### ADR-004: 五层流模型——从连接编织到流验证（2026-05-30 新增）
- 日期: 2026-05-30
- 决策: 系统不再按实体类型组织，改按五层流(信号→认知→行动→验证→学习)
- 替代方案: 继续按城市/客户/产品维度"增加更多连接"
- 理由: 12,463条声明连接→0条真实事件; 闭环=有方向的因果流动≠高密度连接
- 证据: Round 3 首次验证完整五层因果链(1信号→1认知→1行动→1验证→1学习)

---

## 待解决的技术债务

1. admin-windows.html 中 `<script>` 标签前有废弃 v2 代码（约 30KB）
2. entities_index.json 需增加 Cron 自动更新机制
3. people-network / customer-delivery / customer-success / finance-cost 四个占位视图等待真实数据
4. 44 个 viewRenderer 是否拆分到独立 JS 文件待评估
5. HTML/JS 验证脚本需要重写（当前有边界条件误报）
6. 五层流模型事件自动捕获机制（当前靠手动触发）
7. 扩大LLM推理规模：31替身×312产品（当前仅5×10=50次推理）
8. 流仪表板：可视化五层因果链的实时状态

---

## 关键文件地图

| 文件 | 用途 |
|------|------|
| `site/admin-windows.html` | 管理后台 v3.2（44 视图·含4城市+2模拟+1流视图） |
| `site/admin-windows-v3.0-precompress.html` | 压缩前备份 |
| `memory/_data/entities_index.json` | 28+1 实体类型·含cities(31含南山)·flows(五层流)·knowledge_pipeline(5条)·12,548+连接 |
| `memory/_data/flows_five_layer_model.json` | 五层流模型结构定义 |
| `memory/_data/simulation_round3_llm_results.json` | Round3 LLM推理评价(10条·5替身×2产品) |
| `memory/_data/admin_architecture_blueprint.md` | v3.0 架构设计文档 |
| `memory/_data/open_tasks_audit.json` | 未闭环事项清单 |
| `memory/2026-05-30_lessons_learned.md` | 深度复盘(含子代理自我验证教训) |
| `memory/2026-05-30_city_round1_report.md` | 城市盘点Round1报告(30城+396连接) |
| `memory/2026-05-30_honest_audit.md` | 知识消化闭环城市维度诚实盘点 |
| `memory/2026-05-30_full_honest_audit.md` | 知识消化闭环全局诚实盘点 |
| `memory/2026-05-30_avatar_simulation_plan.md` | 客户替身模拟闭环方案设计 |
| `memory/2026-05-30_avatar_simulation_report.md` | 客户替身模拟闭环最终报告 |
| `memory/2026-05-30_round3_paradigm_shift.md` | Round3 范式转换完整报告(五层流模型) |
| `memory/_data/simulation_round1_results.json` | Round1模拟评分原始数据 |
| `memory/_data/simulation_round2_results.json` | Round2模拟评分(140条·累计) |
| `site/dashboard-v3.html` | 驾驶舱12标签(含🏙️城市市场) |