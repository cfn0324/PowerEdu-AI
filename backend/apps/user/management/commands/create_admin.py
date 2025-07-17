#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建默认管理员用户的Django管理命令
已弃用：请使用 python admin_manager.py create 命令
"""

import sys
import os
from django.core.management.base import BaseCommand

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from admin_manager import AdminManager
except ImportError:
    # 如果无法导入，则使用原始方法
    from django.contrib.auth.hashers import make_password
    from apps.user.models import User
    AdminManager = None


class Command(BaseCommand):
    help = '创建默认管理员用户 (admin/123456) - 推荐使用 python admin_manager.py create'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username', '-u',
            type=str,
            default='admin',
            help='用户名 (默认: admin)'
        )
        parser.add_argument(
            '--password', '-p',
            type=str,
            default='123456',
            help='密码 (默认: 123456)'
        )
        parser.add_argument(
            '--nickname', '-n',
            type=str,
            default='系统管理员',
            help='昵称 (默认: 系统管理员)'
        )
        parser.add_argument(
            '--force', '-f',
            action='store_true',
            help='强制覆盖已存在的用户'
        )

    def handle(self, *args, **options):
        """执行命令"""
        self.stdout.write(
            self.style.WARNING(
                '⚠️  此命令已弃用，推荐使用: python admin_manager.py create\n'
                '   新工具提供更多功能和更好的用户体验\n'
            )
        )
        
        username = options['username']
        password = options['password']
        nickname = options['nickname']
        force = options['force']
        
        if AdminManager:
            # 使用新的管理器
            manager = AdminManager()
            manager.create_admin(username, password, nickname, force)
        else:
            # 回退到原始方法
            self.create_admin_fallback(username, password, nickname, force)

    def create_admin_fallback(self, username, password, nickname, force):
        """回退方法：创建管理员用户"""
        try:
            # 检查用户是否已存在
            existing_user = User.objects.filter(username=username).first()
            if existing_user:
                if force:
                    existing_user.delete()
                    self.stdout.write(f"⚠️  已删除现有用户: {username}")
                else:
                    self.stdout.write(
                        self.style.WARNING(f'管理员用户 "{username}" 已存在，跳过创建')
                    )
                    return

            # 创建管理员用户
            admin_user = User.objects.create(
                username=username,
                nickname=nickname,
                password=make_password(password)
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'成功创建管理员用户:\n'
                    f'  用户名: {admin_user.username}\n'
                    f'  密码: {password}\n'
                    f'  昵称: {admin_user.nickname}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'创建管理员用户失败: {str(e)}')
            )
