#!/usr/bin/env powershell
# 安装必要的Python依赖

Write-Host "===== 安装Gemini API支持的依赖 =====" -ForegroundColor Green

try {
    # 检查是否在项目目录
    if (-not (Test-Path "requirements.txt")) {
        Write-Host "错误: 未找到requirements.txt文件，请在项目根目录运行此脚本" -ForegroundColor Red
        exit 1
    }

    # 安装aiohttp
    Write-Host "正在安装aiohttp..." -ForegroundColor Yellow
    pip install "aiohttp>=3.8.0"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ aiohttp 安装成功" -ForegroundColor Green
    } else {
        Write-Host "❌ aiohttp 安装失败" -ForegroundColor Red
        exit 1
    }

    # 安装其他可能缺失的依赖
    Write-Host "正在检查其他依赖..." -ForegroundColor Yellow
    pip install -r requirements.txt

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 所有依赖安装成功" -ForegroundColor Green
    } else {
        Write-Host "❌ 部分依赖安装失败，请检查错误信息" -ForegroundColor Yellow
    }

    Write-Host "`n====== 安装完成 ======" -ForegroundColor Cyan
    Write-Host "现在可以使用Gemini API功能了！" -ForegroundColor Green
    Write-Host "请参考 GEMINI_CONFIG_GUIDE.md 配置Gemini模型"

} catch {
    Write-Host "安装过程中出现错误: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n按任意键退出..."
Read-Host "按回车键继续"
