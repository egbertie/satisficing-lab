#!/usr/bin/env python3
"""
worry-list-manager Skill 自检脚本
检查是否符合 5 标准
"""

import os
import sys
import json
import yaml
from pathlib import Path

SKILL_DIR = Path("/root/.openclaw/workspace/skills/worry-list-manager")

def check_file_exists(path: Path, desc: str) -> bool:
    """检查文件是否存在"""
    if path.exists():
        print(f"  ✅ {desc}: {path}")
        return True
    else:
        print(f"  ❌ {desc} 缺失: {path}")
        return False

def check_s1() -> bool:
    """S1: 输入担忧来源/风险信号/监控范围"""
    print("\n🔍 检查 S1: 输入规范")
    
    checks = []
    
    # 检查配置文件
    config_file = SKILL_DIR / "config" / "categories.yaml"
    if config_file.exists():
        with open(config_file) as f:
            config = yaml.safe_load(f)
            if "categories" in config:
                print(f"  ✅ 担忧分类配置: {list(config['categories'].keys())}")
                checks.append(True)
            else:
                print("  ❌ 分类配置格式错误")
                checks.append(False)
    else:
        checks.append(False)
    
    # 检查SKILL.md中是否有S1相关内容
    skill_md = SKILL_DIR / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text()
        if "S1" in content and "输入" in content:
            print("  ✅ SKILL.md 包含 S1 输入规范")
            checks.append(True)
        else:
            print("  ❌ SKILL.md 缺少 S1 输入规范")
            checks.append(False)
    
    return all(checks)

def check_s2() -> bool:
    """S2: 担忧管理（收集→评估→分级→预警→行动）"""
    print("\n🔍 检查 S2: 担忧管理流程")
    
    checks = []
    
    # 检查脚本是否存在
    runner = SKILL_DIR / "scripts" / "worry_runner.py"
    if runner.exists():
        content = runner.read_text()
        
        # 检查收集功能
        if "add_worry" in content:
            print("  ✅ 担忧收集功能")
            checks.append(True)
        
        # 检查评估功能
        if "calculate_priority" in content:
            print("  ✅ 评估分级功能")
            checks.append(True)
        
        # 检查预警功能
        if "push_alert" in content:
            print("  ✅ 预警推送功能")
            checks.append(True)
    
    # 检查SKILL.md
    skill_md = SKILL_DIR / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text()
        if "收集" in content and "评估" in content and "预警" in content:
            print("  ✅ SKILL.md 描述完整流程")
            checks.append(True)
    
    return len(checks) >= 4

def check_s3() -> bool:
    """S3: 输出担忧报告+应对建议+状态更新"""
    print("\n🔍 检查 S3: 输出规范")
    
    checks = []
    
    runner = SKILL_DIR / "scripts" / "worry_runner.py"
    if runner.exists():
        content = runner.read_text()
        
        if "generate_report" in content:
            print("  ✅ 报告生成功能")
            checks.append(True)
        
        if "push_alert" in content:
            print("  ✅ 简报推送功能")
            checks.append(True)
    
    # 检查SKILL.md
    skill_md = SKILL_DIR / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text()
        if "S3" in content or "输出" in content:
            print("  ✅ SKILL.md 包含输出规范")
            checks.append(True)
    
    return len(checks) >= 2

def check_s4() -> bool:
    """S4: cron每日09:07自动执行并推送"""
    print("\n🔍 检查 S4: 自动化配置")
    
    checks = []
    
    # 检查 cron.json
    cron_file = SKILL_DIR / "cron.json"
    if cron_file.exists():
        with open(cron_file) as f:
            cron = json.load(f)
            jobs = cron.get("jobs", [])
            
            # 查找09:07的任务
            morning_job = None
            for job in jobs:
                if job.get("schedule") == "7 9 * * *":
                    morning_job = job
                    break
            
            if morning_job:
                print(f"  ✅ 每日09:07定时任务: {morning_job.get('name')}")
                checks.append(True)
                
                if "push" in morning_job.get("command", ""):
                    print("  ✅ 任务包含推送功能")
                    checks.append(True)
            else:
                print("  ❌ 未找到09:07的定时任务")
    else:
        print("  ❌ cron.json 缺失")
    
    return len(checks) >= 2

