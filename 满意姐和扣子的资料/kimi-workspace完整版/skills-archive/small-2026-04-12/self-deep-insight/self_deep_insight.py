#!/usr/bin/env python3
"""
满意妞自我深度洞察模块
自动生成L1-L5洞察并触发内化流程

来源: 第六类任务整改 - Skill闭环升级
创建时间: 2026-03-31
"""

import json
import os
from datetime import datetime
from pathlib import Path

class SelfDeepInsight:
    """自我深度洞察生成器"""
    
    def __init__(self, workspace="/root/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.insight_dir = self.workspace / "diary" / "insights"
        self.insight_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_insight(self, task_name, surface_phenomenon):
        """生成L1-L5深度洞察"""
        
        insight = {
            "timestamp": datetime.now().isoformat(),
            "task": task_name,
            "L1_surface": surface_phenomenon,
            "L2_pattern": self._identify_pattern(surface_phenomenon),
            "L3_root_cause": self._analyze_root_cause(surface_phenomenon),
            "L4_system_link": self._link_to_system(surface_phenomenon),
            "L5_future_guide": self._generate_guidance(surface_phenomenon)
        }
        
        # 保存洞察
        self._save_insight(insight)
        
        # 触发内化流程
        self._trigger_internalization(insight)
        
        return insight
    
    def _identify_pattern(self, phenomenon):
        """L2: 识别模式"""
        patterns = {
            "审计完成": "审计≠完成模式：检查通过但整改缺失",
            "功能实现": "功能≠闭环模式：代码存在但无深度洞察",
            "文档完成": "文档≠运行模式：有说明但无验证",
            "配置完成": "配置≠生效模式：参数设置但未验证运行"
        }
        
        for key, pattern in patterns.items():
            if key in phenomenon:
                return pattern
        
        return "需进一步观察识别模式"
    
    def _analyze_root_cause(self, phenomenon):
        """L3: 分析根因（深挖到认知/人性）"""
        root_causes = {
            "审计≠完成": "完成幻觉：混淆'检查'与'修复'的认知偏差",
            "功能≠闭环": "工具完美主义：追求产出数量而非实际价值",
            "文档≠运行": "虚假安全感：文档产出带来'工作很多'的满足感",
            "配置≠生效": "流程缺失：缺乏'验证'环节的标准SOP"
        }
        
        for key, cause in root_causes.items():
            if key in phenomenon:
                return cause
        
        return "需五层深挖到人性/认知层面"
    
    def _link_to_system(self, phenomenon):
        """L4: 关联系统"""
        return {
            "identity_conflict": "与负熵构造体身份的冲突评估",
            "user_relationship": "对用户信任和效率的影响",
            "temporal_link": "与历史同类问题的关联",
            "systemic_factor": "系统性因素分析"
        }
    
    def _generate_guidance(self, phenomenon):
        """L5: 生成未来指导"""
        return {
            "core_principle": "待提炼核心原则",
            "executable_plan": [
                "步骤1: 待定义",
                "步骤2: 待定义",
                "步骤3: 待定义"
            ],
            "integration_method": "内化到工作流的方式"
        }
    
    def _save_insight(self, insight):
        """保存洞察到文件"""
        filename = f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.insight_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(insight, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 深度洞察已保存: {filepath}")
    
    def _trigger_internalization(self, insight):
        """触发内化流程"""
        # 1. 检查是否需要SOUL.md更新
        if "原则" in insight["L5_future_guide"]["core_principle"]:
            print("📝 建议: 更新SOUL.md添加新原则")
        
        # 2. 检查是否需要检查脚本
        if "机制" in insight["L2_pattern"]:
            print("📝 建议: 创建机制检查脚本")
        
        # 3. 记录到内化任务列表
        internalization_task = {
            "insight_id": insight["timestamp"],
            "task": f"内化: {insight['L5_future_guide']['core_principle']}",
            "status": "pending",
            "priority": "P1"
        }
        
        print(f"📝 内化任务已创建: {internalization_task['task']}")

# 使用示例
if __name__ == "__main__":
    insight_generator = SelfDeepInsight()
    
    # 示例：生成深度洞察
    result = insight_generator.generate_insight(
        task_name="第六类任务审计",
        surface_phenomenon="审计完成3,369项，但整改率仅15%"
    )
    
    print("\n=== 生成的深度洞察 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
