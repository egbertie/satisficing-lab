---
kia-version: 1.0
tier: T0
title: TASK_MASTER.md - 任务总登记
source: docs/TASK_MASTER.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchA-docs-01]
---

# TASK_MASTER.md - 任务总登记

## 2026-04-11 今日进度

| 任务 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| 后台自动化双经济整改（代码补充+机制化） | P0 | ✅ FIN | 报告已归档至 `A-manyige/对话/2026-04-11/` |
| SkillHub + productmanagerskills + pmaster 安装 | P1 | ✅ FIN | `skills/productmanagerskills/` + `skills/pmaster/` |
| getdesign.md / 一堂课程清单 研究 | P1 | ✅ FIN | 182 门课程已扫描，getdesign 为设计系统 prompt 库 |
| 4-10 尾项拆解为最小单元 | P1 | ✅ FIN | U1~U4 已登记，截止 2026-04-12/13 |
| getdesign CLI 工具编写 | P0 | ✅ FIN | `tools/getdesign-cli/getdesign.py` 已部署并测试通过 |
| 爱可可情报矿脉地图 深挖 | P1 | 🔄 待定 | 路径 A 已确认（用户转发 → process_aibot.py 即时处理），待收到文章后执行 |
| 量子认知学术快扫报告 V1.6 镶嵌 | P1 | ✅ FIN | 已实时写入 `V1.6-满意解研究所总纲底稿-V1.2` 第四章 4.2 节 |
| 一堂 xlsx 图片分析 | P1 | ✅ FIN | 3 张图片内容已解析，并转化为「五路图腾进阶地图」+「12类型冲突阶段分布图」 |
| 双标签（编号决策协议）使用整改 | P0 | ✅ FIN | 已恢复，后续正文用 ①/②/③，决策用 [DEC-xxx: A/B] |
| 内存清理主动机制闭环 | P0 | ✅ FIN | Gateway 已重启，内存从 1422MB 降至 ~788MB；机制写入 guard |
| Token 周报时间调整 | P0 | ✅ FIN | 已升级为阈值触发机制（`scripts/token_weekly_reporter.py`），取消固定准点 |
| 英文 cron 通知整改 | P1 | 🔄 待定 | 确认为 Gateway 系统层消息，需改源码或等官方更新 |
| 洞察任务门神脚本（insight_task_gatekeeper.py） | P0 | ✅ FIN | `scripts/insight_task_gatekeeper.py`，每日 09:17 系统 cron 运行 |
| 敏感词守护脚本（sensitive_word_guardian.py） | P0 | ✅ FIN | `scripts/sensitive_word_guardian.py`，每日 10:17 系统 cron 运行 |
| 学术饲料扫描器（academic_feed_scanner.py） | P1 | ✅ FIN | `scripts/academic_feed_scanner.py`，每周一 09:17 系统 cron 运行 |
| 案例获取监督员（case_acquisition_monitor.py） | P1 | ✅ FIN | `scripts/case_acquisition_monitor.py`，每周日 20:17 系统 cron 运行 |
| 外部情报流水线（external_intel_pipeline.py） | P1 | ✅ FIN | `scripts/external_intel_pipeline.py`，每周二 09:17 系统 cron 运行 |
| 日报守门员脚本（daily_report_gatekeeper.py） | P0 | ✅ FIN | `scripts/daily_report_gatekeeper.py`，扫描近 7 天日报缺失情况 |
| 代码资产审计脚本（code_asset_auditor.py） | P0 | ✅ FIN | `scripts/code_asset_auditor.py`，自动 py_compile 全仓库 Python 文件 |
| Deadline 看门狗（deadline_watchdog.py） | P0 | ✅ FIN | `scripts/deadline_watchdog.py`，自动扫描 P0-P1-P2 超期任务 |
| 文件处理 L1-L5 洞察强制检查器（file_processing_insight_enforcer.py） | P0 | ✅ FIN | `scripts/file_processing_insight_enforcer.py`，检查文件闭环后是否产出洞察 |
| 周报自动汇总脚本（weekly_status_rollup.py） | P1 | ✅ FIN | `scripts/weekly_status_rollup.py`，自动生成周报到日报文件夹 |
| WX-01 BONSAI 思想融入合伙人评估框架 | P1 | 🔄 待执行 | 在 V1.6 问卷/表格中增加「基准画像偏离度」与「可容忍代价边界 ρ」 |
| WX-02 Multiplex/HiLL 重构沟通话术 | P1 | 🔄 待执行 | 增加「多假设并行评估」与「教练点拨语库」，禁止直接给结论 |
| WX-03 COGROUTER L1–L4 认知深度可视化 | P1 | 🔄 待执行 | 在五路图腾进阶地图中标注各阶段认知深度层级 |
| WX-04 案例库「独特性感知」评分机制 | P2 | 🔄 待执行 | 新案例增加「常见度 1–5」评分，每月至少入库 1 个稀有案例 |
| WX-05 How2Everything 式 SOP 评估闭环设计 | P2 | 🔄 待执行 | 定义「关键失败」清单，设计教练自评表 |
| WX-06 RAG Scaling Laws 融入产品技术架构 | P2 | 🔄 待执行 | 白皮书明确「小型决策引擎 + 大型知识库检索」架构 |
| WX-07 深度访谈 → Critic → 轻量跟踪 分层 SKU | P2 | 🔄 待执行 | 两阶段产品 SKU 设计稿 |
| WX-08 精读 Batch B/C/D 高潜力论文 | P3 | ⏸ 队列化 | 每周 academic_feed_scanner 运行后人工 review 1–2 篇 |
| WX-09 Stochastic Attention 应用于合伙人社交网络 | P3 | ⏸ 队列化 | 等待实际客户社交网络数据 |
| WX-10 OpenClaw 科研应用 8 Skill 安装 | P3 | ⏸ 观察中 | 决策：可安装，不急；先检查 clawhub 障碍，有障碍延后 |
| WX-11 105 条微信学术快报 readgzh 批量读取 | P1 | 🔄 部分完成 | 10/105 成功，95/105 因 API 402 失败。明日领积分后继续 |
| 每日 readgzh 积分领取提醒机制 | P0 | ✅ FIN | 已写入 MEMORY.md，满意姐每日首次见面强制提醒 |
| Git 快照 | P0 | ✅ FIN | 986eb660 |

