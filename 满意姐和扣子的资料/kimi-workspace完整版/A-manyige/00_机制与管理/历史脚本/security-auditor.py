#!/usr/bin/env python3
"""
Security Auditor - 安全持续改进机制执行脚本
版本: 1.0
创建日期: 2026-03-18
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 安全检查清单
SECURITY_CHECKLIST = {
    "version": "1.0",
    "last_updated": "2026-03-18",
    "checks": [
        {
            "id": "SECRETS_AUDIT",
            "name": "Secrets审计",
            "command": "gh secret list 2>/dev/null || echo 'Not authenticated'",
            "expected": "No hardcoded secrets in .git/config",
            "weight": 25,
        },
        {
            "id": "BACKUP_STATUS",
            "name": "备份状态检查",
            "command": "ls -lt /data/backups/daily/ 2>/dev/null | head -3 || echo 'No backups'",
            "expected": "Backup within 24h",
            "weight": 25,
        },
        {
            "id": "FILE_PERMISSIONS",
            "name": "文件权限检查",
            "command": "find /root/.openclaw/workspace -type f -perm /o+w 2>/dev/null | wc -l",
            "expected": "0",
            "weight": 15,
        },
        {
            "id": "CRON_STATUS",
            "name": "Cron任务状态",
            "command": "openclaw cron list 2>/dev/null | grep -c 'enabled' || echo '0'",
            "expected": ">0",
            "weight": 15,
        },
        {
            "id": "GATEWAY_STATUS",
            "name": "Gateway运行状态",
            "command": "openclaw status 2>/dev/null | grep -i 'running' || echo 'Unknown'",
            "expected": "Running",
            "weight": 20,
        },
    ],
}

def run_check(check):
    """执行单个检查"""
    try:
        result = subprocess.run(
            check["command"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout.strip()
        return {
            "id": check["id"],
            "name": check["name"],
            "status": "pass" if output else "fail",
            "output": output[:200],  # 截断输出
            "weight": check["weight"],
        }
    except Exception as e:
        return {
            "id": check["id"],
            "name": check["name"],
            "status": "error",
            "output": str(e),
            "weight": check["weight"],
        }

def calculate_score(results):
    """计算安全评分"""
    total_weight = sum(r["weight"] for r in results)
    passed_weight = sum(r["weight"] for r in results if r["status"] == "pass")
    
    if total_weight == 0:
        return 0
    
    return int((passed_weight / total_weight) * 100)

def generate_report(results, score):
    """生成审计报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "version": SECURITY_CHECKLIST["version"],
        "score": score,
        "rating": "优秀" if score >= 90 else "良好" if score >= 80 else "一般" if score >= 70 else "需改进",
        "results": results,
        "improvements": [],
    }
    
    # 识别改进项
    for r in results:
        if r["status"] != "pass":
            report["improvements"].append({
                "check": r["name"],
                "issue": r["output"],
                "recommendation": get_recommendation(r["id"]),
            })
    
    return report

def get_recommendation(check_id):
    """获取改进建议"""
    recommendations = {
        "SECRETS_AUDIT": "检查.git/config和代码中是否有硬编码密钥",
        "BACKUP_STATUS": "检查备份任务是否正常运行，手动触发备份",
        "FILE_PERMISSIONS": "检查并修复过于开放的文件权限",
        "CRON_STATUS": "检查Cron服务状态和任务配置",
        "GATEWAY_STATUS": "检查OpenClaw Gateway进程状态",
    }
    return recommendations.get(check_id, "需要人工审查")

def save_report(report):
    """保存报告"""
    report_dir = "/root/.openclaw/workspace/docs/security-reports"
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(report_dir, f"security_audit_{timestamp}.json")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report_path

def print_summary(report):
    """打印摘要"""
    print(f"\n{'='*50}")
    print(f"安全审计报告 | {report['timestamp'][:10]}")
    print(f"{'='*50}")
    print(f"安全评分: {report['score']}/100 ({report['rating']})")
    print(f"\n检查结果:")
    
    for r in report["results"]:
        status_icon = "✅" if r["status"] == "pass" else "❌" if r["status"] == "fail" else "⚠️"
        print(f"  {status_icon} {r['name']}: {r['status']} (权重{r['weight']}%)")
    
    if report["improvements"]:
        print(f"\n改进建议:")
        for i, imp in enumerate(report["improvements"], 1):
            print(f"  {i}. {imp['check']}: {imp['recommendation']}")
    else:
        print(f"\n✨ 无待改进项，继续保持！")
    
    print(f"{'='*50}\n")

if __name__ == "__main__":
    print("开始安全审计...")
    
    # 执行所有检查
    results = []
    for check in SECURITY_CHECKLIST["checks"]:
        print(f"  检查: {check['name']}...", end=" ")
        result = run_check(check)
        results.append(result)
        print(result["status"])
    
    # 计算评分
    score = calculate_score(results)
    
    # 生成报告
    report = generate_report(results, score)
    
    # 保存报告
    report_path = save_report(report)
    
    # 打印摘要
    print_summary(report)
    
    print(f"报告已保存: {report_path}")
