#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建默认模型配置
"""

from django.db import migrations
from django.contrib.auth.models import User


def create_default_model_configs(apps, schema_editor):
    """创建默认的模型配置"""
    ModelConfig = apps.get_model('knowledge', 'ModelConfig')
    
    # 创建默认模型配置
    configs = [
        {
            'name': 'Mock模型 (测试用)',
            'model_type': 'api',
            'provider': 'mock',
            'model_name': 'mock-model',
            'api_key': '',
            'api_base_url': '',
            'model_path': '',
            'max_tokens': 4096,
            'temperature': 0.7,
            'is_active': True,
            'is_default': True
        },
        {
            'name': 'OpenAI GPT-3.5',
            'model_type': 'api',
            'provider': 'openai',
            'model_name': 'gpt-3.5-turbo',
            'api_key': '',
            'api_base_url': 'https://api.openai.com/v1',
            'model_path': '',
            'max_tokens': 4096,
            'temperature': 0.7,
            'is_active': False,
            'is_default': False
        },
        {
            'name': 'OpenAI GPT-4',
            'model_type': 'api',
            'provider': 'openai',
            'model_name': 'gpt-4',
            'api_key': '',
            'api_base_url': 'https://api.openai.com/v1',
            'model_path': '',
            'max_tokens': 8192,
            'temperature': 0.7,
            'is_active': False,
            'is_default': False
        },
        {
            'name': '智谱AI ChatGLM',
            'model_type': 'api',
            'provider': 'zhipu',
            'model_name': 'chatglm_6b',
            'api_key': '',
            'api_base_url': 'https://open.bigmodel.cn/api/paas/v3',
            'model_path': '',
            'max_tokens': 4096,
            'temperature': 0.7,
            'is_active': False,
            'is_default': False
        }
    ]
    
    for config_data in configs:
        ModelConfig.objects.get_or_create(
            name=config_data['name'],
            defaults=config_data
        )


def reverse_create_default_model_configs(apps, schema_editor):
    """删除默认的模型配置"""
    ModelConfig = apps.get_model('knowledge', 'ModelConfig')
    ModelConfig.objects.filter(
        name__in=[
            'Mock模型 (测试用)',
            'OpenAI GPT-3.5', 
            'OpenAI GPT-4',
            '智谱AI ChatGLM'
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('knowledge', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_default_model_configs,
            reverse_create_default_model_configs
        ),
    ]
