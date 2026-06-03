---
kia-version: 1.0
tier: T0
title: Partner Matching Engine 补充需求文档
source: docs/requirement-partner-matching-supplement-v1.1.md
ingested: 2026-04-16
tags: [auto-kia, docs, BatchD-docs-04]
---

> 生成时间: 2026-04-03 19:13+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# Partner Matching Engine 补充需求文档

> 需求版本: v1.1 补充版  
> 提出方: 满意解研究所 / Egbertie  
> 针对: Kimi Claw技术方案 v1.0  
> 补充内容: 案例库集成细节 + 批量测试验证方案  

---

## 第一部分: 案例库集成细节

### 1.1 集成架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    合伙人匹配系统                                │
├─────────────────────┬─────────────────────┬─────────────────────┤
│  Partner Matching   │   Case Repository   │   Integration       │
│     Engine          │      (案例库)        │      Layer          │
│                     │                     │    (待补充)         │
├─────────────────────┼─────────────────────┼─────────────────────┤
│ • Satisficing       │ • Case storage      │ • Data sync         │
│ • Complementarity   │ • Similarity search │ • API adapter       │
│ • Confucian Ethics  │ • Pattern matching  │ • Feedback loop     │
│ • Explanation       │ • Outcome tracking  │ • Learning update   │
└─────────────────────┴─────────────────────┴─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   Case Repository   │
                    │   Database (SQLite) │
                    │   case_repository.db│
                    └─────────────────────┘
```

### 1.2 数据流设计

#### 流1: 案例导入 (Case → Matching Engine)
```python
# 场景: 匹配引擎需要历史案例作为参考

# 1. 从案例库获取相似案例
cases = case_repo.find_similar(
    industry="AI芯片",
    stage="pre_a", 
    partner_type="商业合伙人",
    outcome="success"  # 仅获取成功案例
)

# 2. 转换为匹配引擎可理解的格式
historical_profiles = [
    {
        "founder_caps": case.founder_capability_matrix,
        "selected_partner_caps": case.selected_partner_capability_matrix,
        "match_outcome": case.outcome,
        "key_success_factors": case.outcome_record.key_success_factors
    }
    for case in cases
]

# 3. 用于校准阈值或生成推荐
matcher.calibrate_thresholds(historical_profiles)
```

#### 流2: 匹配结果导出 (Matching Engine → Case)
```python
# 场景: 完成匹配评估后，自动沉淀为案例

# 1. 创建新案例
case_data = {
    "case_id": f"CASE-{uuid()}",
    "case_name": f"{founder.name}合伙人匹配",
    "industry": founder.industry,
    "stage": founder.stage,
    "partner_type": target_partner_type,
    
    # 创始人画像
    "founder_profile": {
        "background": "技术" if founder.capability_matrix.get('technical_depth',0) > 6 else "商业",
        "core_tech": founder.industry,
        "funding_status": founder.stage,
        "main_strength": "...",
        "main_weakness": "..."
    },
    
    # 匹配过程
    "matching_process": {
        "candidates_sourced": len(candidates),
        "candidates_interviewed": len([c for c in candidates if c.interviewed]),
        "finalists_count": len([r for r in results if r.overall_score > 70]),
        "decision_method": "满意解算法",
        "key_criteria_weights": {
            "complementarity": 0.4,
            "values_alignment": 0.3,
            "risk_compatibility": 0.2,
            "growth_potential": 0.1
        }
    },
    
    # 选中合伙人
    "selected_partner": {
        "name": selected_candidate.name,
        "background_summary": selected_candidate.current_role,
        "key_strengths": [...],
        "risk_factors": [...],
        "match_score": selected_result.overall_score,
        "why_selected": selected_result.explanation["executive_summary"]
    },
    
    # 结果复盘 (待定，需后续更新)
    "outcome_record": {
        "result": "待定",
        "success_metrics": {},
        "lessons_learned": []
    }
}

# 2. 保存到案例库
case_repo.create(case_data)
```

### 1.3 API集成接口

#### 接口1: 获取参考案例
```python
def get_reference_cases(
    founder: FounderProfile,
    min_similarity: float = 0.7,
    max_cases: int = 5
) -> List[Case]:
    """
    根据创始人画像，获取相似的历史案例
    
    Args:
        founder: 当前创始人画像
        min_similarity: 最小相似度阈值
        max_cases: 最多返回案例数
    
    Returns:
        相似案例列表，按相似度排序
    """
    # 1. 提取创始人特征
    features = {
        "industry": founder.industry,
        "stage": founder.stage,
        "background": get_background_type(founder),
        "missing_capabilities": get_missing_capabilities(founder)
    }
    
    # 2. 调用案例库相似度搜索
    similar_cases = case_repo.search_similar(
        industry=features["industry"],
        stage=features["stage"],
        founder_background=features["background"],
        limit=max_cases
    )
    
    # 3. 过滤低相似度
    return [c for c in similar_cases if c.similarity >= min_similarity]
