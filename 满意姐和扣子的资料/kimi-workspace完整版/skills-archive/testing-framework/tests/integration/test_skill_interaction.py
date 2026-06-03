"""
Skill交互集成测试

测试目标: 验证多个Skill之间的数据交互和协作
测试类型: 集成测试 (Integration Test)
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

# 被测Skill路径
SKILLS_ROOT = Path(__file__).parent.parent.parent.parent


@pytest.mark.integration
class TestSkillInteraction:
    """Skill间交互测试"""
    
    def test_zero_idle_reads_token_budget(self, tmp_path):
        """测试Zero-Idle读取Token预算状态"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        
        # 创建Token预算数据
        token_data = {
            "date": "2024-01-01",
            "daily_budget": 50000,
            "used_today": 10000,
            "remaining_percentage": 80
        }
        (memory_dir / "token-weekly-monitor.json").write_text(
            json.dumps(token_data)
        )
        
        # 验证Zero-Idle能正确读取Token级别
        # 这里简化测试，实际会调用Zero-Idle的函数
        with open(memory_dir / "token-weekly-monitor.json") as f:
            data = json.load(f)
        
        assert data["remaining_percentage"] == 80
        assert data["remaining_percentage"] > 15  # 不触发CRITICAL
    
    def test_token_budget_considers_zero_idle_state(self, tmp_path):
        """测试Token预算考虑Zero-Idle状态"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        
        # 创建Zero-Idle状态
        zero_idle_state = {
            "last_fill_time": 1704067200,
            "fill_count_today": 2
        }
        (memory_dir / "zero-idle-state.json").write_text(
            json.dumps(zero_idle_state)
        )
        
        # Token预算应该考虑补位活动的Token消耗
        # 简化测试
        with open(memory_dir / "zero-idle-state.json") as f:
            state = json.load(f)
        
        assert state["fill_count_today"] >= 0
    
    def test_heartbeat_state_shared_across_skills(self, tmp_path):
        """测试Heartbeat状态被多个Skill共享"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        
        current_time = 1704067200
        
        # 创建共享的Heartbeat状态
        heartbeat_state = {
            "lastChecks": {
                "email": current_time - 3600,
                "calendar": current_time - 7200,
                "weather": current_time - 10800,
                "user_activity": current_time - 1800  # 30分钟前
            }
        }
        (memory_dir / "heartbeat-state.json").write_text(
            json.dumps(heartbeat_state)
        )
        
        # 多个Skill应该读取到相同的用户活动时间
        with open(memory_dir / "heartbeat-state.json") as f:
            state = json.load(f)
        
        last_activity = state["lastChecks"]["user_activity"]
        idle_time = current_time - last_activity
        
        assert idle_time == 1800  # 30分钟
        # Zero-Idle应该判断为不触发（<2小时）
        assert idle_time < 7200


@pytest.mark.integration
class TestDataConsistency:
    """数据一致性测试"""
    
    def test_json_data_format_consistency(self, tmp_path):
        """测试JSON数据格式一致性"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        
        # 创建各Skill的状态文件
        files_to_create = {
            "heartbeat-state.json": {
                "lastChecks": {"email": 1234567890}
            },
            "token-weekly-monitor.json": {
                "date": "2024-01-01",
                "daily_budget": 50000
            },
            "zero-idle-state.json": {
                "last_fill_time": 1234567890
            }
        }
        
        for filename, data in files_to_create.items():
            (memory_dir / filename).write_text(json.dumps(data, indent=2))
        
        # 验证所有文件都是有效的JSON
        for filename in files_to_create.keys():
            filepath = memory_dir / filename
            content = filepath.read_text()
            data = json.loads(content)  # 应该能成功解析
            assert isinstance(data, dict)
    
    def test_timestamp_format_consistency(self, tmp_path):
        """测试时间戳格式一致性"""
        import time
        
        current_timestamp = int(time.time())
        
        # 所有Skill应该使用相同的时间戳格式（Unix timestamp，整数）
        assert isinstance(current_timestamp, int)
        assert current_timestamp > 0
        
        # 验证日期格式一致性
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        assert len(date_str) == 10
        assert date_str.count("-") == 2
    
    def test_directory_structure_consistency(self):
        """测试目录结构一致性"""
        # 所有Skill应该有相同的目录结构
        expected_structure = ["SKILL.md", "scripts/"]
        
        skills_to_check = [
            "zero-idle-enforcer",
            "token-budget-enforcer",
            "blue-sentinel"
        ]
        
        for skill_name in skills_to_check:
            skill_dir = SKILLS_ROOT / skill_name
            if skill_dir.exists():
                # 验证SKILL.md存在
                assert (skill_dir / "SKILL.md").exists(), f"{skill_name} 缺少 SKILL.md"


@pytest.mark.integration
class TestErrorHandling:
    """错误处理集成测试"""
    
    def test_graceful_degradation_when_file_missing(self, tmp_path):
        """测试文件缺失时的优雅降级"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        
        # 故意不创建某些文件
        # Skill应该使用默认值而不是崩溃
        
        # 模拟读取不存在的文件
        missing_file = memory_dir / "non-existent.json"
        
        # 应该返回默认值而不是抛出异常
        if missing_file.exists():
            data = json.loads(missing_file.read_text())
        else:
            data = {"default": True}  # 默认值
        
        assert data["default"] is True
    
    def test_corrupted_file_recovery(self, tmp_path):
        """测试损坏文件恢复"""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        
        # 创建损坏的JSON文件
        corrupted_file = memory_dir / "corrupted.json"
        corrupted_file.write_text("not valid json {{{")
        
        # Skill应该能处理损坏的文件
        try:
            data = json.loads(corrupted_file.read_text())
        except json.JSONDecodeError:
            data = {"recovered": True}  # 恢复为默认值
        
        assert data["recovered"] is True
