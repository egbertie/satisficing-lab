#!/usr/bin/env python3
"""
全盘知识漏电深度排查 - 2-3天周期执行
扫描工作空间所有.md文件，发现未入库知识，执行7层标准化入库
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = "/root/.openclaw/workspace"
KNOWLEDGE_DIR = f"{WORKSPACE_ROOT}/knowledge"
INDEX_FILE = f"{KNOWLEDGE_DIR}/INDEX.md"
MEMORY_DIR = f"{WORKSPACE_ROOT}/memory"
LOG_FILE = f"{WORKSPACE_ROOT}/diary/blue-army-super-ingest/knowledge-leak-scan.json"

# 已入库文件模式（用于匹配已入库文档）
INGESTED_PATTERNS = [
    r'_v\d+\.\d+_ingested\.md$',
    r'_ingested\.md$'
]

# 排除的文件模式
EXCLUDE_PATTERNS = [
    r'BOOTSTRAP\.md$',  # 首次启动引导，可删除
    r'~$',              # 备份文件
    r'\.tmp$',          # 临时文件
    r'\.bak$',          # 备份文件
]


def is_excluded(filepath: str) -> bool:
    """检查文件是否在排除列表中"""
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, filepath):
            return True
    return False


def is_already_ingested(filepath: str) -> bool:
    """检查文件是否已入库"""
    filename = os.path.basename(filepath)
    
    # 检查文件名是否匹配已入库模式
    for pattern in INGESTED_PATTERNS:
        if re.search(pattern, filename):
            return True
    
    # 检查INDEX.md中是否已有记录
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # 提取文件名（不含扩展名）
            base_name = filename.replace('.md', '')
            if base_name in content:
                return True
    
    return False


def scan_workspace() -> dict:
    """扫描工作空间，找出未入库的.md文件"""
    leaked_files = []
    total_scanned = 0
    
    # 扫描工作空间根目录
    for md_file in Path(WORKSPACE_ROOT).glob("*.md"):
        filepath = str(md_file)
        total_scanned += 1
        
        if is_excluded(filepath):
            continue
            
        if not is_already_ingested(filepath):
            leaked_files.append({
                "path": filepath,
                "filename": md_file.name,
                "size": md_file.stat().st_size,
                "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
            })
    
    # 扫描子目录（learning_output, docs等）
    scan_dirs = [
        f"{WORKSPACE_ROOT}/learning_output",
        f"{WORKSPACE_ROOT}/docs",
        f"{WORKSPACE_ROOT}/system-v3",
    ]
    
    for scan_dir in scan_dirs:
        if os.path.exists(scan_dir):
            for md_file in Path(scan_dir).rglob("*.md"):
                filepath = str(md_file)
                total_scanned += 1
                
                if is_excluded(filepath):
                    continue
                    
                if not is_already_ingested(filepath):
                    leaked_files.append({
                        "path": filepath,
                        "filename": md_file.name,
                        "size": md_file.stat().st_size,
                        "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                    })
    
    return {
        "scan_time": datetime.now().isoformat(),
        "total_scanned": total_scanned,
        "leaked_count": len(leaked_files),
        "leaked_files": leaked_files
    }


def generate_batch_id() -> str:
    """生成批次ID"""
    return f"LEAK-{datetime.now().strftime('%y%m%d')}"


def create_daily_report(scan_result: dict) -> str:
    """生成日报内容"""
    report_lines = [
        "# 知识漏电排查日报",
        f"",
        f"**排查时间**: {scan_result['scan_time']}",
        f"**批次ID**: {generate_batch_id()}",
        f"",
        "## 扫描统计",
        f"",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| 扫描文件总数 | {scan_result['total_scanned']} |",
        f"| 发现漏电文件 | {scan_result['leaked_count']} |",
        f"| 入库完成率 | {(scan_result['total_scanned'] - scan_result['leaked_count']) / scan_result['total_scanned'] * 100:.1f}% |",
        f"",
    ]
    
    if scan_result['leaked_files']:
        report_lines.extend([
            "## 漏电文件清单",
            "",
            "| 文件名 | 路径 | 大小 | 修改时间 |",
            "|--------|------|------|----------|",
        ])
        
        for f in scan_result['leaked_files'][:20]:  # 最多显示20个
            report_lines.append(f"| {f['filename']} | `{f['path']}` | {f['size']} | {f['modified'][:10]} |")
        
        if len(scan_result['leaked_files']) > 20:
            report_lines.append(f"| ... | ... | ... | 还有 {len(scan_result['leaked_files']) - 20} 个文件 |")
        
        report_lines.extend([
            "",
            "## 处理建议",
            "",
            f"发现 {scan_result['leaked_count']} 个未入库文件，建议使用 `super-knowledge-ingest` Skill 执行7层标准化入库。",
            "",
        ])
    else:
        report_lines.extend([
            "## 结论",
            "",
            "✅ **无漏电** - 所有.md文件已完成7层标准化入库",
            "",
        ])
    
    return "\n".join(report_lines)


def save_scan_log(scan_result: dict):
    """保存扫描日志"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # 读取已有日志
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
    
    # 添加新记录
    logs.append(scan_result)
    
    # 只保留最近30次记录
    logs = logs[-30:]
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def save_daily_report(report: str):
    """保存日报到memory目录"""
    today = datetime.now().strftime('%Y-%m-%d')
    report_file = f"{MEMORY_DIR}/{today}-knowledge-leak-report.md"
    
    os.makedirs(MEMORY_DIR, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report_file


def trigger_skill_ingest(leaked_files: list):
    """
    触发super-knowledge-ingest skill进行入库
    实际执行需要OpenClaw环境支持
    """
    if not leaked_files:
        return
    
    # 生成批次信息
    batch_id = generate_batch_id()
    file_list = [f['path'] for f in leaked_files]
    
    # 记录到待处理队列
    queue_file = f"{WORKSPACE_ROOT}/.knowledge_ingest_queue.json"
    queue = []
    if os.path.exists(queue_file):
        try:
            with open(queue_file, 'r', encoding='utf-8') as f:
                queue = json.load(f)
        except:
            queue = []
    
    queue.append({
        "batch_id": batch_id,
        "created_at": datetime.now().isoformat(),
        "files": file_list,
        "status": "pending"
    })
    
    with open(queue_file, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)
    
    print(f"已添加 {len(file_list)} 个文件到入库队列 (批次: {batch_id})")


def main():
    print(f"[{datetime.now().isoformat()}] 开始知识漏电深度排查...")
    print(f"扫描目录: {WORKSPACE_ROOT}")
    print(f"知识库索引: {INDEX_FILE}")
    print("-" * 60)
    
    # 执行扫描
    scan_result = scan_workspace()
    
    print(f"扫描完成:")
    print(f"  - 扫描文件总数: {scan_result['total_scanned']}")
    print(f"  - 发现漏电文件: {scan_result['leaked_count']}")
    print(f"  - 当前入库率: {(scan_result['total_scanned'] - scan_result['leaked_count']) / scan_result['total_scanned'] * 100:.1f}%")
    
    # 保存扫描日志
    save_scan_log(scan_result)
    print(f"  - 扫描日志已保存: {LOG_FILE}")
    
    # 生成日报
    daily_report = create_daily_report(scan_result)
    report_file = save_daily_report(daily_report)
    print(f"  - 日报已生成: {report_file}")
    
    # 触发入库（如果有漏电文件）
    if scan_result['leaked_files']:
        trigger_skill_ingest(scan_result['leaked_files'])
        print(f"\n⚠️  发现 {scan_result['leaked_count']} 个未入库文件，已添加到处理队列")
        print(f"   建议使用 super-knowledge-ingest Skill 执行7层标准化入库")
    else:
        print(f"\n✅ 无漏电 - 所有.md文件已完成7层标准化入库")
    
    print("-" * 60)
    print(f"[{datetime.now().isoformat()}] 排查完成")


if __name__ == "__main__":
    main()
