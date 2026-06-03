#!/usr/bin/env python3
"""
5标准Skill验证脚本
版本: V2.0
验证所有完整5标准的Skill是否真正能运行
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def find_complete_skills():
    """找到所有完整5标准的Skill"""
    skills_dir = Path("/root/.openclaw/workspace/skills")
    complete_skills = []
    
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
            
        has_skill_md = (skill_dir / "SKILL.md").exists()
        has_script = False
        has_cron = False
        
        # 检查脚本
        scripts_dir = skill_dir / "scripts"
        all_scripts = []
        if scripts_dir.exists():
            all_scripts = list(scripts_dir.glob("*.py")) + list(scripts_dir.glob("*.sh"))
            if all_scripts:
                has_script = True
        
        # 检查Cron
        if (skill_dir / "cron.json").exists() or \
           (skill_dir / "cron-config.sh").exists() or \
           (skill_dir / "cron.d").exists():
            has_cron = True
        
        if has_skill_md and has_script and has_cron:
            complete_skills.append({
                "name": skill_dir.name,
                "path": skill_dir,
                "scripts": [s.name for s in all_scripts]
            })
    
    return complete_skills

def verify_skill(skill_info):
    """验证单个Skill"""
    name = skill_info["name"]
    path = skill_info["path"]
    scripts = skill_info["scripts"]
    
    results = {
        "name": name,
        "scripts_verified": 0,
        "scripts_failed": 0,
        "errors": [],
        "status": "unknown"
    }
    
    for script_name in scripts:
        script_path = path / "scripts" / script_name
        
        # 检查文件存在
        if not script_path.exists():
            results["errors"].append(f"{script_name}: 文件不存在")
            results["scripts_failed"] += 1
            continue
        
        # 检查可执行权限
        if not os.access(script_path, os.X_OK):
            # 尝试添加权限
            try:
                os.chmod(script_path, 0o755)
            except Exception as e:
                results["errors"].append(f"{script_name}: 无法添加执行权限 - {e}")
                results["scripts_failed"] += 1
                continue
        
        # 尝试运行 --help 或 status
        try:
            if script_name.endswith('.py'):
                result = subprocess.run(
                    ['python3', str(script_path), '--help'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                result = subprocess.run(
                    [str(script_path), '--help'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            if result.returncode == 0:
                results["scripts_verified"] += 1
            else:
                results["errors"].append(f"{script_name}: 运行返回非零 - {result.stderr[:100]}")
                results["scripts_failed"] += 1
                
        except subprocess.TimeoutExpired:
            results["errors"].append(f"{script_name}: 运行超时")
            results["scripts_failed"] += 1
        except Exception as e:
            results["errors"].append(f"{script_name}: 运行异常 - {str(e)[:100]}")
            results["scripts_failed"] += 1
    
    # 确定状态
    if results["scripts_failed"] == 0 and results["scripts_verified"] > 0:
        results["status"] = "✅ 通过"
    elif results["scripts_verified"] > 0:
        results["status"] = "🟡 部分通过"
    else:
        results["status"] = "❌ 失败"
    
    return results

def main():
    log("=== 5标准Skill验证开始 ===")
    
    # 找到所有完整5标准的Skill
    complete_skills = find_complete_skills()
    log(f"发现 {len(complete_skills)} 个完整5标准的Skill")
    
    # 逐个验证
    results = []
    passed = 0
    partial = 0
    failed = 0
    
    for i, skill in enumerate(complete_skills, 1):
        log(f"验证 {i}/{len(complete_skills)}: {skill['name']}")
        result = verify_skill(skill)
        results.append(result)
        
        if result["status"] == "✅ 通过":
            passed += 1
        elif result["status"] == "🟡 部分通过":
            partial += 1
        else:
            failed += 1
    
    # 生成报告
    log("=== 验证完成 ===")
    log(f"通过: {passed} | 部分通过: {partial} | 失败: {failed}")
    
    # 保存详细报告
    report_path = Path("/root/.openclaw/workspace/docs/VERIFICATION_REPORT_1445.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 5标准Skill验证报告\n")
        f.write(f"> 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 汇总\n\n")
        f.write(f"- 验证总数: {len(results)}\n")
        f.write(f"- ✅ 通过: {passed}\n")
        f.write(f"- 🟡 部分通过: {partial}\n")
        f.write(f"- ❌ 失败: {failed}\n\n")
        f.write("## 详细结果\n\n")
        
        for r in results:
            f.write(f"### {r['name']}\n")
            f.write(f"- 状态: {r['status']}\n")
            f.write(f"- 验证通过脚本: {r['scripts_verified']}\n")
            f.write(f"- 失败脚本: {r['scripts_failed']}\n")
            if r['errors']:
                f.write("- 错误:\n")
                for err in r['errors']:
                    f.write(f"  - {err}\n")
            f.write("\n")
    
    log(f"详细报告已保存: {report_path}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())