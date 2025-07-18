#!/usr/bin/env powershell
# PowerEdu-AI 启动脚本

Write-Host "===== PowerEdu-AI 启动脚本 =====" -ForegroundColor Green

# 检查是否已在项目根目录
if (-not (Test-Path "package.json") -or -not (Test-Path "backend")) {
    Write-Host "错误: 请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

Write-Host "正在启动后端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "cd backend; python manage.py runserver 0.0.0.0:8000"

Write-Host "等待后端服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "正在启动前端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "cd frontend; npm run dev"

Write-Host "等待前端服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "服务启动完成!" -ForegroundColor Green
Write-Host "前端访问地址: http://localhost:5173" -ForegroundColor Cyan
Write-Host "后端API地址: http://localhost:8000/api" -ForegroundColor Cyan
Write-Host "测试页面: http://localhost:5173/knowledge/test" -ForegroundColor Cyan

Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
