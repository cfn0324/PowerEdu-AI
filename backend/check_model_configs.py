#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查模型配置
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu.settings')
django.setup()

from apps.knowledge.models import ModelConfig

def check_model_configs():
    """检查模型配置"""
    print("=" * 60)
    print("模型配置检查")
    print("=" * 60)
    
    configs = ModelConfig.objects.all()
    print(f"模型配置总数: {configs.count()}")
    
    for config in configs:
        print(f"\n模型配置: {config.name}")
        print(f"  ID: {config.id}")
        print(f"  类型: {config.model_type}")
        print(f"  模型名: {config.model_name}")
        print(f"  激活状态: {config.is_active}")
        print(f"  API密钥: {'已设置' if config.api_key else '未设置'}")
        print(f"  API基础URL: {config.api_base_url}")
        print(f"  创建时间: {config.created_at}")
    
    # 检查激活的配置
    active_configs = ModelConfig.objects.filter(is_active=True)
    print(f"\n激活的配置数: {active_configs.count()}")
    
    if active_configs.exists():
        default_config = active_configs.first()
        print(f"默认配置: {default_config.name} (ID: {default_config.id})")
        return default_config
    else:
        print("没有激活的配置")
        return None

if __name__ == "__main__":
    check_model_configs()
