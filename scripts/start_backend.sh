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

# 检查并清理占用的端口
check_and_clean_ports() {
    local http_port=5000
    local ws_port=5005
    
    print_info "检查端口占用情况..."
    
    # 检查HTTP端口
    if lsof -i :$http_port -t &> /dev/null; then
        print_warning "HTTP端口 $http_port 已被占用"
        local pid=$(lsof -i :$http_port -t)
        print_info "尝试终止占用HTTP端口的进程 (PID: $pid)..."
        kill -15 $pid 2>/dev/null || kill -9 $pid 2>/dev/null
        sleep 1
        if lsof -i :$http_port -t &> /dev/null; then
            print_error "无法释放HTTP端口 $http_port，请手动终止占用进程"
            print_info "可以使用命令: sudo kill -9 $(lsof -i :$http_port -t)"
            exit 1
        else
            print_success "HTTP端口 $http_port 已释放"
        fi
    else
        print_success "HTTP端口 $http_port 可用"
    fi
    
    # 检查WebSocket端口
    if lsof -i :$ws_port -t &> /dev/null; then
        print_warning "WebSocket端口 $ws_port 已被占用"
        local pid=$(lsof -i :$ws_port -t)
        print_info "尝试终止占用WebSocket端口的进程 (PID: $pid)..."
        kill -15 $pid 2>/dev/null || kill -9 $pid 2>/dev/null
        sleep 1
        if lsof -i :$ws_port -t &> /dev/null; then
            print_error "无法释放WebSocket端口 $ws_port，请手动终止占用进程"
            print_info "可以使用命令: sudo kill -9 $(lsof -i :$ws_port -t)"
            exit 1
        else
            print_success "WebSocket端口 $ws_port 已释放"
        fi
    else
        print_success "WebSocket端口 $ws_port 可用"
    fi
}

# 启动后端服务
start_backend() {
    print_info "正在启动后端服务..."
    
    # 激活虚拟环境
    source "${VENV_DIR}/bin/activate"
    
    # 进入后端目录
    cd "$BACKEND_DIR"
    
    # 设置环境变量
    export FLASK_RUN_HOST="0.0.0.0"
    export FLASK_RUN_PORT="5000"
    export FLASK_DEBUG="1"
    export WS_PORT="5005"
    
    # 启动后端服务
    print_info "启动Flask应用，HTTP服务监听端口5000，WebSocket服务监听端口5005"
    python app.py &
    BACKEND_PID=$!
    
    # 返回项目根目录
    cd "$PROJECT_ROOT"
    
    print_success "后端服务已启动，PID: $BACKEND_PID"
}

# 主函数
main() {
    print_info "正在启动RVC控制端后端服务..."
    
    # 检查虚拟环境
    check_venv
    
    # 检查并清理占用的端口
    check_and_clean_ports
    
    # 启动后端服务
    start_backend
    
    print_success "服务已启动"
    print_info "HTTP服务: http://0.0.0.0:5000"
    print_info "WebSocket服务: ws://0.0.0.0:5005"
}

# 执行主函数
main 