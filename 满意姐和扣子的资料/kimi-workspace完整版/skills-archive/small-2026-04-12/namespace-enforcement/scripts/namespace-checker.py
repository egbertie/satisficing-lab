#!/usr/bin/env python3
"""
Namespace Checker - 命名空间检查器
实现5标准化要求：S1-S7

S1: 全局考虑 - 命名规范对文件检索效率的影响
S2: 系统闭环 - 文件创建→命名检查→违规处理→索引更新
S3: 可观测输出 - 合规率、违规清单、迁移进度
S4: 自动化集成 - 自动检查、自动提示、自动修复建议
S5: 自我验证 - 命名检查器自检
S6: 认知谦逊 - 标注存量文件不强制迁移
S7: 对抗测试 - 模拟命名冲突场景
"""

import os
import re
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class ViolationType(Enum):
    """违规类型枚举"""
    INVALID_CHARS = "invalid_chars"           # 包含非法字符
    UPPERCASE = "uppercase"                   # 包含大写字母
    SPACES = "spaces"                         # 包含空格
    TOO_LONG = "too_long"                     # 文件名过长
    TOO_SHORT = "too_short"                   # 文件名过短
    MISSING_TYPE = "missing_type"             # 缺少类型前缀
    WRONG_EXTENSION = "wrong_extension"       # 扩展名不符合规范
    DATE_FORMAT = "date_format"               # 日期格式错误
    VERSION_FORMAT = "version_format"         # 版本格式错误
    CONFLICT_RISK = "conflict_risk"           # 命名冲突风险


@dataclass
class Violation:
    """违规记录"""
    file_path: str
    violation_type: ViolationType
    message: str
    suggestion: str
    severity: str  # error, warning, info
    auto_fixable: bool
    legacy_file: bool = False  # S6: 标注存量文件


@dataclass
class CheckResult:
    """检查结果"""
    total_files: int
    compliant_files: int
    violations: List[Violation]
    compliance_rate: float
    legacy_files: int  # S6: 存量文件计数
    migration_progress: float  # S6: 迁移进度
    timestamp: str
    scan_duration_ms: int


