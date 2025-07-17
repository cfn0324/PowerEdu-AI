#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PowerEdu-AI 登录诊断工具
检查前端API登录和Django Admin登录
"""

import os
import django
import requests
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu.settings')
django.setup()

from apps.user.models import User as CustomUser
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.hashers import check_password

def test_custom_user_login():
    """测试自定义用户模型登录（前端API）"""
    print("🔍 测试自定义用户模型登录（前端API）")
    print("-" * 50)
    
    try:
        # 检查用户
        user = CustomUser.objects.get(username='admin')
        print(f"✅ 找到自定义用户: {user.username}")
        print(f"   昵称: {user.nickname}")
        print(f"   用户ID: {user.id}")
        
        # 验证密码
        is_valid = check_password('123456', user.password)
        print(f"   密码验证: {'✅ 正确' if is_valid else '❌ 错误'}")
        
        # 测试API登录
        try:
            response = requests.post(
                'http://localhost:8000/api/user/login',
                json={'username': 'admin', 'password': '123456'},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    print(f"   API登录: ✅ 成功")
                    print(f"   Token: {data['token'][:30]}...")
                else:
                    print(f"   API登录: ❌ 失败 - {data}")
            else:
                print(f"   API登录: ❌ HTTP错误 {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("   API登录: ⚠️  后端服务未启动")
        except Exception as e:
            print(f"   API登录: ❌ 异常 - {e}")
            
    except CustomUser.DoesNotExist:
        print("❌ 自定义用户 'admin' 不存在")
    except Exception as e:
        print(f"❌ 检查自定义用户失败: {e}")

def test_django_user_login():
    """测试Django用户模型登录（Django Admin）"""
    print("\n🔍 测试Django用户模型登录（Django Admin）")
    print("-" * 50)
    
    try:
        # 检查Django用户
        user = DjangoUser.objects.get(username='admin')
        print(f"✅ 找到Django用户: {user.username}")
        print(f"   邮箱: {user.email}")
        print(f"   超级用户: {'是' if user.is_superuser else '否'}")
        print(f"   员工状态: {'是' if user.is_staff else '否'}")
        print(f"   用户ID: {user.id}")
        
        # 验证密码
        is_valid = user.check_password('123456')
        print(f"   密码验证: {'✅ 正确' if is_valid else '❌ 错误'}")
        
        # 检查Django Admin访问权限
        if user.is_superuser and user.is_staff:
            print("   Django Admin权限: ✅ 有权限访问")
            print("   登录地址: http://localhost:8000/admin")
        else:
            print("   Django Admin权限: ❌ 无权限访问")
            
    except DjangoUser.DoesNotExist:
        print("❌ Django用户 'admin' 不存在")
        print("💡 请运行: python admin_manager.py create-django")
    except Exception as e:
        print(f"❌ 检查Django用户失败: {e}")

def check_system_status():
    """检查系统状态"""
    print("\n🔍 系统状态检查")
    print("-" * 50)
    
    # 检查自定义用户数量
    custom_users = CustomUser.objects.count()
    print(f"自定义用户数量: {custom_users}")
    
    # 检查Django用户数量
    django_users = DjangoUser.objects.count()
    print(f"Django用户数量: {django_users}")
    
    # 检查后端服务
    try:
        response = requests.get('http://localhost:8000/api/user/banner', timeout=5)
        if response.status_code == 200:
            print("后端服务: ✅ 运行中")
        else:
            print(f"后端服务: ⚠️  异常 ({response.status_code})")
    except requests.exceptions.ConnectionError:
        print("后端服务: ❌ 未启动")
    except Exception as e:
        print(f"后端服务: ❌ 错误 - {e}")
    
    # 检查前端服务
    try:
        response = requests.get('http://localhost:5173', timeout=5)
        if response.status_code == 200:
            print("前端服务: ✅ 运行中")
        else:
            print(f"前端服务: ⚠️  异常 ({response.status_code})")
    except requests.exceptions.ConnectionError:
        print("前端服务: ❌ 未启动")
    except Exception as e:
        print(f"前端服务: ❌ 错误 - {e}")

def main():
    """主函数"""
    print("🔌 PowerEdu-AI 登录诊断工具")
    print("=" * 60)
    
    check_system_status()
    test_custom_user_login()
    test_django_user_login()
    
    print("\n" + "=" * 60)
    print("📋 诊断总结:")
    print("1. 前端登录使用: 自定义用户模型 (admin/123456)")
    print("2. Django Admin使用: Django用户模型 (admin/123456)")
    print("3. 前端地址: http://localhost:5173")
    print("4. Django Admin地址: http://localhost:8000/admin")
    print("\n💡 如果Django Admin无法登录，请运行:")
    print("   python admin_manager.py create-django")

if __name__ == "__main__":
    main()
