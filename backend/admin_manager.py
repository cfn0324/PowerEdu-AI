#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PowerEdu-AI 管理员管理工具 (简化版)

核心功能：
- 创建管理员用户
- 重置密码
- 验证密码

使用方法：
python admin_manager.py create         # 创建默认管理员
python admin_manager.py reset admin    # 重置密码
python admin_manager.py verify admin 123456  # 验证密码
"""

import os
import sys
import argparse
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu.settings')
django.setup()

from apps.user.models import User
from django.contrib.auth.hashers import make_password, check_password


class AdminManager:
    """管理员管理类"""
    
    def __init__(self):
        self.default_username = 'admin'
        self.default_password = '123456'
        self.default_nickname = '系统管理员'
    
    def create_admin(self, username=None, password=None, nickname=None, force=False):
        """创建管理员用户"""
        username = username or self.default_username
        password = password or self.default_password
        nickname = nickname or self.default_nickname
        
        try:
            existing_user = User.objects.filter(username=username).first()
            if existing_user:
                if force:
                    existing_user.delete()
                    print(f"⚠️  已删除现有用户: {username}")
                else:
                    print(f"❌ 用户 '{username}' 已存在。使用 --force 参数强制覆盖")
                    return False
            
            admin_user = User.objects.create(
                username=username,
                nickname=nickname,
                password=make_password(password)
            )
            
            print(f"✅ 成功创建管理员用户:")
            print(f"   用户名: {admin_user.username}")
            print(f"   密码: {password}")
            print(f"   昵称: {admin_user.nickname}")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建管理员用户失败: {str(e)}")
            return False
    
    def reset_password(self, username, new_password=None):
        """重置用户密码"""
        new_password = new_password or self.default_password
        
        try:
            user = User.objects.get(username=username)
            user.password = make_password(new_password)
            user.save()
            
            print(f"✅ 成功重置用户密码:")
            print(f"   用户名: {user.username}")
            print(f"   新密码: {new_password}")
            
            return True
            
        except User.DoesNotExist:
            print(f"❌ 用户 '{username}' 不存在")
            return False
        except Exception as e:
            print(f"❌ 重置密码失败: {str(e)}")
            return False
    
    def verify_password(self, username, password):
        """验证用户密码"""
        try:
            user = User.objects.get(username=username)
            is_valid = check_password(password, user.password)
            
            print(f"🔍 密码验证结果:")
            print(f"   用户名: {user.username}")
            print(f"   密码验证: {'✅ 正确' if is_valid else '❌ 错误'}")
            
            return is_valid
            
        except User.DoesNotExist:
            print(f"❌ 用户 '{username}' 不存在")
            return False
        except Exception as e:
            print(f"❌ 验证密码失败: {str(e)}")
            return False
    
    def init_system_data(self):
        """初始化系统数据（创建默认管理员）"""
        print("🔄 初始化系统数据...")
        success = self.create_admin()
        
        if success:
            print("\n✅ 系统数据初始化完成!")
            print("🔑 可以使用以下账户登录:")
            print(f"   用户名: {self.default_username}")
            print(f"   密码: {self.default_password}")
        else:
            print("\n⚠️  系统数据初始化完成，但管理员用户已存在")
        
        return success


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='PowerEdu-AI 管理员管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 创建管理员命令
    create_parser = subparsers.add_parser('create', help='创建管理员用户')
    create_parser.add_argument('-u', '--username', default='admin', help='用户名 (默认: admin)')
    create_parser.add_argument('-p', '--password', default='123456', help='密码 (默认: 123456)')
    create_parser.add_argument('-n', '--nickname', default='系统管理员', help='昵称 (默认: 系统管理员)')
    create_parser.add_argument('-f', '--force', action='store_true', help='强制覆盖已存在的用户')
    
    # 重置密码命令
    reset_parser = subparsers.add_parser('reset', help='重置用户密码')
    reset_parser.add_argument('username', help='用户名')
    reset_parser.add_argument('-p', '--password', default='123456', help='新密码 (默认: 123456)')
    
    # 验证密码命令
    verify_parser = subparsers.add_parser('verify', help='验证用户密码')
    verify_parser.add_argument('username', help='用户名')
    verify_parser.add_argument('password', help='密码')
    
    # 初始化系统数据命令
    init_parser = subparsers.add_parser('init', help='初始化系统数据')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = AdminManager()
    print("🔌 PowerEdu-AI 管理员管理工具")
    print("=" * 40)
    
    if args.command == 'create':
        manager.create_admin(args.username, args.password, args.nickname, args.force)
    elif args.command == 'reset':
        manager.reset_password(args.username, args.password)
    elif args.command == 'verify':
        manager.verify_password(args.username, args.password)
    elif args.command == 'init':
        manager.init_system_data()


if __name__ == "__main__":
    main()
