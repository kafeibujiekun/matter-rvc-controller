#!/bin/bash

# RVC控制端开发环境启动脚本
# 用于一键启动后端和前端服务

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
FRONTEND_DIR="${PROJECT_ROOT}/frontend"

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
    
    # 启动后端服务
    python app.py &
    BACKEND_PID=$!
    
    print_success "后端服务已启动，PID: $BACKEND_PID"
    
    # 返回项目根目录
    cd "$PROJECT_ROOT"
}

# 启动前端服务
start_frontend() {
    print_info "正在启动前端开发服务器..."
    
    # 进入前端目录
    cd "$FRONTEND_DIR"
    
    # 启动前端服务
    npm run serve &
    FRONTEND_PID=$!
    
    print_success "前端开发服务器已启动，PID: $FRONTEND_PID"
    
    # 返回项目根目录
    cd "$PROJECT_ROOT"
}

# 清理函数，用于捕获SIGINT信号（Ctrl+C）
cleanup() {
    print_info "正在关闭服务..."
    
    # 关闭后端服务
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        print_success "后端服务已关闭"
    fi
    
    # 关闭前端服务
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        print_success "前端服务已关闭"
    fi
    
    exit 0
}

# 注册清理函数
trap cleanup SIGINT SIGTERM

# 主函数
main() {
    print_info "正在启动RVC控制端开发环境..."
    
    # 检查虚拟环境
    check_venv
    
    # 启动后端服务
    start_backend
    
    # 启动前端服务
    start_frontend
    
    print_info "开发环境已启动，按 Ctrl+C 停止所有服务"
    
    # 等待用户中断
    wait
}

# 执行主函数
main 