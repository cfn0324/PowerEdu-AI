#!/usr/bin/env python
"""
成就系统状态检查脚本
用于检查成就系统是否正确初始化
"""

import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu.settings')
django.setup()

from apps.user.achievement_models import Achievement, UserAchievement, StudyStats
from apps.user.models import User


def check_achievements():
    """检查成就数据"""
    print("检查成就数据...")
    
    achievements = Achievement.objects.all()
    print(f"✓ 成就总数: {achievements.count()}")
    
    if achievements.count() == 0:
        print("❌ 警告: 未发现任何成就数据!")
        print("   请运行: cd backend && python manage.py init_achievements")
        return False
    
    # 按类型统计
    type_counts = {}
    for achievement in achievements:
        type_name = {
            1: '学习时长',
            2: '课程完成', 
            3: '连续学习',
            4: '知识探索',
            5: '互动参与'
        }.get(achievement.achievement_type, '未知')
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    for type_name, count in type_counts.items():
        print(f"  - {type_name}: {count}个")
    
    return True


def check_users():
    """检查用户数据"""
    print("\n检查用户数据...")
    
    users = User.objects.all()
    print(f"✓ 用户总数: {users.count()}")
    
    if users.count() == 0:
        print("❌ 警告: 未发现任何用户!")
        return False
    
    # 检查管理员账户
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        print("✓ 管理员账户: admin (已存在)")
    else:
        print("❌ 警告: 管理员账户不存在!")
        print("   请运行: cd backend && python admin_manager.py create")
    
    return True


def check_user_stats():
    """检查用户统计数据"""
    print("\n检查用户统计数据...")
    
    stats = StudyStats.objects.all()
    print(f"✓ 统计记录数: {stats.count()}")
    
    return True


def check_database():
    """检查数据库连接"""
    print("检查数据库连接...")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✓ 数据库连接正常")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def main():
    """主检查函数"""
    print("🔍 PowerEdu-AI 成就系统状态检查")
    print("=" * 40)
    
    checks = [
        check_database,
        check_users,
        check_achievements,
        check_user_stats,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ 检查过程中出现错误: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("📊 检查结果汇总:")
    
    if all(results):
        print("✅ 所有检查项目通过!")
        print("🚀 成就系统应该可以正常工作")
    else:
        print("❌ 发现问题，请按照上述提示进行修复")
        print("\n📋 常见修复步骤:")
        print("1. cd backend")
        print("2. python manage.py migrate")
        print("3. python admin_manager.py create")
        print("4. python manage.py init_achievements")


if __name__ == '__main__':
    main()
