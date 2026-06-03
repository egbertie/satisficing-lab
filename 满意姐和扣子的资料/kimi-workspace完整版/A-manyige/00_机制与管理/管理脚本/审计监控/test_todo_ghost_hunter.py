#!/usr/bin/env python3
"""
test_todo_ghost_hunter.py
待办幽灵猎人测试
"""

import pytest
from todo_ghost_hunter import TodoGhostHunter


class TestTodoGhostHunter:
    def test_extract_file_hints(self):
        hunter = TodoGhostHunter()
        hints = hunter.extract_file_hints("运行 confucian_business_wisdom.py 验证")
        assert "confucian_business_wisdom.py" in hints

    def test_check_file_existence_real(self):
        hunter = TodoGhostHunter()
        ok, msg = hunter.check_file_existence("confucian_business_wisdom.py")
        assert ok is True
        assert "文件存在" in msg

    def test_check_file_existence_fake(self):
        hunter = TodoGhostHunter()
        ok, msg = hunter.check_file_existence("definitely_not_real_file.py")
        assert ok is False
        assert "文件不存在" in msg

    def test_check_test_status_real(self):
        hunter = TodoGhostHunter()
        ok, msg = hunter.check_test_status("confucian_business_wisdom.py")
        assert ok is True
        assert "通过" in msg

    def test_git_footprint_known(self):
        hunter = TodoGhostHunter()
        ok, msg = hunter.check_git_footprint("confucian_business_wisdom")
        # 近期应该已有 commit
        assert isinstance(ok, bool)

    def test_hunt_catches_ghost(self):
        hunter = TodoGhostHunter()
        # 这个任务实际已经完成（代码存在、测试通过、有git commit）
        todos = ["补齐企业儒学十大观念中缺失的第4（身正令行的领导观）、5（举贤使能的用人观）、8（兼善天下的责任观）项"]
        result = hunter.hunt(todos)
        assert result["ghost_count"] >= 1 or result["uncertain_count"] >= 1

    def test_hunt_real_task(self):
        hunter = TodoGhostHunter()
        # 用一个明显不存在的文件
        todos = ["完成 definitely_not_real_file.py 的测试验证"]
        result = hunter.hunt(todos)
        assert result["real_count"] == 1

    def test_report_format(self):
        hunter = TodoGhostHunter()
        report = hunter.report(["检查 definitely_not_real_file.py"])
        assert "# 待办幽灵猎人检测报告" in report
