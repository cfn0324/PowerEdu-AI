#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化系统默认数据的Django管理命令
"""

import sys
import os
from django.core.management.base import BaseCommand

# 添加项目根目录到路径，以便导入admin_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from admin_manager import AdminManager
except ImportError:
    # 如果无法导入，则使用原始方法
    from django.contrib.auth.hashers import make_password
    from apps.user.models import User
    AdminManager = None


class Command(BaseCommand):
    help = '初始化系统默认数据'

    def handle(self, *args, **options):
        """执行命令"""
        self.stdout.write('开始初始化系统默认数据...\n')
        
        if AdminManager:
            # 使用新的管理器
            manager = AdminManager()
            
            # 创建自定义用户模型的管理员
            custom_success = manager.create_admin()
            
            if custom_success:
                self.stdout.write(self.style.SUCCESS('\n✅ 系统默认数据初始化完成！'))
                self.stdout.write('🔑 可以使用以下账户:')
                self.stdout.write('   【前端登录】用户名: admin, 密码: 123456')
                self.stdout.write('   Django Admin地址: http://localhost:8000/admin')
            else:
                self.stdout.write(self.style.WARNING('\n⚠️  管理员用户已存在，跳过创建'))
        else:
            # 回退到原始方法
            self.create_admin_user_fallback()
            self.stdout.write(self.style.SUCCESS('\n✅ 系统默认数据初始化完成！'))

    def create_admin_user_fallback(self):
        """回退方法：创建默认管理员用户"""
        try:
            # 检查admin用户是否已存在
            if User.objects.filter(username='admin').exists():
                self.stdout.write('  - 管理员用户 "admin" 已存在，跳过创建')
                return

            # 创建admin用户
            admin_user = User.objects.create(
                username='admin',
                nickname='系统管理员',
                password=make_password('123456')  # 对密码进行哈希处理
            )
            
            self.stdout.write(f'  - 成功创建管理员用户: {admin_user.username}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  - 创建管理员用户失败: {str(e)}')
            )
