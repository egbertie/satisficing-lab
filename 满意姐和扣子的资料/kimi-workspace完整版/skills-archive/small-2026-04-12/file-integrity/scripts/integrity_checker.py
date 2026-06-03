#!/usr/bin/env python3
"""
文件完整性检查脚本

支持检查项：
1. 文件存在性
2. 文件大小（>0字节）
3. 内容可读性（无编码错误）
4. 关键章节完整性（正则匹配标题）

用法：
    python integrity_checker.py --path /path/to/file --config config/check_rules.json
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CheckResult:
    """单个检查项的结果"""
    name: str
    passed: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    critical: bool = False


@dataclass
class IntegrityReport:
    """完整性检查报告"""
    file_path: str
    timestamp: str
    passed: bool
    results: List[CheckResult]
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "timestamp": self.timestamp,
            "passed": self.passed,
            "summary": self.summary,
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "critical": r.critical,
                    "details": r.details
                }
                for r in self.results
            ]
        }
    
    def to_text(self) -> str:
        lines = [
            "=" * 60,
            "文件完整性检查报告",
            "=" * 60,
            f"检查文件: {self.file_path}",
            f"检查时间: {self.timestamp}",
            f"总体状态: {'✅ 通过' if self.passed else '❌ 失败'}",
            "-" * 60,
            "检查详情:",
            "-" * 60
        ]
        
        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            critical = " [关键]" if result.critical else ""
            lines.append(f"\n[{status}]{critical} {result.name}")
            lines.append(f"  消息: {result.message}")
            if result.details:
                for key, value in result.details.items():
                    lines.append(f"  {key}: {value}")
        
        lines.extend([
            "-" * 60,
            "汇总:",
            f"  总计: {self.summary.get('total', 0)}",
            f"  通过: {self.summary.get('passed', 0)}",
            f"  失败: {self.summary.get('failed', 0)}",
            f"  关键失败: {self.summary.get('critical_failed', 0)}",
            "=" * 60
        ])
        
        return "\n".join(lines)


class FileIntegrityChecker:
    """文件完整性检查器"""
    
    def __init__(self, config_path: str):
        """初始化检查器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.results: List[CheckResult] = []
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def check_file(self, file_path: str) -> IntegrityReport:
        """执行完整的文件检查
        
        Args:
            file_path: 要检查的文件路径
            
        Returns:
            IntegrityReport: 检查报告
        """
        self.results = []
        checks = self.config.get("checks", {})
        
        # 1. 检查文件存在性
        if checks.get("exists", {}).get("enabled", True):
            self._check_exists(file_path, checks["exists"])
        
        # 2. 检查文件大小
        if checks.get("size", {}).get("enabled", True):
            self._check_size(file_path, checks["size"])
        
        # 3. 检查内容可读性
        if checks.get("readable", {}).get("enabled", True):
            self._check_readable(file_path, checks["readable"])
        
        # 4. 检查关键章节完整性
        if checks.get("structure", {}).get("enabled", True):
            self._check_structure(file_path, checks["structure"])
        
        # 生成报告
        return self._generate_report(file_path)
    
    def _check_exists(self, file_path: str, config: Dict[str, Any]) -> None:
        """检查文件是否存在"""
        exists = os.path.exists(file_path)
        self.results.append(CheckResult(
            name="文件存在性",
            passed=exists,
            message="文件存在" if exists else f"文件不存在: {file_path}",
            details={"path": file_path, "exists": exists},
            critical=config.get("critical", True)
        ))
    
    def _check_size(self, file_path: str, config: Dict[str, Any]) -> None:
        """检查文件大小"""
        if not os.path.exists(file_path):
            self.results.append(CheckResult(
                name="文件大小",
                passed=False,
                message="无法检查大小：文件不存在",
                critical=config.get("critical", True)
            ))
            return
        
        try:
            size = os.path.getsize(file_path)
            min_bytes = config.get("min_bytes", 1)
            passed = size >= min_bytes
            
            self.results.append(CheckResult(
                name="文件大小",
                passed=passed,
                message=f"文件大小: {size} 字节" if passed else f"文件太小: {size} 字节 (最小要求: {min_bytes})",
                details={"size": size, "min_bytes": min_bytes},
                critical=config.get("critical", True)
            ))
        except Exception as e:
            self.results.append(CheckResult(
                name="文件大小",
                passed=False,
                message=f"检查文件大小失败: {str(e)}",
                critical=config.get("critical", True)
            ))
    
    def _check_readable(self, file_path: str, config: Dict[str, Any]) -> None:
        """检查内容可读性"""
        if not os.path.exists(file_path):
            self.results.append(CheckResult(
                name="内容可读性",
                passed=False,
                message="无法检查可读性：文件不存在",
                critical=config.get("critical", True)
            ))
            return
        
        errors = []
        lines_to_check = config.get("lines", 100)
        
        # 尝试不同的编码
        encodings = ['utf-8', 'gbk', 'latin-1', 'cp1252']
        content = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= lines_to_check:
                            break
                        lines.append(line)
                    content = ''.join(lines)
                    used_encoding = encoding
                    break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                errors.append(f"{encoding}: {str(e)}")
                continue
        
        if content is None:
            self.results.append(CheckResult(
                name="内容可读性",
                passed=False,
                message=f"无法读取文件内容，尝试了以下编码: {', '.join(encodings)}",
                details={"errors": errors},
                critical=config.get("critical", True)
            ))
        else:
            # 检查是否有乱码特征（过多的替换字符）
            replacement_count = content.count('\ufffd')
            passed = replacement_count == 0
            
            self.results.append(CheckResult(
                name="内容可读性",
                passed=passed,
                message=f"成功使用 {used_encoding} 编码读取 {len(content)} 字符" if passed 
                        else f"检测到 {replacement_count} 个乱码字符",
                details={
                    "encoding": used_encoding,
                    "chars_read": len(content),
                    "replacement_chars": replacement_count,
                    "sample": content[:200] + "..." if len(content) > 200 else content
                },
                critical=config.get("critical", True)
            ))
    
    def _check_structure(self, file_path: str, config: Dict[str, Any]) -> None:
        """检查关键章节完整性"""
        if not os.path.exists(file_path):
            self.results.append(CheckResult(
                name="章节结构完整性",
                passed=False,
                message="无法检查结构：文件不存在",
                critical=config.get("critical", False)
            ))
            return
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            required_headers = config.get("required_headers", [])
            missing_headers = []
            found_headers = []
            
            for pattern in required_headers:
                if re.search(pattern, content, re.MULTILINE):
                    found_headers.append(pattern)
                else:
                    missing_headers.append(pattern)
            
            passed = len(missing_headers) == 0
            
            self.results.append(CheckResult(
                name="章节结构完整性",
                passed=passed,
                message=f"找到 {len(found_headers)}/{len(required_headers)} 个必需章节" if passed
                        else f"缺少 {len(missing_headers)} 个必需章节: {missing_headers}",
                details={
                    "found": found_headers,
                    "missing": missing_headers,
                    "total_required": len(required_headers)
                },
                critical=config.get("critical", False)
            ))
            
        except Exception as e:
            self.results.append(CheckResult(
                name="章节结构完整性",
                passed=False,
                message=f"检查结构失败: {str(e)}",
                critical=config.get("critical", False)
            ))
    
    def _generate_report(self, file_path: str) -> IntegrityReport:
        """生成检查报告"""
        total = len(self.results)
        passed_count = sum(1 for r in self.results if r.passed)
        failed_count = total - passed_count
        critical_failed = sum(1 for r in self.results if not r.passed and r.critical)
        
        # 总体通过：没有关键失败且所有检查通过（或只有非关键失败）
        overall_passed = critical_failed == 0 and passed_count == total
        
        return IntegrityReport(
            file_path=file_path,
            timestamp=datetime.now().isoformat(),
            passed=overall_passed,
            results=self.results,
            summary={
                "total": total,
                "passed": passed_count,
                "failed": failed_count,
                "critical_failed": critical_failed
            }
        )


