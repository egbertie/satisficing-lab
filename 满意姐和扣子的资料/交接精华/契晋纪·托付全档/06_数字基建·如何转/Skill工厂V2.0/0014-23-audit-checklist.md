# Cognitive Audit Checklist — 10 Items

## Usage

Apply this checklist to every output, plan, claim, or decision being audited. 
Each item must be checked explicitly. Find at least one issue. Never output "一切正常".

---

## Item 1: 信源独立性 (Source Independence)

**Question**: Is the information source single-point?

**Red flags**:
- Only one source cited
- All sources trace back to the same origin
- No cross-validation attempted

**Example finding**:
```
[幻觉嫌疑] 声称"行业平均估值3亿"，但仅引用单一媒体报道
- 证据: 文中仅列出1个来源，且为自媒体账号
- 影响: 可能被断章取义，影响投资决策
```

---

## Item 2: 时效性 (Timeliness)

**Question**: Is the data expired?

**Red flags**:
- Data older than 12 months for fast-moving fields
- Market conditions changed since data collection
- Citing pre-pandemic norms for post-pandemic decisions

---

## Item 3: 因果混淆 (Causal Confusion)

**Question**: Correlation ≠ causation?

**Red flags**:
- "A happened after B, therefore B caused A"
- Confounding variables not controlled
- Reverse causality not considered

**Example finding**:
```
[逻辑跳跃] "使用五维决策的团队成功率更高"→"五维决策导致成功"
- 前提: 相关=因果
- 漏洞: 可能是成功团队更愿意采用系统化方法（选择性偏差）
```

---

## Item 4: 幸存者偏差 (Survivorship Bias)

**Question**: Only seeing successes?

**Red flags**:
- Case studies only include successful outcomes
- Failed cases omitted from analysis
- "All our clients are satisfied" (unsatisfied ones left)

---

## Item 5: 基底率忽视 (Base Rate Neglect)

**Question**: Ignoring base rates?

**Red flags**:
- Specific case details overwhelm statistical base rates
- "This startup looks great" ignoring 90% startup failure rate
- Conditional probability errors (P(A|B) vs P(B|A))

---

## Item 6: 锚定效应 (Anchoring Effect)

**Question**: Anchored to initial information?

**Red flags**:
- First number mentioned becomes the reference point
- Unable to adjust away from initial estimate
- Negotiation outcomes clustered near opening offer

---

## Item 7: 确认偏误 (Confirmation Bias)

**Question**: Only seeking confirming evidence?

**Red flags**:
- Evidence search stops after finding support
- Disconfirming evidence ignored or dismissed
- "I knew it" retrofitting

---

## Item 8: 语言腐败 (Language Corruption)

**Question**: Using vague words to hide problems?

**Red flags**:
- "大概", "可能", "应该", "差不多", "基本上"
- Adjectives without quantities ("很大", "很多", "非常快")
- Jargon masking lack of substance

**Example finding**:
```
[语言腐败] "Token消耗比较大"未量化
- 证据: 原文使用"比较大"而非具体数字
- 影响: 无法判断是否超出预算
整改: 改为"Token消耗37万，超出预估25万的48%"
```

---

## Item 9: 数学谬误 (Mathematical Error)

**Question**: Calculation errors? Unit confusion?

**Red flags**:
- Percentage points vs percentages confused
- Compounding errors in chained calculations
- Order-of-magnitude mistakes

---

## Item 10: 样本偏差 (Sample Bias)

**Question**: Sample unrepresentative?

**Red flags**:
- Convenience sampling (only easy-to-reach respondents)
- Self-selection bias (volunteers differ from population)
- Small sample sizes with strong conclusions

---

## Audit Scoring

| Issues Found | Audit Grade |
|-------------|-------------|
| 0 | FAILED — must find at least 1 issue |
| 1-2 | 🟢 Acceptable with minor fixes |
| 3-4 | 🟡 Requires significant revision |
| 5+ | 🔴 Major problems — freeze and rebuild |
