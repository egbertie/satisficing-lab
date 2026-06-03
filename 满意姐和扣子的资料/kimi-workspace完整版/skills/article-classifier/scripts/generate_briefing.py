#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简报生成脚本
根据指定时间段内的文章生成周/月/季度简报
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def load_index(index_path):
    """加载文章索引"""
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_period_dates(period_type, reference_date=None):
    """
    获取指定周期的起止日期
    
    Args:
        period_type: 'weekly', 'monthly', 'quarterly'
        reference_date: 参考日期 (datetime)，默认为今天
    
    Returns:
        tuple: (start_date, end_date)
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    if period_type == 'weekly':
        # 周一到周日
        days_since_monday = reference_date.weekday()
        start_date = reference_date - timedelta(days=days_since_monday)
        end_date = start_date + timedelta(days=6)
    elif period_type == 'monthly':
        # 当月 1 日到月末
        start_date = reference_date.replace(day=1)
        if reference_date.month == 12:
            end_date = reference_date.replace(year=reference_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = reference_date.replace(month=reference_date.month + 1, day=1) - timedelta(days=1)
    elif period_type == 'quarterly':
        # 季度
        quarter = (reference_date.month - 1) // 3
        quarter_start_month = quarter * 3 + 1
        start_date = reference_date.replace(month=quarter_start_month, day=1)
        if quarter_start_month + 3 > 12:
            end_date = reference_date.replace(year=reference_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = reference_date.replace(month=quarter_start_month + 3, day=1) - timedelta(days=1)
    else:
        raise ValueError(f"Unknown period_type: {period_type}")
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def filter_articles_by_period(articles, start_date, end_date):
    """按日期范围筛选文章"""
    filtered = []
    for article in articles:
        article_date = article.get('date', '')
        if start_date <= article_date <= end_date:
            filtered.append(article)
    return filtered

def generate_category_stats(articles):
    """生成分类统计"""
    stats = {}
    for article in articles:
        category = article.get('category', '未分类')
        stats[category] = stats.get(category, 0) + 1
    
    total = len(articles)
    lines = []
    for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total * 100) if total > 0 else 0
        lines.append(f"| {category} | {count} | {percentage:.1f}% |")
    
    return '\n'.join(lines), stats

def generate_article_summaries(articles, max_summaries=10):
    """生成文章摘要"""
    if not articles:
        return "本期无文章内容。"
    
    lines = []
    for i, article in enumerate(articles[:max_summaries], 1):
        title = article.get('title', '无标题')
        summary = article.get('summary', article.get('content', '')[:100])
        category = article.get('category', '')
        lines.append(f"### {i}. {title}")
        lines.append(f"**分类**: {category}")
        lines.append(f"**摘要**: {summary}...")
        lines.append("")
    
    return '\n'.join(lines)

def generate_trend_analysis(articles, stats):
    """生成趋势分析"""
    if not articles:
        return "本期数据不足，无法分析趋势。"
    
    # 找出最热门的分类
    if stats:
        top_category = max(stats.items(), key=lambda x: x[1])
        hot_topics = f"本期最热门的分类是 **{top_category[0]}**，共 {top_category[1]} 篇文章。"
    else:
        hot_topics = "本期文章数量较少，暂无明显热点。"
    
    return {
        'hot_topics': hot_topics,
        'emerging_trends': "需要根据文章内容进行深度分析...",
        'notable_signals': "建议关注本期高频出现的关键词和主题..."
    }

def generate_advice(articles, stats):
    """生成针对性建议"""
    advice = {
        'career': "基于本期内容，建议关注以下发展方向...",
        'investment': "从投资角度，以下领域值得关注...",
        'personal_growth': "个人提升方面，建议重点学习..."
    }
    
    # 根据分类统计给出建议
    if '技术前沿' in stats:
        advice['career'] += " 技术前沿内容较多，建议持续关注 AI 和大模型相关技能。"
        advice['investment'] += " 科技领域热度高，可关注相关投资机会。"
    
    if '商业财经' in stats:
        advice['investment'] += " 商业财经内容丰富，建议结合宏观经济形势进行投资判断。"
    
    if '职场成长' in stats:
        advice['personal_growth'] += " 职场成长类文章较多，建议实践其中的方法和技巧。"
    
    return advice

def generate_briefing(template_path, output_path, index_path, period_type='weekly', reference_date=None):
    """
    生成简报
    
    Args:
        template_path: 模板文件路径
        output_path: 输出文件路径
        index_path: 索引文件路径
        period_type: 'weekly', 'monthly', 'quarterly'
        reference_date: 参考日期
    """
    # 加载模板
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 加载索引
    index_data = load_index(index_path)
    articles = index_data.get('articles', [])
    
    # 获取日期范围
    start_date, end_date = get_period_dates(period_type, reference_date)
    
    # 筛选文章
    filtered_articles = filter_articles_by_period(articles, start_date, end_date)
    
    # 生成统计
    category_stats_text, stats = generate_category_stats(filtered_articles)
    
    # 生成摘要
    article_summaries = generate_article_summaries(filtered_articles)
    
    # 生成趋势分析
    trends = generate_trend_analysis(filtered_articles, stats)
    
    # 生成建议
    advice = generate_advice(filtered_articles, stats)
    
    # 生成精选文章
    top_articles = "\n".join([f"{i+1}. {a.get('title', '无标题')} - {a.get('category', '')}" 
                              for i, a in enumerate(filtered_articles[:5])])
    
    # 替换模板变量
    briefing = template
    briefing = briefing.replace('{{period_type}}', {'weekly': '周报', 'monthly': '月报', 'quarterly': '季报'}[period_type])
    briefing = briefing.replace('{{generate_date}}', datetime.now().strftime('%Y-%m-%d %H:%M'))
    briefing = briefing.replace('{{start_date}}', start_date)
    briefing = briefing.replace('{{end_date}}', end_date)
    briefing = briefing.replace('{{category_stats}}', category_stats_text if category_stats_text else '| 无数据 | 0 | 0% |')
    briefing = briefing.replace('{{article_summaries}}', article_summaries)
    briefing = briefing.replace('{{hot_topics}}', trends['hot_topics'])
    briefing = briefing.replace('{{emerging_trends}}', trends['emerging_trends'])
    briefing = briefing.replace('{{notable_signals}}', trends['notable_signals'])
    briefing = briefing.replace('{{economic_impact}}', '需要根据具体内容分析...')
    briefing = briefing.replace('{{lifestyle_impact}}', '需要根据具体内容分析...')
    briefing = briefing.replace('{{industry_impact}}', '需要根据具体内容分析...')
    briefing = briefing.replace('{{career_advice}}', advice['career'])
    briefing = briefing.replace('{{investment_advice}}', advice['investment'])
    briefing = briefing.replace('{{personal_growth_advice}}', advice['personal_growth'])
    briefing = briefing.replace('{{top_articles}}', top_articles if top_articles else '本期无精选文章')
    briefing = briefing.replace('{{notes}}', '简报由 article-classifier 技能自动生成')
    briefing = briefing.replace('{{total_count}}', str(len(filtered_articles)))
    
    # 保存简报
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(briefing)
    
    return output_path

def main():
    """主函数 - 用于测试"""
    print("简报生成脚本已就绪")
    print("此脚本由 article-classifier 技能调用")

if __name__ == '__main__':
    main()
