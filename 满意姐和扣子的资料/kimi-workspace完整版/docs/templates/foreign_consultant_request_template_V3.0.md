---
kia-version: 1.0
tier: T0
title: 外援需求模板 V3.0（历史教训硬化版）
source: docs/templates/foreign_consultant_request_template_V3.0.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchD-docs-04]
---

# 外援需求模板 V3.0（历史教训硬化版）

> **版本**: V3.0 — 从 V2.1 跃迁至"历史教训硬化版"  
> **生效时间**: 2026-04-09  
> **编制**: 蓝军 Skeptor-7 + 满意姐  
> **核心原则**: 每一轮历史外援的失败，都必须以混凝土的形式浇筑进模板。模板不是文档，是防线。

---

## 零、历史教训摘要（外援必读）

此前多轮外援协作暴露了以下**系统性问题**。这些问题不是偶发，而是模式。如果你不看这一节，你的交付物有极高概率被直接退回。

| 历史事件 | 问题表现 | 我方损失 |
|----------|----------|----------|
| 2026-04-05 外援内化 | P0 核心4项首次运行0%通过（4/4崩溃），AST突变引擎用错误的`pytest`调用方式制造虚假kill_rate | 6小时审计+全部退回 |
| 2026-04-06 认知增强交付物 | 22个模块评分30/100，文档声称"生产就绪"，实测`NameError`/`TypeError`/`IntegrityError`泛滥 | 8小时审计+强制退回 |
| 2026-04-09 Partner Matching方案 | 建立在虚构基础设施上（`openclaw skills register`、`PipelineClient`、`apiVersion: openclaw.io/v1`），提议Docker Compose 4服务+本地7B LLM+Prometheus，完全忽略已存在的6个可复用资产 | 方案60%不可用 |
| 共性模式 | 量大质不精：81模块抽样可用率7.9%；clean stub冒充完成；数据依赖隐匿 | Token与时间的无谓消耗 |

**所以，本模板不是建议，是契约。**

---

## 一、我方运行环境（零假设清单）

### 1.1 绝对真实的基础设施

| 项目 | 实际情况 |
|------|----------|
| **主机** | 单台 Linux VPS（Ubuntu 22.04+），无 GPU |
| **Python** | `python3`（3.12.3），系统**没有** `python` 命令 |
| **工作目录** | `/root/.openclaw/workspace` |
| **依赖注入** | `sys.path.insert(0, '/root/.openclaw/workspace')` |
| **基类** | `defense_base_components.py` 中的 `BaseComponent`（新组件必须继承） |
| **测试** | `pytest`，运行命令必须是 `python3 -m pytest` 或 `pytest` |
| **平台** | OpenClaw/KimiClaw 是**一个代理执行框架**，不是一个有云原生 CLI/SDK 的"平台" |
| **容器化** | 本阶段**禁止**默认提案 Docker Compose / Kubernetes，除非用户单独书面批准 |

### 1.2 常见幻觉负面清单（必看）

以下技术/概念在往期外援方案中**反复出现，但我方环境中根本不存在**。如果你的方案中使用了其中任何一个，必须**单独附上一页可运行证明**，包括： shell 命令、实际输出截图、运行环境验证。

- ❌ `openclaw skills register`
- ❌ `PipelineClient` 或任何 OpenClaw Python SDK
- ❌ `apiVersion: openclaw.io/v1` 或任何 OpenClaw YAML Pipeline 语法
- ❌ `docker-compose.yml` 作为默认交付物
- ❌ 本地 7B/13B LLM（如 llama.cpp / Mistral / QLoRA）作为默认依赖
- ❌ `sentence-transformers` 或任何 >500MB 的模型作为默认依赖
- ❌ Prometheus / Grafana / K8s / 微服务拆分
- ❌ 使用 `python` 而非 `python3`
- ❌ 假设存在 `~/.openclaw/config.yaml` 或其他固定配置文件路径
- ❌ `OPENCLAW_PLATFORM_URL`、`OPENCLAW_WEBHOOK_SECRET` 或任何假设 OpenClaw 是一个可 HTTP 调用的"平台服务"
- ❌ `Trigger Pipeline Engine` 作为需要监听 webhook 的独立服务（它只是一个本地 Python 触发逻辑）
- ❌ `call_skill("kimi_search")` 或任何假设 Skills 有统一 HTTP/SDK 调用接口的代码

**如果你用了以上任何一个而没有附可运行证明，我方有权在第一轮就将方案整体退回。**

---

## 二、交付方式革命：禁止"大而全"，强制"小而硬"

### 2.1 分批交付禁令

**禁止一次性交付超过 5 个模块/文件。**

往期"81模块"、"22模块"、"19模块"的大规模交付已被反复证明：**量大=质不精=全部退回。**

