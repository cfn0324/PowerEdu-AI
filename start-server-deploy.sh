#!/bin/bash

# PowerEdu-AI 服务器部署启动脚本
# 专门用于解决前后端连接问题

echo "🔌 PowerEdu-AI 服务器部署启动脚本"
echo "========================================="

# 获取服务器IP地址
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "📍 服务器IP地址: $SERVER_IP"

# 设置项目路径
PROJECT_ROOT=$(pwd)
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "📁 项目目录: $PROJECT_ROOT"

# 1. 启动Django后端
echo ""
echo "🚀 启动Django后端服务..."
cd "$BACKEND_DIR"

# 检查Python虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

# 安装依赖
pip install -r ../requirements.txt

# 数据库初始化
python manage.py migrate
python manage.py collectstatic --noinput

# 启动Django服务（绑定到所有接口）
echo "启动Django服务 (0.0.0.0:8000)..."
nohup python manage.py runserver 0.0.0.0:8000 > ../logs/django-server.log 2>&1 &
DJANGO_PID=$!

echo "✅ Django服务已启动 (PID: $DJANGO_PID)"

# 2. 启动前端服务
echo ""
echo "🚀 启动前端服务..."
cd "$FRONTEND_DIR"

# 安装前端依赖
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install --legacy-peer-deps
fi

# 使用部署专用配置启动前端
echo "启动前端服务 (使用部署配置)..."
nohup npm run dev:deploy > ../logs/vite-server.log 2>&1 &
VITE_PID=$!

echo "✅ 前端服务已启动 (PID: $VITE_PID)"

# 3. 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 8

# 4. 测试服务连接
echo ""
echo "🔍 测试服务连接..."

# 测试Django API
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/ | grep -q "200\|404\|405"; then
    echo "✅ Django API服务正常"
else
    echo "❌ Django API服务异常"
fi

# 测试前端服务
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/ | grep -q "200"; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常"
fi

# 5. 显示访问信息
echo ""
echo "🎉 部署完成！"
echo "========================================="
echo "📱 访问地址："
echo "   🌐 前端应用: http://$SERVER_IP:5173"
echo "   🔗 API接口: http://$SERVER_IP:8000/api/"
echo "   👤 管理后台: http://$SERVER_IP:8000/admin/"
echo ""
echo "🔑 默认管理员账户："
echo "   用户名: admin"
echo "   密码: 123456"
echo ""
echo "📋 进程信息："
echo "   Django PID: $DJANGO_PID"
echo "   Vite PID: $VITE_PID"
echo ""
echo "📄 日志文件："
echo "   Django: $PROJECT_ROOT/logs/django-server.log"
echo "   前端: $PROJECT_ROOT/logs/vite-server.log"
echo ""
echo "💡 提示："
echo "   - 确保服务器防火墙开放5173和8000端口"
echo "   - 如果仍有连接问题，请检查日志文件"
echo "   - 前端现在会自动检测服务器环境并连接正确的后端"
echo ""

# 创建停止脚本
cat > stop-server.sh << EOF
#!/bin/bash
echo "停止PowerEdu-AI服务..."
kill $DJANGO_PID $VITE_PID 2>/dev/null
pkill -f "manage.py runserver" 2>/dev/null
pkill -f "vite.*deploy" 2>/dev/null
echo "服务已停止"
EOF

chmod +x stop-server.sh
echo "📝 已创建停止脚本: ./stop-server.sh"

echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap "echo ''; echo '停止服务...'; ./stop-server.sh; exit" INT
wait
