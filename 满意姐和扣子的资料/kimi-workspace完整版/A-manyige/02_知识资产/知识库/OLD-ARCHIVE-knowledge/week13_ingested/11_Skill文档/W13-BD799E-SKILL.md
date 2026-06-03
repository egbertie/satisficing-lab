---
# 知识元数据 (5标准化)
knowledge_id: W13-BD799E
title: Seven-Standard Auditor Skill
category: 11_Skill文档
source: skills/.archive_seven-standard-auditor/SKILL.md
ingested_at: 2026-03-27 17:59:30
word_count: 962
week: 13
s1_input: true
s2_process: true
s3_output: true
s4_auto: true
s5_verify: true
s6_limit: true
s7_test: true
---

# Seven-Standard Auditor Skill

> **知识ID**: W13-BD799E  
> **分类**: 11_Skill文档  
> **来源**: `skills/.archive_seven-standard-auditor/SKILL.md`  
> **入库时间**: 2026-03-27

---

## 正文

# Seven-Standard Auditor Skill
## 7标准检验Skill - 自动检验任意文档的7标准达成率

## Purpose
自动检验任意交付物是否符合7标准（S1-S7），生成标准化合规报告。

## 7-Standard Definition

### S1 全局考虑 (Global Coverage)
- 覆盖全部工作维度（人/事/物/环境）
- 外部集成考虑
- 边界情况处理

### S2 系统考虑 (System Closure)
- 输入→处理→输出→反馈闭环
- 故障处理机制
- 边界定义清晰

### S3 迭代机制 (Iteration Mechanism)
- Plan-Do-Check-Act循环
- 反馈收集机制
- 优化触发条件

### S4 Skill化 (Skill Standardization)
- SKILL.md格式规范
- 可安装可调用
- 标准化接口

### S5 自动化 (Automation)
- 自动检验能力
- Cron监控
- 自动报告生成

### S6 认知谦逊 (Epistemic Humility)
- 标注来源
- 标注置信度
- 承认局限

### S7 对抗验证 (Devil's Advocacy)
- 反方观点
- 失效场景
- 替代方案

## Commands
- audit [file_path] - 检验指定文档的7标准达成率
- audit-all [directory] - 批量检验目录下所有文档
- report - 生成7标准合规报告
- benchmark - 生成7标准自身检验报告（元检验）

## Scoring Rules
| 标准 | 权重 | 达标阈值 |
|------|------|----------|
| S1 全局 | 15% | ≥60% |
| S2 系统 | 15% | ≥50% |
| S3 迭代 | 15% | ≥50% |
| S4 Skill化 | 15% | ≥80% |
| S5 自动化 | 15% | ≥50% |
| S6 谦逊 | 15% | ≥50% |
| S7 对抗 | 10% | ≥30% |

**综合达标线**: 70%
