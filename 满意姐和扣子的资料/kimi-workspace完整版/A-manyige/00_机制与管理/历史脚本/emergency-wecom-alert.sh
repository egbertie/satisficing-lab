#!/bin/bash
# ============================================================
# 紧急企微告警脚本
# Emergency WeCom Alert Script
# ============================================================
# 用法:
#   ./emergency-wecom-alert.sh <level> <message> [options]
#
# 参数:
#   level: P0/P1/P2/P3 (告警级别)
#   message: 告警消息内容
#
# 选项:
#   -w, --webhook <name>    指定 webhook 名称 (默认: system_alerts)
#   -t, --template <name>   使用指定模板
#   -a, --at-all           @所有人
#   -f, --file <path>      附加文件内容
#   -h, --help             显示帮助
#
# 示例:
#   ./emergency-wecom-alert.sh P0 "系统核心服务异常"
#   ./emergency-wecom-alert.sh P1 "Token使用率超过80%" -w system_alerts
#   ./emergency-wecom-alert.sh P2 "定时任务执行完成" -t task_success
# ============================================================

set -euo pipefail

# 脚本路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$WORKSPACE_DIR/skills/disaster-recovery-wecom/config.yaml"

# 默认值
LEVEL="P2"
MESSAGE=""
WEBHOOK_NAME="system_alerts"
TEMPLATE=""
AT_ALL=false
ATTACH_FILE=""
DRY_RUN=false

# 颜色定义
RED='\033[0;31m'
ORANGE='\033[0;33m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================
# 函数定义
# ============================================================

show_help() {
    head -n 25 "$0" | tail -n 23
    exit 0
}

log() {
    local level="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" >&2
}

log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }

# 检查依赖
check_dependencies() {
    local deps=("curl" "python3")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "缺少依赖: $dep"
            exit 1
        fi
    done
}

# 解析配置文件（使用Python，因为YAML解析较复杂）
parse_config() {
    local key="$1"
    python3 -c "
import yaml
import sys

with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)

keys = '$key'.split('.')
value = config
for k in keys:
    if isinstance(value, dict) and k in value:
        value = value[k]
    else:
        sys.exit(1)

if isinstance(value, str):
    print(value)
else:
    import json
    print(json.dumps(value))
" 2>/dev/null
}

# 获取 Webhook URL
get_webhook_url() {
    local name="$1"
    
    # 检查是否使用默认 key（未配置）
    if [[ "$name" == "YOUR_"* ]] || [[ "$name" == *"YOUR_"* ]]; then
        echo ""
        return
    fi
    
    python3 -c "
import yaml
import sys

with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)

webhooks = config.get('webhooks', {})
if '$name' in webhooks:
    webhook = webhooks['$name']
    if webhook.get('enabled', True):
        print(webhook.get('url', ''))
" 2>/dev/null
}

# 获取告警级别配置
get_severity_config() {
    local level="$1"
    python3 -c "
import yaml

with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)

