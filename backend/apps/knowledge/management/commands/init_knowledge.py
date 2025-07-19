#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化知识库系统的Django管理命令
"""

from django.core.management.base import BaseCommand
from apps.knowledge.models import ModelConfig, KnowledgeBase


class Command(BaseCommand):
    help = '初始化知识库系统数据'

    def handle(self, *args, **options):
        """执行命令"""
        self.stdout.write('开始初始化知识库系统数据...\n')
        
        # 创建默认的Gemini模型配置
        try:
            gemini_config, created = ModelConfig.objects.get_or_create(
                name="Gemini默认配置",
                defaults={
                    'provider': 'google',
                    'model_name': 'gemini-2.0-flash-exp',
                    'api_key': 'your-gemini-api-key-here',
                    'api_base_url': 'https://generativelanguage.googleapis.com/v1beta/models',
                    'temperature': 0.1,
                    'max_tokens': 8192,
                    'is_active': True,
                    'description': '默认的Google Gemini配置，支持知识库问答'
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 创建默认Gemini配置: {gemini_config.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Gemini配置已存在: {gemini_config.name}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ 创建Gemini配置失败: {str(e)}')
            )
        
        # 创建默认知识库（如果不存在）
        try:
            # 需要一个默认用户来创建知识库
            from apps.user.models import User
            admin_user = User.objects.filter(username='admin').first()
            
            if admin_user:
                kb, created = KnowledgeBase.objects.get_or_create(
                    name="电力系统知识库",
                    defaults={
                        'description': '电力系统相关技术文档和学习资料的知识库',
                        'created_by': admin_user,
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ 创建默认知识库: {kb.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'- 默认知识库已存在: {kb.name}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING('- 未找到admin用户，跳过创建默认知识库')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ 创建默认知识库失败: {str(e)}')
            )
        
        self.stdout.write('\n' + self.style.SUCCESS('知识库系统初始化完成！'))
        self.stdout.write('请在Django Admin中配置正确的Gemini API密钥。')
