#!/usr/bin/env python3
"""
quality-closure - 质量闭环管理器
真正实现版本

功能:
- 质量问题追踪
- 整改任务管理
- 闭环验证
- 质量报告归档
- 持续改进追踪

作者: 满意妞 (重构)
版本: 2.0.1-real
日期: 2026-04-03
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class IssueStatus(Enum):
    """问题状态"""
    OPEN = "open"           # 待处理
    IN_PROGRESS = "in_progress"  # 处理中
    RESOLVED = "resolved"   # 已解决
    VERIFIED = "verified"   # 已验证
    CLOSED = "closed"       # 已关闭
    REOPENED = "reopened"   # 重新打开


class IssueSeverity(Enum):
    """问题严重度"""
    CRITICAL = "critical"   # 严重
    HIGH = "high"           # 高
    MEDIUM = "medium"       # 中
    LOW = "low"             # 低


class ClosureType(Enum):
    """闭环类型"""
    FIXED = "fixed"         # 已修复
    MITIGATED = "mitigated" # 已缓解
    ACCEPTED = "accepted"   # 已接受
    DUPLICATE = "duplicate" # 重复
    INVALID = "invalid"     # 无效


@dataclass
class QualityIssue:
    """质量问题"""
    id: str
    title: str
    description: str
    severity: str
    status: str
    created_at: str
    assigned_to: str
    root_cause: str = ""
    solution: str = ""
    verified_by: str = ""
    closed_at: str = ""
    closure_type: str = ""
    reopen_count: int = 0
    comments: List[Dict] = field(default_factory=list)


@dataclass
class ClosureReport:
    """闭环报告"""
    period: str
    total_issues: int
    open_issues: int
    closed_count: int
    reopened_count: int
    avg_resolution_days: float
    closure_rate: float
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    trends: List[Dict]
    recommendations: List[str]
    timestamp: str


class QualityClosure:
    """质量闭环管理器"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """初始化"""
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.issues_file = self.data_dir / "issues.json"
        self.issues: List[QualityIssue] = []
        
        self._load_issues()
    
    def _load_issues(self):
        """加载问题列表"""
        if self.issues_file.exists():
            try:
                with open(self.issues_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.issues = [QualityIssue(**item) for item in data]
            except Exception:
                self.issues = []
    
    def _save_issues(self):
        """保存问题列表"""
        with open(self.issues_file, 'w', encoding='utf-8') as f:
            data = [self._issue_to_dict(issue) for issue in self.issues]
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _issue_to_dict(self, issue: QualityIssue) -> Dict:
        """转换问题为字典"""
        return {
            'id': issue.id,
            'title': issue.title,
            'description': issue.description,
            'severity': issue.severity,
            'status': issue.status,
            'created_at': issue.created_at,
            'assigned_to': issue.assigned_to,
            'root_cause': issue.root_cause,
            'solution': issue.solution,
            'verified_by': issue.verified_by,
            'closed_at': issue.closed_at,
            'closure_type': issue.closure_type,
            'reopen_count': issue.reopen_count,
            'comments': issue.comments
        }
    
    def create_issue(self, title: str, description: str, severity: str,
                    assigned_to: str = "") -> QualityIssue:
        """创建问题"""
        issue_id = f"QI-{len(self.issues) + 1:04d}"
        
        issue = QualityIssue(
            id=issue_id,
            title=title,
            description=description,
            severity=severity,
            status=IssueStatus.OPEN.value,
            created_at=datetime.now().isoformat(),
            assigned_to=assigned_to,
            comments=[]
        )
        
        self.issues.append(issue)
        self._save_issues()
        
        return issue
    
    def update_status(self, issue_id: str, new_status: str,
                     comment: str = "", user: str = "") -> Optional[QualityIssue]:
        """更新问题状态"""
        issue = self.get_issue(issue_id)
        if not issue:
            return None
        
        old_status = issue.status
        issue.status = new_status
        
        # 记录评论
        if comment:
            issue.comments.append({
                'user': user,
                'timestamp': datetime.now().isoformat(),
                'content': comment,
                'status_change': f"{old_status} -> {new_status}"
            })
        
        # 处理重新打开
        if new_status == IssueStatus.REOPENED.value:
            issue.reopen_count += 1
        
        # 处理关闭
        if new_status == IssueStatus.CLOSED.value:
            issue.closed_at = datetime.now().isoformat()
        
        self._save_issues()
        return issue
    
    def resolve_issue(self, issue_id: str, solution: str, root_cause: str,
                     user: str = "") -> Optional[QualityIssue]:
        """解决问题"""
        issue = self.get_issue(issue_id)
        if not issue:
            return None
        
        issue.solution = solution
        issue.root_cause = root_cause
        issue.status = IssueStatus.RESOLVED.value
        
        issue.comments.append({
            'user': user,
            'timestamp': datetime.now().isoformat(),
            'content': f"问题已解决\n根因: {root_cause}\n方案: {solution}",
            'status_change': f"-> {IssueStatus.RESOLVED.value}"
        })
        
        self._save_issues()
        return issue
    
    def verify_issue(self, issue_id: str, verified: bool, user: str = "",
                    notes: str = "") -> Optional[QualityIssue]:
        """验证问题"""
        issue = self.get_issue(issue_id)
        if not issue:
            return None
        
        if verified:
            issue.status = IssueStatus.VERIFIED.value
            issue.verified_by = user
            closure_type = ClosureType.FIXED.value
        else:
            issue.status = IssueStatus.REOPENED.value
            issue.reopen_count += 1
            closure_type = ""
        
        issue.closure_type = closure_type
        
        issue.comments.append({
            'user': user,
            'timestamp': datetime.now().isoformat(),
            'content': f"验证结果: {'通过' if verified else '不通过'}\n{notes}",
            'status_change': f"-> {issue.status}"
        })
        
        self._save_issues()
        return issue
    
    def close_issue(self, issue_id: str, closure_type: str, user: str = "",
                   comment: str = "") -> Optional[QualityIssue]:
        """关闭问题"""
        issue = self.get_issue(issue_id)
        if not issue:
            return None
        
        issue.status = IssueStatus.CLOSED.value
        issue.closure_type = closure_type
        issue.closed_at = datetime.now().isoformat()
        
        issue.comments.append({
            'user': user,
            'timestamp': datetime.now().isoformat(),
            'content': f"问题关闭 ({closure_type})\n{comment}",
            'status_change': f"-> {IssueStatus.CLOSED.value}"
        })
        
        self._save_issues()
        return issue
    
    def get_issue(self, issue_id: str) -> Optional[QualityIssue]:
        """获取问题"""
        for issue in self.issues:
            if issue.id == issue_id:
                return issue
        return None
    
    def list_issues(self, status: Optional[str] = None,
                   severity: Optional[str] = None,
                   assigned_to: Optional[str] = None) -> List[QualityIssue]:
        """列出问题"""
        result = self.issues
        
        if status:
            result = [i for i in result if i.status == status]
        
        if severity:
            result = [i for i in result if i.severity == severity]
        
        if assigned_to:
            result = [i for i in result if i.assigned_to == assigned_to]
        
        return result
    
    def generate_report(self, period: str = "monthly") -> ClosureReport:
        """生成闭环报告"""
        now = datetime.now()
        
        # 计算周期
        if period == "weekly":
            start_date = now - timedelta(days=7)
        elif period == "monthly":
            start_date = now - timedelta(days=30)
        elif period == "quarterly":
            start_date = now - timedelta(days=90)
        else:
            start_date = datetime.min
        
        # 统计
        total = len(self.issues)
        open_issues = len([i for i in self.issues if i.status == IssueStatus.OPEN.value])
        closed = len([i for i in self.issues if i.status == IssueStatus.CLOSED.value])
        reopened = len([i for i in self.issues if i.reopen_count > 0])
        
        # 按严重度统计
        by_severity = {}
        for sev in IssueSeverity:
            by_severity[sev.value] = len([i for i in self.issues if i.severity == sev.value])
        
        # 按状态统计
        by_status = {}
        for status in IssueStatus:
            by_status[status.value] = len([i for i in self.issues if i.status == status.value])
        
        # 计算平均解决时间
        resolution_days = []
        for issue in self.issues:
            if issue.closed_at and issue.created_at:
                try:
                    created_dt = datetime.fromisoformat(issue.created_at)
                    closed_dt = datetime.fromisoformat(issue.closed_at)
                    days = (closed_dt - created_dt).total_seconds() / 86400
                    resolution_days.append(days)
                except (ValueError, TypeError):
                    pass
        
        avg_resolution = sum(resolution_days) / len(resolution_days) if resolution_days else 0
        
        # 计算闭环率
        total_closed_or_verified = len([
            i for i in self.issues
            if i.status in [IssueStatus.CLOSED.value, IssueStatus.VERIFIED.value]
        ])
        closure_rate = total_closed_or_verified / total if total > 0 else 0
        
        # 生成建议
        recommendations = self._generate_recommendations(
            closure_rate, avg_resolution, reopened, open_issues
        )
        
        return ClosureReport(
            period=period,
            total_issues=total,
            open_issues=open_issues,
            closed_count=closed,
            reopened_count=reopened,
            avg_resolution_days=avg_resolution,
            closure_rate=closure_rate,
            by_severity=by_severity,
            by_status=by_status,
            trends=[],
            recommendations=recommendations,
            timestamp=now.isoformat()
        )
    
    def _generate_recommendations(self, closure_rate: float, avg_days: float,
                                 reopened: int, open_count: int) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if closure_rate < 0.8:
            recommendations.append(f"🚨 闭环率仅 {closure_rate:.1%}，需要加强问题跟进")
        elif closure_rate >= 0.95:
            recommendations.append(f"✅ 闭环率 {closure_rate:.1%}，表现优秀")
        
        if avg_days > 7:
            recommendations.append(f"⏰ 平均解决时间 {avg_days:.1f} 天，建议优化流程")
        
        if reopened > 0:
            recommendations.append(f"⚠️ 有 {reopened} 个问题被重新打开，需关注修复质量")
        
        if open_count > 10:
            recommendations.append(f"📋 积压 {open_count} 个待处理问题，建议安排清理")
        
        return recommendations
    
    def export_report(self, report: ClosureReport, format: str = "json") -> str:
        """导出报告"""
        if format == "json":
            return json.dumps(report.__dict__, ensure_ascii=False, indent=2, default=str)
        elif format == "markdown":
            return self._format_markdown(report)
        return ""
    
    def _format_markdown(self, report: ClosureReport) -> str:
        """格式化为Markdown"""
        lines = [
            "# 质量闭环报告",
            "",
            f"**统计周期**: {report.period}",
            f"**报告时间**: {report.timestamp}",
            "",
            "---",
            "",
            "## 📊 总体统计",
            "",
            f"- **总问题数**: {report.total_issues}",
            f"- **待处理**: {report.open_issues}",
            f"- **已关闭**: {report.closed_count}",
            f"- **重新打开**: {report.reopened_count}",
            f"- **闭环率**: {report.closure_rate:.1%}",
            f"- **平均解决时间**: {report.avg_resolution_days:.1f} 天",
            "",
            "---",
            "",
            "## 📁 按严重度分布",
            ""
        ]
        
        severity_icons = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        for severity, count in report.by_severity.items():
            icon = severity_icons.get(severity, '⚪')
            lines.append(f"- {icon} **{severity.upper()}**: {count}")
        
        lines.extend([
            "",
            "---",
            "",
            "## 📋 按状态分布",
            ""
        ])
        
        for status, count in report.by_status.items():
            lines.append(f"- **{status}**: {count}")
        
        if report.recommendations:
            lines.extend([
                "",
                "---",
                "",
                "## 💡 改进建议",
                ""
            ])
            for rec in report.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        return '\n'.join(lines)


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quality Closure - 质量闭环管理器')
    parser.add_argument('--create', nargs=3, metavar=('TITLE', 'DESC', 'SEVERITY'),
                       help='创建问题: 标题 描述 严重度')
    parser.add_argument('--list', action='store_true',
                       help='列出所有问题')
    parser.add_argument('--status', choices=[s.value for s in IssueStatus],
                       help='筛选状态')
    parser.add_argument('--resolve', nargs=4, metavar=('ID', 'SOLUTION', 'ROOT_CAUSE', 'USER'),
                       help='解决问题')
    parser.add_argument('--verify', nargs=3, metavar=('ID', 'VERIFIED', 'USER'),
                       help='验证问题 (VERIFIED: true/false)')
    parser.add_argument('--close', nargs=4, metavar=('ID', 'TYPE', 'USER', 'COMMENT'),
                       help='关闭问题')
    parser.add_argument('--report', action='store_true',
                       help='生成闭环报告')
    parser.add_argument('--period', default='monthly',
                       choices=['weekly', 'monthly', 'quarterly'],
                       help='报告周期')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown',
                       help='报告格式')
    parser.add_argument('--data-dir', help='数据目录')
    
    args = parser.parse_args()
    
    try:
        qc = QualityClosure(args.data_dir)
        
        if args.create:
            issue = qc.create_issue(args.create[0], args.create[1], args.create[2])
            print(f"✅ 问题已创建: {issue.id}")
            print(f"   标题: {issue.title}")
            print(f"   严重度: {issue.severity}")
            
        elif args.list:
            issues = qc.list_issues(status=args.status)
            if not issues:
                print("暂无问题")
            else:
                print(f"共 {len(issues)} 个问题:")
                print("-" * 60)
                for issue in issues:
                    print(f"{issue.id} [{issue.status}] {issue.severity}: {issue.title}")
                    
        elif args.resolve:
            issue = qc.resolve_issue(args.resolve[0], args.resolve[1],
                                    args.resolve[2], args.resolve[3])
            if issue:
                print(f"✅ 问题已解决: {issue.id}")
            else:
                print(f"❌ 未找到问题: {args.resolve[0]}")
                
        elif args.verify:
            verified = args.verify[1].lower() == 'true'
            issue = qc.verify_issue(args.verify[0], verified, args.verify[2])
            if issue:
                status = "通过" if verified else "不通过"
                print(f"✅ 验证{status}: {issue.id}")
            else:
                print(f"❌ 未找到问题: {args.verify[0]}")
                
        elif args.close:
            issue = qc.close_issue(args.close[0], args.close[1], args.close[2], args.close[3])
            if issue:
                print(f"✅ 问题已关闭: {issue.id}")
            else:
                print(f"❌ 未找到问题: {args.close[0]}")
                
        elif args.report:
            report = qc.generate_report(args.period)
            output = qc.export_report(report, args.format)
            print(output)
            
        else:
            # 显示状态
            report = qc.generate_report('monthly')
            print("=" * 50)
            print("Quality Closure - 质量闭环管理器")
            print("=" * 50)
            print(f"总问题数: {report.total_issues}")
            print(f"待处理: {report.open_issues}")
            print(f"已关闭: {report.closed_issues}")
            print(f"闭环率: {report.closure_rate:.1%}")
            print(f"平均解决时间: {report.avg_resolution_days:.1f} 天")
            print("=" * 50)
            print("\n使用 --help 查看可用命令")
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=__import__('sys').stderr)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
