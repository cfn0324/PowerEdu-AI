# 管理员管理工具使用指南

## 概述

`admin_manager.py` 是PowerEdu-AI平台的统一管理员管理工具，支持两种用户系统：
- **自定义用户模型**：用于前端API登录
- **Django用户模型**：用于Django Admin后台管理

## 功能特性

- ✅ 创建管理员用户（自定义用户模型）
- ✅ 创建Django超级用户（Django Admin）
- ✅ 重置用户密码
- ✅ 验证用户密码
- ✅ 查看用户信息
- ✅ 列出所有用户
- ✅ 删除用户
- ✅ 初始化系统数据

## 重要说明

**PowerEdu-AI项目使用了两套用户系统：**

1. **自定义用户模型** (`apps.user.models.User`)
   - 用于前端API登录
   - 存储用户昵称、头像等扩展信息
   - 登录地址：http://localhost:5173

2. **Django用户模型** (`django.contrib.auth.models.User`)
   - 用于Django Admin后台管理
   - 具有超级用户权限
   - 登录地址：http://localhost:8000/admin

## 使用方法

### 1. 基本命令

```bash
# 查看帮助
python admin_manager.py --help

# 查看子命令帮助
python admin_manager.py create --help
```

### 2. 创建管理员

```bash
# 创建默认自定义用户管理员 (admin/123456)
python admin_manager.py create

# 创建Django Admin超级用户 (admin/123456)
python admin_manager.py create-django

# 创建自定义管理员
python admin_manager.py create -u myuser -p mypass -n "我的管理员"

# 强制覆盖已存在的用户
python admin_manager.py create -f
```

### 3. 用户列表管理

```bash
# 列出自定义用户
python admin_manager.py list

# 列出Django用户
python admin_manager.py list --django
```

### 4. 系统初始化

```bash
# 初始化系统数据（同时创建两种用户）
python admin_manager.py init
```

### 5. 诊断工具

```bash
# 运行登录诊断
python login_diagnostic.py
```

### 3. 密码管理

```bash
# 重置admin密码为默认密码(123456)
python admin_manager.py reset admin

# 重置admin密码为自定义密码
python admin_manager.py reset admin -p newpassword

# 验证用户密码
python admin_manager.py verify admin 123456
```

### 4. 用户信息管理

```bash
# 查看用户信息
python admin_manager.py info admin

# 列出所有用户
python admin_manager.py list

# 删除用户
python admin_manager.py delete testuser

# 强制删除用户（跳过确认）
python admin_manager.py delete testuser -f
```

### 5. 系统初始化

```bash
# 初始化系统数据（创建默认管理员）
python admin_manager.py init
```

## Django管理命令

除了直接使用`admin_manager.py`，您也可以使用Django管理命令：

```bash
# 初始化系统数据
python manage.py init_data

# 创建管理员（已弃用，推荐使用admin_manager.py）
python manage.py create_admin
```

## 默认账户信息

- **用户名**: admin
- **密码**: 123456
- **昵称**: 系统管理员

## 常见问题

### Q: 忘记管理员密码怎么办？
A: 使用重置密码命令：
```bash
python admin_manager.py reset admin
```

### Q: 如何创建多个管理员？
A: 使用不同的用户名创建：
```bash
python admin_manager.py create -u admin2 -p password2 -n "第二管理员"
```

### Q: 如何查看系统中有哪些用户？
A: 使用列表命令：
```bash
python admin_manager.py list
```

### Q: 误删用户怎么恢复？
A: 重新创建用户：
```bash
python admin_manager.py create -u username -p password -n "昵称"
```

## 安全建议

1. **修改默认密码**: 首次部署后请立即修改默认密码
2. **使用强密码**: 密码应包含大小写字母、数字和特殊字符
3. **定期更换**: 建议定期更换管理员密码
4. **限制访问**: 仅授权人员可以执行管理员操作

## 集成到启动脚本

新的管理器已经集成到系统启动脚本中，首次运行时会自动创建默认管理员账户。
