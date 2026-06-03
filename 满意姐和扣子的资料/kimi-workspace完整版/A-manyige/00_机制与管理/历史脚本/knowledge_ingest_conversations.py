#!/usr/bin/env python3
"""
知识入库修正脚本 - 补充对话记录入库

诚实修正：之前只入库了skill文档，遗漏了最重要的对话记录
"""

import shutil
from pathlib import Path
from datetime import datetime

# 源文件
MEMORY_DIR = Path("~/.openclaw/workspace/memory").expanduser()
# 目标目录
OUTPUT_DIR = Path("~/.openclaw/workspace/diary/knowledge-ingest/ingested").expanduser()

def ingest_conversation_records():
    """入库对话记录"""
    count = 0
    
    for md_file in MEMORY_DIR.glob("*.md"):
        if md_file.name in ["README.md"]:
            continue
            
        dst_path = OUTPUT_DIR / f"memory_{md_file.name}"
        
        try:
            shutil.copy2(md_file, dst_path)
            print(f"✅ 入库对话记录: {md_file.name}")
            count += 1
        except Exception as e:
            print(f"❌ 失败: {md_file.name} - {e}")
    
    return count

if __name__ == "__main__":
    print("🔄 修正知识入库 - 补充对话记录...")
    print()
    
    count = ingest_conversation_records()
    
    print()
    print(f"📊 对话记录入库完成: {count} 个文件")
    print("   这些文件包含你的指令、决策、反馈，是最重要的知识")
