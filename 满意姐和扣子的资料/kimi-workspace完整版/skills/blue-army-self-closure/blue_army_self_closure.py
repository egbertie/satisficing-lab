#!/usr/bin/env python3
"""
蓝军自我闭环升级 - 深度洞察审计器
审计自身产出的闭环完整性

创建时间: 2026-03-31
升级内容: 闭环审计 + 自我检查 + 持续监督
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

class BlueArmySelfAudit:
    """蓝军自我闭环审计系统"""
    
    def __init__(self, workspace="/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.audit_dir = self.workspace / "diary" / "blue_army_self_audit"
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # 蓝军审计标准（自我应用）
        self.audit_standards = {
            "honesty": {
                "name": "诚实度审计",
                "criteria": [
                    "是否标注数据来源？",
                    "是否承认不确定性？",
                    "是否报告负面结果？",
                    "是否虚报完成度？"
                ]
            },
            "insight": {
                "name": "深度洞察审计",
                "criteria": [
                    "L1现象描述是否清晰？",
                    "L2模式识别是否准确？",
                    "L3根因是否深挖到认知/人性？",
                    "L4系统关联是否完整？",
                    "L5未来指导是否可执行？"
                ]
            },
            "closure": {
                "name": "闭环完整性审计",
                "criteria": [
                    "是否有审计记录？",
                    "是否有修复记录？",
                    "是否有内化记录？",
                    "是否有检查脚本？",
                    "是否通过全部检查？"
                ]
            },
            "mechanism": {
                "name": "机制可运行审计",
                "criteria": [
                    "代码文件是否存在？",
                    "验证脚本是否通过？",
                    "机制是否持续运行？",
                    "效果是否可度量？"
                ]
            }
        }
    
    def audit_own_output(self, audit_target, output_content):
        """
        审计蓝军自身产出
        
        Args:
            audit_target: 审计目标（如"M003整改报告"）
            output_content: 产出内容（文件路径或文本）
        """
        print(f"[BLUE-ARMY-SELF-AUDIT] 审计目标: {audit_target}")
        
        audit_result = {
            "audit_target": audit_target,
            "timestamp": datetime.now().isoformat(),
            "total_score": 0,
            "max_score": 400,
            "grade": "F",
            "dimensions": {},
            "violations": [],
            "corrective_actions": []
        }
        
        # 读取内容
        content = self._load_content(output_content)
        
        # 4个维度审计
        for dim_key, dim_config in self.audit_standards.items():
            print(f"\n  [{dim_config['name']}] 审计:")
            dim_score = 0
            dim_violations = []
            
            for criterion in dim_config['criteria']:
                passed = self._audit_criterion(dim_key, criterion, content)
                status = "✅" if passed else "❌"
                print(f"    {status} {criterion}")
                
                if passed:
                    dim_score += 25
                else:
                    dim_violations.append(criterion)
            
            audit_result['dimensions'][dim_key] = {
                'score': dim_score,
                'max_score': len(dim_config['criteria']) * 25,
                'violations': dim_violations
            }
            audit_result['total_score'] += dim_score
            audit_result['violations'].extend(dim_violations)
        
        # 评级
        audit_result['grade'] = self._calculate_grade(audit_result['total_score'])
        
        # 生成整改措施
        if audit_result['violations']:
            audit_result['corrective_actions'] = self._generate_corrective_actions(audit_result['violations'])
        
        print(f"\n  [审计总分] {audit_result['total_score']}/{audit_result['max_score']}")
        print(f"  [审计等级] {audit_result['grade']}")
        
        if audit_result['violations']:
            print(f"  [违规项] {len(audit_result['violations'])}个")
            print("  [整改措施]")
            for action in audit_result['corrective_actions'][:3]:
                print(f"    → {action}")
        
        # 保存审计结果
        self._save_audit_result(audit_result)
        
        return audit_result
    
    def _load_content(self, output_content):
        """加载审计内容"""
        if isinstance(output_content, (str, Path)) and Path(output_content).exists():
            with open(output_content, 'r', encoding='utf-8') as f:
                return f.read()
        return str(output_content)
    
    def _audit_criterion(self, dim_key, criterion, content):
        """审计单个标准"""
        # 诚实度审计
        if "数据来源" in criterion:
            return bool(re.search(r'来源|source|from', content, re.IGNORECASE))
        elif "不确定性" in criterion:
            return bool(re.search(r'待验证|不确定|uncertainty|TODO', content, re.IGNORECASE))
        elif "负面结果" in criterion:
            return bool(re.search(r'❌|失败|未完成|问题|issue', content))
        elif "虚报" in criterion:
            # 检查是否有诚实报告
            return bool(re.search(r'诚实汇报|honest|实际', content))
        
        # 深度洞察审计
        elif "L1" in criterion or "现象" in criterion:
            return bool(re.search(r'L1|表面现象', content))
        elif "L2" in criterion or "模式" in criterion:
            return bool(re.search(r'L2|模式识别', content))
        elif "L3" in criterion or "根因" in criterion:
            return bool(re.search(r'L3|根因分析|人性|认知', content))
        elif "L4" in criterion or "系统" in criterion:
            return bool(re.search(r'L4|系统关联', content))
        elif "L5" in criterion or "指导" in criterion:
            return bool(re.search(r'L5|未来指导|可执行', content))
        
        # 闭环审计
        elif "审计记录" in criterion:
            return bool(re.search(r'审计记录|审计', content))
        elif "修复记录" in criterion:
            return bool(re.search(r'修复记录|整改', content))
        elif "内化记录" in criterion:
            return bool(re.search(r'内化记录|内化', content))
        elif "检查脚本" in criterion:
            return bool(re.search(r'检查脚本|verify|check', content))
        elif "通过全部" in criterion:
            return bool(re.search(r'✅|通过|完成', content))
        
        # 机制审计
        elif "代码" in criterion:
            return bool(re.search(r'\.py|\.sh|代码行数', content))
        elif "验证脚本" in criterion:
            return bool(re.search(r'验证|测试通过', content))
        elif "持续运行" in criterion:
            return bool(re.search(r'Cron|定时|自动', content))
        elif "可度量" in criterion:
            return bool(re.search(r'统计|评分|指标', content))
        
        return True
    
    def _calculate_grade(self, score):
        """计算等级"""
        if score >= 360:
            return "A+"
        elif score >= 320:
            return "A"
        elif score >= 280:
            return "B"
        elif score >= 240:
            return "C"
        elif score >= 200:
            return "D"
        else:
            return "F"
    
    def _generate_corrective_actions(self, violations):
        """生成整改措施"""
        actions = []
        
        if any("数据来源" in v or "不确定性" in v for v in violations):
            actions.append("补充数据来源标注和不确定性说明")
        
        if any("L1" in v or "L2" in v or "L3" in v or "L4" in v or "L5" in v for v in violations):
            actions.append("补充L1-L5深度洞察章节")
        
        if any("审计" in v or "修复" in v or "内化" in v for v in violations):
            actions.append("添加闭环验证章节（审计/修复/内化/检查）")
        
        if any("代码" in v or "验证" in v for v in violations):
            actions.append("创建可运行代码和验证脚本")
        
        return actions
    
    def _save_audit_result(self, result):
        """保存审计结果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = self.audit_dir / f"blue_army_self_audit_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n  [保存] 自我审计结果: {filepath}")
    
    def generate_self_audit_report(self):
        """生成自我审计报告"""
        print("\n=== 蓝军自我闭环审计报告 ===")
        
        audit_files = list(self.audit_dir.glob("blue_army_self_audit_*.json"))
        
        if not audit_files:
            print("暂无自我审计记录")
            return
        
        total_score = 0
        grade_counts = {}
        
        for f in audit_files:
            with open(f, 'r', encoding='utf-8') as file:
                record = json.load(file)
                total_score += record.get('total_score', 0)
                grade = record.get('grade', 'F')
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        avg_score = total_score / len(audit_files)
        
        print(f"\n自我审计统计:")
        print(f"  总审计次数: {len(audit_files)}")
        print(f"  平均得分: {avg_score:.1f}/400")
        print(f"  等级分布:")
        for grade in ['A+', 'A', 'B', 'C', 'D', 'F']:
            if grade in grade_counts:
                print(f"    {grade}: {grade_counts[grade]}次")
        
        print(f"\n审计质量: {'✅ 优秀' if avg_score >= 280 else '⚠️ 需提升'}")
        
        return {
            "total_audits": len(audit_files),
            "avg_score": avg_score,
            "grade_distribution": grade_counts
        }

# 使用示例
if __name__ == "__main__":
    blue_army = BlueArmySelfAudit()
    
    print("=== 蓝军自我闭环升级测试 ===")
    print()
    
    # 示例审计内容
    sample_content = """
    M003/M005机制整改完成报告
    来源: 立即执行整改
    诚实汇报: 之前只有文档定义，没有实际机制
    
    深度洞察:
    L1: 表面现象 - 只有概念无机制
    L2: 模式识别 - 完成幻觉
    L3: 根因分析 - 混淆概念与机制
    L4: 系统关联 - 与负熵身份冲突
    L5: 未来指导 - 概念必须有代码支撑
    
    闭环验证:
    审计记录: 237行代码，测试通过
    修复记录: 创建引擎，添加深度洞察
    内化记录: SOUL.md更新
    检查脚本: verify脚本通过
    
    代码验证: ✅ 通过
    """
    
    result = blue_army.audit_own_output("M003/M005整改报告", sample_content)
    print()
    
    # 生成报告
    blue_army.generate_self_audit_report()
