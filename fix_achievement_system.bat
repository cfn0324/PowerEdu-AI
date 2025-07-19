@echo off
echo 🔧 PowerEdu-AI 成就系统修复脚本
echo =====================================

cd backend

echo.
echo 📋 步骤1: 数据库迁移
python manage.py migrate

echo.
echo 👤 步骤2: 创建管理员账户
python admin_manager.py create

echo.
echo 🏆 步骤3: 初始化成就数据
python manage.py init_achievements

echo.
echo 🎯 步骤4: 初始化知识库
python manage.py init_knowledge

echo.
echo ✅ 修复完成! 
echo 🚀 请重新访问成就页面测试功能
echo.
pause
