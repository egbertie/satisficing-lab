#!/usr/bin/env python3
# 文件: /root/.openclaw/workspace/scripts/skill_interceptor.py
# 功能: Skill使用拦截器 - 强制使用Skill
# 作者: Skeptor-7 (蓝军)
# 创建时间: 2026-04-04

import os
import sys
import json
from pathlib import Path

# Skill映射表 - 操作类型到Skill的映射
SKILL_MAPPING = {
    # 飞书文档操作
    "doc_read": ["feishu_fetch_doc", "feishu_read_doc"],
    "doc_create": ["feishu_create_doc"],
    "doc_update": ["feishu_update_doc"],
    
    # 飞书文件操作
    "file_list": ["feishu_drive_file"],
    "file_upload": ["feishu_drive_file"],
    "file_download": ["feishu_drive_file"],
    
    # 飞书消息
    "message_send": ["feishu_im_user_message", "message"],
    "message_read": ["feishu_im_user_get_messages"],
    
    # 飞书日程
    "calendar_event": ["feishu_calendar_event"],
    "calendar_freebusy": ["feishu_calendar_freebusy"],
    
    # 飞书任务
    "task_create": ["feishu_task_task"],
    "task_list": ["feishu_task_tasklist"],
    
    # 飞书多维表格
    "bitable_read": ["feishu_bitable_app_table_record"],
    "bitable_write": ["feishu_bitable_app_table_record"],
    
    # 飞书电子表格
    "sheet_read": ["feishu_sheet"],
    "sheet_write": ["feishu_sheet"],
    
    # 通用操作
    "web_search": ["kimi_search", "web_search"],
    "web_fetch": ["kimi_fetch", "web_fetch"],
    "file_parse": ["read", "feishu_fetch_doc"],
    "data_analysis": ["feishu_sheet", "feishu_bitable_app_table_record"],
}

class SkillInterceptor:
    def __init__(self):
        self.workspace = "/root/.openclaw/workspace"
        self.violation_log = f"{self.workspace}/.skill_violations.json"
    
    def find_available_skills(self, operation_type):
        """查找操作类型对应的Skill"""
        return SKILL_MAPPING.get(operation_type, [])
    
    def check_before_operation(self, operation_type, description=""):
        """操作前检查 - 强制使用Skill"""
        available_skills = self.find_available_skills(operation_type)
        
        if available_skills:
            print(f"⚠️ 检测到操作类型: {operation_type}")
            print(f"可用Skill: {', '.join(available_skills)}")
            print(f"❌ 操作被阻止：必须使用Skill，禁止手动实现")
            print(f"操作描述: {description}")
            
            # 记录违规
            self.log_violation(operation_type, available_skills, description)
            
            return False
        
        print(f"✅ {operation_type}: 无强制Skill要求")
        return True
    
    def log_violation(self, operation_type, skills, description):
        """记录Skill违规"""
        violation = {
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type,
            "required_skills": skills,
            "description": description
        }
        
        # 读取现有记录
        violations = []
        if os.path.exists(self.violation_log):
            with open(self.violation_log, 'r') as f:
                try:
                    violations = json.load(f)
                except:
                    violations = []
        
        violations.append(violation)
        
        # 写入记录
        with open(self.violation_log, 'w') as f:
            json.dump(violations, f, indent=2)
    
    def get_violation_stats(self):
        """获取违规统计"""
        if not os.path.exists(self.violation_log):
            return {"total": 0, "by_type": {}}
        
        with open(self.violation_log, 'r') as f:
            violations = json.load(f)
        
        stats = {"total": len(violations), "by_type": {}}
        for v in violations:
            op_type = v["operation_type"]
            stats["by_type"][op_type] = stats["by_type"].get(op_type, 0) + 1
        
        return stats

# 主程序
if __name__ == "__main__":
    from datetime import datetime
    
    interceptor = SkillInterceptor()
    
    if len(sys.argv) < 2:
        print("用法: skill_interceptor.py <operation_type> [description]")
        print("示例: skill_interceptor.py doc_read '读取飞书文档'")
        sys.exit(1)
    
    operation_type = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else ""
    
    success = interceptor.check_before_operation(operation_type, description)
    sys.exit(0 if success else 1)
