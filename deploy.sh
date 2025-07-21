#!/bin/bash

# PowerEdu-AI 生产环境部署脚本
# 使用方法: sudo ./deploy.sh

set -e
# 8. 安装前端依赖并构建
echo "🎨 构建前端..."
cd frontend

# 清理可能存在的缓存
sudo -u $SERVER_USER npm cache clean --force 2>/dev/null || true
rm -rf node_modules package-lock.json dist 2>/dev/null || true

# 安装依赖（使用legacy-peer-deps解决依赖冲突）
sudo -u $SERVER_USER npm install --legacy-peer-deps

# 使用生产环境配置构建
if [ -f "vite.config.production.js" ]; then
    sudo -u $SERVER_USER npm run build:prod
else
    sudo -u $SERVER_USER npm run build
fi
cd .."🚀 开始部署PowerEdu-AI到生产环境..."

# 配置变量
PROJECT_NAME="poweredu-ai"
PROJECT_PATH="/var/www/$PROJECT_NAME"
DOMAIN="your-domain.com"  # 请修改为您的域名
SERVER_USER="www-data"

# 检查是否以root身份运行
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用sudo运行此脚本"
    exit 1
fi

# 1. 更新系统包
echo "📦 更新系统包..."
apt update && apt upgrade -y

# 2. 安装必要的系统包
echo "📦 安装系统依赖..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    nginx \
    postgresql \
    postgresql-contrib \
    redis-server \
    git \
    curl \
    supervisor

# 3. 创建项目目录
echo "📁 创建项目目录..."
mkdir -p $PROJECT_PATH
mkdir -p $PROJECT_PATH/logs
chown -R $SERVER_USER:$SERVER_USER $PROJECT_PATH

# 4. 克隆项目代码（如果目录不存在）
if [ ! -d "$PROJECT_PATH/.git" ]; then
    echo "📥 克隆项目代码..."
    cd /tmp
    git clone https://github.com/cfn0324/PowerEdu-AI.git
    cp -r PowerEdu-AI/* $PROJECT_PATH/
    chown -R $SERVER_USER:$SERVER_USER $PROJECT_PATH
    rm -rf PowerEdu-AI
fi

cd $PROJECT_PATH

# 5. 创建Python虚拟环境
echo "🐍 创建Python虚拟环境..."
sudo -u $SERVER_USER python3 -m venv venv
sudo -u $SERVER_USER venv/bin/pip install --upgrade pip

# 6. 安装Python依赖
echo "📦 安装Python依赖..."
sudo -u $SERVER_USER venv/bin/pip install -r requirements.txt
sudo -u $SERVER_USER venv/bin/pip install gunicorn psycopg2-binary

# 7. 安装前端依赖并构建
echo "🎨 构建前端..."
cd frontend
sudo -u $SERVER_USER npm install
sudo -u $SERVER_USER npm run build
cd ..

# 8. 配置数据库
echo "🗄️ 配置数据库..."
sudo -u postgres createdb $PROJECT_NAME 2>/dev/null || echo "数据库已存在"
sudo -u postgres createuser $PROJECT_NAME 2>/dev/null || echo "用户已存在"

# 9. Django配置
echo "⚙️ 配置Django..."
cd backend

# 创建环境变量文件
if [ ! -f "../.env.production" ]; then
    cp ../.env.production.example ../.env.production
    echo "⚠️  请编辑 .env.production 文件并配置您的环境变量"
fi

# 收集静态文件
sudo -u $SERVER_USER DJANGO_SETTINGS_MODULE=edu.settings_production ../venv/bin/python manage.py collectstatic --noinput

# 数据库迁移
sudo -u $SERVER_USER DJANGO_SETTINGS_MODULE=edu.settings_production ../venv/bin/python manage.py migrate

# 创建超级用户（如果不存在）
echo "👤 创建管理员用户..."
sudo -u $SERVER_USER DJANGO_SETTINGS_MODULE=edu.settings_production ../venv/bin/python manage.py init_data

cd ..

# 10. 配置Nginx
echo "🌐 配置Nginx..."
cp nginx.conf /etc/nginx/sites-available/$PROJECT_NAME
ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 更新Nginx配置中的域名
sed -i "s/your-domain.com/$DOMAIN/g" /etc/nginx/sites-available/$PROJECT_NAME
sed -i "s|/var/www/poweredu-ai|$PROJECT_PATH|g" /etc/nginx/sites-available/$PROJECT_NAME

# 测试Nginx配置
nginx -t

# 11. 配置Systemd服务
echo "🔧 配置系统服务..."
cp poweredu-ai-gunicorn.service /etc/systemd/system/
sed -i "s|/var/www/poweredu-ai|$PROJECT_PATH|g" /etc/systemd/system/poweredu-ai-gunicorn.service

# 重新加载systemd
systemctl daemon-reload

# 启用并启动服务
systemctl enable poweredu-ai-gunicorn
systemctl enable nginx
systemctl enable redis-server

# 12. 启动服务
echo "🚀 启动服务..."
systemctl start redis-server
systemctl start poweredu-ai-gunicorn
systemctl restart nginx

# 13. 设置防火墙
echo "🔥 配置防火墙..."
ufw allow 22
ufw allow 80
ufw allow 443
echo "y" | ufw enable

# 14. 显示状态
echo ""
echo "✅ 部署完成！"
echo ""
echo "📊 服务状态："
systemctl status poweredu-ai-gunicorn --no-pager -l
echo ""
systemctl status nginx --no-pager -l
echo ""
echo "🌐 访问地址："
echo "  网站: http://$DOMAIN"
echo "  管理后台: http://$DOMAIN/admin"
echo "  API文档: http://$DOMAIN/api/docs"
echo ""
echo "🔑 管理员账户："
echo "  用户名: admin"
echo "  密码: 123456"
echo ""
echo "⚠️  重要提醒："
echo "1. 请修改 $PROJECT_PATH/.env.production 中的配置"
echo "2. 请修改默认管理员密码"
echo "3. 如需HTTPS，请配置SSL证书"
echo "4. 建议设置定期备份"

echo ""
echo "📝 查看日志命令："
echo "  应用日志: journalctl -u poweredu-ai-gunicorn -f"
echo "  Nginx日志: tail -f /var/log/nginx/error.log"
echo "  应用错误日志: tail -f $PROJECT_PATH/logs/gunicorn_error.log"
