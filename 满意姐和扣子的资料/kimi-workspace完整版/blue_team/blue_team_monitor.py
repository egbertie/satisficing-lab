#!/usr/bin/env python3
"""
蓝军监控告警系统 - 执行脚本
由蓝军Skeptor-7设计，满意姐执行
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class BlueTeamMonitor:
    """蓝军监控系统 - 满意姐执行"""
    
    def __init__(self, alert_db_path: str = "blue_team/alerts/alert.db"):
        self.alert_db_path = alert_db_path
        self.current_file = None
        self.checkpoints = {}
        self._init_db()
    
    def _init_db(self):
        """初始化告警数据库"""
        Path(self.alert_db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.alert_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE,
                timestamp TEXT,
                level TEXT,
                category TEXT,
                trigger_condition TEXT,
                file_name TEXT,
                message TEXT,
                action TEXT,
                status TEXT DEFAULT 'active',
                resolved_by TEXT,
                resolved_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def set_current_file(self, file_name: str):
        """设置当前监控文件"""
        self.current_file = file_name
        self.checkpoints = {
            'file_name': file_name,
            'phases': {},
            'checks': {}
        }
    
    # ========== 规则1: 流程合规性监控 ==========
    
    def check_phase0(self, file_info: bool, prev_file_saved: bool, 
                     duplicate_checked: bool, completeness: bool) -> bool:
        """检查阶段0: 前置确认"""
        self.checkpoints['phases']['phase0'] = {
            'file_info': file_info,
            'prev_file_saved': prev_file_saved,
            'duplicate_checked': duplicate_checked,
            'completeness': completeness
        }
        
        passed = True
        
        if not file_info:
            self.trigger_alert("P0", "流程合规性", "阶段0缺失: 未告知文件名")
            passed = False
        
        if not prev_file_saved:
            self.trigger_alert("P0", "流程合规性", "阶段0缺失: 未确认上文件记录")
            passed = False
        
        if not duplicate_checked:
            self.trigger_alert("P0", "流程合规性", "阶段0缺失: 未检查重复文件")
            passed = False
        
        if not completeness:
            self.trigger_alert("P0", "流程合规性", "阶段0缺失: 未检查文件完整性")
            passed = False
        
        return passed
    
    def check_phase1(self, paragraph_count: int, declared_count: int) -> bool:
        """检查阶段1: 全量提取"""
        self.checkpoints['phases']['phase1'] = {
            'paragraph_count': paragraph_count,
            'declared_count': declared_count,
            'complete': paragraph_count >= declared_count
        }
        
        if paragraph_count < declared_count:
            self.trigger_alert(
                "P0", "文件完整性",
                f"阶段1不完整: 提取{paragraph_count}段，文档实际{declared_count}段"
            )
            return False
        
        return True
    
    def check_phase2(self, architecture_identified: bool, data_sources_identified: bool) -> bool:
        """检查阶段2: 深度洞察"""
        self.checkpoints['phases']['phase2'] = {
            'architecture': architecture_identified,
            'data_sources': data_sources_identified
        }
        
        passed = True
        
        if not architecture_identified:
            self.trigger_alert("P0", "流程合规性", "阶段2缺失: 未识别核心架构")
            passed = False
        
        if not data_sources_identified:
            self.trigger_alert("P0", "流程合规性", "阶段2缺失: 未识别数据源")
            passed = False
        
        return passed
    
    def check_phase3(self, capability_assessed: bool) -> bool:
        """检查阶段3: 能力评估"""
        self.checkpoints['phases']['phase3'] = {'assessed': capability_assessed}
        
        if not capability_assessed:
            self.trigger_alert("P0", "流程合规性", "阶段3缺失: 未进行能力评估")
            return False
        
        return True
    
    def check_phase4(self, code_delivered: bool, tests_passed: bool) -> bool:
        """检查阶段4: 实际实施"""
        self.checkpoints['phases']['phase4'] = {
            'code_delivered': code_delivered,
            'tests_passed': tests_passed
        }
        
        passed = True
        
        if not code_delivered:
            self.trigger_alert("P0", "流程合规性", "阶段4缺失: 未交付代码/文档")
            passed = False
        
        if not tests_passed:
            self.trigger_alert("P1", "实施质量", "阶段4: 功能测试未通过")
            passed = False
        
        return passed
    
    def check_phase5(self, condition_recorded: bool, record_location: str) -> bool:
        """检查阶段5: 条件记录"""
        self.checkpoints['phases']['phase5'] = {
            'recorded': condition_recorded,
            'location': record_location
        }
        
        if not condition_recorded:
            self.trigger_alert("P0", "流程合规性", "阶段5缺失: 未记录技术迭代条件")
            return False
        
        return True
    
    def check_phase6(self, asset_integrated: bool) -> bool:
        """检查阶段6: 资产整合"""
        self.checkpoints['phases']['phase6'] = {'integrated': asset_integrated}
        
        if not asset_integrated:
            self.trigger_alert("P1", "资产整合", "阶段6: 未与已有资产整合")
            return False
        
        return True
    
    def check_phase7(self, task_registered: bool) -> bool:
        """检查阶段7: 任务登记"""
        self.checkpoints['phases']['phase7'] = {'registered': task_registered}
        
        if not task_registered:
            self.trigger_alert("P0", "流程合规性", "阶段7缺失: 未进行任务登记")
            return False
        
        return True
    
    # ========== 规则2: 文件完整性监控 ==========
    
    def check_completeness(self, actual_count: int, expected_count: int) -> bool:
        """检查文件完整性"""
        self.checkpoints['checks']['completeness'] = {
            'actual': actual_count,
            'expected': expected_count,
            'passed': actual_count >= expected_count
        }
        
        if actual_count < expected_count:
            self.trigger_alert(
                "P0", "文件完整性",
                f"段落提取不完整: {actual_count}/{expected_count} ({actual_count/expected_count*100:.1f}%)"
            )
            return False
        
        return True
    
    # ========== 规则3: 重复文件检测监控 ==========
    
    def check_duplicate_detection(self, file_name: str, duplicate_checked: bool,
                                   version_count: int = 1, processed_version: str = None) -> bool:
        """检查重复文件检测"""
        self.checkpoints['checks']['duplicate'] = {
            'checked': duplicate_checked,
            'version_count': version_count,
            'processed_version': processed_version
        }
        
        if not duplicate_checked:
            self.trigger_alert("P0", "重复检测", f"未对 {file_name} 执行重复检测")
            return False
        
        if version_count > 1 and not processed_version:
            self.trigger_alert("P0", "重复检测", 
                f"检测到{version_count}个版本，但未明确告知处理哪个版本")
            return False
        
        return True
    
    # ========== 规则4: 实施质量监控 ==========
    
    def check_implementation_quality(self, test_results: List[bool], 
                                     syntax_errors: int = 0) -> bool:
        """检查实施质量"""
        if not test_results:
            self.trigger_alert("P1", "实施质量", "未执行功能测试")
            return False
        
        pass_rate = sum(test_results) / len(test_results)
        
        self.checkpoints['checks']['quality'] = {
            'test_count': len(test_results),
            'pass_count': sum(test_results),
            'pass_rate': pass_rate,
            'syntax_errors': syntax_errors
        }
        
        if syntax_errors > 0:
            self.trigger_alert("P0", "实施质量", f"代码存在{syntax_errors}个语法错误")
            return False
        
        if pass_rate < 0.8:
            self.trigger_alert("P1", "实施质量", 
                f"测试通过率{pass_rate:.0%}，低于80%标准")
            return False
        
        return True
    
    # ========== 规则5: Token消耗监控 ==========
    
    def check_token_consumption(self, tokens: int, file_type: str = "tech_scheme") -> bool:
        """检查Token消耗"""
        thresholds = {
            'case_analysis': {'yellow': 5000, 'red': 8000},
            'tech_scheme': {'yellow': 8000, 'red': 12000},
            'deep_insight': {'yellow': 10000, 'red': 15000}
        }
        
        threshold = thresholds.get(file_type, {'yellow': 5000, 'red': 8000})
        
        self.checkpoints['checks']['token'] = {
            'consumed': tokens,
            'threshold_yellow': threshold['yellow'],
            'threshold_red': threshold['red']
        }
        
        if tokens > threshold['red']:
            self.trigger_alert("P0", "Token消耗", 
                f"Token消耗{tokens}，超过熔断阈值{threshold['red']}")
            return False
        
        if tokens > threshold['yellow']:
            self.trigger_alert("P1", "Token消耗",
                f"Token消耗{tokens}，超过告警阈值{threshold['yellow']}")
            return True  # 黄线不阻断，仅提醒
        
        return True
    
    # ========== 告警触发与记录 ==========
    
    def trigger_alert(self, level: str, category: str, message: str):
        """触发告警"""
        alert_id = f"ALT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{len(self.get_active_alerts())+1:03d}"
        
        alert = {
            'alert_id': alert_id,
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'category': category,
            'trigger_condition': message,
            'file_name': self.current_file,
            'message': message,
            'action': self._get_action(level),
            'status': 'active'
        }
        
        # 保存到数据库
        self._save_alert(alert)
        
        # 打印告警
        icon = "🔴" if level == "P0" else "🟡" if level == "P1" else "🟢"
        print(f"{icon} [{level}] {category}: {message}")
        print(f"   文件: {self.current_file}")
        print(f"   建议动作: {alert['action']}")
    
    def _get_action(self, level: str) -> str:
        """根据级别获取建议动作"""
        actions = {
            "P0": "立即暂停处理，强制回退修复",
            "P1": "记录债务，继续处理但需优化",
            "P2": "提醒注意，后续改进"
        }
        return actions.get(level, "关注")
    
    def _save_alert(self, alert: Dict):
        """保存告警到数据库"""
        conn = sqlite3.connect(self.alert_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts 
            (alert_id, timestamp, level, category, trigger_condition, file_name, message, action, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert['alert_id'], alert['timestamp'], alert['level'],
            alert['category'], alert['trigger_condition'], alert['file_name'],
            alert['message'], alert['action'], alert['status']
        ))
        
        conn.commit()
        conn.close()
    
    def get_active_alerts(self) -> List[Dict]:
        """获取活跃告警"""
        conn = sqlite3.connect(self.alert_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM alerts WHERE status = 'active' ORDER BY timestamp DESC
        ''')
        
        columns = [description[0] for description in cursor.description]
        alerts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return alerts
    
    def resolve_alert(self, alert_id: str, resolved_by: str):
        """解决告警"""
        conn = sqlite3.connect(self.alert_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE alerts 
            SET status = 'resolved', resolved_by = ?, resolved_at = ?
            WHERE alert_id = ?
        ''', (resolved_by, datetime.now().isoformat(), alert_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 告警 {alert_id} 已解决 by {resolved_by}")
    
    def generate_report(self) -> str:
        """生成监控报告"""
        alerts = self.get_active_alerts()
        
        report = f"""
