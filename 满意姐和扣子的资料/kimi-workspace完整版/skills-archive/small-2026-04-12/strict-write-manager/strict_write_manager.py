"""
严格写入纪律管理器 - Strict Write Manager
核心模块: 解决"说一套做一套"问题
版本: 1.0.0
日期: 2026-04-02
"""

import hashlib
import os
import json
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class WriteStatus(Enum):
    """写入状态枚举"""
    SUCCESS = "success"
    FAILED = "failed"
    VERIFICATION_FAILED = "verification_failed"
    HASH_MISMATCH = "hash_mismatch"


@dataclass
class WriteResult:
    """写入结果数据结构"""
    status: WriteStatus
    file_path: str
    content_hash: str
    timestamp: float
    size_bytes: int
    message: str
    retry_count: int = 0


class StrictWriteManager:
    """
    严格写入纪律管理器
    
    核心机制:
    1. 内容哈希生成 (SHA-256)
    2. 强制磁盘同步 (fsync)
    3. 写入后验证 (hash比对)
    4. 索引原子更新
    
    新限制声明:
    - 每次写入增加50-100ms延迟（fsync开销）
    - 大文件(>100KB)需要分段处理
    - 无法保证断电场景的数据完整性（无UPS）
    """
    
    def __init__(self, index_path: str = "~/.openclaw/strict_write_index.json"):
        self.index_path = Path(index_path).expanduser()
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.write_history: list = []
        self.stats = {
            "total_writes": 0,
            "success_count": 0,
            "failure_count": 0,
            "verification_failures": 0,
            "hash_mismatches": 0
        }
    
    def _generate_hash(self, content: str) -> str:
        """生成内容SHA-256哈希（前16字符）"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def _verify_write(self, file_path: Path, expected_hash: str) -> bool:
        """验证写入内容是否与预期哈希一致"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                written_content = f.read()
            actual_hash = self._generate_hash(written_content)
            return actual_hash == expected_hash
        except Exception as e:
            return False
    
    def write_with_verification(
        self, 
        content: str, 
        file_path: str,
        max_retries: int = 3,
        segment_threshold: int = 100 * 1024  # 100KB
    ) -> WriteResult:
        """
        带验证的严格写入
        
        Args:
            content: 要写入的内容
            file_path: 目标文件路径
            max_retries: 最大重试次数
            segment_threshold: 大文件分段阈值(字节)
        
        Returns:
            WriteResult: 写入结果
        """
        file_path_obj = Path(file_path)
        file_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # 1. 生成内容哈希
        content_hash = self._generate_hash(content)
        
        # 检查是否为大文件
        content_size = len(content.encode('utf-8'))
        is_large_file = content_size > segment_threshold
        
        for attempt in range(max_retries):
            try:
                if is_large_file:
                    # 大文件分段写入
                    result = self._write_large_file(content, file_path_obj, content_hash)
                else:
                    # 常规写入
                    result = self._write_normal(content, file_path_obj, content_hash)
                
                if result.status == WriteStatus.SUCCESS:
                    # 更新统计
                    self.stats["total_writes"] += 1
                    self.stats["success_count"] += 1
                    # 记录历史
                    self.write_history.append(asdict(result))
                    return result
                
            except Exception as e:
                if attempt == max_retries - 1:
                    # 最终失败
                    self.stats["total_writes"] += 1
                    self.stats["failure_count"] += 1
                    return WriteResult(
                        status=WriteStatus.FAILED,
                        file_path=str(file_path_obj),
                        content_hash=content_hash,
                        timestamp=time.time(),
                        size_bytes=content_size,
                        message=f"写入失败(重试{max_retries}次): {str(e)}",
                        retry_count=attempt + 1
                    )
                # 短暂延迟后重试
                time.sleep(0.1 * (attempt + 1))
        
        return result
    
    def _write_normal(self, content: str, file_path: Path, content_hash: str) -> WriteResult:
        """常规文件写入（带fsync验证）"""
        # 2. 写入文件（带fsync）
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # 强制写入磁盘
        
        # 3. 验证写入
        if not self._verify_write(file_path, content_hash):
            self.stats["verification_failures"] += 1
            self.stats["hash_mismatches"] += 1
            return WriteResult(
                status=WriteStatus.HASH_MISMATCH,
                file_path=str(file_path),
                content_hash=content_hash,
                timestamp=time.time(),
                size_bytes=len(content.encode('utf-8')),
                message="哈希验证失败：写入内容与预期不符"
            )
        
        # 4. 更新索引
        self._update_index(file_path, content_hash)
        
        return WriteResult(
            status=WriteStatus.SUCCESS,
            file_path=str(file_path),
            content_hash=content_hash,
            timestamp=time.time(),
            size_bytes=len(content.encode('utf-8')),
            message="写入成功并验证通过"
        )
    
    def _write_large_file(self, content: str, file_path: Path, content_hash: str) -> WriteResult:
        """
        大文件分段写入
        
        新限制: 大文件分段处理增加复杂度
        """
        segment_size = 50 * 1024  # 50KB分段
        content_bytes = content.encode('utf-8')
        total_size = len(content_bytes)
        
        # 写入临时文件
        temp_path = file_path.with_suffix('.tmp')
        
        try:
            with open(temp_path, 'wb') as f:
                for i in range(0, total_size, segment_size):
                    segment = content_bytes[i:i+segment_size]
                    f.write(segment)
                    f.flush()
                os.fsync(f.fileno())
            
            # 验证临时文件
            with open(temp_path, 'r', encoding='utf-8') as f:
                written_content = f.read()
            
            if self._generate_hash(written_content) != content_hash:
                temp_path.unlink(missing_ok=True)
                return WriteResult(
                    status=WriteStatus.HASH_MISMATCH,
                    file_path=str(file_path),
                    content_hash=content_hash,
                    timestamp=time.time(),
                    size_bytes=total_size,
                    message="大文件分段写入验证失败"
                )
            
            # 原子替换
            temp_path.replace(file_path)
            
            # 再次验证
            if not self._verify_write(file_path, content_hash):
                return WriteResult(
                    status=WriteStatus.VERIFICATION_FAILED,
                    file_path=str(file_path),
                    content_hash=content_hash,
                    timestamp=time.time(),
                    size_bytes=total_size,
                    message="原子替换后验证失败"
                )
            
            # 更新索引
            self._update_index(file_path, content_hash)
            
            return WriteResult(
                status=WriteStatus.SUCCESS,
                file_path=str(file_path),
                content_hash=content_hash,
                timestamp=time.time(),
                size_bytes=total_size,
                message="大文件分段写入成功"
            )
            
        except Exception as e:
            temp_path.unlink(missing_ok=True)
            raise e
    
    def _update_index(self, file_path: Path, content_hash: str):
        """更新写入索引"""
        index_entry = {
            "file_path": str(file_path),
            "content_hash": content_hash,
            "timestamp": time.time(),
            "size_bytes": file_path.stat().st_size if file_path.exists() else 0
        }
        
        # 读取现有索引
        index_data = []
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
            except:
                index_data = []
        
        # 添加新条目（保留最近100条）
        index_data.append(index_entry)
        index_data = index_data[-100:]
        
        # 保存索引（也使用严格写入）
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
    
    def verify_file_integrity(self, file_path: str) -> bool:
        """
        验证文件完整性
        
        用途: 检查已写入文件是否与索引一致
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return False
        
        # 读取现有索引
        if not self.index_path.exists():
            return False
        
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        except:
            return False
        
        # 查找文件条目
        file_entry = None
        for entry in index_data:
            if entry["file_path"] == str(file_path_obj):
                file_entry = entry
                break
        
        if not file_entry:
            return False  # 索引中无此文件
        
        # 验证当前内容
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        current_hash = self._generate_hash(current_content)
        return current_hash == file_entry["content_hash"]
    
    def get_stats(self) -> Dict:
        """获取写入统计"""
        return self.stats.copy()
    
    def run_stress_test(self, test_dir: str = "/tmp/strict_write_test", num_writes: int = 100) -> Dict:
        """
        压力测试
        
        成功标准: 连续100次写入操作零失败
        """
        import random
        import string
        
        test_path = Path(test_dir)
        test_path.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        failure_count = 0
        
        print(f"开始压力测试: {num_writes}次写入...")
        
        for i in range(num_writes):
            # 生成随机内容
            content_size = random.randint(100, 10000)
            random_content = ''.join(random.choices(string.ascii_letters + string.digits, k=content_size))
            
            file_path = test_path / f"test_file_{i:03d}.txt"
            
            result = self.write_with_verification(random_content, str(file_path))
            
            if result.status == WriteStatus.SUCCESS:
                success_count += 1
            else:
                failure_count += 1
                print(f"  写入 #{i+1} 失败: {result.message}")
        
        # 验证所有文件
        integrity_count = 0
        for i in range(num_writes):
            file_path = test_path / f"test_file_{i:03d}.txt"
            if file_path.exists() and self.verify_file_integrity(str(file_path)):
                integrity_count += 1
        
        results = {
            "total_writes": num_writes,
            "success_count": success_count,
            "failure_count": failure_count,
            "integrity_count": integrity_count,
            "success_rate": success_count / num_writes * 100,
            "integrity_rate": integrity_count / num_writes * 100,
            "passed": success_count == num_writes and integrity_count == num_writes
        }
        
        return results


# 便捷函数接口
def strict_write(content: str, file_path: str) -> WriteResult:
    """便捷写入函数"""
    manager = StrictWriteManager()
    return manager.write_with_verification(content, file_path)


def verify_file(file_path: str) -> bool:
    """便捷验证函数"""
    manager = StrictWriteManager()
    return manager.verify_file_integrity(file_path)


if __name__ == "__main__":
    import sys
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="严格写入纪律管理器")
    parser.add_argument("--test", action="store_true", help="运行完整测试套件")
    parser.add_argument("--stress-test", action="store_true", help="运行压力测试")
    parser.add_argument("--verify", type=str, help="验证指定文件完整性")
    args = parser.parse_args()
    
    if args.test:
        # 完整测试套件 (≥10项)
        print("=" * 70)
        print("严格写入纪律管理器 - 完整测试套件 (v1.0.0)")
        print("=" * 70)
        
        manager = StrictWriteManager()
        test_results = []
        
        # 测试1: 正常文本写入
        print("\n[测试1/12] 正常文本写入...")
        try:
            test_content = "测试内容\n多行文本\n验证写入"
            result = manager.write_with_verification(test_content, "/tmp/test_01.txt")
            passed = result.status == WriteStatus.SUCCESS
            test_results.append(("正常文本写入", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: {result.message}")
        except Exception as e:
            test_results.append(("正常文本写入", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试2: 大文件写入(>100KB)
        print("\n[测试2/12] 大文件分段写入(150KB)...")
        try:
            large_content = "X" * (150 * 1024)
            result = manager.write_with_verification(large_content, "/tmp/test_02.txt")
            passed = result.status == WriteStatus.SUCCESS and result.size_bytes == len(large_content)
            test_results.append(("大文件分段写入", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: 大小={result.size_bytes}")
        except Exception as e:
            test_results.append(("大文件分段写入", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试3: 中文内容写入
        print("\n[测试3/12] 中文内容写入...")
        try:
            chinese_content = "中文测试内容\n包含特殊字符：【】、。！\n" + "中" * 1000
            result = manager.write_with_verification(chinese_content, "/tmp/test_03.txt")
            passed = result.status == WriteStatus.SUCCESS
            test_results.append(("中文内容写入", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
        except Exception as e:
            test_results.append(("中文内容写入", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试4: 空内容写入
        print("\n[测试4/12] 空内容写入...")
        try:
            result = manager.write_with_verification("", "/tmp/test_04.txt")
            passed = result.status == WriteStatus.SUCCESS
            test_results.append(("空内容写入", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
        except Exception as e:
            test_results.append(("空内容写入", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试5: 文件完整性验证
        print("\n[测试5/12] 文件完整性验证...")
        try:
            is_valid = manager.verify_file_integrity("/tmp/test_01.txt")
            test_results.append(("文件完整性验证", is_valid))
            print(f"  {'✅ PASS' if is_valid else '❌ FAIL'}")
        except Exception as e:
            test_results.append(("文件完整性验证", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试6: 多次覆盖写入
        print("\n[测试6/12] 多次覆盖写入...")
        try:
            all_passed = True
            for i in range(5):
                content = f"版本{i}\n内容更新"
                result = manager.write_with_verification(content, "/tmp/test_06.txt")
                if result.status != WriteStatus.SUCCESS:
                    all_passed = False
                    break
            test_results.append(("多次覆盖写入", all_passed))
            print(f"  {'✅ PASS' if all_passed else '❌ FAIL'}")
        except Exception as e:
            test_results.append(("多次覆盖写入", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试7: 深层目录写入
        print("\n[测试7/12] 深层目录写入...")
        try:
            result = manager.write_with_verification(
                "深层目录测试", 
                "/tmp/deep/nested/dir/test_07.txt"
            )
            passed = result.status == WriteStatus.SUCCESS
            test_results.append(("深层目录写入", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
        except Exception as e:
            test_results.append(("深层目录写入", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试8: JSON内容写入
        print("\n[测试8/12] JSON内容写入...")
        try:
            import json
            json_content = json.dumps({"key": "value", "nested": {"a": 1, "b": [1,2,3]}}, indent=2)
            result = manager.write_with_verification(json_content, "/tmp/test_08.json")
            passed = result.status == WriteStatus.SUCCESS
            test_results.append(("JSON内容写入", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
        except Exception as e:
            test_results.append(("JSON内容写入", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试9: 特殊字符内容
        print("\n[测试9/12] 特殊字符内容...")
        try:
            special_chars = "<>&\"'\\n\\t`~!@#$%^&*()_+-=[]{}|;':\",./<>?"
            result = manager.write_with_verification(special_chars, "/tmp/test_09.txt")
            passed = result.status == WriteStatus.SUCCESS
            test_results.append(("特殊字符内容", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}")
        except Exception as e:
            test_results.append(("特殊字符内容", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试10: 统计功能
        print("\n[测试10/12] 统计功能...")
        try:
            stats = manager.get_stats()
            passed = "total_writes" in stats and "success_count" in stats
            test_results.append(("统计功能", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: 总写入={stats['total_writes']}")
        except Exception as e:
            test_results.append(("统计功能", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试11: 哈希生成一致性
        print("\n[测试11/12] 哈希生成一致性...")
        try:
            content = "一致性测试内容"
            hash1 = manager._generate_hash(content)
            hash2 = manager._generate_hash(content)
            passed = hash1 == hash2 and len(hash1) == 16
            test_results.append(("哈希生成一致性", passed))
            print(f"  {'✅ PASS' if passed else '❌ FAIL'}: hash={hash1}")
        except Exception as e:
            test_results.append(("哈希生成一致性", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试12: 索引更新
        print("\n[测试12/12] 索引更新...")
        try:
            index_exists = manager.index_path.exists()
            test_results.append(("索引更新", index_exists))
            print(f"  {'✅ PASS' if index_exists else '❌ FAIL'}: 索引文件={manager.index_path}")
        except Exception as e:
            test_results.append(("索引更新", False))
            print(f"  ❌ FAIL: {e}")
        
        # 测试总结
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
            sys.exit(0)
        else:
            print("\n❌ 存在失败的测试:")
            for name, passed in test_results:
                if not passed:
                    print(f"  - {name}")
            sys.exit(1)
    
    elif args.stress_test:
        # 压力测试
        print("=" * 70)
        print("严格写入纪律管理器 - 压力测试")
        print("=" * 70)
        
        manager = StrictWriteManager()
        results = manager.run_stress_test(num_writes=100)
        
        print(f"\n总写入: {results['total_writes']}")
        print(f"成功: {results['success_count']}")
        print(f"失败: {results['failure_count']}")
        print(f"成功率: {results['success_rate']:.1f}%")
        print(f"完整性率: {results['integrity_rate']:.1f}%")
        
        if results['passed']:
            print("\n✅ 压力测试通过!")
            sys.exit(0)
        else:
            print("\n❌ 压力测试失败!")
            sys.exit(1)
    
    elif args.verify:
        # 验证指定文件
        manager = StrictWriteManager()
        is_valid = manager.verify_file_integrity(args.verify)
        print(f"文件 '{args.verify}' 完整性验证: {'通过' if is_valid else '失败'}")
        sys.exit(0 if is_valid else 1)
    
    else:
        # 默认运行快速测试
        print("=" * 60)
        print("严格写入纪律管理器 - 快速测试")
        print("=" * 60)
        print("\n使用 --test 运行完整测试套件")
        print("使用 --stress-test 运行压力测试(100次)")
        print("使用 --verify <文件路径> 验证文件完整性")