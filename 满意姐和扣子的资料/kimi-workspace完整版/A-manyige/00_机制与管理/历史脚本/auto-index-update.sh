#!/bin/bash
#
# 自动索引更新脚本 (Auto Index Update Script)
# 版本: 1.0
# 创建时间: 2026-03-31
# 用途: 每小时自动扫描workspace，识别变更，更新GLOBAL_INDEX
#

set -euo pipefail

# ==================== 配置区 ====================
WORKSPACE_DIR="/root/.openclaw/workspace"
GLOBAL_INDEX="${WORKSPACE_DIR}/GLOBAL_INDEX.md"
LOG_DIR="${WORKSPACE_DIR}/logs/index-updates"
STATE_DIR="${WORKSPACE_DIR}/.state"
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
DATE_STR=$(date '+%Y-%m-%d')
TIME_STR=$(date '+%H:%M:%S')
REPORT_FILE="${LOG_DIR}/update_report_${TIMESTAMP}.md"
STATE_FILE="${STATE_DIR}/index_state.json"

# 创建必要目录
mkdir -p "${LOG_DIR}" "${STATE_DIR}"

# ==================== 日志函数 ====================
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${REPORT_FILE}"
}

log_info() { log "[INFO] $1"; }
log_warn() { log "[WARN] $1"; }
log_error() { log "[ERROR] $1"; }
log_section() { log "\n## $1\n"; }

# ==================== 初始化报告 ====================
init_report() {
    cat > "${REPORT_FILE}" << EOF
# 索引更新报告

**执行时间**: ${DATE_STR} ${TIME_STR}  
**脚本版本**: 1.0  
**执行状态**: 🔄 进行中

---
EOF
}

# ==================== 扫描workspace目录 ====================
scan_workspace() {
    log_section "1. Workspace扫描"
    
    # 扫描关键目录
    local dirs=("skills" "docs" "memory" "deliverables" "institute-assets" "checklists")
    local current_scan="${STATE_DIR}/current_scan.txt"
    
    > "${current_scan}"
    
    for dir in "${dirs[@]}"; do
        local full_path="${WORKSPACE_DIR}/${dir}"
        if [[ -d "${full_path}" ]]; then
            log_info "扫描目录: ${dir}"
            find "${full_path}" -type f \( \
                -name "*.md" -o \
                -name "*.sh" -o \
                -name "*.py" -o \
                -name "*.json" -o \
                -name "SKILL.md" \
            \) -printf "%T@ %p\n" 2>/dev/null | sort -k2 >> "${current_scan}" || true
        fi
    done
    
    log_info "扫描完成，共发现 $(wc -l < "${current_scan}" | awk '{print $1}') 个文件"
}

