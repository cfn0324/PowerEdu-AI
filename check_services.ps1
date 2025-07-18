#!/usr/bin/env powershell
# PowerEdu-AI 服务检查脚本

Write-Host "===== PowerEdu-AI 服务检查 =====" -ForegroundColor Green

# 检查后端服务
Write-Host "检查后端服务 (http://localhost:8000)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/knowledge/" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 后端服务正常" -ForegroundColor Green
    } else {
        Write-Host "❌ 后端服务异常: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ 后端服务无法访问: $($_.Exception.Message)" -ForegroundColor Red
}

# 检查前端服务
Write-Host "检查前端服务 (http://localhost:5173)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 前端服务正常" -ForegroundColor Green
    } else {
        Write-Host "❌ 前端服务异常: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ 前端服务无法访问: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n====== 诊断建议 ======" -ForegroundColor Cyan
Write-Host "1. 如果后端服务无法访问，请检查："
Write-Host "   - Python 环境是否正确安装"
Write-Host "   - Django 依赖是否已安装 (pip install -r requirements.txt)"
Write-Host "   - 数据库是否已迁移 (python manage.py migrate)"
Write-Host ""
Write-Host "2. 如果前端服务无法访问，请检查："
Write-Host "   - Node.js 环境是否正确安装"
Write-Host "   - npm 依赖是否已安装 (npm install)"
Write-Host "   - 端口 5173 是否被占用"
Write-Host ""
Write-Host "3. 如果服务正常但功能异常，请："
Write-Host "   - 访问测试页面: http://localhost:5173/knowledge/test"
Write-Host "   - 检查浏览器控制台错误"
Write-Host "   - 检查网络请求是否正常"

Write-Host "`n按任意键退出..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
