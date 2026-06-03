#!/usr/bin/env python3
"""
缺陷追踪管理器 - S3标准实现

功能:
- 记录测试发现的缺陷
- 追踪缺陷状态
- 生成缺陷报告
- 统计缺陷指标

使用方法:
    python defect_tracker.py --list              # 列出所有缺陷
    python defect_tracker.py --report            # 生成缺陷报告
    python defect_tracker.py --add "描述"        # 添加新缺陷
    python defect_tracker.py --close DEF-001     # 关闭缺陷
    python defect_tracker.py --metrics           # 显示统计指标
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

PROJECT_ROOT = Path(__file__).parent
REPORTS_DIR = PROJECT_ROOT / "reports"
DEFECTS_FILE = REPORTS_DIR / "defects.json"


class DefectSeverity(Enum):
    """缺陷严重级别"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DefectStatus(Enum):
    """缺陷状态"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    CLOSED = "closed"
    WONT_FIX = "wont_fix"


class DefectType(Enum):
    """缺陷类型"""
    LOGIC_ERROR = "logic_error"
    BOUNDARY_ERROR = "boundary_error"
    NULL_POINTER = "null_pointer"
    RESOURCE_LEAK = "resource_leak"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UI_ISSUE = "ui_issue"
    OTHER = "other"


@dataclass
class Defect:
    """缺陷记录"""
    id: str
    timestamp: str
    skill: str
    test_case: str
    severity: str
    type: str
    description: str
    stack_trace: Optional[str]
    status: str
    assigned_to: Optional[str]
    fixed_in: Optional[str]
    closed_at: Optional[str]
    notes: Optional[str]


class DefectTracker:
    """缺陷追踪器"""
    
    def __init__(self):
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.defects: List[Defect] = []
        self._load()
    
    def _load(self):
        """加载缺陷数据"""
        if DEFECTS_FILE.exists():
            with open(DEFECTS_FILE, "r") as f:
                data = json.load(f)
                self.defects = [Defect(**d) for d in data.get("defects", [])]
    
    def _save(self):
        """保存缺陷数据"""
        data = {
            "defects": [asdict(d) for d in self.defects],
            "updated_at": datetime.now().isoformat()
        }
        with open(DEFECTS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    
    def _generate_id(self) -> str:
        """生成缺陷ID"""
        count = len(self.defects) + 1
        return f"DEF-{count:03d}"
    
    def add(
        self,
        skill: str,
        test_case: str,
        severity: str,
        defect_type: str,
        description: str,
        stack_trace: str = None,
        assigned_to: str = None
    ) -> str:
        """添加新缺陷"""
        defect = Defect(
            id=self._generate_id(),
            timestamp=datetime.now().isoformat(),
            skill=skill,
            test_case=test_case,
            severity=severity,
            type=defect_type,
            description=description,
            stack_trace=stack_trace,
            status=DefectStatus.OPEN.value,
            assigned_to=assigned_to,
            fixed_in=None,
            closed_at=None,
            notes=None
        )
        
        self.defects.append(defect)
        self._save()
        
        print(f"✅ 缺陷已记录: {defect.id}")
        return defect.id
    
    def close(self, defect_id: str, fixed_in: str = None, notes: str = None) -> bool:
        """关闭缺陷"""
        for defect in self.defects:
            if defect.id == defect_id:
                defect.status = DefectStatus.CLOSED.value
                defect.closed_at = datetime.now().isoformat()
                if fixed_in:
                    defect.fixed_in = fixed_in
                if notes:
                    defect.notes = notes
                self._save()
                print(f"✅ 缺陷已关闭: {defect_id}")
                return True
        
        print(f"❌ 缺陷未找到: {defect_id}")
        return False
    
    def update_status(self, defect_id: str, status: str) -> bool:
        """更新缺陷状态"""
        for defect in self.defects:
            if defect.id == defect_id:
                defect.status = status
                self._save()
                print(f"✅ 状态已更新: {defect_id} -> {status}")
                return True
        
        print(f"❌ 缺陷未找到: {defect_id}")
        return False
    
    def list_defects(
        self,
        status: str = None,
        severity: str = None,
        skill: str = None
    ) -> List[Defect]:
        """列出缺陷"""
        result = self.defects
        
        if status:
            result = [d for d in result if d.status == status]
        if severity:
            result = [d for d in result if d.severity == severity]
        if skill:
            result = [d for d in result if d.skill == skill]
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取缺陷统计指标"""
        total = len(self.defects)
        open_count = len([d for d in self.defects if d.status == DefectStatus.OPEN.value])
        closed_count = len([d for d in self.defects if d.status == DefectStatus.CLOSED.value])
        
        by_severity = {}
        by_skill = {}
        by_type = {}
        
        for defect in self.defects:
            # 按严重级别统计
            by_severity[defect.severity] = by_severity.get(defect.severity, 0) + 1
            # 按Skill统计
            by_skill[defect.skill] = by_skill.get(defect.skill, 0) + 1
            # 按类型统计
            by_type[defect.type] = by_type.get(defect.type, 0) + 1
        
        return {
            "total": total,
            "open": open_count,
            "closed": closed_count,
            "closure_rate": (closed_count / total * 100) if total > 0 else 0,
            "by_severity": by_severity,
            "by_skill": by_skill,
            "by_type": by_type
        }
    
    def generate_report(self) -> Path:
        """生成缺陷报告"""
        metrics = self.get_metrics()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "metrics": metrics,
            "open_defects": [asdict(d) for d in self.defects if d.status == DefectStatus.OPEN.value],
            "recently_closed": [asdict(d) for d in self.defects if d.status == DefectStatus.CLOSED.value][-10:]
        }
        
        report_file = REPORTS_DIR / "defect_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        # 同时生成Markdown报告
        md_file = REPORTS_DIR / "defect_report.md"
        self._generate_markdown_report(md_file, metrics)
        
        return report_file
    
    def _generate_markdown_report(self, file_path: Path, metrics: Dict):
        """生成Markdown格式报告"""
        lines = [
            "# 缺陷追踪报告",
            f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## 统计概览",
            f"\n- 总缺陷数: {metrics['total']}",
            f"- 未关闭: {metrics['open']}",
            f"- 已关闭: {metrics['closed']}",
            f"- 关闭率: {metrics['closure_rate']:.1f}%",
            "\n## 按严重级别分布",
        ]
        
        for severity, count in sorted(metrics['by_severity'].items()):
            lines.append(f"- {severity}: {count}")
        
        lines.extend(["\n## 按Skill分布"])
        for skill, count in sorted(metrics['by_skill'].items()):
            lines.append(f"- {skill}: {count}")
        
        lines.extend(["\n## 未关闭缺陷"])
        open_defects = [d for d in self.defects if d.status == DefectStatus.OPEN.value]
        if open_defects:
            lines.append("\n| ID | Skill | 严重级别 | 描述 | 时间 |")
            lines.append("|----|-------|----------|------|------|")
            for d in open_defects:
                desc = d.description[:40] + "..." if len(d.description) > 40 else d.description
                time = d.timestamp[:10]
                lines.append(f"| {d.id} | {d.skill} | {d.severity} | {desc} | {time} |")
        else:
            lines.append("\n暂无未关闭缺陷 🎉")
        
        with open(file_path, "w") as f:
            f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="缺陷追踪管理器")
    parser.add_argument("--list", action="store_true", help="列出所有缺陷")
    parser.add_argument("--report", action="store_true", help="生成缺陷报告")
    parser.add_argument("--add", type=str, help="添加新缺陷（描述）")
    parser.add_argument("--close", type=str, help="关闭指定ID的缺陷")
    parser.add_argument("--metrics", action="store_true", help="显示统计指标")
    parser.add_argument("--skill", type=str, help="筛选指定Skill")
    parser.add_argument("--severity", type=str, choices=["critical", "high", "medium", "low"])
    parser.add_argument("--type", type=str, default="logic_error")
    parser.add_argument("--test-case", type=str, default="unknown")
    
    args = parser.parse_args()
    
    tracker = DefectTracker()
    
    if args.add:
        tracker.add(
            skill=args.skill or "unknown",
            test_case=args.test_case,
            severity=args.severity or "medium",
            defect_type=args.type,
            description=args.add
        )
    
    elif args.close:
        tracker.close(args.close)
    
    elif args.list:
        defects = tracker.list_defects(
            skill=args.skill,
            severity=args.severity
        )
        
        print(f"\n{'ID':<10} {'Skill':<20} {'严重级别':<10} {'状态':<12} {'描述'}")
        print("-" * 100)
        for d in defects:
            desc = d.description[:40] + "..." if len(d.description) > 40 else d.description
            print(f"{d.id:<10} {d.skill:<20} {d.severity:<10} {d.status:<12} {desc}")
        print(f"\n总计: {len(defects)} 个缺陷")
    
    elif args.report:
        report_path = tracker.generate_report()
        print(f"✅ 报告已生成: {report_path}")
        print(f"   Markdown: {REPORTS_DIR / 'defect_report.md'}")
    
    elif args.metrics:
        metrics = tracker.get_metrics()
        print("\n=== 缺陷统计指标 ===")
        print(f"总缺陷数: {metrics['total']}")
        print(f"未关闭: {metrics['open']}")
        print(f"已关闭: {metrics['closed']}")
        print(f"关闭率: {metrics['closure_rate']:.1f}%")
        
        if metrics['by_severity']:
            print("\n按严重级别:")
            for sev, count in sorted(metrics['by_severity'].items()):
                print(f"  {sev}: {count}")
        
        if metrics['by_skill']:
            print("\n按Skill:")
            for skill, count in sorted(metrics['by_skill'].items()):
                print(f"  {skill}: {count}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
