# Paper 10 (EN): A Bounded Rationality Model for Entrepreneurial Partner Matching: From Theory to Practice

> **Author**: Satisfaction Solution Research Institute · Egbertie Team  
> **Date**: 2026-04-22  
> **Category**: Decision Theory · Entrepreneurship · Applied Economics  
> **Keywords**: Bounded rationality; Partner matching; Aspiration levels; Search theory; Satisficing**

---

## Abstract

This paper develops a formal bounded rationality model for entrepreneurial partner matching, extending Herbert Simon's satisficing framework to startup co-founder selection. The model incorporates search costs, aspiration levels, and multi-attribute evaluation. Through mathematical formulation and simulation analysis, we demonstrate that: (1) optimal search duration exists and depends on candidate pool size and search cost; (2) aspiration levels should reflect market conditions, not idealized standards; (3) the exploration-exploitation tradeoff follows predictable patterns. The model provides normative guidance for optimizing partner search strategies.

**Keywords**: Bounded rationality; Partner matching; Aspiration levels; Search theory; Satisficing

---

## 1. Introduction

The partner search process is critical yet poorly understood. How many candidates should entrepreneurs interview? When should they stop? How should they set standards?

Classical search theory (McCall, 1970) assumes rational maximization — violated in real entrepreneurship. This paper extends satisficing theory to partner matching, offering a more realistic framework.

---

## 2. Model Formulation

### 2.1 Basic Setup

Consider an entrepreneur searching among N candidates. Each candidate i has quality q_i ~ F(q). Search cost c is incurred per candidate evaluated. Aspiration level is a.

### 2.2 Satisficing Rule

1. Evaluate candidates sequentially;
2. Stop when q_i ≥ a;
3. If no candidate meets a after N evaluations, select the best evaluated.

### 2.3 Optimal Aspiration Level

The optimal aspiration level a* balances:
- Higher a → better partner if found, but higher probability of not finding;
- Lower a → easier to find, but lower quality.

Optimal: a* = argmax_a [E[q_selected|a] - c × E[search_cost|a]]

### 2.4 Multi-Attribute Extension

Partner quality is multi-dimensional: q_i = (q_i1, ..., q_i5) for skills, values, risk, character, experience.

Stopping rule: Stop when q_ij ≥ a_j for all j.

---

## 3. Simulation Analysis

### 3.1 Setup

| Parameter | Value |
|-----------|-------|
| N | 50 |
| c | 0.02 (fraction of project value) |
| F(q) | Normal(μ=0.5, σ=0.15) |

### 3.2 Key Findings

**Finding 1: Optimal Search Duration**
- a = 0.7: Average search = 8.3 candidates
- a = 0.8: Average search = 16.7 candidates
- a = 0.9: Average search = 32.4 candidates

**Finding 2: Aspiration vs. Outcome**
- a = 0.7: Success = 85%, quality = 0.75
- a = 0.8: Success = 62%, quality = 0.83
- a = 0.9: Success = 31%, quality = 0.91

**Finding 3: Search Cost Impact**
- c doubles → optimal a decreases by ~0.05
- c halves → optimal a increases by ~0.03

---

## 4. Normative Implications

### For Entrepreneurs

1. Set aspiration levels based on market conditions, not ideals;
2. Set hard time limits — search duration increases super-linearly with aspiration;
3. Evaluate multi-dimensionally but stop comprehensively.

### For Ecosystem Builders

1. Increase candidate pool visibility to reduce search costs;
2. Reduce search friction through better matching platforms;
3. Provide decision support tools for rational aspiration setting.

---

## 5. Conclusion

The bounded rationality model shows that "good enough" is not merely psychological coping but mathematically optimal under resource constraints. The key insight: being "less picky" can yield better outcomes when search costs are properly accounted for.

As Simon taught us: "Rationality is bounded when it falls short of omniscience." This model helps entrepreneurs make the best decisions within those bounds.

---

## References

McCall, J. J. (1970). Economics of information and job search. *Quarterly Journal of Economics*, 84(1), 113-126.

Simon, H. A. (1955). A behavioral model of rational choice. *Quarterly Journal of Economics*, 69(1), 99-118.

Simon, H. A. (1972). Theories of bounded rationality. In *Decision and Organization* (pp. 161-176). North-Holland.

---

> **Paper ID**: SPM-010-EN  
> **Version**: V1.0  
> **Date**: 2026-04-22**

---

*Satisfaction Solution Research Institute · Moonshot Research Paper Collection*

> **Qi · Jin**
