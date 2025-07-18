#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中的模型配置
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu.settings')
django.setup()

from apps.knowledge.models import ModelConfig

def check_model_configs():
    """检查模型配置"""
    print("====== 检查数据库中的模型配置 ======")
    
    # 检查所有模型配置
    all_configs = ModelConfig.objects.all()
    print(f"数据库中总共有 {all_configs.count()} 个模型配置")
    
    for config in all_configs:
        print(f"\n配置ID: {config.id}")
        print(f"名称: {config.name}")
        print(f"模型类型: {config.model_type}")
        print(f"模型名称: {config.model_name}")
        print(f"API基础URL: {config.api_base_url}")
        print(f"是否激活: {config.is_active}")
        print(f"是否默认: {config.is_default}")
        print(f"API密钥: {config.api_key[:10]}..." if config.api_key else "无")
        print(f"创建时间: {config.created_at}")
        print("-" * 50)
    
    # 检查激活的Gemini配置
    print("\n====== 检查激活的Gemini配置 ======")
    gemini_configs = ModelConfig.objects.filter(
        model_name__icontains='gemini',
        is_active=True
    )
    
    print(f"找到 {gemini_configs.count()} 个激活的Gemini配置")
    for config in gemini_configs:
        print(f"配置ID: {config.id}, 名称: {config.name}, 模型: {config.model_name}")
    
    # 检查默认配置
    print("\n====== 检查默认配置 ======")
    default_configs = ModelConfig.objects.filter(is_default=True)
    print(f"找到 {default_configs.count()} 个默认配置")
    for config in default_configs:
        print(f"配置ID: {config.id}, 名称: {config.name}, 模型: {config.model_name}")

if __name__ == "__main__":
    check_model_configs()
