@echo off
echo 🚀 启动AI教育预测系统测试环境...

echo.
echo 📊 检查Python环境...
python --version

echo.
echo 🔧 检查后端Django服务...
cd /d "d:\xm\PowerEdu-AI\backend"
python manage.py check --verbosity=2

echo.
echo 🔮 测试AI预测模块导入...
python -c "import sys; sys.path.append('d:/xm/PowerEdu-AI/backend'); import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu.settings'); import django; django.setup(); from ai_prediction.model_manager import ModelManager; print('✅ AI模块导入成功')"

echo.
echo 🎯 启动后端服务器 (端口 8000)
start /B python manage.py runserver 8000

echo.
echo ⏱️ 等待服务器启动...
timeout /t 3 /nobreak > nul

echo.
echo 🌐 启动前端开发服务器...
cd /d "d:\xm\PowerEdu-AI\frontend"
start /B npm run dev

echo.
echo ✅ 系统启动完成！
echo 后端服务: http://localhost:8000
echo 前端服务: http://localhost:5173
echo.
echo 请在浏览器中访问前端地址测试功能...
pause