## 2026-04-12 追加任务（缓冲消息驱动）

| 任务 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| 5 个审计脚本注册系统 cron | P0 | ✅ FIN | daily_report_gatekeeper / code_asset_auditor / deadline_watchdog / file_processing_insight_enforcer / weekly_status_rollup |
| 外部 Skill 站点入库 | P1 | ✅ FIN | `memory/resource-inventory/external-skills-sites.md` 已创建，含 42plugin / gona.ai / crawhub.ai / Coze |
| Coze 技能链接可用性测试 | P1 | ✅ FIN | 3 个链接均 HTTP 200，但平台隔离无法在 OpenClaw 直接调用，标记为「仅参考」 |
| archive/broken-code-2026-04-11 观察期清理 | P0 | 🔄 待执行 | 截止 2026-05-12，到期后无需求则删除。deadline_watchdog 将自动提醒 |
| 决策/确认任务清单增加「建议选项」机制 | P0 | 🔄 待内化 | 已确认规则，需写入快速参考卡并每次执行 |
| 04-04 ~ 04-10 日报补录 | P1 | ⏸ 队列化 | 数据缺失，无法自动补录。后续通过 daily_report_gatekeeper 防止再发 |
| U1 Type02 雷达图问卷 v0.1 | P1 | ⏸ 队列化 | 蓝军负责，原截止 2026-04-13 18:00，Token 高压期延后处理 |
| U2 Type07 角色扮演脚本 v0.1 | P1 | ⏸ 队列化 | 蓝军负责，原截止 2026-04-13 18:00，Token 高压期延后处理 |
| U3 Type09 决策树框架 v0.1 | P1 | ⏸ 队列化 | 蓝军负责，原截止 2026-04-13 18:00，Token 高压期延后处理 |
| 统一系统护士 (unified_system_nurse.py) | P0 | ✅ FIN | 覆盖磁盘/内存/Token/Skills/Cron 监控+条件清理，每日 06:17 cron 运行 |
| Token 消耗节奏策略 V1.0 | P0 | ✅ FIN | S-曲线模型替代绝对阈值，time_progress 挂钩 + 波动容差 |
| 自建 Skill 战略启动（归档→合并→自建） | P1 | 🔄 待执行 | 基于 https://mp.weixin.qq.com/s/GJ41aM1e2uWzTyJFxwZKHg 升级 skill 治理体系，目标: 整合基因、剔除垃圾、自建核心 |
| Token 休眠机制断链修复（数据源+cron+pace_ratio联动） | P0 | ✅ FIN | hibernation-control.py 已切到 token-zero-tracker.json, auto-check cron 已恢复, resolve_level 已融合绝对阈值+pace_ratio 双轨模型 |
| 报告交付协议 V1.0 | P0 | ✅ FIN | 每次提交报告必须附文档路径 + 同步当日对话副本，已写入 memory/report-delivery-protocol-v1.0.md |
| 一堂方法论图片全量内化 | P0 | 🔄 阶段性完成/长期挖掘 | OCR 270/245 完成+25 后台补完中；映射骨架 V0.1、Batch-0 双经济测试、阶段性全景报告已落盘；决策确认 [A-①] P0-1~P0-6 全量血液化，任务不终结、持续补充挖掘 |
| 四文档（PDF）深度洞察与血液化 | P0 | ✅ FIN | 3 份完成（年入千万/讲师经纪/私董陪跑），1 份缺失（失败课 http_429）；总报告 + 3 份子 MD 已落盘并同步至对话文件夹 |
| 知识入库全闭环机制标准化 | P0 | ✅ FIN | `docs/knowledge-ingestion-closed-loop-v1.0.md` 已生效，含 12 步标准流程 + 6 条质量红线，经四文档实战验证 |

