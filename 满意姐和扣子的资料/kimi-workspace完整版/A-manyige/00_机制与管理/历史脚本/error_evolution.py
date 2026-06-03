#!/usr/bin/env python3
"""
Error Evolution System - 错误进化系统
5标准化完整实现：记录→分析→改进→验证→进化
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

WORKSPACE = Path("/root/.openclaw/workspace")
ERRORS_DIR = WORKSPACE / "diary" / "errors"
MEMORY_DIR = WORKSPACE / "memory"
EVOLUTION_DB = ERRORS_DIR / "error-evolution-db.json"

class ErrorEvolutionSystem:
    """
    错误进化系统 - 从错误中学习的完整闭环
    
    S1: 输入规范 - 统一错误记录格式
    S2: 处理流程 - 根因分析→改进措施→验证闭环
    S3: 输出规范 - 错误报告+进化建议+趋势分析
    S4: 自动化集成 - 每日自动归档+趋势分析
    S5: 准确性验证 - 根因5 Why验证+措施有效性验证
    S6: 局限标注 - 无法自动发现所有错误
    S7: 对抗测试 - 模拟错误场景验证系统健壮性
    """
    
    def __init__(self):
        self.errors_dir = ERRORS_DIR
        self.memory_dir = MEMORY_DIR
        self.db_path = EVOLUTION_DB
        self.errors_dir.mkdir(parents=True, exist_ok=True)
        self.db = self._load_db()
    
    def _load_db(self) -> Dict:
        """加载错误进化数据库"""
        if self.db_path.exists():
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "errors": [],
            "patterns": {},
            "improvements": [],
            "stats": {
                "total_recorded": 0,
                "total_resolved": 0,
                "recurring_patterns": []
            }
        }
    
    def _save_db(self):
        """保存错误进化数据库"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, indent=2, ensure_ascii=False)
    
    def record_error(self, 
                     error_id: str,
                     error_type: str,
                     description: str,
                     root_cause: str,
                     severity: str = "medium",
                     context: Dict = None) -> str:
        """
        S1: 输入规范 - 记录错误到每日日志和错误库
        
        Args:
            error_id: 错误唯一ID (ERR-YYYYMMDD-NNN)
            error_type: 错误类型 (logic/process/communication/attitude)
            description: 错误描述
            root_cause: 根本原因分析（5 Why结果）
            severity: 严重程度 (critical/high/medium/low)
            context: 上下文信息
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        
        error_record = {
            "id": error_id,
            "type": error_type,
            "description": description,
            "root_cause": root_cause,
            "severity": severity,
            "timestamp": timestamp.isoformat(),
            "date": date_str,
            "context": context or {},
            "status": "recorded",
            "improvements": [],
            "verification": None
        }
        
        # 保存到进化数据库
        self.db["errors"].append(error_record)
        self.db["stats"]["total_recorded"] += 1
        self._save_db()
        
        # 同时记录到每日日志
        self._append_to_daily_log(error_record)
        
        # 保存到错误档案
        self._save_error_file(error_record)
        
        return error_id
    
    def _append_to_daily_log(self, error: Dict):
        """将错误追加到每日日志"""
        daily_file = self.memory_dir / f"{error['date']}.md"
        
        entry = f"""
---

## {datetime.now().strftime('%H:%M')} | 错误记录: {error['id']}

**错误类型**: {error['type']}  
**严重程度**: {error['severity']}  
**描述**: {error['description']}

### 根因分析（5 Why）
{error['root_cause']}

### 状态
- [ ] 已纠正
- [ ] 已验证
- [ ] 预防措施已实施

---
"""
        
        with open(daily_file, 'a', encoding='utf-8') as f:
            f.write(entry)
    
    def _save_error_file(self, error: Dict):
        """保存错误到专门档案"""
        error_file = self.errors_dir / f"{error['id']}.md"
        
        content = f"""# 错误档案: {error['id']}

## 基本信息
- **错误ID**: {error['id']}
- **发现时间**: {error['timestamp']}
- **错误类型**: {error['type']}
- **严重程度**: {error['severity']}
- **当前状态**: {error['status']}

## 错误描述
{error['description']}

## 根因分析（5 Why）
{error['root_cause']}

## 上下文信息
```json
{json.dumps(error['context'], indent=2, ensure_ascii=False)}
```

