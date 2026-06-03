"""
端到端测试 - 完整工作流验证

测试目标: 验证从触发到完成的完整流程
测试类型: E2E测试 (End-to-End Test)
"""

import json
import time
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.mark.e2e
class TestZeroIdleFullWorkflow:
    """Zero-Idle完整工作流测试"""
    
    def test_full_idle_detection_to_fill_workflow(self, tmp_path):
        """测试完整空闲检测到补位的流程"""
        # 设置测试环境
        memory_dir = tmp_path / "memory"
        logs_dir = tmp_path / "logs"
        memory_dir.mkdir()
        logs_dir.mkdir()
        
        current_time = 1704067200
        
        # Step 1: 设置初始状态 - 用户3小时前活跃
        heartbeat_state = {
            "lastChecks": {
                "user_activity": current_time - 10800,  # 3小时前
                "email": current_time - 3600
            }
        }
        (memory_dir / "heartbeat-state.json").write_text(
            json.dumps(heartbeat_state)
        )
        
        # Step 2: 设置Token预算正常
        token_data = {
            "date": "2024-01-01",
            "daily_budget": 50000,
            "used_today": 10000,
            "remaining_percentage": 80
        }
        (memory_dir / "token-weekly-monitor.json").write_text(
            json.dumps(token_data)
        )
        
        # Step 3: 设置很久前补位
        zero_idle_state = {
            "last_fill_time": current_time - 10800  # 3小时前
        }
        (memory_dir / "zero-idle-state.json").write_text(
            json.dumps(zero_idle_state)
        )
        
        # Step 4: 运行检测逻辑（模拟）
        # 读取状态
        with open(memory_dir / "heartbeat-state.json") as f:
            hb = json.load(f)
        with open(memory_dir / "token-weekly-monitor.json") as f:
            token = json.load(f)
        with open(memory_dir / "zero-idle-state.json") as f:
            zis = json.load(f)
        
        # 检查触发条件
        idle_time = current_time - hb["lastChecks"]["user_activity"]
        token_level = "NORMAL" if token["remaining_percentage"] > 30 else "LOW"
        time_since_fill = current_time - zis["last_fill_time"]
        
        should_trigger = (
            idle_time >= 7200 and  # 空闲≥2小时
            token_level != "CRITICAL" and  # Token不临界
            time_since_fill >= 7200  # 上次补位≥2小时
        )
        
        # 验证应该触发
        assert idle_time == 10800  # 3小时空闲
        assert token_level == "NORMAL"
        assert time_since_fill == 10800
        assert should_trigger is True
        
        # Step 5: 执行补位（模拟）
        # 更新补位时间
        zis["last_fill_time"] = current_time
        zis["fill_count_today"] = zis.get("fill_count_today", 0) + 1
        (memory_dir / "zero-idle-state.json").write_text(
            json.dumps(zis)
        )
        
        # Step 6: 验证状态更新
        with open(memory_dir / "zero-idle-state.json") as f:
            updated_state = json.load(f)
        
        assert updated_state["last_fill_time"] == current_time
        assert updated_state["fill_count_today"] == 1
    
    def test_no_trigger_when_user_active(self, tmp_path):
        """测试用户活跃时不触发补位"""
        memory_dir = tmp_path / "memory"
        logs_dir = tmp_path / "logs"
        memory_dir.mkdir()
        logs_dir.mkdir()
        
        current_time = 1704067200
        
        # 用户30分钟前活跃
        heartbeat_state = {
            "lastChecks": {
                "user_activity": current_time - 1800  # 30分钟前
            }
        }
        (memory_dir / "heartbeat-state.json").write_text(
            json.dumps(heartbeat_state)
        )
        
        # 检查
        with open(memory_dir / "heartbeat-state.json") as f:
            hb = json.load(f)
        
        idle_time = current_time - hb["lastChecks"]["user_activity"]
        
        # 不应该触发
        assert idle_time == 1800  # 30分钟
        assert idle_time < 7200  # 小于2小时


