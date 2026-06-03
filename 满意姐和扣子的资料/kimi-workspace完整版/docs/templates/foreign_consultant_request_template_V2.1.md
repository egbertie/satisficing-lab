---
kia-version: 1.0
tier: T0
title: 外援需求清单标准模板 V2.1
source: docs/templates/foreign_consultant_request_template_V2.1.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchD-docs-04]
---

# 外援需求清单标准模板 V2.1

> **版本**: V2.1（基于 2026-04-09 Partner Matching 外援反馈迭代）  
> **编制原则**: 假设外援是完全陌生的委托方，所有背景、约束、验收标准必须一次性写透。  
> **核心咒语**: 保守做法，循序渐进；拒绝空气代码，拒绝过度工程化。

---

## 零、必读前置约束（新增）

### 0.1 基础设施现实清单 — 禁止幻觉

| 项目 | 真实状态 | 常见幻觉（必须避免） |
|------|---------|---------------------|
| **OpenClaw** | Linux 主机上的 Python agent workspace runner | 不是一个带 CLI `openclaw skills register` 的 K8s 编排平台 |
| **Skill 机制** | Python 文件放在 `/root/.openclaw/workspace`，通过 `import` 复用 | 不存在 YAML Pipeline Runtime (`apiVersion: openclaw.io/v1`) |
| **触发调度** | `daily_asset_runner.py` + Linux cron | 不存在 `openclaw pipelines deploy` |
| **本地算力** | 单台 Ubuntu 云主机，CPU/内存有限 | 不是 GPU 服务器，7B LLM 本地运行必须**先验证再写入方案** |
| **Python 命令** | 必须是 `python3`，系统**没有** `python` | 不能使用 `python` 或 `python3.11` 等假设 |
| **工作目录** | `/root/.openclaw/workspace` | 所有 import 需写 `sys.path.insert(0, '/root/.openclaw/workspace')` |

### 0.2 本阶段明确禁止的方案（红线条款）

除非用户**单独书面批准**，否则以下技术在需求中默认**禁用**：
- ❌ Docker Compose / Kubernetes（单主机直接运行优先）
- ❌ 本地大模型部署（7B+）作为默认依赖（必须先用 Kimi API / 规则引擎跑通）
- ❌ 虚构的 CLI/SDK（如 `openclaw.*`、`PipelineClient(base_url="http://openclaw-internal:8080")`）
- ❌ 从零重写已有资产（见 0.3 节可复用清单）
- ❌ 超过当前阶段所需的监控/可观测性堆栈（Prometheus/Grafana 等）

### 0.3 现有可直接复用资产清单（强制查阅）

在提出任何"新建 XX 模块"之前，外援必须先检查以下清单：

**合伙人匹配相关**
- `hardtech_partner_conflict_window.py` — 冲突窗口评估
- `hardtech_partner_risk_scanner.py` — 5条避坑铁律风险扫描
- `hardtech_partner_selection_casebook.py` — 成功案例/失败模式扫描
- `perceptual_decision_knowledge_graph.py` — 感知力决策知识图谱
- `cka_knowledge_base_builder.py` / `cka_meta_library_builder.py` — 知识库构建

**基础组件**
- `defense_base_components.py` — `BaseComponent` 基类
- `report_template_system.py` — 报告模板生成器

**调度与情报**
- `daily_asset_runner.py` — 资产激活调度器
- `kimi_search` / `agent-reach` — 已内置于 OpenClaw 平台
- `feishu_*` / `wecom_*` — 飞书/企微 API 工具集已可用

**如果方案中提出新建与上述资产功能重叠的模块，必须说明：**
1. 为什么不复用现有资产？
2. 如果不复用，增量价值是什么？

### 0.4 创始人 5 分钟检验（验收铁律）

任何代码交付必须通过以下检验：
1. `python3 -u filename.py` 在该 Linux 主机上**零退出**（`exit 0`）
2. `pytest tests/xxx.py -v` **全部通过**
3. README 能在 **5 分钟内**让一个焦虑的创始人看懂如何本地启动
4. 不存在 "clean stub"（只返回 `None` / `pass` 的函数必须标注 `TODO: IMPLEMENT`）
5. 不存在虚构 API / 虚构 runtime / 虚构模型路径

