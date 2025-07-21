#!/bin/bash

# PowerEdu-AI 依赖修复脚本
# 解决Linux/Mac环境下的npm依赖冲突问题

echo "🔧 PowerEdu-AI 依赖修复脚本"
echo "================================"

# 检查当前目录
if [ ! -f "package.json" ]; then
    echo "❌ 请在前端目录(frontend)下运行此脚本"
    exit 1
fi

# 1. 清理现有依赖
echo "🧹 清理现有依赖..."
rm -rf node_modules package-lock.json

# 2. 清理npm缓存
echo "🗑️ 清理npm缓存..."
npm cache clean --force

# 3. 创建.npmrc文件解决依赖冲突
echo "⚙️ 配置npm设置..."
cat > .npmrc << EOF
legacy-peer-deps=true
fund=false
audit=false
EOF

# 4. 安装依赖
echo "📦 安装依赖..."
npm install --legacy-peer-deps

# 5. 验证安装
if [ -d "node_modules" ]; then
    echo "✅ 依赖安装完成"
    echo ""
    echo "📝 可以使用以下命令启动："
    echo "   npm run dev    # 开发模式"
    echo "   npm run build  # 生产构建"
else
    echo "❌ 依赖安装失败"
    exit 1
fi

echo ""
echo "🎉 修复完成！"