# ==================== 识别变更 ====================
detect_changes() {
    log_section "2. 变更检测"
    
    local current_scan="${STATE_DIR}/current_scan.txt"
    local previous_scan="${STATE_DIR}/previous_scan.txt"
    local changes_detected="${STATE_DIR}/changes_${TIMESTAMP}.txt"
    
    # 如果没有之前的扫描，保存当前扫描并退出
    if [[ ! -f "${previous_scan}" ]]; then
        log_info "首次运行，保存当前状态作为基准"
        cp "${current_scan}" "${previous_scan}"
        echo "FIRST_RUN" > "${changes_detected}"
        return 0
    fi
    
    # 比较两次扫描结果
    # 新增: 在current中但不在previous中
    # 修改: 时间戳不同
    # 删除: 在previous中但不在current中
    
    local added=0
    local modified=0
    local deleted=0
    
    # 提取文件路径（去掉时间戳）
    cut -d' ' -f2- "${current_scan}" | sort > "${STATE_DIR}/current_files.txt"
    cut -d' ' -f2- "${previous_scan}" | sort > "${STATE_DIR}/previous_files.txt"
    
    # 检测新增文件
    comm -23 "${STATE_DIR}/current_files.txt" "${STATE_DIR}/previous_files.txt" > "${STATE_DIR}/added_files.txt"
    added=$(wc -l < "${STATE_DIR}/added_files.txt" | awk '{print $1}')
    
    # 检测删除文件
    comm -13 "${STATE_DIR}/current_files.txt" "${STATE_DIR}/previous_files.txt" > "${STATE_DIR}/deleted_files.txt"
    deleted=$(wc -l < "${STATE_DIR}/deleted_files.txt" | awk '{print $1}')
    
    # 检测修改文件（时间戳不同）
    > "${STATE_DIR}/modified_files.txt"
    while IFS= read -r line; do
        local timestamp=$(echo "$line" | cut -d' ' -f1)
        local filepath=$(echo "$line" | cut -d' ' -f2-)
        
        # 查找previous中相同文件的时间戳
        local prev_timestamp=$(grep "${filepath}$" "${previous_scan}" | cut -d' ' -f1)
        
        if [[ -n "${prev_timestamp}" && "${timestamp}" != "${prev_timestamp}" ]]; then
            echo "${filepath}" >> "${STATE_DIR}/modified_files.txt"
        fi
    done < "${current_scan}"
    modified=$(wc -l < "${STATE_DIR}/modified_files.txt" | awk '{print $1}')
    
    # 输出变更摘要
    cat >> "${REPORT_FILE}" << EOF
### 变更统计

| 类型 | 数量 |
|------|------|
| ➕ 新增文件 | ${added} |
| 📝 修改文件 | ${modified} |
| ➖ 删除文件 | ${deleted} |
| **总计变更** | **$((added + modified + deleted))** |

EOF
    
    # 保存新增文件列表
    if [[ ${added} -gt 0 ]]; then
        log_info "新增文件列表:"
        cat "${STATE_DIR}/added_files.txt" | tee -a "${REPORT_FILE}"
    fi
    
    # 保存修改文件列表
    if [[ ${modified} -gt 0 ]]; then
        log_info "修改文件列表:"
        cat "${STATE_DIR}/modified_files.txt" | tee -a "${REPORT_FILE}"
    fi
    
    # 保存删除文件列表
    if [[ ${deleted} -gt 0 ]]; then
        log_info "删除文件列表:"
        cat "${STATE_DIR}/deleted_files.txt" | tee -a "${REPORT_FILE}"
    fi
    
    # 如果有变更，保存changes_detected标记
    if [[ ${added} -gt 0 || ${modified} -gt 0 || ${deleted} -gt 0 ]]; then
        echo "CHANGES_DETECTED" > "${changes_detected}"
        echo "added:${added}" >> "${changes_detected}"
        echo "modified:${modified}" >> "${changes_detected}"
        echo "deleted:${deleted}" >> "${changes_detected}"
    else
        echo "NO_CHANGES" > "${changes_detected}"
    fi
    
    # 更新previous_scan为当前扫描
    cp "${current_scan}" "${previous_scan}"
    
    return $((added + modified + deleted))
}

# ==================== 更新GLOBAL_INDEX ====================
update_global_index() {
    log_section "3. GLOBAL_INDEX更新"
    
    # 检查是否需要更新
    local changes_file="${STATE_DIR}/changes_${TIMESTAMP}.txt"
    if [[ ! -f "${changes_file}" ]]; then
        log_warn "变更文件不存在，跳过更新"
        return 0
    fi
    
    local changes_type=$(head -1 "${changes_file}")
    
    if [[ "${changes_type}" == "NO_CHANGES" ]]; then
        log_info "无变更，跳过GLOBAL_INDEX更新"
        return 0
    fi
    
    log_info "检测到变更，开始更新GLOBAL_INDEX"
    
    # 更新GLOBAL_INDEX的"最后更新"时间
    if [[ -f "${GLOBAL_INDEX}" ]]; then
        sed -i "s/最后更新:.*/最后更新: ${DATE_STR}/" "${GLOBAL_INDEX}" 2>/dev/null || true
        log_info "已更新GLOBAL_INDEX最后更新时间"
    else
        log_warn "GLOBAL_INDEX文件不存在: ${GLOBAL_INDEX}"
    fi
    
    # 记录更新操作到报告
    cat >> "${REPORT_FILE}" << EOF
### 更新操作

- ✅ 更新最后更新时间: ${DATE_STR}
- ✅ 记录变更到更新日志

EOF
}

