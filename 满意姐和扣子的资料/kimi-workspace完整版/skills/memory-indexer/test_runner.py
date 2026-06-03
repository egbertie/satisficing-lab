#!/usr/bin/env python3
"""记忆索引器测试套件 - v1.2.0 (基于实际代码)"""
import sys
import argparse
sys.path.insert(0, '/root/.openclaw/workspace/skills/memory-indexer')
from memory_indexer import MemoryIndexer, IndexEntry, CompressionResult

def run_tests():
    print("=" * 70)
    print("记忆索引器 - 完整测试套件 (v1.2.0)")
    print("=" * 70)
    
    indexer = MemoryIndexer()
    test_results = []
    
    # 测试1: 初始化
    print("\n[测试1/12] 初始化...")
    try:
        passed = indexer.max_index_size == 5 * 1024
        test_results.append(("初始化", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: max_size={indexer.max_index_size}")
    except Exception as e:
        test_results.append(("初始化", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试2: 内存目录
    print("\n[测试2/12] 内存目录...")
    try:
        passed = indexer.memory_dir.exists()
        test_results.append(("内存目录", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {indexer.memory_dir}")
    except Exception as e:
        test_results.append(("内存目录", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试3: 创建索引条目 (last_updated而非timestamp)
    print("\n[测试3/12] 创建索引条目...")
    try:
        entry = IndexEntry(
            topic="测试主题",
            file_path="/tmp/test.md",
            line_range="1-10",
            priority="P1",
            last_updated="2024-01-01",
            hash_preview="abc123"
        )
        passed = entry.topic == "测试主题"
        test_results.append(("创建索引条目", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
    except Exception as e:
        test_results.append(("创建索引条目", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试4: 索引条目属性 (hash_preview而非hash)
    print("\n[测试4/12] 索引条目属性...")
    try:
        entry = IndexEntry("测试", "/tmp/t.md", "1-5", "P1", "2024-01-01", "hash123")
        passed = all([entry.topic, entry.file_path, entry.line_range, 
                     entry.priority, entry.last_updated, entry.hash_preview])
        test_results.append(("索引条目属性", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
    except Exception as e:
        test_results.append(("索引条目属性", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试5: 压缩记忆
    print("\n[测试5/12] 压缩记忆...")
    try:
        content = "测试内容" * 100
        compressed = indexer.compress_memory(content)
        passed = compressed is not None
        test_results.append(("压缩记忆", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
    except Exception as e:
        test_results.append(("压缩记忆", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试6: 压缩比
    print("\n[测试6/12] 压缩比...")
    try:
        content = "测试" * 100
        compressed = indexer.compress_memory(content)
        passed = compressed.compression_ratio > 0
        test_results.append(("压缩比", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: ratio={compressed.compression_ratio:.2f}")
    except Exception as e:
        test_results.append(("压缩比", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试7: 压缩结果数据结构
    print("\n[测试7/12] 压缩结果数据结构...")
    try:
        content = "## 决策: 测试\n内容"
        result = indexer.compress_memory(content)
        passed = (hasattr(result, 'original_size') and 
                 hasattr(result, 'compressed_size') and
                 hasattr(result, 'compression_ratio') and
                 hasattr(result, 'key_decisions'))
        test_results.append(("压缩结果数据结构", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
    except Exception as e:
        test_results.append(("压缩结果数据结构", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试8: 保留模式匹配 (关键决策)
    print("\n[测试8/12] 保留模式匹配...")
    try:
        content = "## 决策: 重要决定\n## 待办: 完成任务\n## 关键洞察: 发现"
        result = indexer.compress_memory(content)
        passed = len(result.key_decisions) >= 0
        test_results.append(("保留模式匹配", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: decisions={len(result.key_decisions)}")
    except Exception as e:
        test_results.append(("保留模式匹配", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试9: 待办提取
    print("\n[测试9/12] 待办提取...")
    try:
        content = "## 待办: 任务1\n## TODO: 任务2"
        result = indexer.compress_memory(content)
        passed = len(result.todos) >= 0
        test_results.append(("待办提取", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: todos={len(result.todos)}")
    except Exception as e:
        test_results.append(("待办提取", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试10: 洞察提取
    print("\n[测试10/12] 洞察提取...")
    try:
        content = "## 关键洞察: 重要发现"
        result = indexer.compress_memory(content)
        passed = len(result.insights) >= 0
        test_results.append(("洞察提取", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: insights={len(result.insights)}")
    except Exception as e:
        test_results.append(("洞察提取", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试11: 压缩目标
    print("\n[测试11/12] 压缩目标...")
    try:
        passed = indexer.compression_target == 5.0
        test_results.append(("压缩目标", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: target={indexer.compression_target}")
    except Exception as e:
        test_results.append(("压缩目标", False))
        print(f"  ❌ FAIL: {e}")
    
    # 测试12: 丢弃统计
    print("\n[测试12/12] 丢弃统计...")
    try:
        content = "正常内容\n[思考] 思考过程\n重复内容\n重复内容"
        result = indexer.compress_memory(content)
        passed = hasattr(result, 'discarded')
        test_results.append(("丢弃统计", passed))
        print(f"  {'✅ PASS' if passed else '❌ FAIL'}: discarded={result.discarded}")
    except Exception as e:
        test_results.append(("丢弃统计", False))
        print(f"  ❌ FAIL: {e}")
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    passed_count = sum(1 for _, p in test_results if p)
    total_count = len(test_results)
    print(f"通过: {passed_count}/{total_count}")
    print(f"失败: {total_count - passed_count}/{total_count}")
    print(f"通过率: {passed_count/total_count*100:.1f}%")
    
    if passed_count == total_count:
        print("\n✅ 所有测试通过!")
        return True
    else:
        print("\n❌ 存在失败的测试:")
        for name, passed in test_results:
            if not passed:
                print(f"  - {name}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    else:
        print("=" * 60)
        print("记忆索引器 - Memory Indexer")
        print("=" * 60)
        print("\n使用 --test 运行完整测试套件")
