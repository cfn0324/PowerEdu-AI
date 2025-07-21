# 🚀 PowerEdu-AI 部署指南

本文档提供了将PowerEdu-AI平台部署到生产服务器的完整指南。

## 📋 部署前准备

### 服务器要求

- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **内存**: 最低4GB，推荐8GB+
- **存储**: 最低10GB可用空间
- **网络**: 稳定的网络连接

### 域名和DNS配置

1. 准备一个域名（如：poweredu.example.com）
2. 将域名的A记录指向您的服务器IP地址
3. 等待DNS解析生效（通常需要几分钟到几小时）

## 🔧 部署方式

提供两种部署方式，请根据需求选择：

### 方式一：传统部署（推荐）

#### 1. 连接服务器

```bash
ssh root@your-server-ip
```

#### 2. 下载项目

```bash
cd /tmp
git clone https://github.com/cfn0324/PowerEdu-AI.git
cd PowerEdu-AI
```

#### 3. 修改配置

编辑 `.env.production` 文件：

```bash
cp .env.production .env.production.backup
nano .env.production
```

**重要配置项**：
```bash
# 修改为您的域名
DOMAIN=your-domain.com
SERVER_IP=your-server-ip
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

# 生成新的密钥（必须修改）
SECRET_KEY=your-very-long-random-secret-key-here

# 数据库配置
DB_PASSWORD=your-secure-database-password

# AI模型API密钥（可选）
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
```

#### 4. 修改Nginx配置

编辑 `nginx.conf` 文件：

```bash
nano nginx.conf
```

将所有的 `your-domain.com` 替换为您的实际域名。

#### 5. 运行部署脚本

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

#### 6. 验证部署

```bash
# 检查服务状态
sudo systemctl status poweredu-ai-gunicorn
sudo systemctl status nginx

# 检查端口监听
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :8000
```

### 方式二：Docker部署

#### 1. 安装Docker

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose -y

# CentOS
sudo yum install docker docker-compose -y

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### 2. 修改配置

同样需要修改 `.env.production` 文件。

#### 3. 启动服务

```bash
sudo docker-compose up -d
```

#### 4. 初始化数据

```bash
# 数据库迁移
sudo docker-compose exec backend python manage.py migrate

# 创建管理员用户
sudo docker-compose exec backend python manage.py init_data
```

## 🔐 SSL证书配置（推荐）

### 使用Let's Encrypt免费证书

#### 1. 安装Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

#### 2. 获取证书

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

#### 3. 自动续期

```bash
sudo crontab -e
# 添加以下行
0 2 * * * /usr/bin/certbot renew --quiet
```

## 🔧 后期维护

### 查看日志

```bash
# 应用日志
sudo journalctl -u poweredu-ai-gunicorn -f

# Nginx日志
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# 应用错误日志
sudo tail -f /var/www/poweredu-ai/logs/gunicorn_error.log
```

### 重启服务

```bash
# 重启应用
sudo systemctl restart poweredu-ai-gunicorn

# 重启Nginx
sudo systemctl restart nginx

# 重新加载Nginx配置
sudo nginx -s reload
```

### 更新代码

```bash
cd /var/www/poweredu-ai

# 备份当前版本
sudo -u www-data git stash

# 拉取最新代码
sudo -u www-data git pull origin main

# 安装新依赖
sudo -u www-data venv/bin/pip install -r requirements.txt

# 前端构建（解决依赖冲突）
cd frontend
# 清理依赖和缓存
sudo -u www-data rm -rf node_modules package-lock.json
# 使用 legacy-peer-deps 解决兼容性问题
sudo -u www-data npm install --legacy-peer-deps
sudo -u www-data npm run build
cd ..

# 数据库迁移
cd backend
sudo -u www-data DJANGO_SETTINGS_MODULE=edu.settings_production ../venv/bin/python manage.py migrate
sudo -u www-data DJANGO_SETTINGS_MODULE=edu.settings_production ../venv/bin/python manage.py collectstatic --noinput
cd ..

# 重启服务
sudo systemctl restart poweredu-ai-gunicorn
```

### 数据库备份

```bash
# 创建备份脚本
sudo tee /usr/local/bin/backup-poweredu.sh > /dev/null <<EOF
#!/bin/bash
BACKUP_DIR="/var/backups/poweredu-ai"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR

# 备份数据库
sudo -u postgres pg_dump poweredu_ai > \$BACKUP_DIR/db_\$DATE.sql

# 备份媒体文件
tar -czf \$BACKUP_DIR/media_\$DATE.tar.gz -C /var/www/poweredu-ai/backend media/

# 删除7天前的备份
find \$BACKUP_DIR -name "*.sql" -mtime +7 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

sudo chmod +x /usr/local/bin/backup-poweredu.sh

# 设置定时备份
sudo crontab -e
# 添加以下行（每天凌晨3点备份）
0 3 * * * /usr/local/bin/backup-poweredu.sh
```

## 🔍 故障排除

### 常见问题

1. **502 Bad Gateway**
   - 检查Django服务是否正常运行
   - 检查端口8000是否被占用

2. **静态文件无法加载**
   - 检查静态文件路径配置
   - 重新收集静态文件

3. **数据库连接失败**
   - 检查数据库服务状态
   - 验证数据库配置信息

4. **权限问题**
   - 检查文件所有者是否为www-data
   - 确保目录权限正确

5. **npm 依赖冲突问题**
   ```bash
   # 如果遇到 ERESOLVE 错误，使用以下命令解决
   cd /var/www/poweredu-ai/frontend
   sudo -u www-data rm -rf node_modules package-lock.json
   sudo -u www-data npm install --legacy-peer-deps
   sudo -u www-data npm run build
   ```

6. **Node.js 版本问题**
   ```bash
   # 如果 Node.js 版本过低，升级到 Node.js 16+
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

7. **Windows环境psycopg2-binary编译错误**
   ```powershell
   # Windows下不需要PostgreSQL，项目使用SQLite
   # 如果遇到psycopg2-binary编译错误，可以忽略
   # 或者安装预编译版本：
   pip install psycopg2-binary --only-binary=psycopg2-binary
   ```

### 性能优化

1. **启用Gzip压缩**
2. **配置Redis缓存**
3. **优化数据库查询**
4. **使用CDN加速静态资源**

## 📞 技术支持

如果在部署过程中遇到问题，可以：

1. 查看项目GitHub Issues
2. 发送邮件到技术支持邮箱
3. 查看详细的错误日志

---

**部署完成后的访问信息**：
- 🌐 网站: https://your-domain.com
- 🔧 管理后台: https://your-domain.com/admin
- 📚 API文档: https://your-domain.com/api/docs
- 🔑 默认管理员: admin / 123456 （请立即修改密码）