levels = config.get('settings', {}).get('severity_levels', {})
if '$level' in levels:
    level_config = levels['$level']
    print(f\"name={level_config.get('name', '')}\")
    print(f\"color={level_config.get('color', '666666')}\")
    print(f\"at_all={level_config.get('at_all', False)}\")
" 2>/dev/null
}

# 生成 markdown 消息
format_message() {
    local level="$1"
    local title="$2"
    local content="$3"
    local extra_info="${4:-}"
    
    local severity_info=$(get_severity_config "$level")
    local level_name=$(echo "$severity_info" | grep "^name=" | cut -d'=' -f2)
    local color=$(echo "$severity_info" | grep "^color=" | cut -d'=' -f2)
    local should_at_all=$(echo "$severity_info" | grep "^at_all=" | cut -d'=' -f2)
    
    # 构建 markdown 内容
    local markdown="<font color=\"#$color\">**[$level - $level_name]**</font>

**$title**

$content"

    # 添加额外信息
    if [[ -n "$extra_info" ]]; then
        markdown="$markdown

---
$extra_info"
    fi

    # 添加时间戳
    markdown="$markdown

<font color=\"gray\">$(date '+%Y-%m-%d %H:%M:%S')</font>"

    # @所有人
    if [[ "$AT_ALL" == "true" ]] || [[ "$should_at_all" == "True" ]]; then
        markdown="$markdown

@所有人"
    fi

    echo "$markdown"
}

# 构建 JSON 请求体
build_request_body() {
    local markdown="$1"
    
    python3 -c "
import json
import sys

markdown = '''$markdown'''
body = {
    'msgtype': 'markdown',
    'markdown': {
        'content': markdown
    }
}
print(json.dumps(body, ensure_ascii=False))
"
}

# 发送通知
send_notification() {
    local webhook_url="$1"
    local body="$2"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] 将发送以下内容到 $webhook_url:"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
        return 0
    fi
    
    # 发送请求
    local response
    response=$(curl -s -w "\n%{http_code}" \
        -H "Content-Type: application/json" \
        -d "$body" \
        "$webhook_url" 2>&1) || {
        log_error "请求失败: $?"
        return 1
    }
    
    local http_code=$(echo "$response" | tail -n1)
    local body_content=$(echo "$response" | sed '$d')
    
    if [[ "$http_code" == "200" ]]; then
        local errcode=$(echo "$body_content" | python3 -c "import sys,json; print(json.load(sys.stdin).get('errcode','unknown'))" 2>/dev/null)
        if [[ "$errcode" == "0" ]]; then
            log_info "通知发送成功"
            return 0
        else
            local errmsg=$(echo "$body_content" | python3 -c "import sys,json; print(json.load(sys.stdin).get('errmsg','unknown error'))" 2>/dev/null)
            log_error "企微API返回错误: $errcode - $errmsg"
            return 1
        fi
    else
        log_error "HTTP错误: $http_code"
        log_error "响应: $body_content"
        return 1
    fi
}

# 发送测试消息
send_test() {
    local test_message="${1:-这是一条测试消息}"
    
    log_info "发送测试消息..."
    
    # 检查配置
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_error "配置文件不存在: $CONFIG_FILE"
        return 1
    fi
    
    # 获取第一个启用的 webhook
    local webhook_url=$(get_webhook_url "system_alerts")
    
    if [[ -z "$webhook_url" ]] || [[ "$webhook_url" == *"YOUR_"* ]]; then
        log_warn "⚠️  Webhook URL 未配置或未替换默认 key"
        log_warn "请先配置 skills/disaster-recovery-wecom/config.yaml"
        log_warn "然后重新运行此脚本"
        echo ""
        echo "配置文件路径: $CONFIG_FILE"
        echo ""
        return 1
    fi
    
    local markdown="<font color=\"#1E90FF\">**[测试消息]**</font>

**企微告警通道测试**

$test_message

---
<font color=\"gray\">$(date '+%Y-%m-%d %H:%M:%S')</font>"

    local body=$(build_request_body "$markdown")
    send_notification "$webhook_url" "$body"
}

# 使用模板发送
send_with_template() {
    local level="$1"
    local template_name="$2"
    shift 2
    
    local template_file="$WORKSPACE_DIR/skills/disaster-recovery-wecom/templates/${template_name}.md"
    
    if [[ ! -f "$template_file" ]]; then
        log_error "模板文件不存在: $template_file"
        return 1
    fi
    
    # 读取模板并替换变量
    local template_content=$(cat "$template_file")
    
    # 替换占位符
    template_content="${template_content//\{\{LEVEL\}\}/$level}"
    template_content="${template_content//\{\{TIMESTAMP\}\}/$(date '+%Y-%m-%d %H:%M:%S')}"
    template_content="${template_content//\{\{HOSTNAME\}\}/$(hostname)}"
    
    # 替换额外参数
    for arg in "$@"; do
        if [[ "$arg" == *"="* ]]; then
            local key="${arg%%=*}"
            local value="${arg#*=}"
            template_content="${template_content//\{\{$key\}\}/$value}"
        fi
    done
    
    # 获取 webhook URL
    local webhook_url=$(get_webhook_url "$WEBHOOK_NAME")
    if [[ -z "$webhook_url" ]] || [[ "$webhook_url" == *"YOUR_"* ]]; then
        log_error "Webhook 未配置: $WEBHOOK_NAME"
        return 1
    fi
    
    local body=$(build_request_body "$template_content")
    send_notification "$webhook_url" "$body"
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                show_help
                ;;
            -w|--webhook)
                WEBHOOK_NAME="$2"
                shift 2
                ;;
            -t|--template)
                TEMPLATE="$2"
                shift 2
                ;;
            -a|--at-all)
                AT_ALL=true
                shift
                ;;
            -f|--file)
                ATTACH_FILE="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            test)
                shift
                send_test "$@"
                exit $?
                ;;
            P0|P1|P2|P3)
                LEVEL="$1"
                shift
                if [[ $# -gt 0 ]] && [[ ! "$1" =~ ^- ]]; then
                    MESSAGE="$1"
                    shift
                fi
                ;;
            *)
                if [[ -z "$MESSAGE" ]]; then
                    MESSAGE="$1"
                fi
                shift
                ;;
        esac
    done
}

# ============================================================
# 主程序
# ============================================================

main() {
    # 检查依赖
    check_dependencies
    
    # 解析参数
    parse_args "$@"
    
    # 检查配置文件
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_error "配置文件不存在: $CONFIG_FILE"
        exit 1
    fi
    
    # 如果没有提供消息，显示帮助
    if [[ -z "$MESSAGE" ]] && [[ -z "$TEMPLATE" ]]; then
        show_help
    fi
    
    # 使用模板发送
    if [[ -n "$TEMPLATE" ]]; then
        send_with_template "$LEVEL" "$TEMPLATE" "$@"
        exit $?
    fi
    
    # 构建消息
    local extra_info=""
    if [[ -n "$ATTACH_FILE" ]] && [[ -f "$ATTACH_FILE" ]]; then
        extra_info="<details><summary>附加信息</summary>

\`\`\`
$(cat "$ATTACH_FILE" | head -n 50)
\`\`\`
</details>"
    fi
    
    local markdown=$(format_message "$LEVEL" "系统告警" "$MESSAGE" "$extra_info")
    local body=$(build_request_body "$markdown")
    
    # 获取 webhook URL
    local webhook_url=$(get_webhook_url "$WEBHOOK_NAME")
    
    if [[ -z "$webhook_url" ]] || [[ "$webhook_url" == *"YOUR_"* ]]; then
        log_warn "⚠️  Webhook URL 未配置"
        log_warn "请编辑配置文件: $CONFIG_FILE"
        log_warn "将 YOUR_*_KEY 替换为实际的企微机器人 key"
        echo ""
        echo "当前消息预览:"
        echo "=========================================="
        echo "$markdown"
        echo "=========================================="
        exit 1
    fi
    
    # 发送通知
    send_notification "$webhook_url" "$body"
}

main "$@"
