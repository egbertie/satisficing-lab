#!/bin/bash
# 现有Skill信息收集能力全面评估

echo "=========================================="
echo "满意解研究所 · Skill信息收集能力评估"
echo "=========================================="
echo ""

WORKSPACE="/root/.openclaw/workspace"

echo "📊 一、现有信息收集相关Skill清单"
echo "------------------------------------------"

# 检查现有的信息收集相关Skill
echo ""
echo "【网页抓取类】"
if [ -d "$WORKSPACE/skills/web-scraper" ]; then
    echo "  ✅ web-scraper - 存在"
else
    echo "  ❌ web-scraper - 不存在"
fi

if [ -d "$WORKSPACE/skills/jina-ai" ]; then
    echo "  ✅ jina-ai - 存在"
else
    echo "  ⚠️  jina-ai - 有API配置，无专用Skill"
fi

echo ""
echo "【搜索类】"
if [ -d "$WORKSPACE/skills/brave-search" ]; then
    echo "  ✅ brave-search - 存在"
else
    echo "  ❌ brave-search - 不存在（但有工具）"
fi

if [ -d "$WORKSPACE/skills/kimi-search" ]; then
    echo "  ✅ kimi-search - 存在"
else
    echo "  ⚠️  kimi-search - 有API，无专用Skill"
fi

if [ -d "$WORKSPACE/skills/perplexity-search" ]; then
    echo "  ✅ perplexity-search - 存在"
else
    echo "  ⚠️  perplexity-search - 有API，无专用Skill"
fi

echo ""
echo "【数据处理类】"
if [ -d "$WORKSPACE/skills/data-processor" ]; then
    echo "  ✅ data-processor - 存在"
else
    echo "  ❌ data-processor - 不存在"
fi

if [ -d "$WORKSPACE/skills/knowledge-extractor" ]; then
    echo "  ✅ knowledge-extractor - 存在"
else
    echo "  ❌ knowledge-extractor - 不存在"
fi

echo ""
echo "【RSS/信息流类】"
if [ -d "$WORKSPACE/skills/rss-monitor" ]; then
    echo "  ✅ rss-monitor - 存在"
else
    echo "  ❌ rss-monitor - 不存在"
fi

if [ -d "$WORKSPACE/skills/news-aggregator" ]; then
    echo "  ✅ news-aggregator - 存在"
else
    echo "  ❌ news-aggregator - 不存在"
fi

echo ""
echo "------------------------------------------"
echo "📋 二、现有API配置检查"
echo "------------------------------------------"

check_api() {
    local name=$1
    local file=$2
    if [ -f "$file" ]; then
        echo "  ✅ $name - 已配置"
    else
        echo "  ❌ $name - 未配置"
    fi
}

check_api "Jina AI" "$WORKSPACE/config/jina_config.json"
check_api "Perplexity" "$WORKSPACE/config/perplexity_config.json"
check_api "GitHub Models" "$WORKSPACE/config/github_models.json"
check_api "Brave Search" "$WORKSPACE/.brave_api_key"
check_api "Kimi Search" "$WORKSPACE/.kimi_search_config"

echo ""
echo "------------------------------------------"
echo "🔍 三、现有工具脚本检查"
echo "------------------------------------------"

check_script() {
    local name=$1
    local file=$2
    if [ -f "$file" ]; then
        echo "  ✅ $name"
    else
        echo "  ❌ $name"
    fi
}

check_script "网页提取" "$WORKSPACE/scripts/web_extract.py"
check_script "搜索工具" "$WORKSPACE/scripts/search_tool.py"
check_script "RSS抓取" "$WORKSPACE/scripts/rss_fetcher.py"
check_script "新闻聚合" "$WORKSPACE/scripts/news_aggregator.py"
check_script "数据清洗" "$WORKSPACE/scripts/data_cleaner.py"
check_script "信息分析" "$WORKSPACE/scripts/info_analyzer.py"

echo ""
echo "------------------------------------------"
echo "📊 四、能力缺口分析"
echo "------------------------------------------"

echo ""
echo "【关键缺口】"
echo "  ❌ 统一的网页抓取Skill（虽有API但无封装）"
echo "  ❌ 智能搜索编排Skill（多源搜索整合）"
echo "  ❌ 信息去重和清洗Skill"
echo "  ❌ 知识图谱构建Skill"
echo "  ❌ 自动信息监控Skill（RSS+网页变更）"
echo "  ❌ 信息可信度评估Skill"
echo "  ❌ 多语言信息处理Skill"

echo ""
echo "【部分具备】"
echo "  ⚠️ Jina AI API - 有配置但缺乏高级封装"
echo "  ⚠️ Perplexity API - 有配置但缺乏定时搜索"
echo "  ⚠️ 夜间经验萃取 - 有框架但需完善"

echo ""
echo "【已具备】"
echo "  ✅ 基础网页抓取（Jina AI）"
echo "  ✅ 基础搜索（web_search工具）"
echo "  ✅ 简单RSS监控（部分配置）"

echo ""
echo "=========================================="
