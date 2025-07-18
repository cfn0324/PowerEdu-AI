# 大文件上传配置说明

## 问题解决方案

如果您遇到大于10MB的文件上传失败，我们已经实施了以下解决方案：

### 1. 后端配置优化

**Django设置 (backend/edu/settings.py):**
- `FILE_UPLOAD_MAX_MEMORY_SIZE`: 500MB
- `DATA_UPLOAD_MAX_MEMORY_SIZE`: 500MB  
- `FILE_UPLOAD_HANDLERS`: 优化的文件上传处理器
- `FILE_UPLOAD_PERMISSIONS`: 适当的文件权限

### 2. 上传接口优化

**单文件上传 (/api/knowledge/documents/upload):**
- 文件大小限制: 500MB
- 分块写入: 8KB chunks，减少内存使用
- 唯一文件名: 防止文件名冲突
- 详细错误处理和日志记录

**批量上传 (/api/knowledge/documents/{kb_id}/batch-upload):**
- 支持多文件上传，每个文件最大500MB
- 独立处理每个文件，失败不影响其他文件
- 详细的上传结果统计

### 3. 前端优化

**文件大小检查:**
- 前端预检查: 500MB限制
- 明确的错误提示
- 上传进度显示

### 4. 测试验证

运行以下命令测试大文件上传功能：

```bash
cd backend
python test_large_file_upload.py
```

### 5. 生产环境配置

如果在生产环境中部署，请确保：

**Nginx配置 (如果使用):**
```nginx
client_max_body_size 500M;
client_body_timeout 300s;
```

**Apache配置 (如果使用):**
```apache
LimitRequestBody 524288000  # 500MB
```

**uWSGI配置 (如果使用):**
```ini
post-buffering = 8192
buffer-size = 65536
```

### 6. 监控和日志

大文件上传过程会产生详细的日志，包括：
- 文件保存过程
- 文档处理进度
- 错误详情和堆栈跟踪

查看日志以监控上传状态：
```bash
# Django开发服务器会在终端显示日志
# 或者在生产环境中查看日志文件
```

### 7. 性能建议

对于特别大的文件（>100MB），建议：
- 使用批量上传时分批处理
- 在网络条件较好的环境下进行
- 考虑对大文件进行预处理或分割

### 8. 故障排除

如果仍然遇到问题：

1. **检查磁盘空间**: 确保有足够的存储空间
2. **内存使用**: 大文件处理需要足够的内存
3. **网络超时**: 检查网络连接稳定性
4. **日志查看**: 查看后端日志获取详细错误信息

现在您可以上传最大500MB的单个文件！