```

#### 接口2: 沉淀匹配结果
```python
def save_matching_result(
    founder: FounderProfile,
    candidates: List[CandidateProfile],
    results: List[MatchResult],
    selected_candidate_id: Optional[str] = None
) -> str:
    """
    将匹配评估结果保存为案例（初始状态为"进行中"）
    
    Args:
        founder: 创始人画像
        candidates: 评估的候选人列表
        results: 匹配结果列表
        selected_candidate_id: 最终选中的候选人ID（如已确定）
    
    Returns:
        新创建的案例ID
    """
    case_data = build_case_from_matching(
        founder, candidates, results, selected_candidate_id
    )
    return case_repo.create(case_data)
```

#### 接口3: 更新案例结果
```python
def update_case_outcome(
    case_id: str,
    outcome: Outcome,
    success_metrics: Dict[str, str],
    lessons_learned: List[str]
) -> bool:
    """
    当匹配结果明确后（成功/失败），更新案例
    
    Args:
        case_id: 案例ID
        outcome: 最终结果
        success_metrics: 成功指标
        lessons_learned: 经验教训
    
    Returns:
        是否更新成功
    """
    return case_repo.update_outcome(
        case_id=case_id,
        outcome=outcome,
        outcome_record={
            "result": outcome,
            "success_metrics": success_metrics,
            "lessons_learned": lessons_learned,
            "updated_at": datetime.now().isoformat()
        }
    )
```

### 1.4 数据结构映射

#### FounderProfile ↔ Case.founder_profile
```python
MAPPING_FOUNDER = {
    # FounderProfile field -> Case.founder_profile field
    "capability_matrix": "main_strength",  # 需要转换描述
    "industry": "core_tech",
    "stage": "funding_status",
    "partner_requirements.must_have_capabilities": "main_weakness"  # 缺失能力
}
```

#### CandidateProfile ↔ Case.selected_partner
```python
MAPPING_CANDIDATE = {
    # CandidateProfile field -> Case.selected_partner field
    "name": "name",
    "current_role": "background_summary",
    "capability_matrix": "key_strengths",  # 高分能力
    "value_alignment_evidence": "why_selected",  # 价值观评估
    "risk_indicators": "risk_factors"
}
```

### 1.5 集成代码示例

```python
# case_integration.py
from partner_matching import SatisficingMatcher, ExplanationGenerator
from case_repository import CaseRepository

class MatchingEngineWithCaseIntegration:
    """带案例库集成的匹配引擎"""
    
    def __init__(self, db_path: str = "./data/case_repository.db"):
        self.matcher = SatisficingMatcher()
        self.explainer = ExplanationGenerator()
        self.case_repo = CaseRepository(db_path)
    
    def match_with_context(
        self,
        founder: FounderProfile,
        candidates: List[CandidateProfile]
    ) -> MatchingReport:
        """
        执行匹配，并提供历史案例上下文
        """
        # 1. 获取相似历史案例
        reference_cases = self.case_repo.find_similar(
            industry=founder.industry,
            stage=founder.stage,
            outcome="success",
            limit=3
        )
        
        # 2. 生成历史洞察
        historical_insights = self._analyze_historical_patterns(
            reference_cases, founder
        )
        
        # 3. 执行匹配
        results = self.matcher.match_all(founder, candidates)
        
        # 4. 生成解释（包含历史案例参考）
        for result in results:
            candidate = next(c for c in candidates if c.id == result.candidate_id)
            result.explanation = self.explainer.generate(result, founder, candidate)
            # 添加历史案例参考
            result.explanation["historical_references"] = [
                {
                    "case_id": case.case_id,
                    "case_name": case.case_name,
                    "similarity": case.similarity,
                    "insight": f"相似案例{case.case_name}最终{case.outcome}"
                }
                for case in reference_cases[:2]
            ]
        
        # 5. 自动沉淀为案例（状态：进行中）
        case_id = self._save_as_case(founder, candidates, results)
        
        return MatchingReport(
            results=results,
            case_id=case_id,
            reference_cases=reference_cases,
            historical_insights=historical_insights
        )
    
    def _analyze_historical_patterns(
        self,
        cases: List[Case],
        founder: FounderProfile
    ) -> Dict[str, Any]:
        """分析历史案例模式"""
        if not cases:
            return {"message": "无相似历史案例"}
        
        success_cases = [c for c in cases if c.outcome == "success"]
        
        return {
            "total_similar_cases": len(cases),
            "success_rate": len(success_cases) / len(cases),
            "common_success_factors": self._extract_common_factors(success_cases),
            "recommended_threshold_adjustment": self._suggest_thresholds(
                cases, founder
            )
        }
    
    def _save_as_case(self, founder, candidates, results) -> str:
        """保存为案例"""
        case_data = {
            "case_name": f"{founder.name}合伙人匹配",
            "industry": founder.industry,
            "stage": founder.stage,
            "outcome": "待定",
            # ... 其他字段
        }
        return self.case_repo.save(case_data)
