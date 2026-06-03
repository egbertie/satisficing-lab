---
name: research-orchestrator
description: Conduct deep research with multi-source analysis, generating professional reports. Use when user needs comprehensive research, market analysis, competitive analysis, technical investigation, or detailed reports. Supports web search, academic sources, fact verification, and PDF/Markdown output. Works like ChatGPT Deep Research or Claude Research mode.
version: 1.1.0
license: MIT-0
metadata: {"openclaw": {"emoji": "🔬", "requires": {"bins": ["curl", "python3", "node"], "env": []}}}
---

# Research Orchestrator

Transform OpenClaw into a Manus-level deep research agent with parallel sub-agents, iterative search, and professional report generation.

## Features

- 🤖 **Parallel Sub-Agents**: Use `sessions_spawn` for concurrent research
- 🔄 **Iterative Search**: Search → Analyze gaps → Search again
- 📊 **Multi-Source**: Web search + academic sources
- ✅ **Fact Verification**: Cross-validation with confidence
- 📄 **Professional Reports**: Markdown + PDF with styling
- 🌍 **Multi-Language**: Auto-detect user language

## Trigger Conditions

- "Deep research on..." / "深度研究..."
- "Comprehensive analysis of..." / "全面分析..."
- "Research report about..." / "...研究报告"
- "Market analysis" / "市场分析"
- "帮我研究一下..."

---

## Execution Workflow

When user requests deep research, follow this exact workflow:

### Step 1: Create Task Structure

```bash
TASK_ID=$(date +%Y%m%d_%H%M%S)
WORKSPACE="${OPENCLAW_WORKSPACE:-$PWD}"
TASK_DIR="$WORKSPACE/research-orchestrator/tasks/$TASK_ID"

mkdir -p "$TASK_DIR/research"
mkdir -p "$TASK_DIR/analysis"
mkdir -p "$TASK_DIR/output"

echo "📋 Task created: $TASK_ID"
echo "📁 Workspace: $TASK_DIR"
```

### Step 2: Analyze & Decompose Task

Based on user query, identify 3-5 research angles. Example for "AI芯片市场2026":

```
Research Angles:
1. Market Size & Growth - 市场规模与增长
2. Key Players - 主要厂商分析
3. Technology Trends - 技术发展趋势
4. Investment & M&A - 投资与并购
5. Policy Environment - 政策环境
```

Save plan to `$TASK_DIR/plan.md`.

### Step 3: Launch Parallel Sub-Agents

**CRITICAL**: Use `sessions_spawn` to create parallel research agents.

For each research angle, spawn a sub-agent:

```
sessions_spawn with:
- session: "research-$TASK_ID-{angle_id}"
- mode: "run"
- task: Research instructions for this angle
- streamTo: "parent" (for progress visibility)
```

**Research Agent Instructions Template**:

```
You are a research agent. Your task: {angle_name}

Search Queries:
{queries}

Instructions:
1. Use web-search skill to search each query
2. For each result, extract key facts
3. Note source URL and assess credibility
4. Save findings to: $TASK_DIR/research/{angle_id}.md

Format findings as:
## {angle_name}

### Key Findings
- Finding 1 [Source: url] (Confidence: High)
- Finding 2 [Source: url] (Confidence: Medium)

### Data Points
| Metric | Value | Source | Confidence |
|--------|-------|--------|------------|

### Sources
1. [Source Name](url) - Credibility: High
```

### Step 4: Iterative Search (Gap Analysis)

After initial research completes, analyze gaps:

```python
# Analyze what's missing
gaps = identify_gaps(task_dir)

# For each gap, spawn another search
for gap in gaps:
    sessions_spawn with additional queries
```

### Step 5: Fact Verification

Cross-verify key claims:

```
For each major finding:
1. Check if multiple sources agree
2. Assess source credibility
3. Flag conflicting information
4. Assign confidence score
```

### Step 6: Deep Analysis

Synthesize research into insights:

```
Analysis should include:
1. Key Insights - Most important findings
2. Trend Analysis - Where things are heading
3. Risk Assessment - What could go wrong
4. Opportunities - Where to focus
```

### Step 7: Generate Report

Create professional report with:

```bash
# Generate Markdown report
python3 $TASK_DIR/../scripts/report_generator.py generate $TASK_DIR {lang}

# Convert to PDF
python3 $TASK_DIR/../scripts/pdf_converter.py convert $TASK_DIR/output/report.md
```

---

## Real Execution Example

User: "帮我深度研究一下2026年AI芯片市场"

Agent should:

```
1. Create task structure
   mkdir -p tasks/20260323_100000/{research,analysis,output}

2. Decompose into angles
   - market_size, competitors, technology, investment

3. Launch 4 parallel sub-agents using sessions_spawn
   
   Agent 1 (market_size):
   "Search: 'AI chip market size 2026', '半导体市场规模预测'
    Find market size data, growth rates, forecasts
    Save to tasks/.../research/market_size.md"
   
   Agent 2 (competitors):
   "Search: 'NVIDIA AMD Intel AI chips market share'
    Analyze key players, their strategies
    Save to tasks/.../research/competitors.md"
   
   Agent 3 (technology):
   "Search: 'AI chip architecture trends 2026', 'GPU NPU发展'
    Identify technology trends
    Save to tasks/.../research/technology.md"
   
   Agent 4 (investment):
   "Search: 'AI chip investment 2026', 'AI芯片投融资'
    Track investment and M&A activity
    Save to tasks/.../research/investment.md"

4. Wait for agents to complete (stream progress)

5. Verify facts across sources

6. Generate analysis report

7. Create final report (MD + PDF)

8. Output:
   📄 report.md
   📄 report.pdf
```

---

## Progress Tracking

Show progress during execution:

```
📊 Research Progress
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Task: AI芯片市场2026
Status: Researching

Phase: Parallel Research
├─ market_size: ✅ Done (8 sources)
├─ competitors: 🔄 Running (5 sources)
├─ technology: ⏳ Pending
└─ investment: ⏳ Pending

Total Sources: 13
Elapsed: 3m 45s
```

---

## Multi-Language Support

Output language matches user input:

- User writes in Chinese → Output Chinese report
- User writes in English → Output English report
- User specifies "用英文输出" → Output in specified language

---

## Key Differences from Basic Skills

| Basic Skill | Research Orchestrator |
|-------------|----------------------|
| Single execution | Parallel sub-agents |
| One search | Iterative multi-search |
| Simple output | Professional reports |
| No verification | Fact cross-checking |
| Static results | Dynamic gap analysis |

---

## Dependencies

- python3 - Script execution
- curl - API calls
- node - PDF generation (md-to-pdf)
- web-search skill - Web searching

---

## Notes

- Research typically takes 5-15 minutes
- Parallel agents provide 3-4x speedup
- Reports include source citations
- Professional PDF formatting included
- Supports 50+ languages
