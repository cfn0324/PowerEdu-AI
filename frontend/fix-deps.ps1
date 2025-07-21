# PowerEdu-AI Windows 依赖修复脚本
# 解决Windows环境下的依赖问题

Write-Host "🔧 PowerEdu-AI 依赖修复脚本" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue

# 检查当前目录
if (-not (Test-Path "package.json")) {
    Write-Host "❌ 请在前端目录(frontend)下运行此脚本" -ForegroundColor Red
    exit 1
}

# 1. 清理现有依赖
Write-Host "🧹 清理现有依赖..." -ForegroundColor Yellow
Remove-Item "node_modules" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "package-lock.json" -Force -ErrorAction SilentlyContinue

# 2. 清理npm缓存
Write-Host "🗑️ 清理npm缓存..." -ForegroundColor Yellow
npm cache clean --force

# 3. 创建.npmrc文件解决依赖冲突
Write-Host "⚙️ 配置npm设置..." -ForegroundColor Yellow
@"
legacy-peer-deps=true
fund=false
audit=false
"@ | Out-File -FilePath ".npmrc" -Encoding UTF8

# 4. 安装依赖
Write-Host "📦 安装依赖..." -ForegroundColor Yellow
npm install --legacy-peer-deps

# 5. 验证安装
if (Test-Path "node_modules") {
    Write-Host "✅ 依赖安装完成" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 可以使用以下命令启动：" -ForegroundColor Cyan
    Write-Host "   npm run dev    # 开发模式" -ForegroundColor White
    Write-Host "   npm run build  # 生产构建" -ForegroundColor White
} else {
    Write-Host "❌ 依赖安装失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 修复完成！" -ForegroundColor Green
