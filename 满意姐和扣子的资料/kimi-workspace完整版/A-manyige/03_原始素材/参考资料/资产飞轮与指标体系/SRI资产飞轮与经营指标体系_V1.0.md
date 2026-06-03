# 满意解研究所资产飞轮与经营指标体系 V1.0

> **来源**：两张系统性关键图片的内化与血液化
> - `sri_asset_flywheel_production_layer.png`（生产层：资产飞轮）
> - `sri_management_indicators_operating_layer.png`（指标层：经营语言）
> **代码资产**：`sri_asset_flywheel.py`
> **落盘时间**：2026-04-09

---

## 一、核心理念

### 1.1 生产层：Prompt / Skill / Memory / Workflow / Case Library 都是企业资产

不要只沉淀对话，要沉淀**可复用的管理资产**。

在 `EnterpriseAssetFlywheel` 中，我们将以下五类生产资料视为核心资产持续经营：

| 资产类型 | 示例 | 沉淀方式 |
|----------|------|----------|
| **Prompt** | SKU-A诊断开场白、风险结果解释Prompt | 版本化保存，按角色分类 |
| **Skill** | `hardtech_partner_conflict_window`、风险扫描器 | 代码模块直接注册为技能资产 |
| **Memory** | 一堂128案例库、`yitang_methodology_kit` | 知识库更新日志与摘要 |
| **Workflow** | SKU-A轻咨询工作流 | 流程节点与执行耗时记录 |
| **Case Library** | 硬科技合伙人冲突真实案例集 | 匿名化存储，版本迭代 |

这些资产共同构成 **SRI Agent OS** —— 不是依赖单一模型，而是经营自己的操作系统。

### 1.2 经营层：最终回到管理层关心的五类指标

只有进入经营语言，AI Agent 才能从创新项目变成组织能力。

| 指标 | 映射来源 | 计算公式 | 健康目标 |
|------|----------|----------|----------|
| **时间 (Time)** | Workflow 效率 | 最近评估平均耗时（分钟） | ≤ 15 分钟 |
| **质量 (Quality)** | Case 质量 / 诊断准确性 | 最近评估平均得分（0-100） | ≥ 80% |
| **风险 (Risk)** | 执行过程异常 | 高风险/极高风险评估事件数 | 0 件 |
| **成本 (Cost)** | 投入产出比 | 按 SKU 模型加权平均单位成本 | SKU-A: ¥500 |
| **复用率 (Reuse)** | Prompt / Skill / Memory 复用 | 已使用资产数 / 总活跃资产数 ×100% | ≥ 75% |

---

## 二、代码资产结构

### 2.1 `EnterpriseAssetFlywheel`（生产层）

```python
fw = EnterpriseAssetFlywheel()
fw.seed_default_assets()           # 幂等：注册 SRI 核心资产
aid = fw.register_asset("prompt", "新Prompt", "1.0", "诊断顾问", "用途摘要")
fw.record_usage(aid)               # 记录该资产被复用一次
fw.export_dashboard()              # 导出资产看板
```

### 2.2 `ManagementIndicators`（经营层）

```python
mi = ManagementIndicators()
mi.capture_snapshot(note="每日晨间快照")   # 采集五类指标并存入历史
mi.dashboard()                               # 读取最新快照（或实时计算）
mi.markdown_report()                         # 输出 Markdown 看板
```

### 2.3 与现有系统的关系

```
sku_a_assessment_orchestrator.py
         ↓ 产生评估结果
partner_matching_db.py (assessment_results)
         ↓ ManagementIndicators 读取
dashboard / markdown_report
         ↓ API 暴露
partner_matching_api.py
    ├── POST /v1/assessments/sku-a
    ├── GET  /v1/assets/status
    └── GET  /v1/metrics/dashboard
```

---

## 三、API 使用示例

### 3.1 获取资产状态

```bash
curl -H "X-API-Key: dev-sri-key-2026" \
  http://localhost:8000/v1/assets/status
```

返回示例：

```json
{
  "timestamp": "2026-04-09T21:27:26",
  "assets_by_type": {
    "prompt": 2,
    "skill": 3,
    "memory": 2,
    "workflow": 1,
    "case_library": 1
  },
  "top_reused": [...],
  "reuse_summary": {
    "reuse_rate": 75.0,
    "total_active": 9,
    "used_assets": 6
  }
}
```

### 3.2 获取经营指标看板

```bash
curl -H "X-API-Key: dev-sri-key-2026" \
  http://localhost:8000/v1/metrics/dashboard
```

返回示例：

```json
{
  "timestamp": "2026-04-09T21:27:26",
  "time_minutes": 12.5,
  "quality_rate": 82.5,
  "risk_count": 0,
  "cost_yuan": 500.0,
  "reuse_rate": 75.0,
  "source": "latest_snapshot"
}
```

---

## 四、持续迭代方向

1. **时间指标**：接入 API 实际请求耗时（已打通 `duration_seconds` 字段）
2. **质量指标**：引入 NPS / 客户完课率（一堂指标体系融合）
3. **风险指标**：接入 `intelligence_collection_system` 舆情异常信号
4. **复用率**：模型/渠道/场景切换时自动记录资产复用，验证"迁移成本越低"的假设
5. **可视化**：从 Markdown 看板升级为轻量 Web Dashboard（单 HTML + Chart.js）

---

*本文件为满意解研究所"底层逻辑之一"，须深刻记住、不断强调、不断内化。*
