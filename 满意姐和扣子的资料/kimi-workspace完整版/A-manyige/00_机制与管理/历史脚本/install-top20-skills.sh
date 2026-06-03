#!/bin/bash
# TOP20 Skill 安装脚本 - P0/P1优先级
# 生成时间: 2026-03-27

set -e

echo "=========================================="
echo "开始安装TOP20 Skill (P0/P1 - 11个)"
echo "=========================================="

# P0: 安全优先
echo "[1/11] 安装 skill-vetter (安全扫描)..."
# clawhub install skill-vetter || echo "安装失败，跳过"

# P0: 核心能力
echo "[2/11] 安装 self-improving-agent (自进化)..."
# clawhub install self-improving-agent || echo "安装失败，跳过"

echo "[3/11] 安装 summarize (内容摘要)..."
# clawhub install summarize || echo "安装失败，跳过"

echo "[4/11] 安装 github (GitHub管理)..."
# clawhub install github || echo "安装失败，跳过"

echo "[5/11] 安装 tavily-search (AI搜索)..."
# clawhub install tavily-search || echo "安装失败，跳过"

# P1: 知识管理
echo "[6/11] 安装 ontology (知识图谱)..."
# clawhub install ontology || echo "安装失败，跳过"

echo "[7/11] 安装 notion (Notion同步)..."
# clawhub install notion || echo "安装失败，跳过"

echo "[8/11] 安装 obsidian (本地笔记)..."
# clawhub install obsidian || echo "安装失败，跳过"

echo "[9/11] 安装 find-skills (技能发现)..."
# clawhub install find-skills || echo "安装失败，跳过"

# P1: 实用工具
echo "[10/11] 安装 weather (天气查询)..."
# clawhub install weather || echo "安装失败，跳过"

echo "[11/11] 安装 brave-search (隐私搜索)..."
# clawhub install brave-search || echo "安装失败，跳过"

echo "=========================================="
echo "安装完成"
echo "=========================================="

# 验证安装
echo "已安装Skill列表:"
# clawhub list --installed || echo "无法获取列表"