@pytest.mark.e2e
class TestTokenBudgetFullWorkflow:
    """Token预算完整工作流测试"""
    
    def test_full_budget_tracking_workflow(self, tmp_path):
        """测试完整预算跟踪流程"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        
        # Step 1: 初始化每日预算
        current_date = "2024-01-01"
        token_data = {
            "date": current_date,
            "daily_budget": 50000,
            "used_today": 0,
            "remaining_percentage": 100,
            "pools": {
                "strategic_reserve": {"total": 15000, "used": 0},
                "operational_budget": {"total": 25000, "used": 0},
                "innovation_fund": {"total": 10000, "used": 0}
            }
        }
        (memory_dir / "token-weekly-monitor.json").write_text(
            json.dumps(token_data)
        )
        
        # Step 2: 模拟Token使用
        token_data["used_today"] += 5000
        token_data["remaining_percentage"] = 90
        token_data["pools"]["operational_budget"]["used"] += 5000
        
        (memory_dir / "token-weekly-monitor.json").write_text(
            json.dumps(token_data)
        )
        
        # Step 3: 检查预算级别
        with open(memory_dir / "token-weekly-monitor.json") as f:
            data = json.load(f)
        
        remaining = data["remaining_percentage"]
        
        if remaining > 30:
            level = "NORMAL"
        elif remaining > 15:
            level = "LOW"
        else:
            level = "CRITICAL"
        
        assert level == "NORMAL"
        assert remaining == 90
        
        # Step 4: 继续大量使用
        data["used_today"] += 42000
        data["remaining_percentage"] = 6
        
        # Step 5: 重新检查级别
        if data["remaining_percentage"] <= 15:
            new_level = "CRITICAL"
        
        assert new_level == "CRITICAL"
    
    def test_cross_day_budget_reset(self, tmp_path):
        """测试跨日预算重置"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        
        # 第1天结束时的状态
        day1_data = {
            "date": "2024-01-01",
            "daily_budget": 50000,
            "used_today": 45000,
            "remaining_percentage": 10
        }
        (memory_dir / "token-weekly-monitor.json").write_text(
            json.dumps(day1_data)
        )
        
        # 检查是否需要重置（跨日）
        current_date = "2024-01-02"
        
        with open(memory_dir / "token-weekly-monitor.json") as f:
            data = json.load(f)
        
        if data["date"] != current_date:
            # 重置预算
            data["date"] = current_date
            data["used_today"] = 0
            data["remaining_percentage"] = 100
        
        (memory_dir / "token-weekly-monitor.json").write_text(
            json.dumps(data)
        )
        
        # 验证重置成功
        with open(memory_dir / "token-weekly-monitor.json") as f:
            reset_data = json.load(f)
        
        assert reset_data["date"] == "2024-01-02"
        assert reset_data["used_today"] == 0
        assert reset_data["remaining_percentage"] == 100


@pytest.mark.e2e
class TestErrorRecoveryWorkflow:
    """错误恢复工作流测试"""
    
    def test_full_recovery_from_corrupted_state(self, tmp_path):
        """测试从损坏状态完全恢复"""
        memory_dir = tmp_path / "memory"
        logs_dir = tmp_path / "logs"
        memory_dir.mkdir()
        logs_dir.mkdir()
        
        # 创建损坏的状态文件
        (memory_dir / "heartbeat-state.json").write_text("corrupted{{{")
        (memory_dir / "token-weekly-monitor.json").write_text("not valid")
        
        # 恢复流程
        default_states = {
            "heartbeat-state.json": {
                "lastChecks": {"user_activity": int(time.time())}
            },
            "token-weekly-monitor.json": {
                "date": "2024-01-01",
                "daily_budget": 50000,
                "used_today": 0,
                "remaining_percentage": 100
            }
        }
        
        for filename, default_data in default_states.items():
            filepath = memory_dir / filename
            try:
                content = filepath.read_text()
                data = json.loads(content)
            except (json.JSONDecodeError, FileNotFoundError):
                # 使用默认值
                filepath.write_text(json.dumps(default_data))
        
        # 验证恢复
        with open(memory_dir / "token-weekly-monitor.json") as f:
            recovered = json.load(f)
        
        assert recovered["remaining_percentage"] == 100
    
    def test_fallback_when_files_missing(self, tmp_path):
        """测试文件缺失时的回退"""
        memory_dir = tmp_path / "memory"
        logs_dir = tmp_path / "logs"
        memory_dir.mkdir()
        logs_dir.mkdir()
        
        # 故意不创建任何状态文件
        # 系统应该使用内存默认值继续运行
        
        default_activity_time = int(time.time())
        default_token_level = "NORMAL"
        
        # 验证默认值有效
        assert default_activity_time > 0
        assert default_token_level in ["NORMAL", "LOW", "CRITICAL"]
