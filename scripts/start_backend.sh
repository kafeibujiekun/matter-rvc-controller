#!/bin/bash

# RVC控制端后端启动脚本
# 用于启动后端服务器

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${PROJECT_ROOT}/venv"
BACKEND_DIR="${PROJECT_ROOT}/backend"

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查虚拟环境是否存在
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Python虚拟环境不存在，请先运行 ./scripts/setup_dev_env.sh 设置开发环境"
        exit 1
    fi
}

# 启动后端服务
start_backend() {
    print_info "正在启动后端服务..."
    
    # 激活虚拟环境
    source "${VENV_DIR}/bin/activate"
    
    # 进入后端目录
    cd "$BACKEND_DIR"
    
    # 设置环境变量，确保WebSocket服务器绑定到所有接口
    export FLASK_RUN_HOST="0.0.0.0"
    export FLASK_RUN_PORT="5000"
    export FLASK_DEBUG="1"
    
    # 启动后端服务
    print_info "启动Flask应用，监听所有接口，端口5000"
    python app.py
    
    # 返回项目根目录
    cd "$PROJECT_ROOT"
}

# 主函数
main() {
    print_info "正在启动RVC控制端后端服务..."
    
    # 检查虚拟环境
    check_venv
    
    # 启动后端服务
    start_backend
}

# 执行主函数
main 