---

## 一、关于我们（从零开始介绍）

| 项目 | 内容 |
|------|------|
| **机构名称** | 满意解研究所（Satisficing Research Institute） |
| **核心业务** | 硬科技转化的合伙人匹配决策教练 |
| **目标客户** | 获得政府补贴或投资的初创期硬件企业家 |
| **核心方法论** | 左脑逻辑风控 + 右脑直觉（感知力）综合决策 |
| **当前阶段** | 商业筹划中，已完成 V1.5 官宣，正在推进 V1.6 产品化 |
| **团队构成** | 创始人 Egbertie + AI 数字替身协作团队（蓝军 Skeptor-7、满意姐） |
| **首年目标** | 建立 30 个合伙人匹配案例库，跑通决策服务闭环 |

### 决策哲学
- **满意解（Satisficing）**：不求理论最优，求实战最适。
- **保守做法，循序渐进**：先跑通最小可用，再逐步叠加。
- **诚实至上**：拒绝空气代码、拒绝半成品、拒绝虚假忙碌。

---

## 二、需求正文

### [需求编号] 需求标题

#### 2.1 业务背景
（为什么要做这件事，解决什么痛点）

#### 2.2 功能要求（必须项）
| 编号 | 功能 | 详细说明 |
|------|------|----------|
| X-1 | ... | ... |

#### 2.3 功能要求（可选项 / 加分项）
（明确标出哪些是 V1.0 之后才需要的，避免过度交付）

#### 2.4 交付物清单
- [ ] 代码文件及清单
- [ ] README.md（含环境安装、本地启动、curl/调用示例）
- [ ] `tests/test_xxx.py`（pytest 基座，happy path + 异常 path）
- [ ] 运行验证日志（`python3 -u filename.py` + `pytest -v` 文本输出）
- [ ] `docs/技术迭代条件记录.md`（如有后续升级空间）

#### 2.5 技术约束（新增强制项）
| 约束 | 要求 |
|------|------|
| 框架 | FastAPI / Python 3.12 |
| 部署 | 单主机直接运行，**本阶段不上 Docker Compose** |
| 数据库 | SQLite 优先，除非数据量>10GB才考虑 PostgreSQL |
| 测试 | `pytest` 必须通过 |
| 基类 | 新组件必须继承 `defense_base_components.BaseComponent` |
| 报告 | 报告类产出优先使用 `report_template_system.py` |

#### 2.6 时间预算
- **期望交付周期**：X 个工作日
- **预算范围**：按人天报价

---

## 三、合作方式与硬性要求

1. **先外援，再内补**：交付完整可运行的 V1.0，后续由我方维护。
2. **测试即底线**：没有 `pytest` 的代码视为未完成。
3. **诚实文化**：禁止空气代码、禁止虚构 API、禁止过度工程化。
4. **知识产权**：交付代码归满意解研究所所有，外援保留署名权和脱敏案例展示权。

---

## 四、报价与联系

| 信息项 | 说明 |
|--------|------|
| 报价 | 人天 × 单价 |
| 交付时间线 | 各里程碑（设计 Review / MVP / 测试 / 交付）预计日期 |
| 团队/个人简介 | 相关项目经验 |
| 额外资源需求 | 是否需要付费 API、第三方 SaaS 等 |

---

## 附录：模板迭代日志

| 版本 | 日期 | 迭代原因 | 关键改进 |
|------|------|----------|----------|
| V2.1 | 2026-04-09 | Partner Matching 外援方案出现虚构 runtime 与过度工程化 | 新增 0.1 基础设施现实清单、0.2 红线条款、0.3 现有资产清单、0.4 创始人5分钟检验 |
| V2.0 | 2026-04-08 | 历史交付物可用率仅 7.9% | 增加运行验证日志、数据依赖标注、stub 标注 |
| V1.0 | 2026-04-09 | 初始版本 | 基础需求框架 |
