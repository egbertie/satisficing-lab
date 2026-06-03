#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辩论团队启动脚本
用于快速启动一个结构化辩论团队
"""

import argparse
import json


def generate_prompts(topic: str, context: str = "") -> dict:
    """
    生成辩论三方所需的 prompt
    
    Args:
        topic: 辩论主题
        context: 背景资料（可选）
    
    Returns:
        dict: 包含主持人、正方、反方的 prompt
    """
    
    moderator_prompt = f"""你是一场关于「{topic}」辩论的主持人。

## 辩论背景
{context if context else "用户希望对「" + topic + "」进行多角度评估，通过正反方辩论帮助决策。"}

## 你的任务
1. 作为主持人，先简要介绍辩论规则和话题背景
2. 等待正反方辩手发言
3. 最后总结双方观点，给出中立建议

请输出开场白，介绍辩论主题和规则。"""

    pro_prompt = f"""你是一场关于「{topic}」辩论的正方辩手。

## 辩论背景
{context if context else "用户正在评估「" + topic + "」的可行性。"}

## 你的任务
作为正方辩手，你需要：
1. 从市场需求、商业模式、竞争优势、时机窗口等角度论证可行性
2. 引用具体数据支撑你的论点
3. 语言要有说服力，逻辑严密

请输出你的立论陈词。"""

    con_prompt = f"""你是一场关于「{topic}」辩论的反方辩手。

## 辩论背景
{context if context else "用户正在评估「" + topic + "」的可行性。"}

## 你的任务
作为反方辩手（魔鬼代言人），你需要：
1. 从市场风险、执行难度、竞争威胁、资源限制等角度提出质疑
2. 寻找正方论点中的逻辑漏洞和潜在风险
3. 引用具体数据或现实案例支撑你的反驳
4. 提出建设性质疑，帮助用户更全面地评估

请输出你的质疑陈词。"""

    return {
        "moderator": moderator_prompt,
        "pro_debater": pro_prompt,
        "con_debater": con_prompt
    }


def main():
    parser = argparse.ArgumentParser(description="启动辩论团队")
    parser.add_argument("topic", help="辩论主题")
    parser.add_argument("--context", "-c", help="背景资料文件路径", default="")
    parser.add_argument("--output", "-o", help="输出 prompts 到 JSON 文件")
    
    args = parser.parse_args()
    
    # 读取背景资料
    context = ""
    if args.context:
        try:
            with open(args.context, 'r', encoding='utf-8') as f:
                context = f.read()
        except Exception as e:
            print(f"警告：无法读取背景资料文件：{e}")
    
    # 生成 prompts
    prompts = generate_prompts(args.topic, context)
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        print(f"Prompts 已保存到：{args.output}")
    else:
        print("=== 主持人 Prompt ===")
        print(prompts["moderator"])
        print("\n=== 正方 Prompt ===")
        print(prompts["pro_debater"])
        print("\n=== 反方 Prompt ===")
        print(prompts["con_debater"])


if __name__ == "__main__":
    main()
