#!/usr/bin/env python3
"""
emergence_matching_system.py
涌现匹配算法实施系统 V1.0
基于《涌现匹配算法实施手册_V1.0》的简化可运行实现

功能:
- 数据挖掘模块（零成本）：结构化信息收集模板
- 社交图谱模块（低成本）：共同联系人分析与可信度评估
- 互动观察模块（无感）：自然场景行为观察清单
- 整合评估框架：三模块信息整合、权重分配、报告生成
- 伦理边界：内置合规检查与禁止行为清单
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from defense_base_components import BaseComponent
from report_template_system import FileProcessingReport


class EmergenceMatchingSystem(BaseComponent):
    """涌现匹配算法实施系统"""
    
    # 伦理禁止行为清单
    ETHICS_FORBIDDEN = [
        "使用生物识别设备进行被动监控",
        "侵入候选人的私人通讯或社交账号",
        "通过欺骗手段获取非公开信息",
        "对候选人进行人格羞辱或恐惧诱导",
        "将收集信息用于合伙人匹配之外的目的",
        "在候选人明确反对后继续进行信息收集",
        "向第三方泄露评估过程中获取的敏感信息",
    ]
    
    # 默认权重配置（可按场景覆写）
    DEFAULT_WEIGHTS = {
        "data_mining": 0.35,      # 模块一：数据挖掘
        "social_graph": 0.30,     # 模块二：社交图谱
        "interaction": 0.35,      # 模块三：互动观察
    }
    
    def __init__(self, candidate_name: str = "", role_type: str = "技术合伙人"):
        super().__init__("emergence_matching_system")
        self.candidate_name = candidate_name
        self.role_type = role_type
        self.evaluation_data = {
            "candidate_name": candidate_name,
            "role_type": role_type,
            "eval_time": datetime.now().isoformat(),
            "ethics_check": {},
            "module_1_data_mining": {},
            "module_2_social_graph": {},
            "module_3_interaction": {},
            "integration": {},
        }
        self.weights = dict(self.DEFAULT_WEIGHTS)
        
    def run_ethics_check(self) -> Dict[str, Any]:
        """伦理边界自检（S6）—— 修复版：从无条件通过改为强制确认+行为扫描"""
        result = {
            "passed": False,
            "violations": [],
            "recommendations": [],
            "reviewed": False,
        }
        
        ethics_input = self.evaluation_data.get("ethics_check", {})
        
        # 1. 强制确认：必须由人工显式标记已审核
        if not ethics_input.get("explicitly_reviewed", False):
            result["violations"].append("未进行人工伦理审核：必须显式确认已阅读 ETHICS_FORBIDDEN 清单")
            result["recommendations"].append("调用 mark_ethics_reviewed() 或在外部工作流中由用户勾选确认")
            return result
        
        # 2. 扫描计划行为/观察行为中是否包含禁止项
        planned = ethics_input.get("planned_actions", [])
        observed = ethics_input.get("observed_behaviors", [])
        all_actions = planned + observed
        
        for forbidden in self.ETHICS_FORBIDDEN:
            for action in all_actions:
                if forbidden in action or any(kw in action for kw in forbidden.split("或")):
                    result["violations"].append(f"检测到禁止行为: {forbidden} → 涉及动作: {action}")
        
        # 3. 高风险行为组合检查
        if len(planned) > 5 and not ethics_input.get("legal_reviewed", False):
            result["violations"].append("信息收集动作超过5项且无法律顾问预审，判定为不合规")
        
        # 4. 最终判定
        result["reviewed"] = True
        if not result["violations"]:
            result["passed"] = True
        else:
            result["recommendations"].append("请移除或修改上述违规动作后重新提交伦理审核")
        
        return result
    
    def mark_ethics_reviewed(self, planned_actions: List[str] = None, 
                             observed_behaviors: List[str] = None,
                             legal_reviewed: bool = False) -> Dict[str, Any]:
        """显式标记伦理检查输入数据"""
        self.evaluation_data["ethics_check"] = {
            "explicitly_reviewed": True,
            "planned_actions": planned_actions or [],
            "observed_behaviors": observed_behaviors or [],
            "legal_reviewed": legal_reviewed,
            "reviewed_at": datetime.now().isoformat(),
        }
        return self.run_ethics_check()
    
    def build_module_1_template(self) -> Dict[str, Any]:
        """模块一：数据挖掘（零成本）结构化模板"""
        return {
            "职业社交平台": {
                "平台": ["LinkedIn", "脉脉", "GitHub", "其他"],
                "职业轨迹": {
                    "晋升速度": "评分(1-5) + 证据摘要",
                    "任期稳定性": "平均任期(月) / 是否有频繁跳槽(5年>3家)",
                    "创业经历": "创始人/早期员工/普通员工 + 成果验证",
                    "风险标记": "履历断档(>6月) / 职位跳跃 / 公司边界模糊",
                },
                "技能图谱": {
                    "核心技能": "列表",
                    "技能-职位匹配度": "高/中/低 + 说明",
                    "背书质量": "互惠性背书占比评估",
                },
            },
            "学术与知识产权": {
                "论文": {
                    "检索渠道": ["Google Scholar", "知网", "arXiv", "DBLP"],
                    "数量": "int",
                    "H指数": "float",
                    "一作比例": "float",
                    "顶会/顶刊": "列表",
                    "领域聚焦度": "评分(1-5)",
                },
                "专利": {
                    "发明人排序": "第一/第二/其他",
                    "技术领域IPC": "列表",
                    "法律状态": "授权/审查中/驳回",
                    "维持状态": "按时缴费/放弃",
                },
                "技术深度综合": "学术产出-产业转化度评分(1-5)",
            },
            "社交媒体观察": {
                "话题偏好": "专业领域占比(%)",
                "表达风格": "理性论证 / 情绪宣泄 / 建设性取向",
                "互动模式": "回应质疑方式 / 处理异议方式 / 冲突升级/降级",
                "价值观信号": {
                    "诚信": "承诺-行动一致性 / 错误承认 / 信息来源标注",
                    "责任": "团队归因 vs 个人归因 / 长期主义表述",
                    "利益观": "双赢表述 vs 零和表述 / 资源分配讨论",
                },
                "风险内容": "极端言论 / 利益冲突 / 诚信质疑 / 法律纠纷",
            },
            "公开演讲与采访": {
                "结构化思维": "评分(1-5)",
                "临场反应": "评分(1-5)",
                "受众适配": "评分(1-5)",
                "行业洞察": "预测前瞻性与准确性",
                "案例储备": "丰富度与细节真实性",
            },
        }
    
    def build_module_2_template(self) -> Dict[str, Any]:
        """模块二：社交图谱（低成本）结构化模板"""
        return {
            "共同联系人清单": [
                {
                    "姓名": "str",
                    "关系强度": "强(一级) / 情境(二级) / 弱(三级)",
                    "信息价值": "高/中/低",
                    "可信度": "评分(1-5)",
                    "侧面了解摘要": "str",
                    "交叉验证状态": "已验证 / 待验证",
                }
            ],
            "社交圈结构": {
                " industry_focus": "行业集中度评估",
                "hierarchy_distribution": "层级分布（高管/中层/执行/创业者）",
                "geographic_coverage": "地域覆盖",
                "connection_diversity": "连接多样性评分(1-5)",
            },
            "社交圈重叠度": {
                "共同联系人数量": "int",
                "关系路径长度": "平均几度连接",
                "网络密度": "高/中/低",
                "信任传递效率": "评分(1-5)",
            },
        }
    
    def build_module_3_template(self) -> Dict[str, Any]:
        """模块三：互动观察（无感）结构化模板"""
        scenes = ["行业活动", "共同朋友聚会", "工作场景自然接触"]
        observations = {
            "对待服务人员态度": {"评分": "1-5", "证据": "str"},
            "时间观念": {"评分": "1-5", "证据": "str"},
            "对待异议反应": {"评分": "1-5", "证据": "str"},
            "压力下表现": {"评分": "1-5", "证据": "str"},
        }
        return {
            "观察场景": {s: dict(observations) for s in scenes},
            "隐蔽记录": {
                "记录方式": "事后即时笔记（不现场使用设备）",
                "整理周期": "24小时内完成结构化整理",
                "长期跟踪": "关键行为时间线",
            },
        }
    
    def build_integration_framework(self) -> Dict[str, Any]:
        """整合评估框架（模块五）"""
        return {
            "预测维度映射": {
                "价值观兼容性": ["社交媒体价值观", "社交圈结构", "对待异议反应"],
                "认知互补性": ["职业轨迹", "学术产出", "技术深度", "结构化思维"],
                "关系修复力": ["互动模式", "压力下表现", "关系修复观察"],
                "长期承诺度": ["创业经历", "长期主义表述", "错误处理方式"],
            },
            "矛盾信息处理流程": [
                "标记矛盾来源与具体信息",
                "评估各来源可信度（独立来源优先）",
                "寻找第三方验证",
                "备注不确定项并建议补充观察",
            ],
            "权重规则": dict(self.weights),
        }
    
    def generate_blank_form(self) -> Dict[str, Any]:
        """生成空白评估表（供人工填写）"""
        return {
            "meta": {
                "candidate_name": self.candidate_name,
                "role_type": self.role_type,
                "evaluator": "",
                "start_date": "",
                "version": "1.0",
            },
            "ethics_check": {item: False for item in self.ETHICS_FORBIDDEN},
            "module_1": self.build_module_1_template(),
            "module_2": self.build_module_2_template(),
            "module_3": self.build_module_3_template(),
            "integration": self.build_integration_framework(),
        }
    
    def compute_score(self, filled_form: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于填写的表单计算整合得分（简化版）
        实际场景：各维度由评估者填写1-5分后聚合
        """
        # 这里仅做框架演示，真实评分需要人工输入后调用
        return {
            "overall_score": None,
            "module_scores": {},
            "dimension_scores": {},
            "notes": "请人工完成各模块评分后，调用 compute_score_from_ratings()",
        }
    
    def compute_score_from_ratings(
        self,
        module_1_rating: float,
        module_2_rating: float,
        module_3_rating: float,
    ) -> Dict[str, Any]:
        """基于三模块评分计算总评"""
        overall = (
            module_1_rating * self.weights["data_mining"] +
            module_2_rating * self.weights["social_graph"] +
            module_3_rating * self.weights["interaction"]
        )
        recommendation = ""
        if overall >= 4.0:
            recommendation = "推荐深入接触"
        elif overall >= 3.0:
            recommendation = "有条件推荐，需补充特定维度观察"
        elif overall >= 2.0:
            recommendation = "谨慎考虑，存在明显风险信号"
        else:
            recommendation = "不建议继续"
        
        return {
            "overall_score": round(overall, 2),
            "module_scores": {
                "data_mining": module_1_rating,
                "social_graph": module_2_rating,
                "interaction": module_3_rating,
            },
            "weights": dict(self.weights),
            "recommendation": recommendation,
        }
    
    @staticmethod
    def safe_filename(name: str, prefix: str = "") -> str:
        """安全文件名转换：清理跨平台非法字符，保留中文但避免路径注入"""
        import re
        if not name or not name.strip():
            safe = "draft"
        else:
            raw = name.strip()
            # 只移除真正的文件系统非法字符（Windows + Unix 交集）和控制字符
            safe = re.sub(r'[\\/:*?"<>|\x00-\x1f]', '_', raw)
            safe = re.sub(r'_+', '_', safe)
            safe = safe.strip('_. ')
            if not safe:
                safe = "draft"
        if prefix:
            return f"{prefix}-{safe}"
        return safe

    def generate_report(self, filled_form: Dict[str, Any] = None) -> str:
        """生成 Markdown 评估报告"""
        if filled_form is None:
            filled_form = self.generate_blank_form()
        
        lines = []
        lines.append("# 涌现匹配算法评估报告")
        lines.append(f"**候选人**: {self.candidate_name or '(待填写)'}")
        lines.append(f"**目标角色**: {self.role_type}")
        lines.append(f"**评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        lines.append("## 一、伦理合规确认")
        lines.append("以下禁止行为清单已确认不存在：")
        for item in self.ETHICS_FORBIDDEN:
            lines.append(f"- [ ] {item}")
        lines.append("")
        lines.append("## 二、模块一：数据挖掘（零成本）")
        lines.append("```json")
        lines.append(json.dumps(filled_form.get("module_1", {}), ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")
        lines.append("## 三、模块二：社交图谱（低成本）")
        lines.append("```json")
        lines.append(json.dumps(filled_form.get("module_2", {}), ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")
        lines.append("## 四、模块三：互动观察（无感）")
        lines.append("```json")
        lines.append(json.dumps(filled_form.get("module_3", {}), ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")
        lines.append("## 五、整合评估")
        lines.append("```json")
        lines.append(json.dumps(filled_form.get("integration", {}), ensure_ascii=False, indent=2))
        lines.append("```")
        
        report_path = Path(self.workspace) / "memory" / f"{self.safe_filename(self.candidate_name, prefix='emergence-matching-report')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(report_path)
    
    def run_full_pipeline(self, candidate_name: str = "", role_type: str = "") -> str:
        """完整评估流水线入口"""
        if candidate_name:
            self.candidate_name = candidate_name
        if role_type:
            self.role_type = role_type
        
        self.evaluation_data["ethics_check"] = self.run_ethics_check()
        form = self.generate_blank_form()
        report_path = self.generate_report(form)
        return report_path


def main():
    """命令行入口"""
    import argparse
    parser = argparse.ArgumentParser(description="涌现匹配算法实施系统")
    parser.add_argument("--candidate", default="", help="候选人姓名")
    parser.add_argument("--role", default="技术合伙人", help="目标角色类型")
    parser.add_argument("--output-form", action="store_true", help="输出空白评估表JSON")
    parser.add_argument("--report", action="store_true", help="生成评估报告")
    args = parser.parse_args()
    
    system = EmergenceMatchingSystem(candidate_name=args.candidate, role_type=args.role)
    
    if args.output_form:
        form = system.generate_blank_form()
        print(json.dumps(form, ensure_ascii=False, indent=2))
    elif args.report:
        path = system.run_full_pipeline()
        print(f"评估报告已生成: {path}")
    else:
        path = system.run_full_pipeline()
        print(f"空白评估表与报告已生成: {path}")


if __name__ == "__main__":
    main()
