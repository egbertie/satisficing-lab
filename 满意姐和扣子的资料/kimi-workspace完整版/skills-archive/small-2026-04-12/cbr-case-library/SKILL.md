> 生成时间: 2026-04-03 13:17+08:00
> 版本: V1.0
> 来源: 系统生成
> 内化完成时间: 待定

# CBR Case Library Skill
# Case-Based Reasoning for Satisficing Research

> **状态**: ✅ **FIN**（4/4测试通过，可生产使用）

## Activation
Trigger: /cbr:search [case description]

## Workflow
1. Parse case features from input
2. Retrieve topK=3 similar cases from knowledge-base/raw/
3. Calculate similarity score (threshold=0.85)
4. Return: Case_ID + similarity + key insights + adaptation suggestions

## Case Database
- Total: 68 Entries
- Categories: HARDTECH-EQUITY / RUSHANG-PHILOSOPHY / PARTNER-CONFLICT
- Update: Auto-index on new Entry

## arXiv Integration (Web Scraping)
URL: https://arxiv.org/search/?query=[keywords]&searchtype=all
Method: BeautifulSoup4 + requests
No API key required
Schedule: Daily 09:00 via GitHub Actions