正确交付节奏：
```
Batch 1: ≤3 个核心模块 → 蓝军 24h 内运行审计 → 100%通过 → Batch 2
Batch 2: ≤3 个模块 → 蓝军审计 → 通过 → Batch 3
...
```

任何试图绕过此禁令、以"完整方案"为名一次性投递大量文件的，将被视为**对历史教训的漠视**，直接触发退回机制。

### 2.2 每个模块的"硬化交付包"

每个 `.py` 文件必须附带以下 4 个文件，缺一不可：

| 伴随文件 | 内容 | 缺失后果 |
|----------|------|----------|
| `test_XXX.py` | `pytest` 测试，覆盖 happy path + 至少 1 个异常 path | 视为未完成 |
| `verify_XXX.sh` | 一键验证脚本：`python3 -u XXX.py` 零退出 + `pytest test_XXX.py -v` | 无法快速复现即退回 |
| `XXX_notes.md` | 如用到了外部数据/API，必须标注 `[NEEDS_EXTERNAL_DATA]` 及获取方式 | 隐匿依赖视为欺诈 |
| `honesty_checklist.json` | 见下文第三节 | 缺失直接扣分 |

---

## 三、诚实认证机制：交付前必须自证清白

### 3.1 `honesty_checklist.json`（每个模块必填）

外援必须在每个模块的根目录提交以下 JSON 文件。蓝军将对照此表进行重点审计。**任何与实测不符的声明，将被记录为诚信问题。**

```json
{
  "module_name": "example_assessor.py",
  "author": "外援姓名/团队",
  "self_assessment": {
    "i_actually_ran_this": true,
    "last_run_exit_code": 0,
    "last_run_timestamp": "2026-04-09T20:00:00+08:00",
    "has_clean_stub": false,
    "has_Unimplemented_TODO": false,
    "uses_fictional_infrastructure": false,
    "test_coverage_percent": 85
  },
  "external_dependencies": {
    "has_data_dependency": false,
    "has_api_dependency": false,
    "has_large_model_dependency": false
  },
  "run_evidence": {
    "command_used": "python3 -u example_assessor.py",
    "pytest_command": "pytest test_example_assessor.py -v",
    "environment": "Ubuntu 22.04, Python 3.12.3"
  }
}
```

**关键字段说明**：
- `has_clean_stub`: 如果函数只返回 `None`/`pass` 却没有真实实现，必须填 `true`。
  **特别注意**：含有 "模拟实现"、"TODO: 实际应替换为真实调用"、"placeholder"、"stub" 等注释或直接 `await asyncio.sleep(0.1)` 返回假数据的代码，**一律视为 clean stub**。
- `uses_fictional_infrastructure`: 如果使用了 1.2 节负面清单中的任何一项，必须填 `true`
- `last_run_exit_code`: `python3 -u filename.py` 的真实退出码

### 3.2 交付文档诚实声明（禁止原版虚假"生产就绪声明"）

**过去常见骗术**：文档末尾写"所有代码均已通过单元测试，可直接部署于标准Python 3.9+环境。"

**该声明已被我方多次证伪，今后严禁出现。**

替代声明模板（必须完整复制，空缺视为拒收）：

```markdown
## 诚实交付声明

1. 本交付包含 **___** 个模块，分 **___** 个批次提交。
2. 我/我们实际运行过每个模块，最后一次运行日期为 **___**。
3. 以下模块含有 clean stub（只返回 None/pass）：**___**（如无请填"无"）。
4. 以下模块使用了 `[NEEDS_EXTERNAL_DATA]`：**___**（如无请填"无"）。
5. 以下模块使用了 1.2 节"常见幻觉负面清单"中的技术：**___**（如无请填"无"，如有请附可运行证明）。
6. 我/我们确认：如果实测与以上声明不符，交付物将被退回。

签名：________ 日期：________
```

---

## 四、验收即真理：蓝军审计铁律

### 4.1 我们不接受的证据

以下任何一项**单独出现**均不能作为"完成"的证据：

- ❌ 代码存在（`ls` 能看到文件）
- ❌ 语法检查通过（`python3 -m py_compile` 无报错）
- ❌ 文档中有"第一性原理"、"高维架构"、"8轮深度洞察"等宏大叙事
- ❌ 作者声称"我想这样设计的"但没有可运行代码
- ❌ 截图或 log 被截断、无法复现

### 4.2 唯一接受的证据

**可复现的运行结果。**

蓝军收到交付后 24 小时内的标准动作：
1. `python3 -u filename.py`（必须零退出，超时10秒视为失败）
2. `pytest test_filename.py -v`（必须全部通过）
3. 如有 API，`curl` 调用必须返回预期结果
4. 检查是否有 `TODO: IMPLEMENT` 或 clean stub

