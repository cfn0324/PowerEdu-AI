#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最简单的验证脚本
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu.settings')
django.setup()

print("Django环境设置成功")

from apps.knowledge.models import ModelConfig
print("模型导入成功")

# 检查配置
config = ModelConfig.objects.filter(model_name__icontains='gemini', is_active=True).first()
if config:
    print(f"找到配置: {config.model_name}")
    print("所有检查完成")
else:
    print("未找到配置")
