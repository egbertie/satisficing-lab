#!/bin/bash
# 3D知识拓扑批量标注脚本
# 命名空间: NGT-TOPO-BATCH-v1.0-FIN-260327

# 配置
BATCH_SIZE=50
TOPOLOGY_DIR="system-v3/topology_3d/annotations"
LOG_FILE="system-v3/topology_3d/batch_progress.log"

# 创建目录
mkdir -p "$TOPOLOGY_DIR"

# 分类定义
KNOWLEDGE_TYPES=("methodology" "implementation" "reference" "template")
EXPERTS=("liu_honglei" "luo_han" "xie_baojian" "xu_sir" "fang_yifeng" "chen_guoxiang" "general")
TEMPORAL=("archived" "active" "evolving" "deprecated")

# 优先级目录（按优先级排序）
PRIORITY_DIRS=(
    "docs"
    "skills"
    "memory"
    "knowledge"
    "A-manyige"
)

# 自动推断知识类型的函数
infer_knowledge_type() {
    local filepath="$1"
    local filename=$(basename "$filepath")
    
    if [[ "$filename" =~ (SKILL|skill) ]]; then
        echo "methodology"
    elif [[ "$filename" =~ (IMPL|implementation|config) ]]; then
        echo "implementation"
    elif [[ "$filename" =~ (INDEX|index|README) ]]; then
        echo "reference"
    else
        echo "reference"
    fi
}

# 自动推断专家的函数
infer_expert() {
    local filepath="$1"
    local content=$(head -100 "$filepath" 2>/dev/null)
    
    if [[ "$content" =~ (黎红雷|儒商|阳明|心学) ]]; then
        echo "liu_honglei"
    elif [[ "$content" =~ (罗汉|数学|软件工程|算法) ]]; then
        echo "luo_han"
    elif [[ "$content" =~ (谢宝剑|深港|战略|地理) ]]; then
        echo "xie_baojian"
    elif [[ "$content" =~ (XU|压力测试|AI|钻木) ]]; then
        echo "xu_sir"
    elif [[ "$content" =~ (方翊沣|脑科学|BCI|神经|睡眠) ]]; then
        echo "fang_yifeng"
    elif [[ "$content" =~ (陈国祥|神经科|能量治疗) ]]; then
        echo "chen_guoxiang"
    else
        echo "general"
    fi
}

# 自动推断时效性的函数
infer_temporal() {
    local filepath="$1"
    local mtime=$(stat -c %Y "$filepath" 2>/dev/null || stat -f %m "$filepath" 2>/dev/null)
    local now=$(date +%s)
    local age_days=$(( (now - mtime) / 86400 ))
    
    if [[ "$filepath" =~ (archive|历史|deprecated) ]]; then
        echo "archived"
    elif [[ "$filepath" =~ (WIP|wip|draft) ]]; then
        echo "evolving"
    elif [ $age_days -gt 180 ]; then
        echo "archived"
    elif [ $age_days -lt 7 ]; then
        echo "active"
    else
        echo "active"
    fi
}

# 生成元数据
generate_metadata() {
    local filepath="$1"
    local filename=$(basename "$filepath")
    local doc_id=$(echo "$filepath" | sha256sum | cut -c1-8)
    
    local topo_x=$(infer_knowledge_type "$filepath")
    local topo_y=$(infer_expert "$filepath")
    local topo_z=$(infer_temporal "$filepath")
    
    cat >> "$TOPOLOGY_DIR/annotations.csv" << EOF
"$doc_id","$filepath","$topo_x","$topo_y","$topo_z"
EOF
}

# 主流程
echo "🚀 Starting 3D Topology Batch Annotation..."
echo "Timestamp: $(date)" > "$LOG_FILE"
echo "Target: All .md files in workspace" >> "$LOG_FILE"

# 初始化CSV
if [ ! -f "$TOPOLOGY_DIR/annotations.csv" ]; then
    echo '"doc_id","filepath","topo_x","topo_y","topo_z"' > "$TOPOLOGY_DIR/annotations.csv"
fi

# 统计
total_processed=0
batch_count=0

# 按优先级处理目录
for dir in "${PRIORITY_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "📁 Processing directory: $dir"
        
        find "$dir" -name "*.md" -type f 2>/dev/null | while read -r file; do
            # 跳过node_modules和.git
            if [[ "$file" == *node_modules* ]] || [[ "$file" == *.git* ]]; then
                continue
            fi
            
            generate_metadata "$file"
            total_processed=$((total_processed + 1))
            
            # 批次日志
            if [ $((total_processed % BATCH_SIZE)) -eq 0 ]; then
                batch_count=$((batch_count + 1))
                echo "✅ Batch $batch_count completed ($total_processed files)" >> "$LOG_FILE"
            fi
        done
    fi
done

echo "✅ Annotation complete!"
echo "Total files processed: $total_processed" >> "$LOG_FILE"
echo "Output: $TOPOLOGY_DIR/annotations.csv"