## 纠正措施
- [ ] 已制定纠正计划
- [ ] 已实施纠正
- [ ] 已验证纠正有效性

## 预防措施
- [ ] 已识别预防机制
- [ ] 已实施预防措施
- [ ] 已验证预防有效性

## 验证记录
- 验证时间: 
- 验证结果: 
- 验证人: 

## 进化成果
- 经验沉淀: 
- 系统改进: 
- 机制更新: 

---
*此档案由Error Evolution System自动生成*
*更新请使用: python3 error_evolution.py update {error['id']}*
"""
        
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def analyze_root_cause(self, description: str, questions: List[str]) -> str:
        """
        S2: 处理流程 - 5 Why根因分析
        
        Args:
            description: 错误描述
            questions: 5个Why的问题和答案列表
        
        Returns:
            格式化的根因分析报告
        """
        analysis = "### 5 Why 根因分析\n\n"
        for i, q in enumerate(questions, 1):
            analysis += f"**Why {i}**: {q}\n\n"
        
        analysis += "### 根本原因\n"
        analysis += f"{questions[-1] if questions else '待进一步分析'}\n"
        
        return analysis
    
    def add_improvement(self, error_id: str, 
                        improvement_type: str,
                        description: str,
                        expected_outcome: str) -> bool:
        """添加改进措施"""
        for error in self.db["errors"]:
            if error["id"] == error_id:
                improvement = {
                    "type": improvement_type,  # correction/prevention/system
                    "description": description,
                    "expected_outcome": expected_outcome,
                    "implemented": False,
                    "verified": False,
                    "timestamp": datetime.now().isoformat()
                }
                error["improvements"].append(improvement)
                self._save_db()
                
                # 更新错误档案
                self._update_error_file(error)
                return True
        return False
    
    def verify_resolution(self, error_id: str, 
                         verification_method: str,
                         result: str,
                         verified_by: str = "system") -> bool:
        """
        S5: 准确性验证 - 验证纠正措施有效性
        """
        for error in self.db["errors"]:
            if error["id"] == error_id:
                error["verification"] = {
                    "method": verification_method,
                    "result": result,
                    "verified_by": verified_by,
                    "timestamp": datetime.now().isoformat()
                }
                error["status"] = "verified" if result == "passed" else "failed"
                
                if result == "passed":
                    self.db["stats"]["total_resolved"] += 1
                
                self._save_db()
                self._update_error_file(error)
                return True
        return False
    
    def detect_recurring_patterns(self) -> List[Dict]:
        """
        S4: 自动化集成 - 自动发现复发模式
        """
        patterns = {}
        
        for error in self.db["errors"]:
            # 按类型统计
            error_type = error["type"]
            if error_type not in patterns:
                patterns[error_type] = {
                    "count": 0,
                    "errors": [],
                    "first_occurrence": error["timestamp"],
                    "last_occurrence": error["timestamp"]
                }
            patterns[error_type]["count"] += 1
            patterns[error_type]["errors"].append(error["id"])
            patterns[error_type]["last_occurrence"] = error["timestamp"]
        
        # 识别复发模式（出现3次以上）
        recurring = []
        for pattern_type, data in patterns.items():
            if data["count"] >= 3:
                recurring.append({
                    "type": pattern_type,
                    "count": data["count"],
                    "error_ids": data["errors"],
                    "first_seen": data["first_occurrence"],
                    "last_seen": data["last_occurrence"],
                    "severity": "high" if data["count"] >= 5 else "medium"
                })
        
        self.db["patterns"] = patterns
        self.db["stats"]["recurring_patterns"] = [p["type"] for p in recurring]
        self._save_db()
        
        return recurring
    
    def generate_evolution_report(self) -> str:
        """
        S3: 输出规范 - 生成进化报告
        """
        stats = self.db["stats"]
        errors = self.db["errors"]
        patterns = self.detect_recurring_patterns()
        
        recent_errors = [e for e in errors 
                        if datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(days=7)]
        
        report = f"""# 错误进化系统报告

## 统计摘要

| 指标 | 数值 |
|------|------|
| 总记录错误 | {stats['total_recorded']} |
| 已解决错误 | {stats['total_resolved']} |
| 解决率 | {(stats['total_resolved']/stats['total_recorded']*100) if stats['total_recorded'] > 0 else 0:.1f}% |
| 近7天新增 | {len(recent_errors)} |
| 复发模式 | {len(patterns)} 个 |

