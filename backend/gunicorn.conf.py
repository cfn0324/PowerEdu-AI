# Gunicorn配置文件
# 保存为 gunicorn.conf.py

import multiprocessing

# 服务器套接字
bind = "127.0.0.1:8000"
backlog = 2048

# 工作进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# 重启
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 调试
reload = False
daemon = False

# 日志
accesslog = "/var/www/poweredu-ai/logs/gunicorn_access.log"
errorlog = "/var/www/poweredu-ai/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 进程命名
proc_name = "poweredu_ai"

# 安全
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