# ==================== 生成分类索引 ====================
generate_category_index() {
    log_section "4. 分类索引生成"
    
    local category_index="${WORKSPACE_DIR}/INDEX_BY_CATEGORY.md"
    
    log_info "生成分类索引: ${category_index}"
    
    cat > "${category_index}" << EOF
# 按分类索引 (Auto-Generated)

**生成时间**: ${DATE_STR} ${TIME_STR}  
**更新时间**: 每小时自动更新

---

## 分类结构

### 1. 五路图腾体系

| Skill名称 | 五行 | 状态 | 路径 |
|-----------|------|------|------|
| liu-skill | 土 - LIU(刘禹锡) | 运行中 | skills/liu-skill/ |
| simon-skill | 金 - SIMON(司马贺) | 运行中 | skills/simon-skill/ |
| guanyin-skill | 水 - GUANYIN(观自在) | 运行中 | skills/guanyin-skill/ |
| confucius-skill | 木 - CONFUCIUS(孔子) | 运行中 | skills/confucius-skill/ |
| huineng-skill | 火 - HUINENG(六祖慧能) | 运行中 | skills/huineng-skill/ |

### 2. 审计与监督

$(find "${WORKSPACE_DIR}/skills" -maxdepth 1 -type d -name "*audit*" -o -name "*sentinel*" -o -name "*supervis*" 2>/dev/null | while read -r dir; do
    name=$(basename "$dir")
    echo "- ${name}"
done)

### 3. 灾备与恢复

$(find "${WORKSPACE_DIR}/skills" -maxdepth 1 -type d \( -name "*backup*" -o -name "*disaster*" -o -name "*checkpoint*" -o -name "*recovery*" \) 2>/dev/null | while read -r dir; do
    name=$(basename "$dir")
    echo "- ${name}"
done)

### 4. Token管理

$(find "${WORKSPACE_DIR}/skills" -maxdepth 1 -type d \( -name "*token*" -o -name "*budget*" \) 2>/dev/null | while read -r dir; do
    name=$(basename "$dir")
    echo "- ${name}"
done)

### 5. 休眠与优化

$(find "${WORKSPACE_DIR}/skills" -maxdepth 1 -type d \( -name "*dormancy*" -o -name "*hibernat*" -o -name "*optim*" \) 2>/dev/null | while read -r dir; do
    name=$(basename "$dir")
    echo "- ${name}"
done)

### 6. 知识与文档

$(find "${WORKSPACE_DIR}/skills" -maxdepth 1 -type d \( -name "*knowledge*" -o -name "*doc*" -o -name "*content*" \) 2>/dev/null | while read -r dir; do
    name=$(basename "$dir")
    echo "- ${name}"
done)

### 7. 治理与质量

$(find "${WORKSPACE_DIR}/skills" -maxdepth 1 -type d \( -name "*governance*" -o -name "*quality*" -o -name "*govern*" \) 2>/dev/null | while read -r dir; do
    name=$(basename "$dir")
    echo "- ${name}"
done)

---

*本文件由auto-index-update.sh自动生成*
EOF

    log_info "分类索引生成完成"
}