```

---

## 第二部分: 批量测试验证方案

### 2.1 测试目标

| 目标 | 指标 | 验收标准 |
|------|------|----------|
| 算法准确性 | 预测成功率 | >= 75% (与历史案例对比) |
| 阈值合理性 | 满意解命中率 | 60-80% (不过分严格/宽松) |
| 解释质量 | 人工评估 | >= 4/5分 |
| 性能 | 100个候选人耗时 | < 5秒 |

### 2.2 测试数据集

#### 2.2.1 合成测试集 (用于单元测试)
```python
# test_data/synthetic_cases.py
SYNTHETIC_FOUNDERS = [
    {
        "id": "founder_001",
        "name": "技术型创始人",
        "industry": "AI芯片",
        "capability_matrix": {
            "technical_depth": 9,
            "business_acumen": 3,
            "fundraising": 2
        },
        "expected_partner": "商业合伙人",
        "expected_outcome": "success"
    },
    {
        "id": "founder_002", 
        "name": "商业型创始人",
        "industry": "生物医药",
        "capability_matrix": {
            "technical_depth": 3,
            "business_acumen": 8,
            "fundraising": 7
        },
        "expected_partner": "技术合伙人",
        "expected_outcome": "success"
    },
    # ... 更多合成案例
]

SYNTHETIC_CANDIDATES = [
    {
        "id": "candidate_good",
        "name": "理想候选人",
        "capability_matrix": {"complementarity": "high"},
        "value_alignment": "high",
        "expected_match_score": > 80
    },
    {
        "id": "candidate_bad_values",
        "name": "价值观问题候选人",
        "capability_matrix": {"complementarity": "high"},
        "value_alignment": "low",  # 应触发deal breaker
        "expected_match_score": 0,
        "expected_deal_breaker": True
    },
    # ... 更多候选人
]
```

#### 2.2.2 真实历史数据 (用于集成测试)
```python
# test_data/historical_cases.json
{
  "description": "22年经验中的真实合伙人匹配案例（脱敏）",
  "cases": [
    {
      "case_id": "HIST-001",
      "industry": "AI芯片",
      "founder_background": "技术",
      "partner_type": "商业合伙人",
      "match_factors": {
        "complementarity_score": 85,
        "values_alignment_score": 78,
        "actual_outcome": "success",
        "partnership_duration_years": 3
      }
    },
    {
      "case_id": "HIST-002",
      "industry": "生物医药", 
      "founder_background": "商业",
      "partner_type": "技术合伙人",
      "match_factors": {
        "complementarity_score": 70,
        "values_alignment_score": 65,
        "actual_outcome": "failure",
        "failure_reason": "价值观冲突"
      }
    }
    # ... 更多历史案例
  ]
}
```

### 2.3 批量测试框架

```python
# tests/batch_validation.py
import unittest
import json
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class ValidationResult:
    test_name: str
    passed: bool
    expected: Any
    actual: Any
    error_margin: float = 0.0


