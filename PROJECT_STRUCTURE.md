# 🔌 PowerEdu-AI 项目结构

> 电力知识库与AI预测平台的完整项目结构

## 📁 项目目录结构

```
PowerEdu-AI/
├── 📁 backend/                    # Django后端服务
│   ├── 📁 ai_prediction/          # AI预测模块
│   │   ├── data_generator.py       # 数据生成器
│   │   ├── data_preprocessor.py    # 数据预处理
│   │   ├── model_manager.py        # 模型管理
│   │   ├── predictor.py           # 预测引擎
│   │   └── visualizer.py          # 数据可视化
│   ├── 📁 apps/                   # Django应用模块
│   │   ├── 📁 core/               # 核心公共模块
│   │   ├── 📁 user/               # 用户管理模块
│   │   ├── 📁 course/             # 课程管理模块
│   │   ├── 📁 knowledge/          # 知识库问答模块
│   │   ├── 📁 prediction/         # AI预测模块
│   │   └── 📁 achievement/        # 成就系统模块
│   ├── 📁 edu/                    # Django项目配置
│   │   ├── settings.py            # 项目设置
│   │   ├── urls.py                # URL路由
│   │   └── wsgi.py                # WSGI配置
│   ├── 📁 media/                  # 媒体文件目录
│   ├── admin_manager.py           # 前端管理员工具
│   ├── manage.py                  # Django管理脚本
│   └── db.sqlite3                 # SQLite数据库
├── 📁 frontend/                   # React前端应用
│   ├── 📁 public/                 # 静态资源
│   ├── 📁 src/                    # 源代码
│   │   ├── 📁 components/         # React组件
│   │   ├── 📁 pages/              # 页面组件
│   │   ├── 📁 hooks/              # 自定义Hook
│   │   ├── 📁 service/            # API服务
│   │   ├── 📁 stores/             # 状态管理
│   │   ├── 📁 router/             # 路由配置
│   │   └── 📁 assets/             # 资源文件
│   ├── package.json               # NPM依赖配置
│   ├── vite.config.js             # Vite构建配置
│   └── index.html                 # 入口HTML
├── .env.example                   # 环境变量示例
├── .gitignore                     # Git忽略文件
├── LICENSE                        # 开源协议
├── PROJECT_STRUCTURE.md           # 项目结构文档(本文件)
├── README.md                      # 项目说明文档
├── requirements.txt               # Python依赖
├── start.ps1                      # Windows启动脚本
└── start.sh                       # Linux/Mac启动脚本
```

## 🎯 核心模块说明

### 后端模块 (backend/)

#### 🤖 AI预测系统 (ai_prediction/)
- **data_generator.py**: 电力负荷数据生成与模拟
- **data_preprocessor.py**: 数据清洗与特征工程
- **model_manager.py**: 机器学习模型管理
- **predictor.py**: 负荷预测引擎
- **visualizer.py**: 预测结果可视化

#### 📚 应用模块 (apps/)
- **core/**: 公共工具和基础服务
- **user/**: 用户认证、权限管理、成就系统
- **course/**: 在线课程、学习进度管理
- **knowledge/**: 知识库管理、智能问答(RAG)
- **prediction/**: AI预测接口、模型配置
- **achievement/**: 成就系统、积分奖励

### 前端模块 (frontend/)

#### 🎨 用户界面 (src/)
- **components/**: 可复用UI组件
- **pages/**: 页面级组件(登录、课程、预测、知识库)
- **hooks/**: 自定义React Hook
- **service/**: API调用服务
- **stores/**: Zustand状态管理
- **router/**: React Router路由配置

## 🚀 启动方式

### 一键启动
```bash
# Windows
.\start.ps1

# Linux/Mac  
./start.sh
```

### 手动启动
```bash
# 后端
cd backend
python manage.py migrate
python manage.py init_data
python manage.py init_achievements
python manage.py runserver

# 前端
cd frontend
npm install
npm run dev
```

## 🔧 技术栈

### 后端技术
- **Django 4.2.7**: Web框架
- **Python 3.8+**: 编程语言
- **SQLite**: 数据库
- **scikit-learn**: 机器学习
- **XGBoost**: 梯度提升算法
- **Django Ninja**: API框架

### 前端技术
- **React 18.2.0**: UI框架
- **Ant Design 5.x**: 组件库
- **Vite 3.2.3**: 构建工具
- **Zustand**: 状态管理
- **React Router**: 路由管理

### AI技术
- **RAG技术**: 检索增强生成
- **Gemini API**: 大语言模型
- **向量检索**: 文档相似度搜索
- **机器学习**: 多算法电力负荷预测

## 🌐 访问地址

- **前端应用**: http://localhost:5173
- **知识库问答**: http://localhost:5173/knowledge  
- **AI预测**: http://localhost:5173/prediction
- **后端API**: http://localhost:8000/api
- **管理后台**: http://localhost:8000/admin

## 📄 开源协议

本项目采用 [MIT License](./LICENSE) 开源协议。
