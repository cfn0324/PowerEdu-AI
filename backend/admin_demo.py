#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
管理员管理工具演示脚本
"""

import subprocess
import sys
import time

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"💻 命令: python admin_manager.py {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            f"python admin_manager.py {cmd}",
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"错误: {result.stderr}")
            
        time.sleep(1)  # 稍微延迟，让用户看清结果
        
    except Exception as e:
        print(f"执行命令时出错: {e}")

def main():
    """主演示函数"""
    print("🎬 PowerEdu-AI 管理员管理工具演示")
    print("=" * 60)
    
    demos = [
        ("list", "列出所有用户"),
        ("info admin", "查看admin用户信息"),
        ("verify admin 123456", "验证admin密码"),
        ("create -u demo -p demo123 -n '演示用户'", "创建演示用户"),
        ("list", "再次列出所有用户（查看新创建的用户）"),
        ("info demo", "查看demo用户信息"),
        ("reset demo -p newpass", "重置demo用户密码"),
        ("verify demo newpass", "验证demo用户新密码"),
        ("delete demo -f", "删除demo用户"),
        ("list", "最终用户列表"),
    ]
    
    for cmd, desc in demos:
        run_command(cmd, desc)
        
        # 在某些关键步骤后暂停
        if "创建演示用户" in desc or "删除demo用户" in desc:
            input("\n按Enter键继续下一个演示...")
    
    print(f"\n{'='*60}")
    print("🎉 演示完成！")
    print("💡 您现在可以使用 python admin_manager.py --help 查看完整功能")
    print(f"{'='*60}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 演示被用户中断")
    except Exception as e:
        print(f"\n\n❌ 演示过程中出现错误: {e}")
