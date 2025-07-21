# 🚨 快速修复部署问题

## npm 依赖冲突解决方案

如果您在部署过程中遇到以下错误：
```
npm ERR! ERESOLVE unable to resolve dependency tree
npm ERR! peer antd@"^4.6.3" from @ant-design/charts@1.4.3
```

### 📋 解决步骤

#### 1. 立即修复（在服务器上）

```bash
# 进入前端目录
cd /tmp/PowerEdu-AI/frontend

# 清理现有依赖
rm -rf node_modules package-lock.json

# 使用兼容模式安装依赖
npm install --legacy-peer-deps

# 构建前端
npm run build:prod
```

#### 2. 如果步骤1失败，使用强制模式

```bash
# 强制安装（忽略冲突）
npm install --force

# 或者使用 yarn（如果可用）
yarn install --ignore-engines
```

#### 3. 继续部署脚本

```bash
# 回到项目根目录
cd /tmp/PowerEdu-AI

# 继续执行部署脚本
sudo ./deploy.sh
```

### 🔧 预防措施

在本地开发环境中：

1. **更新 package.json**：
   - 已移除不兼容的 `@ant-design/charts` 和 `@ant-design/plots`
   - 项目使用 `echarts` 和 `echarts-for-react` 进行图表展示

2. **使用兼容安装命令**：
   ```bash
   npm install --legacy-peer-deps
   ```

3. **或者创建 .npmrc 文件**：
   ```bash
   echo "legacy-peer-deps=true" > frontend/.npmrc
   ```

### 📱 Node.js 版本要求

确保服务器有合适的 Node.js 版本：

```bash
# 检查当前版本
node --version

# 如果版本低于 16，升级 Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证版本
node --version
npm --version
```

### 🔄 完整修复流程

如果部署脚本在前端构建阶段失败：

```bash
cd /var/www/poweredu-ai/frontend

# 1. 清理环境
sudo -u www-data rm -rf node_modules package-lock.json dist

# 2. 更新 npm 缓存
sudo -u www-data npm cache clean --force

# 3. 安装依赖
sudo -u www-data npm install --legacy-peer-deps

# 4. 构建项目
sudo -u www-data npm run build:prod

# 5. 继续其他部署步骤
cd /var/www/poweredu-ai
sudo systemctl restart poweredu-ai-gunicorn
sudo systemctl restart nginx
```

### ✅ 验证修复

部署完成后验证：

```bash
# 检查前端文件是否构建成功
ls -la /var/www/poweredu-ai/frontend/dist/

# 检查服务状态
sudo systemctl status poweredu-ai-gunicorn
sudo systemctl status nginx

# 检查端口监听
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :8000
```

### 📞 还有问题？

如果仍然遇到问题：

1. **检查错误日志**：
   ```bash
   sudo journalctl -u poweredu-ai-gunicorn -f
   tail -f /var/log/nginx/error.log
   ```

2. **手动构建测试**：
   ```bash
   cd frontend
   npm run dev  # 开发模式测试
   ```

3. **降级 Node.js**（如果必要）：
   ```bash
   # 安装 Node.js 16 LTS
   curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

---

💡 **提示**：修复完成后，建议将修改推送到 GitHub 仓库，避免下次部署时遇到相同问题。