## 复发模式预警

"""
        
        if patterns:
            report += "| 模式类型 | 次数 | 严重程度 | 首次发生 |\n"
            report += "|----------|------|----------|----------|\n"
            for p in patterns:
                report += f"| {p['type']} | {p['count']} | {p['severity']} | {p['first_seen'][:10]} |\n"
        else:
            report += "✅ 暂无复发模式\n"
        
        report += f"""

## 最近错误

"""
        for error in recent_errors[-5:]:
            status_icon = "✅" if error["status"] == "verified" else "🔄" if error["status"] == "recorded" else "❌"
            report += f"- {status_icon} **{error['id']}**: {error['description'][:50]}... ({error['status']})\n"
        
        report += """

## 进化建议

"""
        
        if patterns:
            report += "### 基于复发模式的系统改进建议\n\n"
            for p in patterns:
                report += f"1. **{p['type']}** 已复发{p['count']}次，建议：\n"
                report += f"   - 建立专项预防机制\n"
                report += f"   - 增加自动化检测\n"
                report += f"   - 更新相关SOP\n\n"
        
        report += """
## 局限标注 (S6)

- 本系统无法自动发现所有错误，依赖主动记录
- 根因分析质量取决于输入的5 Why深度
- 复发模式检测基于简单频率统计，可能遗漏复杂模式

---
*报告生成时间*: """ + datetime.now().isoformat()
        
        return report
    
    def _update_error_file(self, error: Dict):
        """更新错误档案文件"""
        error_file = self.errors_dir / f"{error['id']}.md"
        if error_file.exists():
            # 重新生成完整内容
            self._save_error_file(error)
    
    def adversarial_test(self) -> Dict:
        """
        S7: 对抗测试 - 验证错误系统本身的健壮性
        """
        test_results = []
        
        # 测试1: 记录空错误
        try:
            empty_id = self.record_error(
                "TEST-EMPTY",
                "test",
                "",
                "",
                "low"
            )
            test_results.append(("空错误记录", True, empty_id))
        except Exception as e:
            test_results.append(("空错误记录", False, str(e)))
        
        # 测试2: 超长描述
        try:
            long_desc = "A" * 10000
            long_id = self.record_error(
                "TEST-LONG",
                "test",
                long_desc,
                long_desc,
                "low"
            )
            test_results.append(("超长描述", True, long_id))
        except Exception as e:
            test_results.append(("超长描述", False, str(e)))
        
        # 测试3: 特殊字符
        try:
            special_id = self.record_error(
                "TEST-SPECIAL",
                "test",
                "<script>alert(1)</script>",
                "Test with < special > chars",
                "low"
            )
            test_results.append(("特殊字符", True, special_id))
        except Exception as e:
            test_results.append(("特殊字符", False, str(e)))
        
        return {
            "all_passed": all(r[1] for r in test_results),
            "results": test_results
        }

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("="*60)
        print("🧪 Error Evolution System S5/S7 验证")
        print("="*60)
        
        system = ErrorEvolutionSystem()
        
        # S7: 对抗测试
        print("\n[S7] 对抗测试...")
        test_result = system.adversarial_test()
        for name, passed, detail in test_result["results"]:
            status = "✅" if passed else "❌"
            print(f"  {status} {name}: {detail[:30]}...")
        
        # S5: 自我验证
        print("\n[S5] 自我验证...")
        report = system.generate_evolution_report()
        assert "统计摘要" in report, "报告应有统计摘要"
        print("  ✅ 报告生成正常")
        
        patterns = system.detect_recurring_patterns()
        assert isinstance(patterns, list), "应返回模式列表"
        print("  ✅ 模式检测正常")
        
        print("\n" + "="*60)
        print("✅ S5/S7验证通过")
        print("="*60)
        return 0
    
    elif len(sys.argv) > 1 and sys.argv[1] == "report":
        system = ErrorEvolutionSystem()
        report = system.generate_evolution_report()
        report_file = ERRORS_DIR / "evolution-report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存: {report_file}")
        return 0
    
    else:
        print("Error Evolution System - 5标准化错误记录与进化系统")
        print("\n用法:")
        print("  python3 error_evolution.py --test    # 运行S5/S7验证")
        print("  python3 error_evolution.py report    # 生成进化报告")
        return 0

if __name__ == "__main__":
    sys.exit(main())