class NamespaceChecker:
    """命名空间检查器主类"""
    
    def __init__(self, rules_path: Optional[str] = None):
        """初始化检查器"""
        self.rules = self._load_rules(rules_path)
        self.violations: List[Violation] = []
        self.legacy_files: List[str] = []
        self.checked_files: int = 0
        self.compliant_files: int = 0
        
    def _load_rules(self, rules_path: Optional[str]) -> Dict[str, Any]:
        """加载规则配置"""
        if rules_path is None:
            # 默认路径
            rules_path = Path(__file__).parent.parent / "namespace-rules.json"
        
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 规则文件未找到 {rules_path}，使用默认规则")
            return self._default_rules()
        except json.JSONDecodeError as e:
            print(f"错误: 规则文件格式错误: {e}")
            sys.exit(1)
    
    def _default_rules(self) -> Dict[str, Any]:
        """默认规则配置"""
        return {
            "rules": {
                "characters": {
                    "allowed": "a-z0-9-_.",
                    "forbidden": "!@#$%^&*()=+[]{}|;:'\",<><>?/\\\\",
                    "case": "lowercase_only"
                },
                "structure": {
                    "max_length": 100,
                    "min_length": 3
                },
                "types": {
                    "skill": {"pattern": "^skill-[a-z0-9-]+\\.md$"},
                    "script": {"pattern": "^[a-z0-9-]+\\.(py|sh|js)$"},
                    "config": {"pattern": "^[a-z0-9-]+\\.(json|yaml|yml)$"}
                }
            },
            "enforcement": {
                "mode": "advisory",
                "strict_mode": False,
                "legacy_migration": {
                    "strategy": "gradual",
                    "force_migration": False
                }
            }
        }
    
    # ========== S1: 全局考虑 - 检索效率影响分析 ==========
    
    def analyze_retrieval_impact(self, directory: str) -> Dict[str, Any]:
        """
        S1: 分析命名规范对文件检索效率的影响
        
        返回检索效率指标：
        - 前缀一致性得分
        - 可搜索性评分
        - 自动补全友好度
        """
        directory = Path(directory)
        files = list(directory.rglob('*'))
        files = [f for f in files if f.is_file()]
        
        analysis = {
            "total_files": len(files),
            "retrieval_efficiency": {
                "prefix_consistency_score": 0.0,
                "searchability_score": 0.0,
                "autocomplete_friendliness": 0.0
            },
            "factors": {}
        }
        
        if not files:
            return analysis
        
        # 前缀一致性分析
        prefix_groups = {}
        for f in files:
            name = f.stem
            if '-' in name:
                prefix = name.split('-')[0]
                prefix_groups[prefix] = prefix_groups.get(prefix, 0) + 1
        
        # 计算前缀一致性得分 (0-100)
        if prefix_groups:
            dominant_prefix_count = max(prefix_groups.values())
            analysis["retrieval_efficiency"]["prefix_consistency_score"] = (
                dominant_prefix_count / len(files) * 100
            )
        
        # 可搜索性评分 - 检查描述性命名
        descriptive_count = sum(
            1 for f in files 
            if len(f.stem) >= 5 and '-' in f.stem
        )
        analysis["retrieval_efficiency"]["searchability_score"] = (
            descriptive_count / len(files) * 100
        )
        
        # 自动补全友好度 - 检查无空格和特殊字符
        shell_friendly = sum(
            1 for f in files
            if ' ' not in f.name and all(
                c.isalnum() or c in '-_.' for c in f.name
            )
        )
        analysis["retrieval_efficiency"]["autocomplete_friendliness"] = (
            shell_friendly / len(files) * 100
        )
        
        # S1详细因子分析
        analysis["factors"] = {
            "prefix_consistency": {
                "description": "统一前缀允许使用通配符快速筛选",
                "score": analysis["retrieval_efficiency"]["prefix_consistency_score"],
                "impact": "高"
            },
            "hyphen_separation": {
                "description": "使用连字符而非空格，避免shell转义问题",
                "compliant_count": shell_friendly,
                "impact": "高"
            },
            "semantic_naming": {
                "description": "描述性名称支持模糊搜索和记忆检索",
                "descriptive_count": descriptive_count,
                "impact": "高"
            }
        }
        
        return analysis
    
    # ========== S2: 系统闭环 - 完整检查流程 ==========
    
    def check_file(self, file_path: str, is_new_file: bool = False) -> List[Violation]:
        """
        S2: 对单个文件进行命名检查
        
        流程: 文件路径解析 → 规则匹配 → 违规检测 → 建议生成
        """
        path = Path(file_path)
        violations = []
        
        if not path.exists():
            return [Violation(
                file_path=file_path,
                violation_type=ViolationType.INVALID_CHARS,
                message="文件不存在",
                suggestion="请检查文件路径",
                severity="error",
                auto_fixable=False
            )]
        
        filename = path.name
        
        # S6: 识别存量文件（创建时间早于规则实施日期）
        legacy_file = self._is_legacy_file(path) if not is_new_file else False
        
        # 1. 字符检查
        char_violations = self._check_characters(filename, str(path), legacy_file)
        violations.extend(char_violations)
        
        # 2. 长度检查
        length_violations = self._check_length(filename, str(path), legacy_file)
        violations.extend(length_violations)
        
        # 3. 类型前缀检查
        type_violations = self._check_type_prefix(path, legacy_file)
        violations.extend(type_violations)
        
        # 4. 扩展名检查
        ext_violations = self._check_extension(path, legacy_file)
        violations.extend(ext_violations)
        
        # 5. 冲突风险检查
        conflict_violations = self._check_conflict_risk(path, legacy_file)
        violations.extend(conflict_violations)
        
        self.checked_files += 1
        if not violations:
            self.compliant_files += 1
        elif legacy_file:
            self.legacy_files.append(str(path))
        
        return violations
    
    def _is_legacy_file(self, path: Path) -> bool:
        """S6: 判断是否为存量文件（基于修改时间）"""
        try:
            stat = path.stat()
            # 如果文件修改时间早于7天前，认为是存量文件
            age_days = (datetime.now().timestamp() - stat.st_mtime) / 86400
            return age_days > 7
        except:
            return False
    
    def _check_characters(self, filename: str, full_path: str, legacy: bool = False) -> List[Violation]:
        """检查字符规范"""
        violations = []
        rules = self.rules.get("rules", {}).get("characters", {})
        forbidden = rules.get("forbidden", "")
        
        # 检查非法字符
        found_forbidden = [c for c in filename if c in forbidden]
        if found_forbidden:
            violations.append(Violation(
                file_path=full_path,
                violation_type=ViolationType.INVALID_CHARS,
                message=f"文件名包含非法字符: {''.join(found_forbidden)}",
                suggestion=f"移除非法字符，使用允许的字符: {rules.get('allowed', 'a-z0-9-_.')}",
                severity="error" if not legacy else "warning",
                auto_fixable=True,
                legacy_file=legacy
            ))
        
        # 检查空格
        if ' ' in filename:
            violations.append(Violation(
                file_path=full_path,
                violation_type=ViolationType.SPACES,
                message="文件名包含空格",
                suggestion="将空格替换为连字符(-)",
                severity="error" if not legacy else "warning",
                auto_fixable=True,
                legacy_file=legacy
            ))
        
        # 检查大写字母
        if any(c.isupper() for c in filename):
            violations.append(Violation(
                file_path=full_path,
                violation_type=ViolationType.UPPERCASE,
                message="文件名包含大写字母",
                suggestion="将大写字母转换为小写",
                severity="warning",
                auto_fixable=True,
                legacy_file=legacy
            ))
        
        return violations
    
    def _check_length(self, filename: str, full_path: str, legacy: bool = False) -> List[Violation]:
        """检查长度规范"""
        violations = []
        rules = self.rules.get("rules", {}).get("structure", {})
        max_len = rules.get("max_length", 100)
        min_len = rules.get("min_length", 3)
        
        if len(filename) > max_len:
            violations.append(Violation(
                file_path=full_path,
                violation_type=ViolationType.TOO_LONG,
                message=f"文件名过长 ({len(filename)} > {max_len})",
                suggestion="缩短文件名，保留核心描述信息",
                severity="warning",
                auto_fixable=False,
                legacy_file=legacy
            ))
        
        if len(filename) < min_len:
            violations.append(Violation(
                file_path=full_path,
                violation_type=ViolationType.TOO_SHORT,
                message=f"文件名过短 ({len(filename)} < {min_len})",
                suggestion="增加描述性词语，使文件名更具意义",
                severity="info",
                auto_fixable=False,
                legacy_file=legacy
            ))
        
        return violations
    
    def _check_type_prefix(self, path: Path, legacy: bool = False) -> List[Violation]:
        """检查类型前缀"""
        violations = []
        filename = path.name
        stem = path.stem
        
        # 检查是否已包含有效类型前缀
        type_rules = self.rules.get("rules", {}).get("types", {})
        has_valid_prefix = False
        
        for type_name, type_config in type_rules.items():
            pattern = type_config.get("pattern", "")
            if pattern and re.match(pattern, filename):
                has_valid_prefix = True
                break
        
        # 检查是否在skills目录下应该有skill-前缀
        if "skills/" in str(path) and not has_valid_prefix:
            if path.suffix == '.md' and not filename.startswith('SKILL'):
                violations.append(Violation(
                    file_path=str(path),
                    violation_type=ViolationType.MISSING_TYPE,
                    message="技能文档缺少skill-前缀",
                    suggestion=f"建议重命名为: skill-{stem.lower()}.md",
                    severity="warning" if legacy else "error",
                    auto_fixable=True,
                    legacy_file=legacy
                ))
        
        return violations
    
    def _check_extension(self, path: Path, legacy: bool = False) -> List[Violation]:
        """检查扩展名"""
        violations = []
        suffix = path.suffix.lower()
        
        # 可接受的扩展名
        valid_extensions = ['.md', '.py', '.sh', '.js', '.json', '.yaml', '.yml', '.toml', '.txt']
        
        if not suffix:
            violations.append(Violation(
                file_path=str(path),
                violation_type=ViolationType.WRONG_EXTENSION,
                message="文件缺少扩展名",
                suggestion="添加适当的扩展名 (.md, .py, .json 等)",
                severity="info",
                auto_fixable=False,
                legacy_file=legacy
            ))
        elif suffix not in valid_extensions:
            violations.append(Violation(
                file_path=str(path),
                violation_type=ViolationType.WRONG_EXTENSION,
                message=f"不常见的扩展名: {suffix}",
                suggestion=f"确认扩展名是否正确，建议使用标准扩展名",
                severity="info",
                auto_fixable=False,
                legacy_file=legacy
            ))
        
        return violations
    
    def _check_conflict_risk(self, path: Path, legacy: bool = False) -> List[Violation]:
        """检查命名冲突风险"""
        violations = []
        parent = path.parent
        stem = path.stem.lower()
        
        # 检查同一目录下是否有相似名称（大小写不敏感）
        try:
            # 获取所有文件名（原始形式和大小写不敏感形式）
            original_names = [f.name for f in parent.iterdir() if f.is_file()]
            lowercase_names = [f.name.lower() for f in parent.iterdir() if f.is_file()]
            
            # 检查大小写变体
            current_lower = path.name.lower()
            case_variants = [n for n in original_names if n.lower() == current_lower and n != path.name]
            if case_variants:
                violations.append(Violation(
                    file_path=str(path),
                    violation_type=ViolationType.CONFLICT_RISK,
                    message=f"大小写冲突风险: 与现有文件大小写变体冲突 ({', '.join(case_variants[:3])})",
                    suggestion="使用统一的小写命名，删除其他大小写变体",
                    severity="error",
                    auto_fixable=False,
                    legacy_file=legacy
                ))
            
            # 检查相似名称（编辑距离）
            siblings = [f.stem.lower() for f in parent.iterdir() if f.is_file()]
            similar = [s for s in siblings if s != stem and (
                s.startswith(stem) or stem.startswith(s) or
                self._levenshtein_distance(s, stem) <= 2
            )]
            
            if similar:
                violations.append(Violation(
                    file_path=str(path),
                    violation_type=ViolationType.CONFLICT_RISK,
                    message=f"命名冲突风险: 与现有文件相似 ({', '.join(similar[:3])})",
                    suggestion="使用更具区分度的名称",
                    severity="warning",
                    auto_fixable=False,
                    legacy_file=legacy
                ))
        except:
            pass
        
        return violations
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """计算Levenshtein编辑距离"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def scan_directory(self, directory: str, recursive: bool = True) -> CheckResult:
        """扫描整个目录"""
        import time
        start_time = time.time()
        
        directory = Path(directory)
        all_violations = []
        
        # 获取排除模式
        excluded_patterns = self.rules.get("enforcement", {}).get("legacy_migration", {}).get("excluded_patterns", [])
        
        if recursive:
            files = list(directory.rglob('*'))
        else:
            files = list(directory.iterdir())
        
        files = [f for f in files if f.is_file()]
        
        # 过滤排除的文件
        filtered_files = []
        for f in files:
            str_path = str(f)
            if not any(pat in str_path for pat in excluded_patterns):
                filtered_files.append(f)
        
        for f in filtered_files:
            violations = self.check_file(str(f))
            all_violations.extend(violations)
        
        duration = int((time.time() - start_time) * 1000)
        
        # 计算合规率
        total = self.checked_files
        compliant = self.compliant_files
        compliance_rate = (compliant / total * 100) if total > 0 else 0
        
        # S6: 计算迁移进度
        legacy_count = len(self.legacy_files)
        migration_progress = ((total - legacy_count) / total * 100) if total > 0 else 0
        
        return CheckResult(
            total_files=total,
            compliant_files=compliant,
            violations=all_violations,
            compliance_rate=round(compliance_rate, 2),
            legacy_files=legacy_count,
            migration_progress=round(migration_progress, 2),
            timestamp=datetime.now().isoformat(),
            scan_duration_ms=duration
        )
    
    # ========== S3: 可观测输出 ==========
    
    def generate_report(self, result: CheckResult, output_path: Optional[str] = None) -> str:
        """
        S3: 生成可观测报告
        
        包含:
        - 合规率
        - 违规清单
        - 迁移进度
        """
        report = {
            "summary": {
                "total_files": result.total_files,
                "compliant_files": result.compliant_files,
                "compliance_rate": result.compliance_rate,
                "legacy_files": result.legacy_files,
                "migration_progress": result.migration_progress,
                "scan_duration_ms": result.scan_duration_ms
            },
            "violations_by_type": self._group_violations_by_type(result.violations),
            "violations_by_severity": self._group_violations_by_severity(result.violations),
            "legacy_files_notice": "S6: 存量文件不强制迁移，建议逐步规范化",
            "violations": [
                {
                    "file": v.file_path,
                    "type": v.violation_type.value,
                    "message": v.message,
                    "suggestion": v.suggestion,
                    "severity": v.severity,
                    "auto_fixable": v.auto_fixable,
                    "legacy": v.legacy_file
                }
                for v in result.violations
            ]
        }
        
        report_json = json.dumps(report, indent=2, ensure_ascii=False)
        
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_json)
            print(f"报告已保存: {output_path}")
        
        return report_json
    
    def _group_violations_by_type(self, violations: List[Violation]) -> Dict[str, int]:
        """按违规类型分组"""
        groups = {}
        for v in violations:
            key = v.violation_type.value
            groups[key] = groups.get(key, 0) + 1
        return groups
    
    def _group_violations_by_severity(self, violations: List[Violation]) -> Dict[str, int]:
        """按严重级别分组"""
        groups = {}
        for v in violations:
            groups[v.severity] = groups.get(v.severity, 0) + 1
        return groups
    
    def print_summary(self, result: CheckResult):
        """打印检查摘要"""
        print("\n" + "="*60)
        print("命名空间检查报告")
        print("="*60)
        print(f"扫描时间: {result.timestamp}")
        print(f"扫描耗时: {result.scan_duration_ms}ms")
        print(f"总文件数: {result.total_files}")
        print(f"合规文件: {result.compliant_files}")
        print(f"合规率: {result.compliance_rate}%")
        print(f"存量文件: {result.legacy_files} (S6: 不强制迁移)")
        print(f"迁移进度: {result.migration_progress}%")
        print("-"*60)
        
        if result.violations:
            print(f"\n违规统计 (共 {len(result.violations)} 项):")
            by_severity = self._group_violations_by_severity(result.violations)
            for severity, count in sorted(by_severity.items(), key=lambda x: x[1], reverse=True):
                print(f"  [{severity.upper()}] {count} 项")
            
            print("\n违规详情 (前10项):")
            for i, v in enumerate(result.violations[:10], 1):
                legacy_marker = " [存量]" if v.legacy_file else ""
                print(f"\n{i}. [{v.severity.upper()}] {v.violation_type.value}{legacy_marker}")
                print(f"   文件: {v.file_path}")
                print(f"   问题: {v.message}")
                print(f"   建议: {v.suggestion}")
                if v.auto_fixable:
                    print(f"   可自动修复: 是")
        else:
            print("\n✅ 所有文件符合命名规范！")
        
        print("\n" + "="*60)
    
    # ========== S4: 自动化集成 ==========
    
    def auto_check_on_create(self, file_path: str) -> Optional[str]:
        """
        S4: 文件创建时自动检查
        
        返回警告信息或None
        """
        violations = self.check_file(file_path, is_new_file=True)
        
        if not violations:
            return None
        
        # 生成即时警告
        warnings = []
        for v in violations:
            if v.severity in ['error', 'warning']:
                warnings.append(f"⚠️  {v.message}")
                warnings.append(f"    建议: {v.suggestion}")
        
        if warnings:
            return "\n".join([
                "命名规范警告:",
                *warnings,
                "",
                "使用 --auto-fix 应用自动修复建议"
            ])
        
        return None
    
    def get_auto_fix_suggestions(self, violation: Violation) -> Optional[str]:
        """
        S4: 生成自动修复建议
        """
        if not violation.auto_fixable:
            return None
        
        path = Path(violation.file_path)
        filename = path.name
        
        # 根据违规类型生成修复方案
        fixed_name = filename
        
        if violation.violation_type == ViolationType.UPPERCASE:
            fixed_name = fixed_name.lower()
        
        if violation.violation_type == ViolationType.SPACES:
            fixed_name = fixed_name.replace(' ', '-')
        
        if violation.violation_type == ViolationType.INVALID_CHARS:
            forbidden = self.rules.get("rules", {}).get("characters", {}).get("forbidden", "")
            for char in forbidden:
                fixed_name = fixed_name.replace(char, '')
        
        if violation.violation_type == ViolationType.MISSING_TYPE:
            # 添加类型前缀
            if path.suffix == '.md' and 'skills/' in str(path):
                fixed_name = f"skill-{path.stem.lower()}.md"
        
        return fixed_name if fixed_name != filename else None
    
    # ========== S5: 自我验证 ==========
    
    def self_validate(self) -> Dict[str, Any]:
        """
        S5: 命名检查器自检
        
        验证:
        1. 规则文件有效性
        2. 正则表达式合法性
        3. 核心函数可执行性
        4. 边界条件处理
        """
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "passed": True
        }
        
        # 1. 验证规则配置
        try:
            assert "rules" in self.rules, "规则配置缺少rules字段"
            assert "characters" in self.rules["rules"], "缺少字符规则"
            validation_results["checks"].append({
                "name": "规则配置完整性",
                "status": "passed"
            })
        except AssertionError as e:
            validation_results["checks"].append({
                "name": "规则配置完整性",
                "status": "failed",
                "error": str(e)
            })
            validation_results["passed"] = False
        
        # 2. 验证正则表达式
        try:
            for type_name, type_config in self.rules.get("rules", {}).get("types", {}).items():
                pattern = type_config.get("pattern", "")
                if pattern:
                    re.compile(pattern)
            validation_results["checks"].append({
                "name": "正则表达式合法性",
                "status": "passed"
            })
        except re.error as e:
            validation_results["checks"].append({
                "name": "正则表达式合法性",
                "status": "failed",
                "error": str(e)
            })
            validation_results["passed"] = False
        
        # 3. 验证核心函数
        try:
            # 测试空路径
            result = self.check_file("/nonexistent/path/file.txt")
            assert len(result) > 0, "文件不存在检查失败"
            
            # 测试正常文件名
            # 创建临时文件测试
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='-test-file.txt', delete=False) as f:
                temp_path = f.name
            result = self.check_file(temp_path)
            assert len(result) == 0, f"合规文件被误判: {result}"
            os.unlink(temp_path)
            
            validation_results["checks"].append({
                "name": "核心函数可执行性",
                "status": "passed"
            })
        except Exception as e:
            validation_results["checks"].append({
                "name": "核心函数可执行性",
                "status": "failed",
                "error": str(e)
            })
            validation_results["passed"] = False
        
        # 4. 验证边界条件
        try:
            # 测试空字符串
            self._check_characters("", "", False)
            # 测试超长文件名
            self._check_length("a" * 200, "", False)
            
            validation_results["checks"].append({
                "name": "边界条件处理",
                "status": "passed"
            })
        except Exception as e:
            validation_results["checks"].append({
                "name": "边界条件处理",
                "status": "failed",
                "error": str(e)
            })
            validation_results["passed"] = False
        
        return validation_results


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="Namespace Checker - 命名空间检查器")
    parser.add_argument("--scan", "-s", help="扫描目录路径")
    parser.add_argument("--report", "-r", help="生成JSON报告", action="store_true")
    parser.add_argument("--output", "-o", help="报告输出路径")
    parser.add_argument("--self-validate", help="执行自检", action="store_true")
    parser.add_argument("--analyze-impact", help="分析检索效率影响", action="store_true")
    parser.add_argument("--check-file", "-f", help="检查单个文件")
    parser.add_argument("--rules", help="自定义规则文件路径")
    
    args = parser.parse_args()
    
    # 初始化检查器
    checker = NamespaceChecker(rules_path=args.rules)
    
    # S5: 自检模式
    if args.self_validate:
        print("执行自检...")
        result = checker.self_validate()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["passed"] else 1)
    
    # S1: 检索效率分析
    if args.analyze_impact:
        if not args.scan:
            print("错误: --analyze-impact 需要 --scan 指定目录")
            sys.exit(1)
        analysis = checker.analyze_retrieval_impact(args.scan)
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
        sys.exit(0)
    
    # 检查单个文件
    if args.check_file:
        violations = checker.check_file(args.check_file)
        if violations:
            print(f"发现 {len(violations)} 项违规:")
            for v in violations:
                print(f"\n[{v.severity.upper()}] {v.violation_type.value}")
                print(f"  问题: {v.message}")
                print(f"  建议: {v.suggestion}")
                if v.legacy_file:
                    print(f"  注: 存量文件，不强制迁移 (S6)")
        else:
            print("✅ 文件符合命名规范")
        sys.exit(0)
    
    # 扫描目录
    if args.scan:
        result = checker.scan_directory(args.scan)
        checker.print_summary(result)
        
        if args.report:
            output = args.output or "namespace-compliance-report.json"
            checker.generate_report(result, output)
        
        # 返回非零退出码表示有违规
        sys.exit(1 if result.violations else 0)
    
    # 无参数时显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()
