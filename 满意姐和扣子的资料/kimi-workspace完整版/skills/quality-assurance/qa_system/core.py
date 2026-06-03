"""
QA System Core Module
5-Standard Quality Assurance Framework
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


class ConfidenceLevel(Enum):
    """置信度等级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class GateStatus(Enum):
    """门禁状态"""
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CONDITIONAL = "conditional"
    SKIPPED = "skipped"


@dataclass
class QualityResult:
    """质量检查结果"""
    result: bool
    confidence: ConfidenceLevel
    score: float = 0.0
    notes: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        return f"Result({self.result}, confidence={self.confidence.value}, score={self.score})"


@dataclass
class GateCheck:
    """门禁检查项"""
    name: str
    description: str
    weight: float
    blocking: bool = True
    required: bool = True
    
    def evaluate(self, target: Any) -> QualityResult:
        """执行检查 - 子类应重写此方法"""
        raise NotImplementedError


@dataclass
class GateResult:
    """门禁执行结果"""
    gate_name: str
    status: GateStatus
    total_score: float
    weighted_score: float
    checks: List[Dict[str, Any]] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_name": self.gate_name,
            "status": self.status.value,
            "total_score": self.total_score,
            "weighted_score": self.weighted_score,
            "checks": self.checks,
            "failed_checks": self.failed_checks,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class PipelineResult:
    """流水线执行结果"""
    status: str
    stage: str
    duration: float
    results: List[GateResult] = field(default_factory=list)
    failed_check: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def passed(self) -> bool:
        return self.status == "PASSED"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "stage": self.stage,
            "duration": self.duration,
            "results": [r.to_dict() for r in self.results],
            "failed_check": self.failed_check,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class AdversarialResult:
    """对抗测试结果"""
    defect_type: str
    description: str
    expected_detection: str
    detected: bool
    details: str = ""
    
    @property
    def status(self) -> str:
        return "PASS" if self.detected else "FAIL"


@dataclass
class AdversarialReport:
    """对抗测试报告"""
    results: List[AdversarialResult]
    detection_rate: float
    status: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_injections": len(self.results),
            "detected": sum(1 for r in self.results if r.detected),
            "missed": sum(1 for r in self.results if not r.detected),
            "detection_rate": self.detection_rate,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "results": [
                {
                    "defect_type": r.defect_type,
                    "description": r.description,
                    "expected_detection": r.expected_detection,
                    "detected": r.detected,
                    "status": r.status,
                    "details": r.details
                }
                for r in self.results
            ]
        }


class QualityMetrics:
    """质量指标收集器"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
    
    def record(self, name: str, value: Any, unit: str = ""):
        """记录指标"""
        self.metrics[name] = {
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_coverage_metrics(self, coverage_data: Dict) -> Dict[str, float]:
        """计算覆盖率指标"""
        return {
            "line_coverage": coverage_data.get("line_coverage", 0.0),
            "branch_coverage": coverage_data.get("branch_coverage", 0.0),
            "function_coverage": coverage_data.get("function_coverage", 0.0),
            "path_coverage": coverage_data.get("path_coverage", 0.0)
        }
    
    def calculate_defect_metrics(self, defects: List[Dict]) -> Dict[str, Any]:
        """计算缺陷指标"""
        total = len(defects)
        open_defects = [d for d in defects if d.get("status") == "open"]
        critical = [d for d in defects if d.get("severity") == "critical"]
        high = [d for d in defects if d.get("severity") == "high"]
        
        return {
            "total_found": total,
            "open": len(open_defects),
            "critical": len(critical),
            "high": len(high),
            "resolution_rate": (total - len(open_defects)) / total if total > 0 else 1.0
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics
        }


class LimitationRegistry:
    """局限性注册表 - S6实现"""
    
    LIMITATIONS = [
        {
            "id": "LIM-001",
            "category": "业务逻辑",
            "description": "无法验证业务逻辑正确性",
            "impact": "高",
            "mitigation": "需求评审+人工验证"
        },
        {
            "id": "LIM-002",
            "category": "AI输出",
            "description": "无法验证AI生成内容质量",
            "impact": "中",
            "mitigation": "人工抽样检查"
        },
        {
            "id": "LIM-003",
            "category": "并发问题",
            "description": "无法检测所有竞争条件",
            "impact": "高",
            "mitigation": "压力测试+代码审查"
        },
        {
            "id": "LIM-004",
            "category": "性能问题",
            "description": "无法预测生产环境性能",
            "impact": "中",
            "mitigation": "性能测试+监控"
        },
        {
            "id": "LIM-005",
            "category": "安全漏洞",
            "description": "无法检测所有安全漏洞",
            "impact": "高",
            "mitigation": "专业安全扫描"
        },
        {
            "id": "LIM-006",
            "category": "UI/UX",
            "description": "无法评估用户体验",
            "impact": "低",
            "mitigation": "用户测试"
        },
        {
            "id": "LIM-007",
            "category": "集成故障",
            "description": "无法验证第三方服务",
            "impact": "中",
            "mitigation": "契约测试+健康检查"
        }
    ]
    
    @classmethod
    def get_all_limitations(cls) -> List[Dict[str, str]]:
        return cls.LIMITATIONS
    
    @classmethod
    def get_by_category(cls, category: str) -> List[Dict[str, str]]:
        return [l for l in cls.LIMITATIONS if l["category"] == category]
    
    @classmethod
    def get_high_impact(cls) -> List[Dict[str, str]]:
        return [l for l in cls.LIMITATIONS if l["impact"] == "高"]


# Global disclaimer
QUALITY_DISCLAIMER = """
## 质量保障系统局限性声明

本系统提供的质量检查结果仅供参考，不构成质量保证。

### 已知局限：
1. **业务逻辑正确性**: 系统无法验证代码是否实现了正确的业务逻辑
2. **测试覆盖盲区**: 无法保证100%代码路径被测试覆盖
3. **工具局限性**: 静态分析工具可能存在误报和漏报
4. **环境差异**: 测试环境与生产环境可能存在差异
5. **并发问题**: 无法检测所有并发和竞争条件问题
6. **安全漏洞**: 无法替代专业安全审计
7. **AI生成内容**: 无法评估AI生成内容的质量和适用性

### 建议：
- 关键业务逻辑需配合需求评审和人工测试
- 定期进行人工代码审查
- 生产环境配合监控和告警
- 安全关键系统需进行专业安全评估
"""
