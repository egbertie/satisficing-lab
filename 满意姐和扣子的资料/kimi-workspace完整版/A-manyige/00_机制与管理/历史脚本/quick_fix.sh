#!/bin/bash
# 满意解知识管理系统 - 快速修复脚本
# 用于紧急情况下的全局替换

echo "========================================"
echo "🔧 满意解知识管理系统 - 快速修复"
echo "========================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 工作目录
WORKING_DIR="A满意哥专属文件夹/02_✅成果交付"
V2_DIR="A满意哥专属文件夹/99_📦完整下载包/V2.0_技术跃升成果集"

# 检查文件存在
if [ ! -d "$WORKING_DIR" ]; then
    echo -e "${RED}❌ 工作目录不存在: $WORKING_DIR${NC}"
    exit 1
fi

echo ""
echo "请选择修复操作:"
echo "1) 修复CONFUCIUS所有过时表述"
echo "2) 修复专家标注（添加/统一拟邀）"
echo "3) 同步所有文件到V2.0下载包"
echo "4) 运行完整一致性检查"
echo "5) 全部执行（推荐）"
echo ""
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo -e "\n${YELLOW}🔄 修复CONFUCIUS过时表述...${NC}"
        
        # 修复核心精神
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/核心精神.*生生不息/核心精神：仁义礼智信/g' {} \;
        
        # 修复决策维度
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/决策维度.*感知力训练/决策维度：合伙人伦理与信任治理/g' {} \;
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/感知力训练、儒商智慧/合伙人伦理、信任治理/g' {} \;
        
        # 修复名称
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/CONFUCIUS（孔子\/儒商）/CONFUCIUS（孔子）/g' {} \;
        
        # 修复相生关系
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/生木（感知力）——内心平静才能感知敏锐/生木（合伙人伦理）——内心平静才能建立伦理共识/g' {} \;
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/木（感知力）生火（极限测试）——感知敏锐才能在极限中顿悟/木（合伙人伦理）生火（极限测试）——伦理共识才能在极限中验证真实/g' {} \;
        
        # 修复XU先生引用
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/XU先生（木）/CONFUCIUS（木）/g' {} \;
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/"生生不息"精神/"仁义礼智信"精神/g' {} \;
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/钻木取火/内外兼修/g' {} \;
        
        echo -e "${GREEN}✅ CONFUCIUS修复完成${NC}"
        ;;
        
    2)
        echo -e "\n${YELLOW}🔄 修复专家标注...${NC}"
        
        experts=("黎红雷" "罗汉" "谢宝剑" "李泽湘" "方翊沣" "陈国祥")
        
        for expert in "${experts[@]}"; do
            # 添加（拟邀）标注
            find "$WORKING_DIR" -name "*.md" -type f -exec sed -i "s/${expert}教授/${expert}教授（拟邀）/g" {} \;
            find "$WORKING_DIR" -name "*.md" -type f -exec sed -i "s/${expert}研究员/${expert}研究员（拟邀）/g" {} \;
            find "$WORKING_DIR" -name "*.md" -type f -exec sed -i "s/${expert}博士/${expert}博士（拟邀）/g" {} \;
        done
        
        # 去重（防止重复标注）
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/（拟邀）（拟邀）/（拟邀）/g' {} \;
        
        echo -e "${GREEN}✅ 专家标注修复完成${NC}"
        ;;
        
    3)
        echo -e "\n${YELLOW}🔄 同步到V2.0下载包...${NC}"
        
        if [ -d "$V2_DIR" ]; then
            cp "$WORKING_DIR"/满意解研究所_V1.3_完全版本.md "$V2_DIR"/ 2>/dev/null && echo -e "${GREEN}✅ V1.3已同步${NC}"
            cp "$WORKING_DIR"/战略定位1.1版本_满意解研究所.md "$V2_DIR"/ 2>/dev/null && echo -e "${GREEN}✅ 战略定位1.1已同步${NC}"
            cp "$WORKING_DIR"/产品工具手册_V1.0.md "$V2_DIR"/ 2>/dev/null && echo -e "${GREEN}✅ 产品工具手册已同步${NC}"
        else
            echo -e "${RED}❌ V2.0下载包目录不存在${NC}"
        fi
        ;;
        
    4)
        echo -e "\n${YELLOW}🔄 运行一致性检查...${NC}"
        python3 scripts/consistency_check.py
        ;;
        
    5)
        echo -e "\n${YELLOW}🚀 执行全部修复操作...${NC}"
        
        # 1. CONFUCIUS修复
        echo -e "\n${YELLOW}[1/4] 修复CONFUCIUS...${NC}"
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/核心精神.*生生不息/核心精神：仁义礼智信/g' {} \;
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/决策维度.*感知力训练/决策维度：合伙人伦理与信任治理/g' {} \;
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/感知力训练、儒商智慧/合伙人伦理、信任治理/g' {} \;
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/CONFUCIUS（孔子\/儒商）/CONFUCIUS（孔子）/g' {} \;
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/生木（感知力）——内心平静才能感知敏锐/生木（合伙人伦理）——内心平静才能建立伦理共识/g' {} \;
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/木（感知力）生火（极限测试）——感知敏锐才能在极限中顿悟/木（合伙人伦理）生火（极限测试）——伦理共识才能在极限中验证真实/g' {} \;
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/XU先生（木）/CONFUCIUS（木）/g' {} \;
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/"生生不息"精神/"仁义礼智信"精神/g' {} \;
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/钻木取火/内外兼修/g' {} \;
        echo -e "${GREEN}✅ CONFUCIUS修复完成${NC}"
        
        # 2. 专家标注修复
        echo -e "\n${YELLOW}[2/4] 修复专家标注...${NC}"
        experts=("黎红雷" "罗汉" "谢宝剑" "李泽湘" "方翊沣" "陈国祥")
        for expert in "${experts[@]}"; do
            find "$WORKING_DIR" -name "*.md" -type f -exec sed -i "s/${expert}教授/${expert}教授（拟邀）/g" {} \;
            find "$WORKING_DIR" -name "*.md" -type f -exec sed -i "s/${expert}研究员/${expert}研究员（拟邀）/g" {} \;
            find "$WORKING_DIR" -name "*.md" -type f -exec sed -i "s/${expert}博士/${expert}博士（拟邀）/g" {} \;
        done
        find "$WORKING_DIR" -name "*.md" -type f -exec sed -i 's/（拟邀）（拟邀）/（拟邀）/g' {} \;
        echo -e "${GREEN}✅ 专家标注修复完成${NC}"
        
        # 3. 同步到V2.0
        echo -e "\n${YELLOW}[3/4] 同步到V2.0下载包...${NC}"
        if [ -d "$V2_DIR" ]; then
            cp "$WORKING_DIR"/满意解研究所_V1.3_完全版本.md "$V2_DIR"/ 2>/dev/null
            cp "$WORKING_DIR"/战略定位1.1版本_满意解研究所.md "$V2_DIR"/ 2>/dev/null
            cp "$WORKING_DIR"/产品工具手册_V1.0.md "$V2_DIR"/ 2>/dev/null
            echo -e "${GREEN}✅ 文件同步完成${NC}"
        fi
        
        # 4. 运行检查
        echo -e "\n${YELLOW}[4/4] 运行一致性检查...${NC}"
        python3 scripts/consistency_check.py
        
        echo -e "\n${GREEN}🎉 全部修复完成！${NC}"
        ;;
        
    *)
        echo -e "${RED}❌ 无效选项${NC}"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "💡 提示: 修改core/目录后运行:"
echo "   python3 scripts/sync_from_core.py"
echo "========================================"
