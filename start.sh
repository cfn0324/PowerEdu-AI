#!/bin/bash

# 电力知识库与AI预测平台启动脚本 (Linux/Mac)

echo "🔌 正在启动电力知识库与AI预测平台..."

# 检查Python环境
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未找到，请先安装Python 3.8+"
    exit 1
fi

# 检查Node.js环境
echo "检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未找到，请先安装Node.js 18.15+"
    exit 1
fi

# 安装Python依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt

# 进入后端目录并初始化数据库
echo "初始化Django数据库..."
cd backend
python3 manage.py migrate

# 启动Django后端（后台运行）
echo "🚀 启动Django后端服务..."
python3 manage.py runserver &
BACKEND_PID=$!

cd ..

# 进入前端目录并安装依赖
echo "安装前端依赖..."
cd frontend
npm install

# 启动React前端
echo "🚀 启动React前端服务..."
npm run dev &
FRONTEND_PID=$!

cd ..

# 显示访问信息
echo ""
echo "✅ 平台启动完成！"
echo ""
echo "📱 访问地址："
echo "  主平台: http://localhost:5173"
echo "  AI预测: http://localhost:5173/prediction"
echo "  后端API: http://localhost:8000"
echo "  管理后台: http://localhost:8000/admin"
echo "  API文档: http://localhost:8000/api/docs"
echo ""
echo "🔑 管理员账户："
echo "  用户名: admin"
echo "  密码: 123456"
echo ""
echo "🎯 AI预测功能已完全集成到主平台中！"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
