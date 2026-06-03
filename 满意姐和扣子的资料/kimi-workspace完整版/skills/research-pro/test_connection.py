#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 连接测试脚本

用于验证 API Key 配置是否正确，网络连通性是否良好
"""

import sys
import time
from pathlib import Path

# 添加主程序路径
sys.path.insert(0, str(Path(__file__).parent))

from main import ConfigManager, TavilySearch, SourceFilter


def test_tavily_connection(config: dict):
    """测试 Tavily API 连接"""
    print("\n" + "=" * 60)
    print("【测试 1】Tavily API 连接")
    print("=" * 60)
    
    if not config.get("api_keys", {}).get("tavily"):
        print("❌ 未配置 Tavily API Key")
        print("   运行以下命令完成配置:")
        print("   python main.py --setup\n")
        return False
    
    try:
        engine = TavilySearch(config)
        
        # 执行测试查询
        print("✓ API Key 已配置")
        print("🔍 执行测试查询：'AI technology trends 2026'...")
        
        start_time = time.time()
        results = engine.search("AI technology trends 2026", num_results=3)
        elapsed = time.time() - start_time
        
        if results:
            print(f"✅ 连接成功！耗时：{elapsed:.2f}秒")
            print(f"✓ 返回结果数：{len(results)} 条")
            
            # 显示第一条结果示例
            first = results[0]
            level, advice = SourceFilter.classify(first["url"])
            print(f"\n示例结果:")
            print(f"  标题：{first['title']}")
            print(f"  URL: {first['url'][:60]}...")
            print(f"  信源等级：{level}级 ({advice})")
            print(f"  摘要：{first['content'][:100]}...\n")
            
            return True
        else:
            print("⚠️  API 调用成功但未返回结果")
            print("   可能原因：查询词过于宽泛或网络问题\n")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")
        
        # 错误诊断
        error_msg = str(e).lower()
        if "authentication" in error_msg or "invalid api key" in error_msg:
            print("\n💡 建议:")
            print("   - API Key 可能不正确")
            print("   - 检查是否包含多余空格")
            print("   - 重新运行：python main.py --setup\n")
        elif "quota" in error_msg or "exceeded" in error_msg:
            print("\n💡 建议:")
            print("   - 本月免费额度已用完")
            print("   - 访问 https://app.tavily.com 查看用量")
            print("   - 考虑升级到付费方案\n")
        elif "timeout" in error_msg or "connection" in error_msg:
            print("\n💡 建议:")
            print("   - 网络连接超时")
            print("   - 检查代理设置或防火墙")
            print("   - 稍后重试\n")
        else:
            print("\n💡 建议:")
            print("   - 查看详细错误信息")
            print("   - 查阅文档：https://docs.researchpro.ai\n")
        
        return False


def test_config_file():
    """测试配置文件格式"""
    print("\n" + "=" * 60)
    print("【测试 2】配置文件检查")
    print("=" * 60)
    
    config_manager = ConfigManager()
    
    try:
        config = config_manager.load()
        print(f"✓ 配置文件位置：{config_manager.config_file}")
        print("✓ 配置文件格式正确")
        
        # 检查配置完整性
        has_tavily = config_manager.has_api_key("tavily")
        has_tencent = config_manager.has_api_key("tencent")
        
        print(f"\nAPI Key 配置状态:")
        print(f"  • Tavily: {'✅ 已配置' if has_tavily else '❌ 未配置'}")
        print(f"  • 腾讯云：{'✅ 已配置' if has_tencent else '❌ 未配置 (可选)'}")
        
        # 检查偏好设置
        prefs = config.get("preferences", {})
        print(f"\n偏好设置:")
        print(f"  • 默认模板：{prefs.get('default_template', 'commercial')}")
        print(f"  • 缓存功能：{'开启' if prefs.get('enable_cache') else '关闭'}")
        print(f"  • 缓存天数：{prefs.get('cache_days', 7)} 天")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置文件读取失败：{str(e)}")
        print("\n💡 建议:")
        print("   删除损坏的配置文件并重新生成:")
        print(f"   rm {config_manager.config_file}")
        print("   python main.py --setup\n")
        return False


def test_network_latency():
    """测试网络延迟"""
    print("\n" + "=" * 60)
    print("【测试 3】网络延迟检测")
    print("=" * 60)
    
    import requests
    
    targets = [
        ("Tavily API", "https://api.tavily.com"),
        ("Tavily 官网", "https://tavily.com"),
        ("腾讯云 API", "https://api.tencentcloudapi.com"),
    ]
    
    for name, url in targets:
        try:
            start = time.time()
            response = requests.head(url, timeout=5)
            elapsed = (time.time() - start) * 1000  # 转换为毫秒
            
            status = "✅" if response.status_code < 400 else "⚠️"
            print(f"{status} {name}: {elapsed:.0f}ms (HTTP {response.status_code})")
            
        except requests.exceptions.Timeout:
            print(f"❌ {name}: 超时 (>5000ms)")
        except Exception as e:
            print(f"❌ {name}: 连接失败 - {str(e)}")
    
    print()


def show_summary(tavily_ok: bool, config_ok: bool):
    """显示测试总结"""
    print("=" * 60)
    print("【测试总结】")
    print("=" * 60)
    
    if tavily_ok and config_ok:
        print("✅ 所有测试通过！ResearchPro 已就绪\n")
        print("开始使用:")
        print("  python main.py --query '你的调研主题' --template commercial\n")
    elif tavily_ok and not config_ok:
        print("⚠️  部分测试通过\n")
        print("建议:")
        print("  1. 检查配置文件权限")
        print("  2. 确认偏好设置合理\n")
    elif not tavily_ok:
        print("❌ Tavily API 测试失败\n")
        print("下一步:")
        print("  1. 根据上方错误提示排查")
        print("  2. 重新配置 API Key: python main.py --setup")
        print("  3. 查阅完整指南：API_KEY_GUIDE.md\n")
    
    print("=" * 60)


def main():
    """主函数"""
    print("\n🔧 ResearchPro 连接测试工具 v1.0\n")
    
    # 测试 1: 配置文件
    config_ok = test_config_file()
    
    # 加载配置
    config_manager = ConfigManager()
    config = config_manager.load()
    
    # 测试 2: Tavily 连接
    tavily_ok = test_tavily_connection(config)
    
    # 测试 3: 网络延迟
    test_network_latency()
    
    # 总结
    show_summary(tavily_ok, config_ok)


if __name__ == "__main__":
    main()
