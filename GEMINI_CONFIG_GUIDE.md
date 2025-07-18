# 🤖 Gemini API 配置指南

## 配置步骤

### 1. 获取Gemini API密钥
1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 创建新的API密钥
3. 复制生成的API密钥

### 2. 在系统中配置Gemini模型

#### 通过前端界面配置
1. 登录系统
2. 进入知识库页面
3. 点击"模型配置"
4. 点击"新增配置"
5. 填写以下信息：
   - **配置名称**: Gemini Pro
   - **模型类型**: API模式
   - **模型名称**: gemini-pro
   - **API密钥**: 你的Gemini API密钥
   - **API基础URL**: https://generativelanguage.googleapis.com
   - **最大Token数**: 4096
   - **温度参数**: 0.7
   - **设为默认**: 是

⚠️ **重要提示**: Gemini API使用v1beta版本，系统会自动构建正确的URL格式：
`https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent`

#### 通过Django Admin配置
1. 访问 `/admin/` 管理界面
2. 进入"Knowledge" → "Model configs"
3. 点击"Add model config"
4. 填写配置信息

### 3. 测试配置

#### 方法1: 使用测试脚本
```bash
cd backend
python test_gemini_api.py
```

#### 方法2: 通过前端测试
1. 进入模型配置页面
2. 点击对应配置的"测试连接"按钮
3. 查看测试结果

#### 方法3: 使用健康检查接口
```bash
curl http://localhost:8000/api/knowledge/health
```

### 4. 在智能问答中使用

1. 进入知识库智能问答页面
2. 在模型选择下拉框中选择"Gemini Pro"
3. 输入问题进行测试

## 常见问题

### Q1: 提示"API调用失败"
**解决方案**:
- 检查API密钥是否正确
- 确认网络连接正常
- 检查API配额是否用完

### Q2: 仍然返回"没有找到相关信息"
**解决方案**:
- 确认已选择正确的模型配置
- 检查模型配置是否设为默认
- 查看后端日志确认API调用情况

### Q3: 响应很慢
**解决方案**:
- 检查网络连接
- 降低max_tokens设置
- 调整temperature参数

## 配置示例

```json
{
  "name": "Gemini Pro",
  "description": "Google Gemini Pro模型",
  "model_type": "api",
  "model_name": "gemini-pro",
  "api_key": "your-api-key-here",
  "api_base_url": "https://generativelanguage.googleapis.com",
  "max_tokens": 4096,
  "temperature": 0.7,
  "is_default": true,
  "is_active": true
}
```

## 支持的模型

- **gemini-pro**: 最新的Gemini Pro模型
- **gemini-pro-vision**: 支持图像输入的Gemini Pro模型（未来版本支持）

## API限制

- 每分钟请求数: 60
- 每天请求数: 1500（免费层）
- 单次请求最大Token数: 30,720（输入） + 2,048（输出）

## 故障排查

### 启用调试日志
在Django settings.py中添加：
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'apps.knowledge': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### 检查API调用日志
查看后端日志文件或控制台输出中的API调用详情。
