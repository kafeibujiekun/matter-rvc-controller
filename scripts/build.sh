#!/bin/bash

# RVC控制端生产环境构建脚本
# 用于构建前端生产版本并复制到后端静态目录

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
DIST_DIR="${FRONTEND_DIR}/dist"
STATIC_DIR="${BACKEND_DIR}/static"
TEMPLATES_DIR="${BACKEND_DIR}/templates"

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

# 构建前端生产版本
build_frontend() {
    print_info "正在构建前端生产版本..."
    
    # 检查npm是否安装
    check_command npm
    
    # 进入前端目录
    cd "$FRONTEND_DIR"
    
    # 创建生产环境配置文件
    if [ ! -f ".env.production" ]; then
        cat > ".env.production" << EOF
# 生产环境配置
VUE_APP_API_URL=/api
VUE_APP_WS_URL=ws://\${window.location.host}/ws
EOF
        print_success "前端生产环境配置文件创建成功"
    fi
    
    # 构建生产版本
    npm run build
    if [ $? -ne 0 ]; then
        print_error "构建前端生产版本失败"
        exit 1
    fi
    
    print_success "前端生产版本构建成功"
    
    # 返回项目根目录
    cd "$PROJECT_ROOT"
}

# 复制前端构建结果到后端静态目录
copy_to_backend() {
    print_info "正在复制前端构建结果到后端静态目录..."
    
    # 检查前端构建结果是否存在
    if [ ! -d "$DIST_DIR" ]; then
        print_error "前端构建结果不存在，请先构建前端"
        exit 1
    fi
    
    # 创建后端静态目录和模板目录
    mkdir -p "$STATIC_DIR"
    mkdir -p "$TEMPLATES_DIR"
    
    # 清空后端静态目录和模板目录
    rm -rf "${STATIC_DIR:?}/"*
    rm -rf "${TEMPLATES_DIR:?}/"*
    
    # 复制静态文件
    cp -r "${DIST_DIR}/js" "$STATIC_DIR"
    cp -r "${DIST_DIR}/css" "$STATIC_DIR"
    cp -r "${DIST_DIR}/img" "$STATIC_DIR" 2>/dev/null || true
    cp -r "${DIST_DIR}/fonts" "$STATIC_DIR" 2>/dev/null || true
    
    # 复制index.html到模板目录
    cp "${DIST_DIR}/index.html" "$TEMPLATES_DIR"
    
    print_success "前端构建结果已复制到后端静态目录"
}

# 主函数
main() {
    print_info "开始构建RVC控制端生产环境版本..."
    
    # 构建前端生产版本
    build_frontend
    
    # 复制前端构建结果到后端静态目录
    copy_to_backend
    
    print_success "RVC控制端生产环境版本构建完成"
    echo ""
    echo "可以通过以下命令启动生产环境服务："
    echo "cd ${BACKEND_DIR}"
    echo "python app.py"
    echo ""
}

# 执行主函数
main 