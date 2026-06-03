#!/usr/bin/env python3
"""
Token监控机制 V2 - 修正版
增加偏差检测，不盲目接受数据
"""

import json
from datetime import datetime
from pathlib import Path

class TokenMonitorV2:
    """Token监控V2 - 带偏差检测"""
    
    def __init__(self):
        self.data_file = Path("/root/.openclaw/workspace/memory/token-weekly-monitor-current.json")
        self.data = self._load_data()
    
    def _load_data(self):
        if self.data_file.exists():
            return json.loads(self.data_file.read_text())
        return None
    
    def validate_input(self, new_percentage, timestamp):
        """验证新数据合理性"""
        alerts = []
        
        if not self.data:
            return {"valid": True, "alerts": ["无历史数据，无法验证趋势"]}
        
        old_percentage = self.data.get("openclawToken", {}).get("percentage", 0)
        old_time = self.data.get("openclawToken", {}).get("lastCheck", "")
        
        # 检查1: 跳跃过大
        jump = abs(new_percentage - old_percentage)
        if jump > 10:
            alerts.append(f"数据跳跃{jump}%（从{old_percentage}%到{new_percentage}%），请确认")
        
        # 检查2: 与时间进度对比
        time_progress = self._calc_time_progress(timestamp)
        diff = new_percentage - time_progress
        if abs(diff) > 15:
            alerts.append(f"消耗({new_percentage}%)与时间进度({time_progress}%)偏差{diff:.1f}%，请确认")
        
        # 检查3: 趋势合理性（每小时最大消耗约2%）
        if old_time:
            from datetime import datetime, timezone
            old_dt = datetime.fromisoformat(old_time.replace('Z', '+00:00'))
            new_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if isinstance(timestamp, str) else datetime.now(timezone.utc)
            # 都转为UTC比较
            if old_dt.tzinfo is None:
                old_dt = old_dt.replace(tzinfo=timezone.utc)
            if new_dt.tzinfo is None:
                new_dt = new_dt.replace(tzinfo=timezone.utc)
            hours_passed = (new_dt - old_dt).total_seconds() / 3600
            if hours_passed > 0:
                max_reasonable = hours_passed * 2  # 每小时最多2%
                if jump > max_reasonable:
                    alerts.append(f"{hours_passed:.1f}小时内消耗{jump}%，超出合理范围({max_reasonable:.1f}%)，请确认")
        
        return {
            "valid": len(alerts) == 0,
            "alerts": alerts,
            "old_percentage": old_percentage,
            "time_progress": time_progress
        }
    
    def _calc_time_progress(self, timestamp):
        """计算时间进度"""
        from datetime import timezone
        cycle_start = datetime(2026, 3, 25, 12, 0, tzinfo=timezone.utc)
        if isinstance(timestamp, str):
            now = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            now = datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        hours = (now - cycle_start).total_seconds() / 3600
        return (hours / 168) * 100
    
    def update(self, percentage, timestamp=None):
        """更新数据（带验证）"""
        timestamp = timestamp or datetime.now().isoformat()
        validation = self.validate_input(percentage, timestamp)
        
        if not validation["valid"]:
            print("⚠️ 数据验证警告:")
            for alert in validation["alerts"]:
                print(f"  - {alert}")
            print("请确认数据正确后再更新")
            return False, validation["alerts"]
        
        # 更新数据
        time_progress = self._calc_time_progress(timestamp)
        self.data = {
            "cycleInfo": {
                "startDate": "2026-03-25",
                "startTime": "12:00",
                "endDate": "2026-04-01",
                "endTime": "11:59",
                "status": "active"
            },
            "openclawToken": {
                "weeklyBudget": 280000,
                "dailyBudget": 40000,
                "consumed": int(280000 * percentage / 100),
                "remaining": int(280000 * (100 - percentage) / 100),
                "percentage": percentage,
                "status": "normal" if percentage < 70 else "warning" if percentage < 90 else "alert",
                "lastCheck": timestamp,
                "notes": f"时间进度{time_progress:.1f}%，消耗{percentage}%"
            },
            "timeProgress": {
                "percentage": round(time_progress, 1)
            },
            "assessment": {
                "consumptionVsTime": f"{percentage}% vs {time_progress:.1f}% = {percentage - time_progress:+.1f}%",
                "status": "normal" if abs(percentage - time_progress) < 10 else "warning"
            }
        }
        
        self.data_file.write_text(json.dumps(self.data, indent=2))
        print(f"✅ 已更新: {percentage}% (时间进度{time_progress:.1f}%)")
        return True, []

if __name__ == "__main__":
    monitor = TokenMonitorV2()
    print("Token监控V2 - 偏差检测机制")
    print(f"当前数据: {monitor.data.get('openclawToken', {}).get('percentage', 'N/A')}%")