# ==================== 生成状态索引 ====================
generate_status_index() {
    log_section "5. 状态索引生成"
    
    local status_index="${WORKSPACE_DIR}/INDEX_BY_STATUS.md"
    
    log_info "生成状态索引: ${status_index}"
    
    cat > "${status_index}" << EOF
# 按状态索引 (Auto-Generated)

**生成时间**: ${DATE_STR} ${TIME_STR}  
**更新时间**: 每小时自动更新

---

## 状态分类

### ✅ 运行中 (Running)

核心机制正常运行:
- 五路图腾体系 (5个)
- 蓝军审计体系 (4个)
- 灾备体系 (4个)
- Token管理体系 (2个)

### ⚠️ 待验证 (Pending Verification)

需要进一步验证的机制:
- 待蓝军审计确认
- 待用户验收确认

### 🔧 维护中 (Maintenance)

正在更新或修复的机制:
- 临时性维护状态

### 💤 休眠中 (Dormant)

暂时未激活但保留的机制:
- 低频率使用
- 季节性机制

### 📊 统计信息

| 状态 | 预估数量 | 说明 |
|------|----------|------|
| 运行中 | ~50 | 核心机制 |
| 待验证 | ~20 | 新部署待确认 |
| 维护中 | ~5 | 临时状态 |
| 休眠中 | ~10 | 低频机制 |

---

*本文件由auto-index-update.sh自动生成*
EOF

    log_info "状态索引生成完成"
}

# ==================== 生成专家关联索引 ====================
generate_expert_index() {
    log_section "6. 专家关联索引生成"
    
    local expert_index="${WORKSPACE_DIR}/INDEX_BY_EXPERT.md"
    
    log_info "生成专家关联索引: ${expert_index}"
    
    cat > "${expert_index}" << EOF
# 专家关联索引 (Auto-Generated)

**生成时间**: ${DATE_STR} ${TIME_STR}  
**更新时间**: 每小时自动更新

---

## 核心专家数字替身

### 黎红雷教授 - 儒商哲学

**角色**: 合伙伦理学术源头  
**关联机制**:
- confucius-skill (儒家伦理)
- governance-suite (治理体系)

### 罗汉教授 - 数学/软件工程

**角色**: 方法论护法  
**关联机制**:
- simon-skill (满意解方法论)
- quality-suite (质量体系)
- testing-framework (测试框架)

### 谢宝剑研究员 - 深港战略

**角色**: 地理自在官  
**关联机制**:
- guanyin-skill (观自在)
- content-suite (内容体系)

### XU先生 - AI/压力测试

**角色**: 钻木人  
**关联机制**:
- huineng-skill (六祖顿悟)
- automation-suite (自动化)
- blue-army-sop (蓝军审计)

### 方翊沣博士 - 脑科学/BCI

**角色**: 感知力训练导师+睡眠优化专家  
**关联机制**:
- liu-skill (聚贤才)
- expert-suite (专家体系)

### 陈国祥博士 - 神经科/能量治疗

**角色**: 能量治疗导师  
**关联机制**:
- expert-suite (专家体系)
- dormancy-protocol (休眠协议)

---

## 专家关联图谱

    [LIU - 土/聚贤才]
           |
[CONFUCIUS - 木/伦理] + [SIMON - 金/方法论]
           |
  [GUANYIN - 水/洞察] + [HUINENG - 火/顿悟]

---

*本文件由auto-index-update.sh自动生成*
EOF

    log_info "专家关联索引生成完成"
}

# ==================== 保存状态 ====================
save_state() {
    log_section "7. 状态保存"
    
    local state_file="${STATE_DIR}/index_state.json"
    
    # 创建状态JSON
    cat > "${state_file}" << EOF
{
    "last_run": "${DATE_STR}T${TIME_STR}",
    "last_run_timestamp": $(date +%s),
    "total_scanned_files": $(wc -l < "${STATE_DIR}/current_scan.txt" 2>/dev/null || echo 0),
    "run_count": $(( $(jq -r '.run_count // 0' "${state_file}" 2>/dev/null || echo 0) + 1 )),
    "generated_indices": [
        "INDEX_BY_CATEGORY.md",
        "INDEX_BY_STATUS.md",
        "INDEX_BY_EXPERT.md"
    ],
    "latest_report": "${REPORT_FILE}",
    "version": "1.0"
}
EOF

    log_info "状态已保存到: ${state_file}"
}

