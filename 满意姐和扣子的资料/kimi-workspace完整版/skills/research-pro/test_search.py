#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ResearchPro 快速测试脚本

用法：
    python test_search.py <TAVILY_API_KEY> "<搜索查询>"
    
示例：
    python test_search.py "tvly-xxx" "SBIT 为什么火了"
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ResearchPro, ConfigManager


def main():
    if len(sys.argv) < 3:
        print("❌ 用法错误！")
        print("\n用法:")
        print("  python test_search.py <TAVILY_API_KEY> \"<搜索查询>\"")
        print("\n示例:")
        print("  python test_search.py \"tvly-abc123\" \"SBIT 为什么火了\"")
        print("\n请提供 Tavily API Key 和搜索查询词。")
        sys.exit(1)
    
    api_key = sys.argv[1]
    query = sys.argv[2]
    
    print("=" * 70)
    print("🔬 ResearchPro 测试运行")
    print("=" * 70)
    print(f"\n📝 搜索查询：{query}")
    print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else f"🔑 API Key: {api_key}")
    print()
    
    # 创建配置
    config_manager = ConfigManager()
    config = config_manager.load()
    config['api_keys']['tavily'] = api_key
    config_manager.save(config)
    
    # 创建 ResearchPro 实例
    rp = ResearchPro(config)
    
    # 执行搜索
    print("⏳ 正在搜索...\n")
    
    try:
        result = rp.search(query, template="commercial")
        
        # 输出结果
        print("\n" + "=" * 70)
        print("✅ 搜索完成！")
        print("=" * 70)
        
        # 显示简报摘要
        print("\n📋 【简报摘要】")
        print("-" * 70)
        print(result.get('brief_summary', '暂无摘要'))
        
        # 显示关键发现
        print("\n\n🎯 【关键发现 TOP 5】")
        print("-" * 70)
        for i, insight in enumerate(result.get('key_insights', [])[:5], 1):
            print(f"{i}. {insight}")
        
        # 显示数据来源
        print("\n\n📚 【数据来源】")
        print("-" * 70)
        for source in result.get('sources', [])[:10]:
            credibility = "⭐" * source.get('credibility_level', 3)
            print(f"[{source.get('domain', 'unknown')}] {source.get('title', '无标题')}")
            print(f"   可信度：{credibility} | 时间：{source.get('published_date', '未知')}")
        
        # 显示统计信息
        stats = result.get('stats', {})
        print("\n\n📊 【统计信息】")
        print("-" * 70)
        print(f"总结果数：{stats.get('total_results', 0)}")
        print(f"S 级信源：{stats.get('s_count', 0)}")
        print(f"A 级信源：{stats.get('a_count', 0)}")
        print(f"B 级信源：{stats.get('b_count', 0)}")
        print(f"搜索耗时：{stats.get('search_duration_ms', 0) / 1000:.2f}秒")
        
        print("\n" + "=" * 70)
        print("✅ 测试成功！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 搜索失败：{str(e)}")
        print("\n可能原因:")
        print("  1. API Key 无效或已过期")
        print("  2. 网络连接问题")
        print("  3. API 额度已用完")
        print("\n请检查 API Key 后重试。")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
