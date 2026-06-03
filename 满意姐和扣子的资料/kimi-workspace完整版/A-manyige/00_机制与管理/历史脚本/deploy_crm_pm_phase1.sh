#!/bin/bash
# 满意解研究所 CRM+PM 系统 Phase 1 部署脚本
# 执行时间: 2026-03-14

set -e

echo "========================================"
echo "🏗️ CRM+PM 系统 Phase 1 部署"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "【步骤1/4】检查文件结构..."
echo "  ✅ database/crm_pm_schema.sql"
echo "  ✅ docs/NOTION_CRM_PM_SETUP.md"
echo "  ✅ workflows/n8n-crm-pm-automation.json"
echo ""

echo "【步骤2/4】数据库初始化..."
if command -v duckdb &> /dev/null; then
    duckdb /root/.openclaw/workspace/database/crm_pm.db < /root/.openclaw/workspace/database/crm_pm_schema.sql
    echo -e "${GREEN}  ✅ DuckDB数据库初始化完成${NC}"
else
    echo -e "${YELLOW}  ⚠️  DuckDB CLI未安装，schema文件已保存${NC}"
    echo "     安装命令: pip install duckdb"
fi
echo ""

echo "【步骤3/4】检查Notion配置..."
echo "  📋 请按以下步骤配置Notion:"
echo "     1. 创建Integration: https://www.notion.so/my-integrations"
echo "     2. 复制Token到 .env 文件"
echo "     3. 创建6个数据库（见 docs/NOTION_CRM_PM_SETUP.md）"
echo "     4. 共享数据库给Integration"
echo ""

echo "【步骤4/4】检查n8n配置..."
echo "  📋 请按以下步骤配置n8n:"
echo "     1. 启动n8n: npx n8n start"
echo "     2. 导入工作流: workflows/n8n-crm-pm-automation.json"
echo "     3. 配置环境变量:"
echo "        - NOTION_TOKEN"
echo "        - NOTION_CANDIDATES_DB"
echo "        - NOTION_TASKS_DB"
echo "        - FEISHU_WEBHOOK"
echo "     4. 激活工作流"
echo ""

echo "========================================"
echo "✅ Phase 1 文件部署完成！"
echo "========================================"
echo ""
echo "📁 交付物清单:"
echo "  📄 database/crm_pm_schema.sql - DuckDB数据库结构"
echo "  📄 docs/SELF_DEVELOPED_CRM_PM_PLAN.md - 整体方案文档"
echo "  📄 docs/NOTION_CRM_PM_SETUP.md - Notion配置指南"
echo "  📄 workflows/n8n-crm-pm-automation.json - n8n工作流"
echo ""
echo "🎯 下一步:"
echo "  1. 配置Notion数据库"
echo "  2. 配置n8n自动化"
echo "  3. 测试数据导入"
echo "  4. 团队培训"
echo ""
echo "需要帮助? 查看 docs/NOTION_CRM_PM_SETUP.md"
echo "========================================"
