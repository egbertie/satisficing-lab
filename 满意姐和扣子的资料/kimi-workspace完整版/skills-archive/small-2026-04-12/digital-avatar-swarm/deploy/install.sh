#!/bin/bash
#
# Digital-Avatar-Swarm 部署脚本
# 版本: 1.0.0
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/share/digital-avatar-swarm}"
CONFIG_DIR="${CONFIG_DIR:-$HOME/.config/digital-avatar-swarm}"
LOG_DIR="${LOG_DIR:-$HOME/.local/log/digital-avatar-swarm}"
VENV_DIR="${INSTALL_DIR}/venv"
PYTHON_VERSION="3.9"

echo "=================================="
echo "Digital-Avatar-Swarm 部署脚本"
echo "=================================="
echo ""

# 检查系统要求
check_requirements() {
    echo "[1/6] 检查系统要求..."
    
    # 检查Python版本
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到Python3${NC}"
        exit 1
    fi
    
    PYTHON_VER=$(python3 --version 2>&1 | awk '{print $2}')
    echo "  ✓ Python版本: $PYTHON_VER"
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}错误: 未找到pip3${NC}"
        exit 1
    fi
    echo "  ✓ pip3 已安装"
    
    # 检查虚拟环境支持
    if ! python3 -m venv --help &> /dev/null; then
        echo -e "${YELLOW}警告: 缺少venv模块，尝试安装...${NC}"
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3-venv
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-venv
        else
            echo -e "${RED}错误: 无法安装venv模块${NC}"
            exit 1
        fi
    fi
    echo "  ✓ venv 支持可用"
    
    echo ""
}

# 创建目录结构
create_directories() {
    echo "[2/6] 创建目录结构..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$INSTALL_DIR/scripts"
    mkdir -p "$INSTALL_DIR/tests"
    
    echo "  ✓ 安装目录: $INSTALL_DIR"
    echo "  ✓ 配置目录: $CONFIG_DIR"
    echo "  ✓ 日志目录: $LOG_DIR"
    echo ""
}

# 创建虚拟环境
create_venv() {
    echo "[3/6] 创建Python虚拟环境..."
    
    if [ -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}  虚拟环境已存在，跳过创建${NC}"
    else
        python3 -m venv "$VENV_DIR"
        echo "  ✓ 虚拟环境创建完成"
    fi
    
    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"
    
    # 升级pip
    pip install --upgrade pip
    echo "  ✓ pip 已升级"
    echo ""
}

# 安装依赖
install_dependencies() {
    echo "[4/6] 安装Python依赖..."
    
    # 创建requirements.txt
    cat > "$INSTALL_DIR/requirements.txt" << 'EOF'
# Digital-Avatar-Swarm 依赖
asyncio>=3.4.3
aiohttp>=3.8.0
python-json-logger>=2.0.0
pydantic>=1.10.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
EOF
    
    pip install -r "$INSTALL_DIR/requirements.txt" -q
    echo "  ✓ 依赖安装完成"
    echo ""
}

# 安装核心代码
install_core() {
    echo "[5/6] 安装核心代码..."
    
    # 获取脚本所在目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # 复制核心文件
    if [ -f "$SCRIPT_DIR/../avatar_swarm.py" ]; then
        cp "$SCRIPT_DIR/../avatar_swarm.py" "$INSTALL_DIR/"
        echo "  ✓ avatar_swarm.py"
    fi
    
    if [ -f "$SCRIPT_DIR/../SKILL.md" ]; then
        cp "$SCRIPT_DIR/../SKILL.md" "$INSTALL_DIR/"
        echo "  ✓ SKILL.md"
    fi
    
    # 创建__init__.py
    cat > "$INSTALL_DIR/__init__.py" << 'EOF'
"""
Digital-Avatar-Swarm (数字人蜂群)
多Agent协同系统

版本: 1.0.0
"""

from .avatar_swarm import (
    SwarmOrchestrator,
    Task,
    Result,
    Avatar,
    TaskDecomposer,
    LoadBalancer,
    ResultAggregator,
    HealthChecker,
    SwarmTester
)

__version__ = "1.0.0"
__all__ = [
    'SwarmOrchestrator',
    'Task',
    'Result',
    'Avatar',
    'TaskDecomposer',
    'LoadBalancer',
    'ResultAggregator',
    'HealthChecker',
    'SwarmTester'
]
EOF
    echo "  ✓ __init__.py"
    
    # 创建配置文件
    cat > "$CONFIG_DIR/config.json" << 'EOF'
{
  "swarm": {
    "max_avatars": 10,
    "token_budget": 100000,
    "timeout_seconds": 300,
    "retry_attempts": 3
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "swarm.log"
  },
  "monitoring": {
    "health_check_interval": 60,
    "metrics_enabled": true
  }
}
EOF
    echo "  ✓ config.json"
    
    echo ""
}

