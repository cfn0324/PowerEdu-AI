# 环境

Python3.8 +

# 使用

# 运行后端

## 如果删除了 db.sqlite3 或者更换 Mysql 时需要做下面的操作，否则可以跳过

```shell
# 生成表
python manage.py migrate
```

```shell
# 创建管理员账号
python manage.py createsuperuser
```

# 运行

```
python manage.py runserver
```

# 访问后台

> 后台账号密码 admin 123456
> http://127.0.0.1:8000/admin
