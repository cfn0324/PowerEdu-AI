# 电力知识库与AI预测平台启动脚本

Write-Host "🔌 正在启动电力知识库与AI预测平台..." -ForegroundColor Green

# 检查Python环境
Write-Host "检查Python环境..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python未找到，请先安装Python 3.8+" -ForegroundColor Red
    exit 1
}

# 检查Node.js环境
Write-Host "检查Node.js环境..." -ForegroundColor Yellow
node --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Node.js未找到，请先安装Node.js 18.15+" -ForegroundColor Red
    exit 1
}

# 安装Python依赖
Write-Host "安装Python依赖..." -ForegroundColor Yellow
pip install -r requirements.txt

# 进入后端目录并初始化数据库
Write-Host "初始化Django数据库..." -ForegroundColor Yellow
Set-Location backend
python manage.py migrate
if (!(Test-Path "db.sqlite3")) {
    Write-Host "创建超级用户账户（可选）..." -ForegroundColor Yellow
    Write-Host "账号: admin, 密码: 123456" -ForegroundColor Cyan
    # python manage.py createsuperuser --noinput --username admin --email admin@example.com
}

# 启动Django后端（后台运行）
Write-Host "🚀 启动Django后端服务..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python manage.py runserver"

Set-Location ..

# 进入前端目录并安装依赖
Write-Host "安装前端依赖..." -ForegroundColor Yellow
Set-Location frontend
npm install

# 启动React前端
Write-Host "🚀 启动React前端服务..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"

Set-Location ..

# 显示访问信息
Write-Host ""
Write-Host "✅ 平台启动完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📱 访问地址：" -ForegroundColor Cyan
Write-Host "  主平台: http://localhost:5173" -ForegroundColor White
Write-Host "  后端API: http://localhost:8000" -ForegroundColor White
Write-Host "  管理后台: http://localhost:8000/admin" -ForegroundColor White
Write-Host ""
Write-Host "🔑 管理员账户：" -ForegroundColor Cyan
Write-Host "  用户名: admin" -ForegroundColor White
Write-Host "  密码: 123456" -ForegroundColor White
Write-Host ""
Write-Host "💡 如需启动独立AI预测系统，请运行：" -ForegroundColor Yellow
Write-Host "  cd standalone_ai && python app.py" -ForegroundColor White

Read-Host "按回车键退出"
