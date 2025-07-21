#!/bin/bash

# PowerEdu-AI Linux服务器环境启动脚本
# 解决服务器环境下的各种问题（无图形界面、依赖冲突等）

set -e  # 遇到错误立即退出

echo "🚀 PowerEdu-AI Linux服务器启动脚本"
echo "====================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 检查必要的命令
log_info "检查系统环境..."
check_command python3
check_command pip3
check_command node
check_command npm

# 获取项目根目录
PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

log_info "项目目录: $PROJECT_ROOT"

# 1. 设置Python环境
log_info "设置Python后端环境..."
cd "$BACKEND_DIR"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    log_info "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装Python依赖
log_info "安装Python依赖..."
pip install -r ../requirements.txt

# 数据库迁移
log_info "执行数据库迁移..."
python manage.py migrate

# 初始化系统数据
log_info "初始化系统数据..."
python manage.py collectstatic --noinput || true
if ! python -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists()" 2>/dev/null; then
    python admin_manager.py create || true
fi

# 2. 设置前端环境
log_info "设置前端环境..."
cd "$FRONTEND_DIR"

# 检查是否存在package.json
if [ ! -f "package.json" ]; then
    log_error "frontend/package.json 文件不存在"
    exit 1
fi

# 修复npm依赖冲突
log_info "修复npm依赖冲突..."

# 清理现有依赖
if [ -d "node_modules" ]; then
    log_warning "清理现有node_modules..."
    rm -rf node_modules
fi

if [ -f "package-lock.json" ]; then
    rm -f package-lock.json
fi

# 清理npm缓存
npm cache clean --force

# 创建.npmrc配置文件解决依赖冲突
log_info "配置npm设置..."
cat > .npmrc << EOF
legacy-peer-deps=true
fund=false
audit=false
auto-install-peers=true
EOF

# 安装依赖
log_info "安装前端依赖..."
npm install --legacy-peer-deps

# 验证安装
if [ ! -d "node_modules" ]; then
    log_error "前端依赖安装失败"
    exit 1
fi

log_success "依赖安装完成"

# 3. 启动服务
log_info "启动服务..."

# 创建启动日志目录
mkdir -p "$PROJECT_ROOT/logs"

# 启动Django后端（后台运行）
log_info "启动Django后端服务..."
cd "$BACKEND_DIR"
source venv/bin/activate

# 检查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_warning "端口8000已被占用，尝试停止现有进程..."
    pkill -f "manage.py runserver" || true
    sleep 2
fi

# 启动Django（后台运行）
nohup python manage.py runserver 0.0.0.0:8000 > "$PROJECT_ROOT/logs/django.log" 2>&1 &
DJANGO_PID=$!

log_info "Django服务已启动 (PID: $DJANGO_PID)"

# 等待Django启动
sleep 5

# 检查Django是否启动成功
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/ | grep -q "200\|404\|405"; then
    log_success "Django服务启动成功"
else
    log_error "Django服务启动失败，请检查日志: $PROJECT_ROOT/logs/django.log"
    exit 1
fi

# 启动Vite前端（服务器模式，不自动打开浏览器）
log_info "启动Vite前端服务（服务器模式）..."
cd "$FRONTEND_DIR"

# 检查端口是否被占用
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_warning "端口5173已被占用，尝试停止现有进程..."
    pkill -f "vite" || true
    sleep 2
fi

# 启动Vite（服务器模式）
nohup npm run dev:server > "$PROJECT_ROOT/logs/vite.log" 2>&1 &
VITE_PID=$!

log_info "Vite服务已启动 (PID: $VITE_PID)"

# 等待Vite启动
sleep 8

# 检查Vite是否启动成功
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/ | grep -q "200"; then
    log_success "Vite服务启动成功"
else
    log_warning "Vite服务可能启动失败，请检查日志: $PROJECT_ROOT/logs/vite.log"
fi

# 保存进程ID到文件
echo "$DJANGO_PID" > "$PROJECT_ROOT/logs/django.pid"
echo "$VITE_PID" > "$PROJECT_ROOT/logs/vite.pid"

# 4. 显示访问信息
echo ""
echo "🎉 PowerEdu-AI 服务启动完成！"
echo "================================"
echo ""
echo "📱 访问地址："
echo "   主应用:     http://服务器IP:5173"
echo "   API接口:    http://服务器IP:8000/api"
echo "   管理后台:   http://服务器IP:8000/admin"
echo ""
echo "🔑 默认账户："
echo "   用户名: admin"
echo "   密码:   123456"
echo ""
echo "📊 服务状态："
echo "   Django PID: $DJANGO_PID"
echo "   Vite PID:   $VITE_PID"
echo ""
echo "📋 日志文件："
echo "   Django: $PROJECT_ROOT/logs/django.log"
echo "   Vite:   $PROJECT_ROOT/logs/vite.log"
echo ""
echo "🛑 停止服务："
echo "   ./stop-server.sh"
echo ""

# 创建停止脚本
cat > "$PROJECT_ROOT/stop-server.sh" << 'EOF'
#!/bin/bash

echo "🛑 停止PowerEdu-AI服务..."

PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)

# 停止Django
if [ -f "$PROJECT_ROOT/logs/django.pid" ]; then
    DJANGO_PID=$(cat "$PROJECT_ROOT/logs/django.pid")
    if kill -0 "$DJANGO_PID" 2>/dev/null; then
        kill "$DJANGO_PID"
        echo "✅ Django服务已停止"
    fi
    rm -f "$PROJECT_ROOT/logs/django.pid"
fi

# 停止Vite
if [ -f "$PROJECT_ROOT/logs/vite.pid" ]; then
    VITE_PID=$(cat "$PROJECT_ROOT/logs/vite.pid")
    if kill -0 "$VITE_PID" 2>/dev/null; then
        kill "$VITE_PID"
        echo "✅ Vite服务已停止"
    fi
    rm -f "$PROJECT_ROOT/logs/vite.pid"
fi

# 强制杀死可能残留的进程
pkill -f "manage.py runserver" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

echo "🎉 所有服务已停止"
EOF

chmod +x "$PROJECT_ROOT/stop-server.sh"

log_success "启动脚本执行完成！"

# 保持脚本运行，显示实时日志
echo ""
echo "📝 显示实时日志（Ctrl+C退出日志查看，服务继续运行）："
echo "================================"
sleep 2

# 显示Django和Vite的实时日志
tail -f "$PROJECT_ROOT/logs/django.log" "$PROJECT_ROOT/logs/vite.log" 2>/dev/null || true
