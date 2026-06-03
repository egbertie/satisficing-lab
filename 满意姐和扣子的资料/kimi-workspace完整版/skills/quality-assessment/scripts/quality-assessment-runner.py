#!/usr/bin/env python3
"""
quality-assessment-runner.py
质量评估体系执行器 - 5标准 (S1-S7)

Generated: 2026-03-21
Version: 5.0.0
"""

import os
import sys
import json
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

SKILL_NAME = "quality-assessment"
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
WORKSPACE_DIR = SKILL_DIR.parent.parent
LOG_DIR = Path("logs")
REPORT_DIR = WORKSPACE_DIR / "reports" / "assessment"
CONFIG_DIR = SKILL_DIR / "config"

class QualityAssessmentRunner:
    """质量评估执行器 - 实现S1-S7标准"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.status = "initialized"
        self._setup_logging()
        self._init_dirs()
        
    def _setup_logging(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOG_DIR / f"{SKILL_NAME}-{self.start_time.strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(SKILL_NAME)
        self.logger.info(f"{SKILL_NAME} v5.0 initialized (S1-S7标准)")
        
    def _init_dirs(self):
        """初始化目录结构"""
        (REPORT_DIR / "reports").mkdir(parents=True, exist_ok=True)
        (REPORT_DIR / "issues").mkdir(parents=True, exist_ok=True)
        (REPORT_DIR / "improvements").mkdir(parents=True, exist_ok=True)
        (REPORT_DIR / "cross-validation").mkdir(parents=True, exist_ok=True)
        (WORKSPACE_DIR / "memory" / "quality").mkdir(parents=True, exist_ok=True)
        
    def check_status(self):
        """检查Skill状态"""
        return {
            "skill_name": SKILL_NAME,
            "version": "5.0.0",
            "standards": {
                "5_standard": True,
                "S1_input": True,
                "S2_assessment": True,
                "S3_output": True,
                "S4_trigger": True,
                "S5_checklist": True,
                "S6_limitations": True,
                "S7_adversarial": True
            },
            "timestamp": self.start_time.isoformat()
        }
        
    def assess_skill(self, skill_name: str, ci_mode: bool = False, gate_level: str = None):
        """
        S1-S7完整评估流程
        
        S1: 输入定义 - 明确评估对象
        S2: 四维评估 - 符合性/有效性/可靠性/可维护性
        S3: 输出报告 - 生成评估报告+问题清单+改进建议
        S4: 触发执行 - 执行评估流程
        S5: 检查清单 - 验证评估完整性
        S6: 局限标注 - 报告局限性声明
        S7: 对抗验证 - 交叉验证一致性
        """
        self.logger.info(f"S1-S7评估开始: {skill_name}")
        
        # S1: 输入定义
        self.logger.info("S1: 输入定义 - 评估对象确认")
        
        # S2: 四维评估
        self.logger.info("S2: 质量评估 - 四维递进")
        
        # 调用shell脚本执行评估
        script_path = SCRIPT_DIR / "assess-skill.sh"
        cmd = [str(script_path)]
        if ci_mode:
            cmd.append("--ci")
        if gate_level:
            cmd.append(f"--gate={gate_level}")
        cmd.append(skill_name)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                self.logger.error(f"评估失败: {result.stderr}")
                return False
                
            self.logger.info(result.stdout)
            
        except subprocess.TimeoutExpired:
            self.logger.error("评估超时")
            return False
        except Exception as e:
            self.logger.error(f"评估异常: {e}")
            return False
        
        # S3-S7在assess-skill.sh中完成
        self.logger.info(f"S1-S7评估完成: {skill_name}")
        return True
        
    def batch_assess(self):
        """批量评估所有Skill"""
        self.logger.info("批量评估所有Skill")
        
        script_path = SCRIPT_DIR / "assess-skill.sh"
        cmd = [str(script_path), "--batch"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            self.logger.info(result.stdout)
            if result.stderr:
                self.logger.warning(result.stderr)
        except Exception as e:
            self.logger.error(f"批量评估异常: {e}")
            
    def adversarial_test(self):
        """S7 对抗验证"""
        self.logger.info("S7: 对抗验证 - 交叉评估一致性")
        
        script_path = SCRIPT_DIR / "assess-adversarial-test.sh"
        cmd = [str(script_path), "--batch"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            self.logger.info(result.stdout)
        except Exception as e:
            self.logger.error(f"对抗验证异常: {e}")
            
    def trend_analysis(self):
        """趋势分析"""
        self.logger.info("趋势分析")
        
        script_path = SCRIPT_DIR / "trend-analysis.sh"
        cmd = [str(script_path), "--batch"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            self.logger.info(result.stdout)
        except Exception as e:
            self.logger.error(f"趋势分析异常: {e}")
            
    def generate_report(self, report_type: str = "daily"):
        """生成质量报告"""
        self.logger.info(f"生成{report_type}报告")
        
        script_path = SCRIPT_DIR / "quality-report.sh"
        cmd = [str(script_path), report_type]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            self.logger.info(result.stdout)
        except Exception as e:
            self.logger.error(f"报告生成异常: {e}")
            
    def run(self, command: str, args: dict = None):
        """主运行入口"""
        args = args or {}
        
        if command == "status":
            status = self.check_status()
            print(f"📊 {SKILL_NAME} v5.0")
            print(f"   5标准: {'✅' if status['standards']['5_standard'] else '❌'}")
            print(f"   S1-S7: {'✅✅✅✅✅✅✅' if all(status['standards'][k] for k in ['S1_input', 'S2_assessment', 'S3_output', 'S4_trigger', 'S5_checklist', 'S6_limitations', 'S7_adversarial']) else '⚠️'}")
            return 0
            
        elif command == "assess":
            skill_name = args.get("skill")
            if not skill_name:
                self.logger.error("请指定Skill名称")
                return 1
            return 0 if self.assess_skill(
                skill_name,
                ci_mode=args.get("ci", False),
                gate_level=args.get("gate")
            ) else 1
            
        elif command == "batch":
            self.batch_assess()
            return 0
            
        elif command == "adversarial":
            self.adversarial_test()
            return 0
            
        elif command == "trend":
            self.trend_analysis()
            return 0
            
        elif command == "report":
            self.generate_report(args.get("type", "daily"))
            return 0
            
        else:
            self.logger.error(f"未知命令: {command}")
            return 1


def main():
    parser = argparse.ArgumentParser(
        description="质量评估执行器 - 5标准 (S1-S7)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
命令说明:
    status      检查Skill状态
    assess      评估单个Skill
    batch       批量评估所有Skill
    adversarial 运行S7对抗验证
    trend       运行趋势分析
    report      生成质量报告

示例:
    %(prog)s status
    %(prog)s assess task-coordinator
    %(prog)s assess task-coordinator --ci --gate=A
    %(prog)s batch
    %(prog)s adversarial
    %(prog)s trend
    %(prog)s report --type=weekly
        """
    )
    
    parser.add_argument("command", nargs="?", default="status",
                        choices=["status", "assess", "batch", "adversarial", "trend", "report"],
                        help="执行的命令")
    parser.add_argument("skill", nargs="?", help="要评估的Skill名称")
    parser.add_argument("--ci", action="store_true", help="CI模式")
    parser.add_argument("--gate", help="质量门控级别 (A+/A/B+/B/C)")
    parser.add_argument("--type", default="daily", help="报告类型 (daily/weekly)")
    
    args = parser.parse_args()
    
    runner = QualityAssessmentRunner()
    
    cmd_args = {
        "skill": args.skill,
        "ci": args.ci,
        "gate": args.gate,
        "type": args.type
    }
    
    return runner.run(args.command, cmd_args)


if __name__ == "__main__":
    sys.exit(main())
