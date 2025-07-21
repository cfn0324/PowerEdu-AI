# PowerEdu-AI Linux服务器环境故障排除指南

## 🔍 常见问题与解决方案

### 1. `spawn xdg-open ENOENT` 错误

**问题描述**: 在没有图形界面的Linux服务器上启动前端时出现此错误

**原因**: Vite尝试自动打开浏览器，但服务器环境没有`xdg-open`命令

**解决方案**:
```bash
# 方案一：使用服务器专用启动脚本（推荐）
./start-linux-server.sh

# 方案二：手动使用服务器模式
cd frontend
npm run dev:server

# 方案三：临时解决
export BROWSER=none
npm run dev
```

### 2. npm依赖冲突 `ERESOLVE unable to resolve dependency tree`

**问题描述**: `@ant-design/charts@1.4.3`要求`antd@^4.6.3`，但项目使用了`antd@5.26.6`

**解决方案**:
```bash
# 方案一：使用修复脚本（推荐）
cd frontend
chmod +x fix-deps.sh && ./fix-deps.sh

# 方案二：手动修复
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
echo "legacy-peer-deps=true" > .npmrc
npm install --legacy-peer-deps

# 方案三：降级charts包
npm install @ant-design/charts@^2.0.0 --save
```

### 3. 端口占用问题

**检查端口占用**:
```bash
# 检查8000端口（Django）
lsof -i :8000
netstat -tulpn | grep 8000

# 检查5173端口（Vite）
lsof -i :5173
netstat -tulpn | grep 5173
```

**强制停止占用进程**:
```bash
# 停止Django进程
pkill -f "manage.py runserver"

# 停止Vite进程
pkill -f "vite"

# 或者使用PID停止
kill -9 <PID>
```

### 4. Python依赖安装失败

**常见错误**: `Failed building wheel for psycopg2-binary`

**解决方案**:
```bash
# 安装系统依赖
sudo apt-get update
sudo apt-get install python3-dev libpq-dev build-essential

# 或者使用预编译版本
pip install psycopg2-binary --no-cache-dir

# 如果仍然失败，跳过该依赖（仅SQLite场景）
pip install -r requirements.txt --ignore-installed psycopg2-binary
```

### 5. 权限问题

**文件权限错误**:
```bash
# 修复脚本权限
chmod +x start-linux-server.sh
chmod +x start.sh
chmod +x frontend/fix-deps.sh

# 修复目录权限
sudo chown -R $USER:$USER .
chmod -R 755 .
```

### 6. 内存不足问题

**Node.js内存溢出**:
```bash
# 增加Node.js内存限制
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build

# 或在package.json中修改scripts
"build": "NODE_OPTIONS='--max-old-space-size=4096' vite build"
```

### 7. 防火墙问题

**端口无法访问**:
```bash
# Ubuntu/Debian
sudo ufw allow 5173
sudo ufw allow 8000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5173/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 8. 环境变量配置

**创建生产环境配置**:
```bash
# 复制环境配置
cp .env.example .env

# 编辑配置文件
nano .env
```

**必要的环境变量**:
```bash
# Django设置
DEBUG=False
ALLOWED_HOSTS=your-server-ip,your-domain.com

# AI模型配置（选择其一）
GEMINI_API_KEY=your-key-here
# 或
OPENAI_API_KEY=your-key-here
# 或
ZHIPU_API_KEY=your-key-here
```

## 🚀 完整的服务器部署流程

### 步骤1: 系统准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install python3 python3-pip python3-venv nodejs npm git curl -y

# 验证版本
python3 --version  # 应该 >= 3.8
node --version     # 应该 >= 18.15
npm --version
```

### 步骤2: 克隆项目
```bash
git clone https://github.com/cfn0324/PowerEdu-AI.git
cd PowerEdu-AI
```

### 步骤3: 一键启动
```bash
# 使用专用服务器启动脚本
chmod +x start-linux-server.sh
./start-linux-server.sh
```

### 步骤4: 验证部署
```bash
# 检查服务状态
curl http://localhost:8000/api/
curl http://localhost:5173/

# 查看日志
tail -f logs/django.log
tail -f logs/vite.log
```

### 步骤5: 配置反向代理（可选）

**Nginx配置示例**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📞 技术支持

如果遇到其他问题，请：

1. 查看日志文件：`logs/django.log` 和 `logs/vite.log`
2. 检查系统资源：`top`、`df -h`、`free -m`
3. 验证网络连接：`curl -I http://localhost:8000`
4. 提交Issue：[GitHub Issues](https://github.com/cfn0324/PowerEdu-AI/issues)

## 🔧 调试命令

```bash
# 查看进程
ps aux | grep python
ps aux | grep node

# 查看端口
netstat -tulpn | grep -E ':(5173|8000)'

# 查看系统资源
htop
df -h
free -m

# 查看日志
journalctl -u your-service-name
tail -f /var/log/syslog
```