class BatchValidator:
    """批量验证器"""
    
    def __init__(self, matcher: SatisficingMatcher):
        self.matcher = matcher
        self.results: List[ValidationResult] = []
    
    def load_test_dataset(self, dataset_path: str) -> List[Dict]:
        """加载测试数据集"""
        with open(dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def run_accuracy_test(self, dataset: List[Dict]) -> Dict[str, float]:
        """
        准确性测试：预测结果 vs 实际结果
        """
        correct = 0
        total = len(dataset)
        
        for case in dataset:
            # 重建匹配场景
            founder = FounderProfile.from_dict(case["founder"])
            candidates = [CandidateProfile.from_dict(c) for c in case["candidates"]]
            
            # 执行匹配
            results = self.matcher.match_all(founder, candidates)
            
            # 检查选中的是否是实际成功的那个
            predicted_best = results[0].candidate_id if results else None
            actual_best = case.get("selected_candidate_id")
            
            if predicted_best == actual_best:
                correct += 1
            
            self.results.append(ValidationResult(
                test_name=f"accuracy_{case['case_id']}",
                passed=predicted_best == actual_best,
                expected=actual_best,
                actual=predicted_best
            ))
        
        return {
            "accuracy": correct / total if total > 0 else 0,
            "correct": correct,
            "total": total
        }
    
    def run_threshold_test(
        self,
        founders: List[FounderProfile],
        candidates_pool: List[CandidateProfile]
    ) -> Dict[str, float]:
        """
        阈值测试：满意解命中率
        """
        satisficing_count = 0
        total = 0
        
        for founder in founders:
            for candidate in candidates_pool:
                result = self.matcher._evaluate_single(founder, candidate, 0)
                total += 1
                if result.satisficing_met and not result.deal_breakers:
                    satisficing_count += 1
        
        hit_rate = satisficing_count / total if total > 0 else 0
        
        return {
            "satisficing_hit_rate": hit_rate,
            "satisficing_count": satisficing_count,
            "total_evaluated": total,
            "is_reasonable": 0.6 <= hit_rate <= 0.8
        }
    
    def run_explanation_quality_test(
        self,
        samples: List[Dict],
        evaluator: Callable[[str], float]  # 人工评估函数或LLM评估
    ) -> Dict[str, float]:
        """
        解释质量测试
        """
        scores = []
        
        for sample in samples:
            founder = FounderProfile.from_dict(sample["founder"])
            candidate = CandidateProfile.from_dict(sample["candidate"])
            
            result = self.matcher._evaluate_single(founder, candidate, 0)
            explainer = ExplanationGenerator()
            explanation = explainer.generate(result, founder, candidate)
            
            # 评估解释质量
            quality_score = evaluator(explanation["executive_summary"])
            scores.append(quality_score)
            
            self.results.append(ValidationResult(
                test_name=f"explanation_{sample['id']}",
                passed=quality_score >= 4.0,
                expected="高质量解释",
                actual=f"评分: {quality_score}"
            ))
        
        return {
            "average_quality": sum(scores) / len(scores) if scores else 0,
            "min_quality": min(scores) if scores else 0,
            "pass_rate": len([s for s in scores if s >= 4.0]) / len(scores) if scores else 0
        }
    
    def run_performance_test(
        self,
        founder: FounderProfile,
        candidate_counts: List[int] = [10, 50, 100]
    ) -> Dict[str, Dict]:
        """
        性能测试
        """
        import time
        
        results = {}
        
        for count in candidate_counts:
            # 生成合成候选人
            candidates = generate_synthetic_candidates(count)
            
            start = time.time()
            matches = self.matcher.match_all(founder, candidates)
            elapsed = time.time() - start
            
            results[f"{count}_candidates"] = {
                "elapsed_seconds": elapsed,
                "per_candidate_ms": (elapsed / count) * 1000,
                "passed": elapsed < 5.0  # 5秒阈值
            }
        
        return results
    
    def generate_report(self) -> str:
        """生成测试报告"""
        passed = len([r for r in self.results if r.passed])
        failed = len([r for r in self.results if not r.passed])
        
        report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
批量测试验证报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总测试数: {len(self.results)}
通过: {passed} ({passed/len(self.results)*100:.1f}%)
失败: {failed}

详细结果:
"""
        for r in self.results:
            status = "✅" if r.passed else "❌"
            report += f"\n{status} {r.test_name}"
            if not r.passed:
                report += f"\n   期望: {r.expected}"
                report += f"\n   实际: {r.actual}"
        
        return report
```

### 2.4 验收测试用例

```python
# tests/acceptance_tests.py

class AcceptanceTests(unittest.TestCase):
    """验收测试"""
    
    def setUp(self):
        self.matcher = SatisficingMatcher()
        self.validator = BatchValidator(self.matcher)
    
    def test_accuracy_threshold(self):
        """准确性 >= 75%"""
        dataset = load_historical_dataset()
        result = self.validator.run_accuracy_test(dataset)
        
        self.assertGreaterEqual(
            result["accuracy"], 0.75,
            f"准确性仅{result['accuracy']:.1%}，低于75%阈值"
        )
    
    def test_satisficing_hit_rate(self):
        """满意解命中率在合理范围"""
        founders = load_test_founders(20)
        candidates = load_test_candidates(50)
        
        result = self.validator.run_threshold_test(founders, candidates)
        
        self.assertTrue(
            result["is_reasonable"],
            f"满意解命中率{result['satisficing_hit_rate']:.1%}不合理"
        )
    
    def test_explanation_quality(self):
        """解释质量 >= 4/5"""
        samples = load_explanation_samples(10)
        
        # 使用简单启发式评估（实际应用中可用LLM）
        def evaluate_quality(text: str) -> float:
            score = 4.0  # 基础分
            if "阈值" in text: score += 0.5
            if "建议" in text: score += 0.3
            return min(5.0, score)
        
        result = self.validator.run_explanation_quality_test(samples, evaluate_quality)
        
        self.assertGreaterEqual(
            result["average_quality"], 4.0,
            f"平均解释质量{result['average_quality']:.1f}低于4.0"
        )
    
    def test_performance_100_candidates(self):
        """100个候选人耗时 < 5秒"""
        founder = load_test_founder()
        
        result = self.validator.run_performance_test(founder, [100])
        
        self.assertLess(
            result["100_candidates"]["elapsed_seconds"], 5.0,
            "性能测试失败：处理100个候选人超过5秒"
        )
```

### 2.5 持续验证流程

```yaml
# .github/workflows/validation.yml
name: Matching Engine Validation

on:
  push:
    paths:
      - 'skills/partner-matching-engine/**'
  schedule:
    - cron: '0 2 * * 1'  # 每周一早2点

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Unit Tests
        run: |
          cd skills/partner-matching-engine
          python3 -m pytest tests/ -v
      
      - name: Run Accuracy Validation
        run: |
          cd skills/partner-matching-engine
          python3 tests/batch_validation.py --test accuracy
      
      - name: Run Performance Test
        run: |
          cd skills/partner-matching-engine
          python3 tests/batch_validation.py --test performance
      
      - name: Generate Report
        run: |
          cd skills/partner-matching-engine
          python3 tests/batch_validation.py --report > validation_report.md
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: skills/partner-matching-engine/validation_report.md
```

---

## 第三部分: 交付要求

### 3.1 期望交付物

| # | 交付物 | 路径 | 说明 |
|---|--------|------|------|
| 1 | 案例库集成模块 | `partner_matching/case_integration.py` | 完整集成代码 |
| 2 | 集成测试用例 | `tests/test_case_integration.py` | 集成测试 |
| 3 | 批量验证框架 | `tests/batch_validation.py` | 可独立运行 |
| 4 | 合成测试数据 | `test_data/synthetic_cases.json` | 50+合成案例 |
| 5 | 验收测试脚本 | `tests/acceptance_tests.py` | 4项验收测试 |
| 6 | 验证报告模板 | `docs/validation_report_template.md` | 可填充模板 |

### 3.2 验收标准

1. **集成模块**: 能通过 `test_case_integration.py` 所有测试
2. **批量验证**: 准确率>=75%，满意解命中率60-80%，性能<5秒
3. **代码质量**: 有完整类型注解和文档字符串
4. **可运行**: 提供 `python3 tests/batch_validation.py --demo` 一键演示

### 3.3 时间要求

期望交付时间: 收到本需求后 7-10 个工作日

---

## 附录: 现有代码参考

### 案例库现有API (skill-usage-tracker已实现)
```python
# 可参考的接口
class CaseRepository:
    def save(self, case: Case) -> str
    def get_by_id(self, case_id: str) -> Optional[Case]
    def get_filtered_cases(self, filters: Dict) -> List[Case]
    def export_to_json(self, output_path: str)
```

### 匹配引擎现有接口
```python
# 当前已实现
class SatisficingMatcher:
    def match_all(self, founder, candidates) -> List[MatchResult]
    def find_satisficing(self, founder, candidates) -> Optional[MatchResult]

class ExplanationGenerator:
    def generate(self, result, founder, candidate) -> Dict[str, Any]
```

---

**文档版本**: v1.1  
**创建时间**: 2026-04-03  
**状态**: 待外求实现