def main():
    parser = argparse.ArgumentParser(
        description="文件完整性检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python integrity_checker.py --path document.md --config check_rules.json
  python integrity_checker.py --path document.md --config check_rules.json --output report.txt
  python integrity_checker.py --path document.md --config check_rules.json --format json
        """
    )
    
    parser.add_argument(
        "--path", "-p",
        required=True,
        help="要检查的文件路径"
    )
    
    parser.add_argument(
        "--config", "-c",
        required=True,
        help="检查规则配置文件路径"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="报告输出文件路径（默认输出到控制台）"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="报告格式（默认: text）"
    )
    
    args = parser.parse_args()
    
    # 验证配置文件存在
    if not os.path.exists(args.config):
        print(f"错误: 配置文件不存在: {args.config}", file=sys.stderr)
        sys.exit(3)
    
    # 执行检查
    try:
        checker = FileIntegrityChecker(args.config)
        report = checker.check_file(args.path)
        
        # 生成报告内容
        if args.format == "json":
            output = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
        else:
            output = report.to_text()
        
        # 输出报告
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"报告已保存到: {args.output}")
        else:
            print(output)
        
        # 返回退出码
        if report.passed:
            sys.exit(0)
        elif report.summary.get("critical_failed", 0) > 0:
            sys.exit(1)
        else:
            sys.exit(2)
            
    except json.JSONDecodeError as e:
        print(f"错误: 配置文件格式无效: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"错误: 检查过程中发生异常: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