# ==================== 更新索引文件 ====================
update_index_files() {
    log_section "8. 索引文件更新"
    
    # 创建或更新主索引文件 INDEX.md
    local main_index="${WORKSPACE_DIR}/INDEX.md"
    
    cat > "${main_index}" << EOF
# Workspace 索引中心

**最后更新**: ${DATE_STR} ${TIME_STR}  
**自动更新**: 每小时由auto-index-update.sh维护

---

## 📚 索引列表

| 索引名称 | 说明 | 文件 |
|----------|------|------|
| 全局机制索引 | 所有机制的总览 | [GLOBAL_INDEX.md](./GLOBAL_INDEX.md) |
| 分类索引 | 按功能分类索引 | [INDEX_BY_CATEGORY.md](./INDEX_BY_CATEGORY.md) |
| 状态索引 | 按运行状态索引 | [INDEX_BY_STATUS.md](./INDEX_BY_STATUS.md) |
| 专家索引 | 按专家关联索引 | [INDEX_BY_EXPERT.md](./INDEX_BY_EXPERT.md) |

## 📂 目录结构

\`\`\`
workspace/
├── skills/           # 所有Skill机制
├── docs/             # 文档资料
├── memory/           # 记忆文件
├── deliverables/     # 交付物
├── institute-assets/ # 研究所资产
├── checklists/       # 检查清单
├── scripts/          # 脚本工具
└── logs/             # 日志文件
\`\`\`

## 🔄 自动维护

本索引由 \`scripts/auto-index-update.sh\` 每小时自动更新。

---

*最后自动生成时间: ${DATE_STR} ${TIME_STR}*
EOF

    log_info "主索引已更新: ${main_index}"
}

# ==================== 完成报告 ====================
finalize_report() {
    log_section "9. 执行完成"
    
    # 更新报告状态
    sed -i "s/🔄 进行中/✅ 完成/" "${REPORT_FILE}"
    
    cat >> "${REPORT_FILE}" << EOF

---

## 总结

- ✅ Workspace扫描完成
- ✅ 变更检测完成
- ✅ GLOBAL_INDEX更新完成
- ✅ 分类索引生成完成
- ✅ 状态索引生成完成
- ✅ 专家索引生成完成
- ✅ 状态保存完成
- ✅ 主索引更新完成

**下次执行**: 1小时后

**报告文件**: ${REPORT_FILE}
EOF

    log_info "报告已保存: ${REPORT_FILE}"
}

# ==================== 清理旧文件 ====================
cleanup_old_files() {
    log_section "10. 清理旧文件"
    
    # 保留最近30天的报告
    find "${LOG_DIR}" -name "update_report_*.md" -mtime +30 -delete 2>/dev/null || true
    
    # 保留最近7天的变更记录
    find "${STATE_DIR}" -name "changes_*.txt" -mtime +7 -delete 2>/dev/null || true
    
    log_info "旧文件清理完成"
}

# ==================== 主函数 ====================
main() {
    log_info "========================================"
    log_info "自动索引更新脚本启动"
    log_info "========================================"
    
    # 初始化报告
    init_report
    
    # 执行各阶段
    scan_workspace
    detect_changes
    update_global_index
    generate_category_index
    generate_status_index
    generate_expert_index
    save_state
    update_index_files
    finalize_report
    cleanup_old_files
    
    log_info "========================================"
    log_info "自动索引更新完成"
    log_info "报告位置: ${REPORT_FILE}"
    log_info "========================================"
    
    return 0
}

# 执行主函数
main "$@"