### 4.3 反舞弊检查点

针对往期出现的**测试逻辑舞弊**（如用错误的 pytest 调用参数伪造 kill_rate），蓝军将额外检查：

- 测试脚本中 `pytest` 的 target 是否是**测试文件**，而不是被测模块本身
- `subprocess.run` 是否错误地将 exit code != 0 等同于"测试通过"或"突变体被杀死"
- 是否有用 `sys.exit(0)` 伪造成功退出的情况

**一经发现测试舞弊，该批次所有模块整体作废，且不再接受同一团队/来源的后续交付（除非重新建立信任）。**

---

## 五、现有可复用资产强制查阅清单

我在设计新模块之前，**必须**先阅读以下文件。如果你提议新建的模块与以下已有资产功能重叠，必须在方案中书面回答：**"为什么不直接复用/扩展已有资产？"**

### 5.1 合伙人匹配已有资产

| 文件 | 功能 |
|------|------|
| `hardtech_partner_conflict_window.py` | 冲突窗口期分析 |
| `hardtech_partner_risk_scanner.py` | 股权/资源/退出/Vesting风险扫描 |
| `hardtech_partner_selection_casebook.py` | 阶段评估+成功/失败模式匹配 |
| `perceptual_decision_knowledge_graph.py` | 商业实战层核心建议提取 |
| `partner_matching_api.py` | FastAPI网关（2026-04-09新增） |
| `sku_a_assessment_orchestrator.py` | SKU-A评估编排器（2026-04-09新增） |

### 5.2 基础组件与模板

| 文件 | 功能 |
|------|------|
| `defense_base_components.py` | `BaseComponent` / `MetricsCollector` / `IndexManager` |
| `report_template_system.py` | 标准化报告生成模板 |

### 5.3 其他系统资产

| 文件 | 功能 |
|------|------|
| `daily_asset_runner.py` | 每日资产激活调度 |
| `yitang_methodology_kit.py` | 一堂方法论工具箱（128案例+指标体系） |

---

## 六、技术约束与红线条款

### 6.1 默认技术栈（违者退回）

| 层面 | 标准 |
|------|------|
| 后端框架 | FastAPI + Pydantic v2 |
| 数据库 | SQLite（默认），PostgreSQL 需单独批准 |
| 部署 | 单主机裸跑，`uvicorn` 直接启动 |
| 缓存/索引 | 本地 JSON / SQLite / 轻量规则引擎 |
| 容器化 | **本阶段禁用** Docker Compose / K8s |
| 本地大模型 | **本阶段禁用** 7B/13B LLM 作为默认依赖 |
| PDF生成 | `md-to-pdf` 或 `weasyprint`（轻量） |

### 6.2 绝对禁止的交付物

以下交付物一经发现，**不问原因，直接退回**：

1. **虚构基础设施的代码**：调用不存在的 SDK/CLI/YAML API
2. **clean stub 冒充完成**：函数体只有 `pass` / `return None` / `raise NotImplementedError`
3. **隐匿的宏大架构文档**：几十页设计文档配几行无法运行的代码
4. **超出限制的批量交付**：一次性 >5 个模块且无批次说明
5. **虚假的"生产就绪声明"**：任何声称"全部通过测试"但无可复现日志的声明
6. **未与已有可运行资产整合的独立项目结构**：如果已有 `partner_matching_api.py` 等可运行资产，却提议新建独立的 `openclaw-evaluation-system/` 目录和 20+ 个新文件来"取代"，视为对现有资产的漠视

---

## 七、沟通与迭代协议

1. **先批后量**：第一批 ≤3 个模块必须在收到需求后 2-3 天内提交，用于校准双方理解。
2. **退回即升级**：任何一次退回都会触发模板审计。如果原因是模板漏洞，模板版本号 +0.1；如果是外援未按模板执行，外援负责修复。
3. **异步为主**：我方验收以代码运行结果为准，不依赖会议纪要或口头确认。
4. **知识产权**：交付代码归满意解研究所所有，外援保留署名权和脱敏案例展示权。

---

## 八、外援回执（发送需求前请对方确认）

请外援在承接前回复以下问题。缺少回执视为未接受：

1. 你是否完整阅读了本模板 V3.0？
2. 你是否接受"分批交付禁令"（每批 ≤5 模块）？
3. 你是否接受"诚实认证机制"（每个模块附带 `honesty_checklist.json`）？
4. 你是否接受"蓝军运行审计"作为唯一验收标准？
5. 你是否已经查阅了第 5 节的"现有可复用资产清单"？

---

*本模板版本: V3.0*  
*上次升级: 2026-04-09（基于 04-05/04-06/04-09 三轮历史教训）*  
*下次审计触发条件: 任何外援交付物被退回或发现模板漏洞*
