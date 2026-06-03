#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例库录入脚本
功能：交互式录入合伙人案例，自动生成ID，验证必填字段，保存数据
预计录入时间：从30分钟缩短到10分钟
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

# 配置路径
BASE_DIR = Path("/root/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "cases"
INDEX_FILE = DATA_DIR / "index.json"
SCHEMA_FILE = BASE_DIR / "schemas" / "case_schema.json"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 选项定义
INDUSTRIES = ["硬科技", "AI", "生物医药", "新能源", "半导体", "消费", "企业服务", "金融科技", "其他"]
INFO_SOURCES = ["公开报道", "深度访谈", "间接了解", "内部资料"]
CONFIDENTIALITY_LEVELS = ["完全公开", "部分脱敏", "高度敏感"]
ROLES = ["CEO", "CTO", "COO", "CFO", "CMO", "首席科学家", "产品负责人", "技术负责人", "运营负责人", "其他"]
BACKGROUNDS = ["学术", "产业", "连续创业", "跨界", "大厂高管", "投资人"]
RELATIONSHIPS = ["师生", "同学", "前同事", "陌生人", "朋友", "家人", "创业伙伴"]
RESULTS = ["成功", "失败", "进行中", "转型", "收购退出", "IPO"]
TOTEMS = ["虎-权威决策", "豹-敏捷执行", "象-资源整合", "狐-策略博弈", "羊-团队凝聚"]


def get_next_case_id():
    """自动生成下一个案例ID"""
    if not INDEX_FILE.exists():
        return "CASE-021"  # 从021开始，已有20个案例
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    case_ids = index.get("cases", [])
    if not case_ids:
        return "CASE-021"
    
    # 提取最大编号
    max_num = 20
    for case_id in case_ids:
        match = re.match(r'CASE-(\d{3})', case_id)
        if match:
            max_num = max(max_num, int(match.group(1)))
    
    return f"CASE-{max_num + 1:03d}"


def input_required(prompt):
    """必填字段输入"""
    while True:
        value = input(f"{prompt} *: ").strip()
        if value:
            return value
        print("  ⚠️  此字段为必填项，请重新输入")


def input_optional(prompt, default=""):
    """选填字段输入"""
    value = input(f"{prompt}: ").strip()
    return value if value else default


def select_option(prompt, options, multiple=False):
    """选项选择"""
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    
    if multiple:
        print("  (可多选，输入数字用逗号分隔，如：1,3,5；直接回车跳过)")
        while True:
            choice = input("  选择: ").strip()
            if not choice:
                return []
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                selected = [options[i] for i in indices if 0 <= i < len(options)]
                if selected:
                    return selected
            except (ValueError, IndexError):
                pass
            print("  ⚠️  输入无效，请重新选择")
    else:
        print("  (输入数字，直接回车跳过)")
        while True:
            choice = input("  选择: ").strip()
            if not choice:
                return ""
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
            except ValueError:
                pass
            print("  ⚠️  输入无效，请重新选择")


def input_list(prompt, max_items=None, min_items=0):
    """列表输入"""
    print(f"\n{prompt}")
    if max_items:
        print(f"  (最多{max_items}条，直接回车结束)")
    else:
        print("  (逐条输入，直接回车结束)")
    
    items = []
    while True:
        if max_items and len(items) >= max_items:
            break
        item = input(f"  {len(items) + 1}. ").strip()
        if not item:
            break
        items.append(item)
    
    while len(items) < min_items:
        print(f"  ⚠️  至少需要{min_items}条，请继续输入")
        item = input(f"  {len(items) + 1}. ").strip()
        if item:
            items.append(item)
    
    return items


def collect_basic_info():
    """收集基础信息"""
    print("\n" + "="*50)
    print("📋 第一步：基础信息")
    print("="*50)
    
    case_id = get_next_case_id()
    print(f"案例ID（自动生成）: {case_id}")
    
    return {
        "case_id": case_id,
        "case_name": input_required("案例名称"),
        "industry": select_option("行业领域", INDUSTRIES),
        "occurrence_time": input_optional("发生时间（格式：YYYY或YYYY-MM）"),
        "info_source": select_option("信息来源", INFO_SOURCES),
        "confidentiality": select_option("脱敏程度", CONFIDENTIALITY_LEVELS)
    }


def collect_partner_info():
    """收集合伙人信息"""
    print("\n" + "="*50)
    print("👥 第二步：合伙人信息")
    print("="*50)
    
    count_str = input_required("合伙人数量")
    try:
        count = int(count_str)
    except ValueError:
        count = 2
    
    print("\n角色分工：")
    roles = []
    for i in range(count):
        role = select_option(f"合伙人{i+1}的角色", ROLES)
        if role:
            roles.append(role)
    
    return {
        "count": count,
        "relationship_type": select_option("关系类型", RELATIONSHIPS),
        "roles": roles,
        "background_types": select_option("背景类型（可多选）", BACKGROUNDS, multiple=True)
    }


def collect_key_decisions():
    """收集关键决策点"""
    print("\n" + "="*50)
    print("🎯 第三步：关键决策点")
    print("="*50)
    
    print("\n【股权设计】")
    equity = {
        "initial_ratio": input_optional("  初始股权比例（如：50%:50%）"),
        "changes": input_optional("  后续变化")
    }
    
    return {
        "equity_design": equity,
        "tech_route": input_optional("技术路线选择"),
        "financing_decision": input_optional("融资决策"),
        "exit_decision": input_optional("退出/分手决策")
    }


def collect_outcome_analysis():
    """收集成败分析"""
    print("\n" + "="*50)
    print("📊 第四步：成败分析")
    print("="*50)
    
    result = select_option("结果", RESULTS)
    
    print("\n【关键成功因素】")
    success_factors = input_list("请输入（1-3条）", max_items=3)
    
    print("\n【关键失败因素】")
    failure_factors = input_list("请输入（1-3条）", max_items=3)
    
    print("\n【预警信号】")
    warning_signals = input_list("早期可识别的信号")
    
    print("\n【可借鉴的教训】")
    lessons = input_list("请输入")
    
    return {
        "result": result,
        "success_factors": success_factors,
        "failure_factors": failure_factors,
        "warning_signals": warning_signals,
        "lessons": lessons
    }


def collect_satisficing_link():
    """收集与满意解的关联"""
    print("\n" + "="*50)
    print("🔗 第五步：与满意解的关联")
    print("="*50)
    
    totems = select_option("适用的五路图腾（可多选）", TOTEMS, multiple=True)
    
    print("\n【风险预警指标】")
    risk_indicators = input_list("请输入")
    
    print("\n【可用于沙盘模拟的环节】")
    simulation = input_list("请输入")
    
    return {
        "totem_applicable": totems,
        "risk_indicators": risk_indicators,
        "simulation_applicable": simulation
    }


def validate_data(data):
    """验证必填字段"""
    required_fields = ["case_id", "case_name", "industry", "result"]
    errors = []
    
    for field in required_fields:
        if not data.get(field):
            errors.append(f"缺少必填字段: {field}")
    
    return errors


def save_case(data):
    """保存案例到文件"""
    # 添加元数据
    now = datetime.now().isoformat()
    data["metadata"] = {
        "created_at": now,
        "updated_at": now,
        "author": os.getenv("USER", "unknown"),
        "tags": []
    }
    
    # 保存案例文件
    case_file = DATA_DIR / f"{data['case_id']}.json"
    with open(case_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 更新索引
    update_index(data['case_id'], data['case_name'])
    
    return case_file


def update_index(case_id, case_name):
    """更新案例库索引"""
    index = {"cases": [], "last_updated": datetime.now().isoformat()}
    
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index = json.load(f)
    
    # 添加到索引
    case_entry = {"id": case_id, "name": case_name}
    if case_entry not in index["cases"]:
        index["cases"].append(case_entry)
        index["last_updated"] = datetime.now().isoformat()
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def preview_data(data):
    """预览录入的数据"""
    print("\n" + "="*50)
    print("👀 数据预览")
    print("="*50)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    """主函数"""
    print("="*50)
    print("📚 合伙人案例库录入系统")
    print("="*50)
    print(f"预计录入时间: 10分钟（传统方式需30分钟）")
    print("\n提示：带 * 的为必填字段，直接回车可跳过选填项")
    
    # 收集数据
    data = {}
    data.update(collect_basic_info())
    data["partners"] = collect_partner_info()
    data["key_decisions"] = collect_key_decisions()
    data["outcome_analysis"] = collect_outcome_analysis()
    data["satisficing_link"] = collect_satisficing_link()
    
    # 预览
    preview_data(data)
    
    # 验证
    errors = validate_data(data)
    if errors:
        print("\n⚠️ 验证失败:")
        for err in errors:
            print(f"  - {err}")
        return
    
    # 确认保存
    confirm = input("\n确认保存? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 已取消保存")
        return
    
    # 保存
    case_file = save_case(data)
    print(f"\n✅ 案例已保存: {case_file}")
    print(f"📊 案例库当前案例数: {len(json.load(open(INDEX_FILE))['cases'])}")
    print(f"\n🎉 录入完成！预计节省时间: ~20分钟")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断录入")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
