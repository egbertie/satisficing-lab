#!/usr/bin/env python3
# 文件: /root/.openclaw/workspace/scripts/conversation_archiver.py
# 功能: 对话强制归档系统
# 作者: Skeptor-7 (蓝军)
# 创建时间: 2026-04-04

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

class ConversationArchiver:
    def __init__(self):
        self.workspace = "/root/.openclaw/workspace"
        self.dialog_dir = f"{self.workspace}/A-manyige/对话"
        self.archive_log = f"{self.workspace}/.archive_status.json"
        self.force_flag = f"{self.workspace}/.force_archive_lock"
    
    def check_archive_status(self, date_str):
        """检查指定日期的归档完整性"""
        date_folder = f"{self.dialog_dir}/📅-按日期/{date_str}"
        
        # 检查必需文件
        required_files = ["README.md", "对话记录.md", "工作记录.md"]
        missing = []
        
        for file in required_files:
            if not os.path.exists(f"{date_folder}/{file}"):
                missing.append(file)
        
        return len(missing) == 0, missing
    
    def enforce_archive(self, date_str):
        """强制归档检查 - 不归档则阻止工作"""
        archived, missing = self.check_archive_status(date_str)
        
        if not archived:
            # 创建强制归档锁
            with open(self.force_flag, 'w') as f:
                json.dump({
                    "date": date_str,
                    "missing_files": missing,
                    "created_at": datetime.now().isoformat(),
                    "message": "必须先完成对话归档才能继续工作"
                }, f, indent=2)
            
            print(f"🚨 归档检查失败！")
            print(f"日期: {date_str}")
            print(f"缺失文件: {', '.join(missing)}")
            print(f"❌ 工作被阻止：请先完成对话归档")
            return False
        
        # 归档完成，移除锁
        if os.path.exists(self.force_flag):
            os.remove(self.force_flag)
        
        print(f"✅ {date_str} 归档检查通过")
        return True
    
    def get_today_date(self):
        return datetime.now().strftime("%Y-%m-%d")

# 主程序
if __name__ == "__main__":
    import sys
    
    archiver = ConversationArchiver()
    
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        date_str = archiver.get_today_date()
    
    success = archiver.enforce_archive(date_str)
    sys.exit(0 if success else 1)
