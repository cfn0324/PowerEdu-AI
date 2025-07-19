# 🔌 PowerEdu-AI 电力知识库与AI预测平台

> 集成电力知识库在线学习与AI负荷预测功能的企业级智能平台

[![Python](https://img.shields.io/badge/Python-3.8+-3776ab.svg?logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2.7-092e20.svg?logo=django&logoColor=white)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-18.2.0-61dafb.svg?logo=react&logoColor=black)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## 📋 项目概述

PowerEdu-AI是一个面向电力行业的综合性智能教育平台，集成了知识库管理、在线学习和AI负荷预测等核心功能。

### 🎯 核心功能

- **📚 在线教育**: 用户管理、课程学习、成就系统
- **🤖 AI预测**: 多模型电力负荷预测与分析  
- **📊 数据可视化**: 交互式图表与性能监控
- **🧠 智能问答**: 基于RAG技术的知识库问答系统

## 🚀 快速启动

### 系统要求
- **Python**: 3.8+
- **Node.js**: 18.15+
- **内存**: 4GB+

### 一键启动

**Windows**:
```powershell
.\start.ps1
```

**Linux/Mac**:
```bash
chmod +x start.sh && ./start.sh
```

## 🔧 管理员配置

启动成功后，创建管理员账户：

```bash
# 进入后端目录
cd backend

# 创建前端管理员
python admin_manager.py create

# 创建Django超级用户
python manage.py createsuperuser

# 初始化成就系统
python manage.py init_achievements
```
```

2. **启动后端**
```bash
cd backend
python manage.py migrate
python manage.py init_data  # 创建默认admin用户
python manage.py init_achievements  # 初始化成就系统
python manage.py runserver
```

3. **启动前端**
```bash
cd frontend
npm run dev
```

4. **AI系统初始化**

访问 `http://localhost:5173/prediction` 并点击"初始化AI系统"按钮完成机器学习模型的训练和配置。

## 🌐 访问地址

- **前端界面**: http://localhost:5173
- **知识库问答**: http://localhost:5173/knowledge
- **AI预测**: http://localhost:5173/prediction  
- **后端API**: http://localhost:8000/api
- **管理后台**: http://localhost:8000/admin

### 🔑 默认账户

系统提供两套管理员系统：

#### 前端管理系统
- **访问地址**: http://localhost:5173
- **用户名**: admin
- **密码**: 123456
- **功能**: 课程管理、用户管理、AI预测、知识库管理等业务功能

#### Django Admin 后台
- **访问地址**: http://localhost:8000/admin  
- **用户名**: admin
- **密码**: admin123
- **功能**: 数据库管理、系统配置、模型管理等底层管理

> 注意：首次运行时，启动脚本会自动执行 `python manage.py init_data` 和 `python manage.py init_achievements` 命令来创建默认账户和初始化成就系统。

### 🛠️ 管理员工具

```bash
## 🏗️ 技术架构

### 后端技术
- **Django 4.2.7** - Web框架
- **Python 3.8+** - 编程语言  
- **SQLite** - 数据库
- **scikit-learn** - 机器学习
- **XGBoost** - 梯度提升算法

### 前端技术
- **React 18.2.0** - UI框架
- **Ant Design 5.x** - 组件库
- **Vite 3.2.3** - 构建工具

### 核心功能模块
- **AI预测系统**: 多种机器学习算法的电力负荷预测
- **知识库系统**: 基于RAG技术的智能问答
- **在线学习**: 课程管理与成就系统
- **数据可视化**: 交互式图表展示

## 📄 开源协议

本项目采用 [MIT License](./LICENSE) 开源协议。

---

**🚀 立即开始：执行 `.\start.ps1` (Windows) 或 `./start.sh` (Linux/Mac) 启动平台！**
