"""
Quality-Assurance System
5-Standard Quality Assurance Framework
"""

__version__ = "5.0.0"
__author__ = "Satisficing Institute"

from .core import (
    QualityResult,
    ConfidenceLevel,
    GateStatus,
    GateResult,
    PipelineResult,
    AdversarialResult,
    AdversarialReport,
    QualityMetrics,
    LimitationRegistry,
    QUALITY_DISCLAIMER
)

from .gates import (
    QualityGate,
    PrerequisitesCheck,
    ComplianceCheck,
    ResultsCheck,
    DocumentationCheck,
    create_gate,
    GATE_CONFIGS
)

from .adversarial import (
    DefectInjector,
    AdversarialTestRunner,
    MutationTesting,
    run_adversarial_tests,
    check_system_limitations
)

__all__ = [
    # Core
    "QualityResult",
    "ConfidenceLevel",
    "GateStatus",
    "GateResult",
    "PipelineResult",
    "AdversarialResult",
    "AdversarialReport",
    "QualityMetrics",
    "LimitationRegistry",
    "QUALITY_DISCLAIMER",
    # Gates
    "QualityGate",
    "PrerequisitesCheck",
    "ComplianceCheck",
    "ResultsCheck",
    "DocumentationCheck",
    "create_gate",
    "GATE_CONFIGS",
    # Adversarial
    "DefectInjector",
    "AdversarialTestRunner",
    "MutationTesting",
    "run_adversarial_tests",
    "check_system_limitations",
]
