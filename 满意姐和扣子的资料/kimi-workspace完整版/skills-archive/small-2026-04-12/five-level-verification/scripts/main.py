#!/usr/bin/env python3
"""
Five-Level Verification - Main Entry Point
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Five-Level Verification System V5.0",
        epilog="""
Examples:
  # 验证所有层级
  python3 main.py --skill example-skill
  
  # 验证特定层级
  python3 main.py --skill example-skill --level L1
  
  # 生成报告
  python3 main.py --skill example-skill --report
  
  # 对抗测试
  python3 main.py --skill example-skill --adversarial
        """
    )
    parser.add_argument(
        "--skill", 
        required=True, 
        help="要验证的Skill名称"
    )
    parser.add_argument(
        "--level", 
        default="all",
        choices=["L1", "L2", "L3", "L4", "L5", "all"],
        help="验证级别 (默认: all)"
    )
    parser.add_argument(
        "--report", 
        action="store_true",
        help="生成详细报告"
    )
    parser.add_argument(
        "--adversarial",
        action="store_true", 
        help="运行对抗测试 (S7)"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI模式 (非交互式)"
    )
    parser.add_argument(
        "--output",
        default="./reports",
        help="报告输出目录 (默认: ./reports)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 5.0.0"
    )
    
    args = parser.parse_args()
    
    print(f"Five-Level Verification V5.0")
    print(f"Skill: {args.skill}")
    print(f"Level: {args.level}")
    print()
    
    # 导入验证器
    from verify import FiveLevelVerifier
    
    verifier = FiveLevelVerifier(args.skill)
    
    if args.adversarial:
        result = verifier.adversarial_test()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    
    if args.level == "all":
        report = verifier.verify_all()
    else:
        passed, result = getattr(verifier, f"verify_{args.level}")()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        report = {"level": args.level, "passed": passed, "result": result}
    
    # 保存报告
    if args.report or args.ci:
        import json
        import os
        from datetime import datetime
        
        os.makedirs(args.output, exist_ok=True)
        report_path = os.path.join(
            args.output,
            f"{args.skill}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n📝 报告已保存: {report_path}")
    
    # CI退出码
    if args.ci:
        overall = report.get("overall_level", "L0")
        if overall < "L3":
            return 1
    
    return 0


if __name__ == "__main__":
    import json
    sys.exit(main())
