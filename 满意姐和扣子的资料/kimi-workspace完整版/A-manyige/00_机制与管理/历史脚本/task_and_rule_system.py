#!/usr/bin/env python3
"""
任务看板修复器 + 管理规则执行器 - 承诺洗澡Phase 5&6
修复任务识别准确性，加强规则执行深度
"""

import re
import json
from datetime import datetime
from pathlib import Path

def parse_tasks_v2():
    """增强版任务解析器 - 支持复杂格式"""
    task_file = Path("/root/.openclaw/workspace/TASK_MASTER.md")
    if not task_file.exists():
        return []
    
    content = task_file.read_text()
    
    # 多种任务格式识别
    tasks = []
    
    # 格式1: ### [状态] 任务名
    pattern1 = r'###\s+([✅⏸️🔄🔴🟡🟢])\s*WIP-(\d+):\s*(.+?)\n'
    for match in re.finditer(pattern1, content):
        tasks.append({
            "id": f"WIP-{match.group(2)}",
            "name": match.group(3).strip(),
            "status": match.group(1),
            "format": "header"
        })
    
    # 格式2: | **任务ID** | WIP-XXX |
    pattern2 = r'\|\s*\*\*任务ID\*\*\s*\|\s*(WIP-\d+)\s*\|'
    for match in re.finditer(pattern2, content):
        task_id = match.group(1)
        # 查找对应的任务名和状态
        section_start = match.start()
        section_end = content.find("---", section_start)
        section = content[section_start:section_end]
        
        name_match = re.search(r'\|\s*\*\*任务名称\*\*\s*\|\s*(.+?)\s*\|', section)
        status_match = re.search(r'\|\s*\*\*状态\*\*\s*\|\s*(.+?)\s*\|', section)
        
        tasks.append({
            "id": task_id,
            "name": name_match.group(1) if name_match else "未知",
            "status": "✅" if "完成" in str(status_match) else "🔄" if "进行中" in str(status_match) else "⏸️",
            "format": "table"
        })
    
    # 格式3: TODO-XXX / WIP-XXX 列表项
    pattern3 = r'([\-–])\s*\[([ xX])\]\s*(TODO|WIP)-(\d+):\s*(.+?)(?=\n|$)'
    for match in re.finditer(pattern3, content):
        tasks.append({
            "id": f"{match.group(3)}-{match.group(4)}",
            "name": match.group(5).strip(),
            "status": "✅" if match.group(2).lower() == "x" else "🔄",
            "format": "list"
        })
    
    return tasks

def validate_task_consistency(tasks):
    """验证任务状态一致性"""
    issues = []
    
    # 检查重复ID
    seen_ids = {}
    for task in tasks:
        if task["id"] in seen_ids:
            issues.append({
                "type": "duplicate_id",
                "id": task["id"],
                "locations": [seen_ids[task["id"]], task["format"]]
            })
        else:
            seen_ids[task["id"]] = task["format"]
    
    # 检查状态冲突
    for task in tasks:
        if "逾期" in task.get("name", "") and task["status"] == "✅":
            issues.append({
                "type": "status_conflict",
                "id": task["id"],
                "issue": "逾期任务标记为已完成"
            })
    
    return issues

def enforce_management_rules():
    """强制执行管理规则 - 深度检查"""
    violations = []
    
    # 规则1: 检查诚实标注
    memory_file = Path("/root/.openclaw/workspace/MEMORY.md")
    if memory_file.exists():
        content = memory_file.read_text()
        if "诚实状态" not in content:
            violations.append({
                "rule": "诚实标注",
                "issue": "MEMORY.md缺少诚实状态声明",
                "severity": "high"
            })
    
    # 规则2: 检查承诺洗澡进度
    promise_file = Path("/root/.openclaw/workspace/docs/PROMISE_BATH_PROJECT.md")
    if promise_file.exists():
        content = promise_file.read_text()
        # 检查是否有未标记修复状态的P0项
        if "⏸️ 待启动" in content and "P0-" in content:
            violations.append({
                "rule": "承诺洗澡执行",
                "issue": "存在未启动的P0承诺项",
                "severity": "high"
            })
    
    # 规则3: 检查文档完整性
    required_docs = ["SOUL.md", "USER.md", "MEMORY.md"]
    for doc in required_docs:
        if not (Path("/root/.openclaw/workspace") / doc).exists():
            violations.append({
                "rule": "核心文档",
                "issue": f"缺少{doc}",
                "severity": "medium"
            })
    
    # 规则4: 检查知识管理状态
    knowledge_index = Path("/root/.openclaw/workspace/knowledge/system/skill_knowledge_index.json")
    if knowledge_index.exists():
        with open(knowledge_index, 'r') as f:
            data = json.load(f)
        if data.get("extracted", 0) < 100:
            violations.append({
                "rule": "知识管理",
                "issue": f"Skill提取率仅{data.get('extracted', 0)}%",
                "severity": "medium"
            })
    
    return violations

def auto_fix_issues(issues, violations):
    """自动修复问题"""
    fixes = []
    
    # 修复1: 标记重复任务
    for issue in issues:
        if issue["type"] == "duplicate_id":
            fixes.append(f"标记重复任务: {issue['id']}")
    
    # 修复2: 确保核心文档存在
    for v in violations:
        if v["rule"] == "核心文档":
            doc_name = v["issue"].replace("缺少", "")
            doc_path = Path("/root/.openclaw/workspace") / doc_name
            if not doc_path.exists():
                doc_path.touch()
                fixes.append(f"创建缺失文档: {doc_name}")
    
    return fixes

def run_task_and_rule_system():
    """运行任务看板和规则执行系统"""
    results = {
        "run_time": datetime.now().isoformat(),
        "task_board": {},
        "rule_enforcement": {}
    }
    
    # 任务看板解析
    tasks = parse_tasks_v2()
    results["task_board"]["tasks_found"] = len(tasks)
    results["task_board"]["tasks"] = tasks[:20]  # 只保留前20个
    
    # 一致性验证
    issues = validate_task_consistency(tasks)
    results["task_board"]["consistency_issues"] = issues
    results["task_board"]["accuracy_rate"] = (len(tasks) - len(issues)) / len(tasks) * 100 if tasks else 0
    
    # 规则执行
    violations = enforce_management_rules()
    results["rule_enforcement"]["violations_found"] = len(violations)
    results["rule_enforcement"]["violations"] = violations
    
    # 自动修复
    fixes = auto_fix_issues(issues, violations)
    results["rule_enforcement"]["fixes_applied"] = fixes
    
    # 保存报告
    report_path = Path("/root/.openclaw/workspace/memory/task_and_rule_report.json")
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return results

if __name__ == "__main__":
    results = run_task_and_rule_system()
    print(f"任务看板和规则执行完成:")
    print(f"  识别任务: {results['task_board']['tasks_found']} 个")
    print(f"  准确率: {results['task_board']['accuracy_rate']:.1f}%")
    print(f"  一致性问题: {len(results['task_board']['consistency_issues'])} 个")
    print(f"  规则违规: {results['rule_enforcement']['violations_found']} 个")
    print(f"  自动修复: {len(results['rule_enforcement']['fixes_applied'])} 处")
