#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的系统状态检查
"""

def main():
    print("🔍 AI预测系统状态检查...")
    
    try:
        # 检查Python版本
        import sys
        print(f"Python版本: {sys.version}")
        
        # 检查Django
        import django
        print(f"Django版本: {django.get_version()}")
        
        # 检查必要的包
        packages = ['numpy', 'pandas', 'scikit-learn', 'plotly']
        for pkg in packages:
            try:
                __import__(pkg)
                print(f"✅ {pkg} - 可用")
            except ImportError:
                print(f"❌ {pkg} - 缺失")
        
        print("🎯 基础检查完成")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    main()