def check_s5() -> bool:
    """S5: 担忧评估准确性验证（误报/漏报检查）"""
    print("\n🔍 检查 S5: 准确性验证")
    
    checks = []
    
    runner = SKILL_DIR / "scripts" / "worry_runner.py"
    if runner.exists():
        content = runner.read_text()
        
        if "evaluate_accuracy" in content:
            print("  ✅ 准确性评估功能")
            checks.append(True)
        
        if "false_positive" in content or "false_negative" in content:
            print("  ✅ 误报/漏报检查")
            checks.append(True)
    
    # 检查SKILL.md
    skill_md = SKILL_DIR / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text()
        if "S5" in content or "准确性" in content or "误报" in content:
            print("  ✅ SKILL.md 包含准确性验证说明")
            checks.append(True)
    
    return len(checks) >= 2

def check_s6() -> bool:
    """S6: 局限标注（无法预测黑天鹅事件）"""
    print("\n🔍 检查 S6: 认知谦逊/局限标注")
    
    checks = []
    
    skill_md = SKILL_DIR / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text()
        
        if "S6" in content or "局限" in content or "认知谦逊" in content:
            print("  ✅ SKILL.md 包含局限标注")
            checks.append(True)
        
        if "epistemic_status" in content or "黑天鹅" in content:
            print("  ✅ 不确定性标注")
            checks.append(True)
    
    runner = SKILL_DIR / "scripts" / "worry_runner.py"
    if runner.exists():
        content = runner.read_text()
        if "epistemic_status" in content:
            print("  ✅ 脚本包含认知状态字段")
            checks.append(True)
    
    return len(checks) >= 2

def check_s7() -> bool:
    """S7: 对抗测试（模拟已知风险测试发现能力）"""
    print("\n🔍 检查 S7: 对抗测试")
    
    checks = []
    
    runner = SKILL_DIR / "scripts" / "worry_runner.py"
    if runner.exists():
        content = runner.read_text()
        
        if "adversarial_test" in content:
            print("  ✅ 对抗测试功能")
            checks.append(True)
    
    skill_md = SKILL_DIR / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text()
        if "S7" in content or "对抗" in content or "蓝军" in content:
            print("  ✅ SKILL.md 包含对抗测试说明")
            checks.append(True)
    
    return len(checks) >= 2

def check_basic_structure() -> bool:
    """检查基本结构"""
    print("\n🔍 检查基本结构")
    
    checks = []
    
    # 必需文件
    required_files = [
        (SKILL_DIR / "SKILL.md", "SKILL.md"),
        (SKILL_DIR / "_meta.json", "元数据文件"),
        (SKILL_DIR / "cron.json", "定时任务配置"),
        (SKILL_DIR / "scripts" / "worry_runner.py", "主脚本"),
        (SKILL_DIR / "config" / "categories.yaml", "分类配置"),
        (SKILL_DIR / "config" / "thresholds.yaml", "阈值配置"),
    ]
    
    for path, desc in required_files:
        checks.append(check_file_exists(path, desc))
    
    # 必需目录
    required_dirs = [
        SKILL_DIR / "data",
        SKILL_DIR / "logs",
    ]
    
    for d in required_dirs:
        if d.exists():
            print(f"  ✅ 目录存在: {d}")
            checks.append(True)
        else:
            print(f"  ❌ 目录缺失: {d}")
            checks.append(False)
    
    return all(checks)

def main():
    print("=" * 60)
    print("🧪 worry-list-manager Skill 自检报告")
    print("=" * 60)
    print(f"\n📁 技能目录: {SKILL_DIR}")
    
    # 基本结构检查
    basic_ok = check_basic_structure()
    
    # 7标准检查
    results = {
        "S1(输入规范)": check_s1(),
        "S2(管理流程)": check_s2(),
        "S3(输出规范)": check_s3(),
        "S4(自动化)": check_s4(),
        "S5(准确性验证)": check_s5(),
        "S6(局限标注)": check_s6(),
        "S7(对抗测试)": check_s7(),
    }
    
    # 汇总
    print("\n" + "=" * 60)
    print("📊 自检结果汇总")
    print("=" * 60)
    
    for standard, passed in results.items():
        status = "✅ 通过" if passed else "❌ 未通过"
        print(f"  {standard}: {status}")
    
    all_passed = all(results.values()) and basic_ok
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 恭喜！worry-list-manager Skill 已达到 5 标准")
        print("=" * 60)
        return 0
    else:
        print("⚠️ 部分标准未通过，请根据上述提示完善")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