📊 蓝军监控告警报告
═══════════════════════════════════════
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
当前文件: {self.current_file}

活跃告警: {len(alerts)} 个
"""
        
        for level in ["P0", "P1", "P2"]:
            level_alerts = [a for a in alerts if a['level'] == level]
            if level_alerts:
                icon = "🔴" if level == "P0" else "🟡" if level == "P1" else "🟢"
                report += f"\n{icon} {level}级告警 ({len(level_alerts)}个):\n"
                for alert in level_alerts[:5]:  # 最多显示5个
                    report += f"  - [{alert['category']}] {alert['message'][:50]}...\n"
        
        if not alerts:
            report += "\n✅ 无活跃告警，监控通过！\n"
        
        report += f"""
检查点状态:
  - 7阶段流程: {sum(1 for p in self.checkpoints.get('phases', {}).values() if isinstance(p, dict) and any(p.values()))}/7 阶段已检查
  - 完整性检查: {'✅ 通过' if self.checkpoints.get('checks', {}).get('completeness', {}).get('passed') else '❌ 未通过'}
  - 重复检测: {'✅ 已执行' if self.checkpoints.get('checks', {}).get('duplicate', {}).get('checked') else '❌ 未执行'}
  - 质量检查: {'✅ 通过' if self.checkpoints.get('checks', {}).get('quality', {}).get('pass_rate', 0) >= 0.8 else '⚠️ 需优化'}
"""
        
        return report


# CLI接口
if __name__ == "__main__":
    import sys
    
    monitor = BlueTeamMonitor()
    
    if len(sys.argv) < 2:
        print("蓝军监控告警系统")
        print("用法:")
        print("  python3 blue_team_monitor.py report          - 生成监控报告")
        print("  python3 blue_team_monitor.py alerts          - 查看活跃告警")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "report":
        print(monitor.generate_report())
    
    elif command == "alerts":
        alerts = monitor.get_active_alerts()
        if alerts:
            print(f"活跃告警 ({len(alerts)}个):")
            for alert in alerts:
                icon = "🔴" if alert['level'] == "P0" else "🟡"
                print(f"{icon} [{alert['level']}] {alert['category']}: {alert['message']}")
        else:
            print("✅ 无活跃告警")
