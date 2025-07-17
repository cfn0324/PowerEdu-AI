#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PowerEdu-AI 管理员管理工具

功能包括：
- 创建管理员用户
- 重置管理员密码
- 查看管理员信息
- 删除管理员用户
- 列出所有用户

使用方法：
python admin_manager.py --help
"""

import os
import sys
import argparse
import django
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu.settings')
django.setup()

from apps.user.models import User
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError


class AdminManager:
    """管理员管理类"""
    
    def __init__(self):
        self.default_username = 'admin'
        self.default_password = '123456'
        self.default_nickname = '系统管理员'
    
    def create_admin(self, username=None, password=None, nickname=None, force=False):
        """
        创建管理员用户
        
        Args:
            username (str): 用户名，默认为 'admin'
            password (str): 密码，默认为 '123456'
            nickname (str): 昵称，默认为 '系统管理员'
            force (bool): 是否强制覆盖已存在的用户
        """
        username = username or self.default_username
        password = password or self.default_password
        nickname = nickname or self.default_nickname
        
        try:
            # 检查用户是否已存在
            existing_user = User.objects.filter(username=username).first()
            if existing_user:
                if force:
                    existing_user.delete()
                    print(f"⚠️  已删除现有用户: {username}")
                else:
                    print(f"❌ 用户 '{username}' 已存在。使用 --force 参数强制覆盖")
                    return False
            
            # 创建新用户
            admin_user = User.objects.create(
                username=username,
                nickname=nickname,
                password=make_password(password)
            )
            
            print(f"✅ 成功创建管理员用户:")
            print(f"   用户名: {admin_user.username}")
            print(f"   密码: {password}")
            print(f"   昵称: {admin_user.nickname}")
            print(f"   创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建管理员用户失败: {str(e)}")
            return False
    
    def reset_password(self, username, new_password=None):
        """
        重置用户密码
        
        Args:
            username (str): 用户名
            new_password (str): 新密码，默认为 '123456'
        """
        new_password = new_password or self.default_password
        
        try:
            user = User.objects.get(username=username)
            user.password = make_password(new_password)
            user.save()
            
            print(f"✅ 成功重置用户密码:")
            print(f"   用户名: {user.username}")
            print(f"   新密码: {new_password}")
            print(f"   昵称: {user.nickname}")
            
            return True
            
        except User.DoesNotExist:
            print(f"❌ 用户 '{username}' 不存在")
            return False
        except Exception as e:
            print(f"❌ 重置密码失败: {str(e)}")
            return False
    
    def verify_password(self, username, password):
        """
        验证用户密码
        
        Args:
            username (str): 用户名
            password (str): 密码
        """
        try:
            user = User.objects.get(username=username)
            is_valid = check_password(password, user.password)
            
            print(f"🔍 密码验证结果:")
            print(f"   用户名: {user.username}")
            print(f"   密码验证: {'✅ 正确' if is_valid else '❌ 错误'}")
            print(f"   昵称: {user.nickname}")
            
            return is_valid
            
        except User.DoesNotExist:
            print(f"❌ 用户 '{username}' 不存在")
            return False
        except Exception as e:
            print(f"❌ 验证密码失败: {str(e)}")
            return False
    
    def show_user_info(self, username):
        """
        显示用户信息
        
        Args:
            username (str): 用户名
        """
        try:
            user = User.objects.get(username=username)
            
            print(f"👤 用户信息:")
            print(f"   用户名: {user.username}")
            print(f"   昵称: {user.nickname or '未设置'}")
            print(f"   头像: {user.avatar or '默认头像'}")
            print(f"   用户ID: {user.id}")
            
            return True
            
        except User.DoesNotExist:
            print(f"❌ 用户 '{username}' 不存在")
            return False
        except Exception as e:
            print(f"❌ 获取用户信息失败: {str(e)}")
            return False
    
    def list_all_users(self):
        """列出所有用户"""
        try:
            users = User.objects.all().order_by('id')
            
            if not users.exists():
                print("📭 系统中暂无用户")
                return True
            
            print(f"👥 系统用户列表 (共 {users.count()} 个用户):")
            print(f"{'ID':<5} {'用户名':<15} {'昵称':<20} {'头像':<30}")
            print("-" * 70)
            
            for user in users:
                avatar_str = str(user.avatar) if user.avatar else '默认'
                print(f"{user.id:<5} {user.username:<15} {user.nickname or '未设置':<20} {avatar_str:<30}")
            
            return True
            
        except Exception as e:
            print(f"❌ 获取用户列表失败: {str(e)}")
            return False
    
    def delete_user(self, username, force=False):
        """
        删除用户
        
        Args:
            username (str): 用户名
            force (bool): 是否强制删除（跳过确认）
        """
        try:
            user = User.objects.get(username=username)
            
            if not force:
                confirm = input(f"⚠️  确认删除用户 '{username}'? (y/N): ")
                if confirm.lower() != 'y':
                    print("❌ 取消删除操作")
                    return False
            
            user.delete()
            print(f"✅ 成功删除用户: {username}")
            
            return True
            
        except User.DoesNotExist:
            print(f"❌ 用户 '{username}' 不存在")
            return False
        except Exception as e:
            print(f"❌ 删除用户失败: {str(e)}")
            return False
    
    def init_system_data(self):
        """初始化系统数据（创建默认管理员）"""
        print("🔄 初始化系统数据...")
        
        # 创建自定义用户模型的默认管理员
        success = self.create_admin()
        
        # 创建Django Admin超级用户
        django_success = self.create_django_superuser()
        
        if success or django_success:
            print("\n✅ 系统数据初始化完成!")
            print("🔑 可以使用以下账户:")
            print(f"   【前端登录】用户名: {self.default_username}, 密码: {self.default_password}")
            print(f"   【Django Admin】用户名: {self.default_username}, 密码: {self.default_password}")
            print(f"   Django Admin地址: http://localhost:8000/admin")
        else:
            print("\n⚠️  系统数据初始化完成，但用户已存在")
        
        return success or django_success
    
    def create_django_superuser(self, username=None, password=None, email=None):
        """
        创建Django Admin超级用户
        
        Args:
            username (str): 用户名，默认为 'admin'
            password (str): 密码，默认为 '123456'
            email (str): 邮箱，默认为 'admin@example.com'
        """
        username = username or self.default_username
        password = password or self.default_password
        email = email or 'admin@example.com'
        
        try:
            # 检查Django用户是否已存在
            existing_user = DjangoUser.objects.filter(username=username).first()
            if existing_user:
                print(f"⚠️  Django超级用户 '{username}' 已存在")
                return False
            
            # 创建Django超级用户
            django_user = DjangoUser.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            print(f"✅ 成功创建Django超级用户:")
            print(f"   用户名: {django_user.username}")
            print(f"   密码: {password}")
            print(f"   邮箱: {django_user.email}")
            print(f"   超级用户: {django_user.is_superuser}")
            print(f"   Django Admin地址: http://localhost:8000/admin")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建Django超级用户失败: {str(e)}")
            return False
    
    def list_django_users(self):
        """列出所有Django用户"""
        try:
            users = DjangoUser.objects.all().order_by('id')
            
            if not users.exists():
                print("📭 Django用户系统中暂无用户")
                return True
            
            print(f"👥 Django用户列表 (共 {users.count()} 个用户):")
            print(f"{'ID':<5} {'用户名':<15} {'邮箱':<25} {'超级用户':<10} {'员工':<8}")
            print("-" * 70)
            
            for user in users:
                print(f"{user.id:<5} {user.username:<15} {user.email:<25} {'是' if user.is_superuser else '否':<10} {'是' if user.is_staff else '否':<8}")
            
            return True
            
        except Exception as e:
            print(f"❌ 获取Django用户列表失败: {str(e)}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='PowerEdu-AI 管理员管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s create                          # 创建默认管理员 (admin/123456)
  %(prog)s create -u myuser -p mypass      # 创建自定义管理员
  %(prog)s reset admin                     # 重置admin密码为123456
  %(prog)s reset admin -p newpass          # 重置admin密码为newpass
  %(prog)s verify admin 123456             # 验证密码
  %(prog)s info admin                      # 显示用户信息
  %(prog)s list                            # 列出所有用户
  %(prog)s delete testuser                 # 删除用户
  %(prog)s init                            # 初始化系统数据
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 创建管理员命令
    create_parser = subparsers.add_parser('create', help='创建管理员用户')
    create_parser.add_argument('-u', '--username', default='admin', help='用户名 (默认: admin)')
    create_parser.add_argument('-p', '--password', default='123456', help='密码 (默认: 123456)')
    create_parser.add_argument('-n', '--nickname', default='系统管理员', help='昵称 (默认: 系统管理员)')
    create_parser.add_argument('-f', '--force', action='store_true', help='强制覆盖已存在的用户')
    
    # 创建Django超级用户命令
    django_parser = subparsers.add_parser('create-django', help='创建Django Admin超级用户')
    django_parser.add_argument('-u', '--username', default='admin', help='用户名 (默认: admin)')
    django_parser.add_argument('-p', '--password', default='123456', help='密码 (默认: 123456)')
    django_parser.add_argument('-e', '--email', default='admin@example.com', help='邮箱 (默认: admin@example.com)')
    
    # 重置密码命令
    reset_parser = subparsers.add_parser('reset', help='重置用户密码')
    reset_parser.add_argument('username', help='用户名')
    reset_parser.add_argument('-p', '--password', default='123456', help='新密码 (默认: 123456)')
    
    # 验证密码命令
    verify_parser = subparsers.add_parser('verify', help='验证用户密码')
    verify_parser.add_argument('username', help='用户名')
    verify_parser.add_argument('password', help='密码')
    
    # 显示用户信息命令
    info_parser = subparsers.add_parser('info', help='显示用户信息')
    info_parser.add_argument('username', help='用户名')
    
    # 列出所有用户命令
    list_parser = subparsers.add_parser('list', help='列出所有用户')
    list_parser.add_argument('--django', action='store_true', help='列出Django用户而不是自定义用户')
    
    # 删除用户命令
    delete_parser = subparsers.add_parser('delete', help='删除用户')
    delete_parser.add_argument('username', help='用户名')
    delete_parser.add_argument('-f', '--force', action='store_true', help='强制删除（跳过确认）')
    
    # 初始化系统数据命令
    init_parser = subparsers.add_parser('init', help='初始化系统数据')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建管理器实例
    manager = AdminManager()
    
    print("🔌 PowerEdu-AI 管理员管理工具")
    print("=" * 50)
    
    # 执行对应的命令
    if args.command == 'create':
        manager.create_admin(args.username, args.password, args.nickname, args.force)
    
    elif args.command == 'create-django':
        manager.create_django_superuser(args.username, args.password, args.email)
    
    elif args.command == 'reset':
        manager.reset_password(args.username, args.password)
    
    elif args.command == 'verify':
        manager.verify_password(args.username, args.password)
    
    elif args.command == 'info':
        manager.show_user_info(args.username)
    
    elif args.command == 'list':
        if args.django:
            manager.list_django_users()
        else:
            manager.list_all_users()
    
    elif args.command == 'delete':
        manager.delete_user(args.username, args.force)
    
    elif args.command == 'init':
        manager.init_system_data()


if __name__ == "__main__":
    main()
