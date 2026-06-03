"""
info-collection-quality - 信息采集与质量控制体系

5-Standard Skill: 全流程质量管控 (S1-S7)
"""

from .info_collection_quality_runner import (
    QualityChecker,
    QualityReport,
    QualityGrade,
    InfoCollectionQualityRunner
)

__version__ = "2.0.0"
__all__ = [
    "QualityChecker",
    "QualityReport", 
    "QualityGrade",
    "InfoCollectionQualityRunner"
]
