# 🏆 成就系统故障排除指南

## 问题描述
观看视频后，学习成就页面无法正常打开或显示异常。

## 🔍 可能的原因

### 1. 成就系统未初始化
**症状**: 页面显示"成就系统暂无数据"
**解决方案**:
```bash
cd backend
python manage.py init_achievements
```

### 2. 数据库迁移未完成
**症状**: 控制台报错相关数据表不存在
**解决方案**:
```bash
cd backend
python manage.py migrate
```

### 3. 用户认证问题
**症状**: 页面显示"登录已过期"
**解决方案**:
- 重新登录系统
- 清除浏览器缓存和本地存储

### 4. API服务异常
**症状**: 网络请求失败
**解决方案**:
- 确保后端服务正在运行: `python manage.py runserver`
- 检查服务器日志中的错误信息

## 🛠️ 快速修复步骤

### 🎯 立即可用方案: 静态演示模式
如果您需要立即查看成就系统功能，可以使用静态演示模式：

1. **访问成就页面**: 进入 `http://localhost:5173/achievement`
2. **启用静态模式**: 
   - 如果页面显示错误，点击"使用静态演示"按钮
   - 或者在页面顶部找到切换开关，选择"静态"模式
3. **功能演示**: 静态模式包含完整的UI展示和模拟数据

### 一键修复脚本 (Windows)
```bash
# 在项目根目录运行
./fix_achievement_system.bat
```

### 手动修复步骤
```bash
# 1. 进入后端目录
cd backend

# 2. 数据库迁移
python manage.py migrate

# 3. 创建管理员账户(如果不存在)
python admin_manager.py create

# 4. 初始化成就数据
python manage.py init_achievements

# 5. 重启服务
python manage.py runserver
```

## 🔧 调试技巧

### 1. 使用静态演示模式
- **优点**: 立即可用，不依赖后端API
- **适用**: 前端功能演示、UI测试、用户体验评估
- **切换方式**: 页面顶部的模式切换开关

### 2. 查看控制台日志
打开浏览器开发者工具(F12)，查看Console标签页中的错误信息。

### 3. 检查网络请求
在Network标签页中查看API请求是否成功返回。

### 4. 查看后端日志
运行后端服务时观察终端输出的日志信息。

## 📋 预防措施

### 1. 确保完整的系统初始化
首次部署时按照README.md中的步骤完整执行:
```bash
cd backend
python manage.py migrate
python admin_manager.py create
python manage.py init_achievements
python manage.py init_knowledge
```

### 2. 定期备份数据
```bash
# 备份数据库
cd backend
python manage.py dumpdata > backup.json
```

### 3. 监控系统日志
定期检查后端服务日志，及时发现和解决问题。

## 🆘 联系支持

如果按照上述步骤仍无法解决问题，请:

1. 提供详细的错误信息和步骤
2. 包含浏览器控制台的错误截图
3. 提供后端服务器的日志信息

---

**最后更新**: 2025年7月19日
**版本**: PowerEdu-AI v1.0