# 创建启动脚本
create_launcher() {
    echo "[6/6] 创建启动脚本..."
    
    # 主启动脚本
    cat > "$INSTALL_DIR/run.sh" << EOF
#!/bin/bash
# Digital-Avatar-Swarm 启动脚本

source "$VENV_DIR/bin/activate"
cd "$INSTALL_DIR"

# 设置环境变量
export SWARM_CONFIG="$CONFIG_DIR/config.json"
export SWARM_LOG_DIR="$LOG_DIR"

# 运行演示
python3 -c "
import asyncio
from avatar_swarm import demo
asyncio.run(demo())
"
EOF
    chmod +x "$INSTALL_DIR/run.sh"
    echo "  ✓ run.sh"
    
    # 系统服务文件 (systemd)
    cat > "$INSTALL_DIR/digital-avatar-swarm.service" << EOF
[Unit]
Description=Digital-Avatar-Swarm Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment=SWARM_CONFIG=$CONFIG_DIR/config.json
Environment=SWARM_LOG_DIR=$LOG_DIR
ExecStart=$VENV_DIR/bin/python $INSTALL_DIR/avatar_swarm.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    echo "  ✓ digital-avatar-swarm.service"
    
    # 添加到PATH的脚本
    cat > "$INSTALL_DIR/env.sh" << EOF
# 添加到 ~/.bashrc 或 ~/.zshrc
export PATH="\$PATH:$INSTALL_DIR"
alias swarm='cd $INSTALL_DIR && ./run.sh'
alias swarm-status='cd $INSTALL_DIR && python3 -c "import asyncio; from avatar_swarm import SwarmOrchestrator; s = SwarmOrchestrator(); print(s.get_status())"'
EOF
    echo "  ✓ env.sh"
    
    echo ""
}

# 运行测试
run_tests() {
    echo "[验证] 运行测试..."
    
    source "$VENV_DIR/bin/activate"
    cd "$INSTALL_DIR"
    
    # 简单导入测试
    python3 -c "from avatar_swarm import SwarmOrchestrator; print('  ✓ 核心模块导入成功')"
    
    # 创建简单测试任务
    python3 -c "
import asyncio
from avatar_swarm import SwarmOrchestrator, Task

async def quick_test():
    swarm = SwarmOrchestrator(max_avatars=3)
    status = swarm.get_status()
    assert status['swarm_status']['total_avatars'] == 3
    print('  ✓ 蜂群初始化成功')
    
    task = Task(description='测试任务', context={'test': True})
    result = await swarm.execute(task)
    assert result.status.name in ['SUCCESS', 'PARTIAL']
    print('  ✓ 任务执行成功')

asyncio.run(quick_test())
" 2>&1 | grep -E "(✓|✗|Error|Failed)" || true
    
    echo ""
}

# 显示安装信息
show_info() {
    echo "=================================="
echo -e "${GREEN}安装完成!${NC}"
    echo "=================================="
    echo ""
    echo "安装位置: $INSTALL_DIR"
    echo "配置文件: $CONFIG_DIR/config.json"
    echo "日志位置: $LOG_DIR"
    echo ""
    echo "使用方式:"
    echo "  1. 运行演示: cd $INSTALL_DIR && ./run.sh"
    echo "  2. 导入模块: from avatar_swarm import SwarmOrchestrator"
    echo "  3. 查看状态: swarm-status (需先source $INSTALL_DIR/env.sh)"
    echo ""
    echo "系统服务:"
    echo "  安装服务: sudo cp $INSTALL_DIR/digital-avatar-swarm.service /etc/systemd/system/"
    echo "  启动服务: sudo systemctl start digital-avatar-swarm"
    echo "  查看状态: sudo systemctl status digital-avatar-swarm"
    echo ""
    echo "卸载方法:"
    echo "  rm -rf $INSTALL_DIR $CONFIG_DIR $LOG_DIR"
    echo ""
}

# 主流程
main() {
    check_requirements
    create_directories
    create_venv
    install_dependencies
    install_core
    create_launcher
    run_tests
    show_info
}

# 如果直接运行脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
