#!/usr/bin/env python3
"""
上下文管理脚本 - 自动检查Workspace文件大小并触发压缩
来源: 05基米爪令牌优化.docx (INGEST-20260401-05)
用途: Token优化P0级配置
"""
import os
import json
from datetime import datetime

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
LIMITS = {
    "AGENTS.md": 4000,
    "SOUL.md": 2000,
    "MEMORY.md": 3000,
    "TOOLS.md": 1000,
    "HEARTBEAT.md": 1000
}

def audit_workspace():
    """检查Workspace文件大小"""
    oversized = []
    total_size = 0
    
    for fname, limit in LIMITS.items():
        path = os.path.join(WORKSPACE, fname)
        if os.path.exists(path):
            size = os.path.getsize(path)
            total_size += size
            if size > limit:
                oversized.append((fname, size, limit))
    
    return oversized, total_size

def compact_session():
    """触发上下文压缩"""
    print("🔄 触发上下文压缩...")
    os.system("openclaw send '/compact'")

def new_session():
    """安全重置会话"""
    print("🔄 创建新会话...")
    os.system("openclaw send '/new'")

def suggest_migration(oversized):
    """建议迁移方案"""
    print("\n💡 建议迁移方案:")
    print("将以下内容移动到 vault/ 目录，保留索引在 MEMORY.md:")
    for fname, size, limit in oversized:
        print(f"  - {fname}: {size} bytes (限制: {limit})")
    print("\n操作命令:")
    for fname, _, _ in oversized:
        print(f"  mv {WORKSPACE}/{fname} {WORKSPACE}/vault/")

def generate_report():
    """生成审计报告"""
    oversized, total_size = audit_workspace()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "workspace": WORKSPACE,
        "total_size_bytes": total_size,
        "total_size_kb": round(total_size / 1024, 2),
        "files_checked": len(LIMITS),
        "oversized_files": len(oversized),
        "files": []
    }
    
    for fname, limit in LIMITS.items():
        path = os.path.join(WORKSPACE, fname)
        if os.path.exists(path):
            size = os.path.getsize(path)
            status = "✅ OK" if size <= limit else "⚠️ 超限"
            report["files"].append({
                "name": fname,
                "size": size,
                "limit": limit,
                "status": status
            })
    
    return report, oversized

def main():
    """主函数"""
    print("="*50)
    print("🔍 Workspace上下文审计")
    print("="*50)
    
    report, oversized = generate_report()
    
    print(f"\n📊 审计结果:")
    print(f"  总大小: {report['total_size_kb']} KB")
    print(f"  检查文件: {report['files_checked']} 个")
    print(f"  超限文件: {report['oversized_files']} 个")
    
    print(f"\n📁 文件详情:")
    for f in report["files"]:
        print(f"  {f['status']} {f['name']}: {f['size']} bytes (限制: {f['limit']})")
    
    if oversized:
        print(f"\n⚠️ 发现 {len(oversized)} 个文件超限制:")
        for fname, size, limit in oversized:
            print(f"  - {fname}: {size} bytes (限制: {limit}, 超出: {size-limit} bytes)")
        suggest_migration(oversized)
        
        # 自动触发压缩
        if report['total_size_bytes'] > 8000:
            compact_session()
    else:
        print("\n✅ 所有文件均在限制范围内")
    
    # 保存报告
    report_path = os.path.join(WORKSPACE, "logs", "context_audit.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "a") as f:
        f.write(json.dumps(report) + "\n")
    
    print(f"\n📝 报告已保存: {report_path}")

if __name__ == "__main__":
    main()