## 2026-04-20 追加任务（专家文件剩余task上架）

| 任务 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| 专家文件-根据学科背景调整侧重点 | P2 | 🔄 待执行 | 法学专家→强调伦理维度；工学专家→强调算法模型；随专家沟通动态调整 |
| 专家文件-方法论质疑回应准备 | P2 | 🔄 待执行 | 预设5类常见质疑及回应话术，纳入专家沟通SOP |
| 12类型案例库课堂实测后升级V1.1 | P1 | ⏸ 队列化 | 待课堂实测完成（预计2026-05月），实测后统一升级所有Type文档 |

## 2026-04-20 追加任务（半成品文件评估与清理）

| 任务 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| 01_汇报体系/日报/2026-03-15_小时协调检查报告 | P3 | ⏸ 过期归档 | 历史文件，0%完成度，已过期，建议归档至OLD-ARCHIVE |
| 01_汇报体系/闭环报告模板.md | P1 | 🔄 待完成 | 模板本身未完成，需补充完整8项检查清单内容 |
| 01_汇报体系/专项报告/Token周期交接报告 | P1 | 🔄 待完成 | 4个任务全未完成，Token周期已交接完成，需更新状态或重新规划 |
| 01_汇报体系/专项报告/Skillhub搜寻结果报告 | P2 | 🔄 待完成 | 9个未完成任务，需评估哪些仍有效、哪些已过期 |
| 01_汇报体系/专项报告/OpenClaw企业办公应用报告 | P2 | 🔄 待完成 | 7个未完成任务，需评估与当前项目关联度 |
| 01_汇报体系/专项报告/URG-001完成报告 | P1 | 🔄 接近完成 | 仅剩1个未完成，建议立即收尾 |

## 2026-04-20 追加任务（A-manyige深层整改待续）

| 任务 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| 02_知识资产/待办 移出该目录 | P1 | 🔄 待执行 | 待办不应在知识资产目录下，需迁移至机制与管理或单独待办区 |
| 03_原始素材/一堂方法论 与 03_原始素材/参考资料/一堂方法论 合并 | P1 | 🔄 待执行 | 重复目录，需合并并统一命名 |
| 03_原始素材/其他资料 和 03_原始素材/未来素材 重命名 | P2 | 🔄 待执行 | 命名不规范，需改为描述性名称 |
| 内容质量检查-半成品文档整理 | P1 | 🔄 待执行 | 识别"有机制开了头无结果"的文件，补充或归档 |
