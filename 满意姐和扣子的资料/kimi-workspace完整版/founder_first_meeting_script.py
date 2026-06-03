#!/usr/bin/env python3
"""
founder_first_meeting_script.py
创始人初始见面话术脚本 V1.0
基于《创始人的初始见面话术V0.5-反方质疑》

功能:
- 生成第一次见面时的破冰话术与价值观探测问题
- 提供反方质疑应对模板
- 根据会面阶段（破冰/需求探测/价值传递/异议处理）输出脚本
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent


class FounderFirstMeetingScript(BaseComponent):
    """创始人初始见面话术脚本"""

    SCRIPTS = {
        "破冰": {
            "开场白": "我花了22年，从银行做到创业，最深的体会是：选对合伙人，比做对产品更重要。",
            "过渡": "今天不着急谈方案，我想先听听你的故事。",
        },
        "需求探测": {
            "价值观探测": "如果项目赚到第一桶金，你和合伙人最想做的第一件事是什么？",
            "风险探测": "你们之间有没有过'差点吵翻'的时刻？最后是怎么过去的？",
            "决策探测": "当信息不全、必须拍板时，你们是怎么做决定的？",
        },
        "价值传递": {
            "核心主张": "我们不帮你找'技能互补'的人，我们帮你找'能一起走十年'的人。",
            "差异点": "五路图腾评估的不只是能力，更是价值观、成长节奏、压力反应的深层兼容。",
        },
        "异议处理": {
            "太贵": "合伙人翻车的成本，通常是服务费的100倍以上。",
            "不需要": "很多创始人也说'我们的关系很好'，但80%的冲突是在第二年爆发的。",
            "时机不对": "最好的时机，恰恰是你们还没有签协议的时候。",
        },
    }

    def __init__(self):
        super().__init__("founder_first_meeting_script")

    def get_script(self, stage: str) -> Dict[str, Any]:
        return self.SCRIPTS.get(stage, {"错误": "未知阶段"})

    def generate_full_script(self) -> str:
        lines = [
            "# 创始人初始见面话术脚本",
            f"**版本**: V0.5 | **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
        ]
        for stage, content in self.SCRIPTS.items():
            lines.append(f"## {stage}阶段")
            for k, v in content.items():
                lines.append(f"- **{k}**：{v}")
            lines.append("")
        return "\n".join(lines)

    def generate_report(self) -> str:
        script = self.generate_full_script()
        report_path = Path(self.workspace) / "memory" / f"first-meeting-script-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(script)
        return str(report_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="创始人初始见面话术脚本")
    parser.add_argument("--report", action="store_true", help="生成话术脚本")
    args = parser.parse_args()

    script_gen = FounderFirstMeetingScript()
    path = script_gen.generate_report()
    print(f"见面话术脚本已生成: {path}")


if __name__ == "__main__":
    main()
