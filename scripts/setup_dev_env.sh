#!/bin/bash

# RVC控制端开发环境配置脚本
# 用于自动设置Python虚拟环境和安装npm依赖

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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 设置Python虚拟环境
setup_python_venv() {
    print_info "正在设置Python虚拟环境..."
    
    # 检查Python是否安装
    check_command python3
    
    # 检查虚拟环境是否已存在
    if [ -d "$VENV_DIR" ]; then
        print_warning "虚拟环境已存在，是否重新创建? [y/N]"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            rm -rf "$VENV_DIR"
        else
            print_info "使用现有虚拟环境"
            return
        fi
    fi
    
    # 创建虚拟环境
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        print_error "创建虚拟环境失败"
        exit 1
    fi
    
    print_success "Python虚拟环境创建成功"
}

# 安装后端依赖
install_backend_deps() {
    print_info "正在安装后端依赖..."
    
    # 激活虚拟环境
    source "${VENV_DIR}/bin/activate"
    
    # 安装依赖
    pip install -r "${BACKEND_DIR}/requirements.txt"
    if [ $? -ne 0 ]; then
        print_error "安装后端依赖失败"
        exit 1
    fi
    
    print_success "后端依赖安装成功"
}

# 安装前端依赖
install_frontend_deps() {
    print_info "正在安装前端依赖..."
    
    # 检查npm是否安装
    check_command npm
    
    # 进入前端目录
    cd "$FRONTEND_DIR"
    
    # 安装依赖
    npm install
    if [ $? -ne 0 ]; then
        print_error "安装前端依赖失败"
        exit 1
    fi
    
    print_success "前端依赖安装成功"
    
    # 返回项目根目录
    cd "$PROJECT_ROOT"
}

# 创建.env文件
create_env_file() {
    print_info "正在创建环境配置文件..."
    
    # 后端.env文件
    if [ ! -f "${BACKEND_DIR}/.env" ]; then
        cat > "${BACKEND_DIR}/.env" << EOF
# 开发环境配置
DEBUG=True
MATTER_SERVER_WS_URL=ws://192.168.2.21:5580/ws
EOF
        print_success "后端环境配置文件创建成功"
    else
        print_warning "后端环境配置文件已存在，跳过创建"
    fi
    
    # 前端.env文件
    if [ ! -f "${FRONTEND_DIR}/.env.local" ]; then
        cat > "${FRONTEND_DIR}/.env.local" << EOF
# 开发环境配置
VUE_APP_API_URL=http://localhost:5000/api
VUE_APP_WS_URL=ws://localhost:5000/ws
EOF
        print_success "前端环境配置文件创建成功"
    else
        print_warning "前端环境配置文件已存在，跳过创建"
    fi
}

# 显示使用说明
show_usage() {
    echo ""
    print_info "开发环境设置完成！"
    echo ""
    echo "使用说明:"
    echo "1. 激活Python虚拟环境:"
    echo "   source ${VENV_DIR}/bin/activate"
    echo ""
    echo "2. 启动后端服务:"
    echo "   cd ${BACKEND_DIR}"
    echo "   python app.py"
    echo ""
    echo "3. 启动前端开发服务器:"
    echo "   cd ${FRONTEND_DIR}"
    echo "   npm run serve"
    echo ""
    echo "4. 构建前端生产版本:"
    echo "   cd ${FRONTEND_DIR}"
    echo "   npm run build"
    echo ""
}

# 主函数
main() {
    print_info "开始设置RVC控制端开发环境..."
    
    # 设置Python虚拟环境
    setup_python_venv
    
    # 安装后端依赖
    install_backend_deps
    
    # 安装前端依赖
    install_frontend_deps
    
    # 创建环境配置文件
    create_env_file
    
    # 显示使用说明
    show_usage
}

# 执行主函数
main 