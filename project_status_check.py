#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电力知识库与AI预测平台 - 项目状态检查脚本
检查项目的完整性和运行状态
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"🐍 Python版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or version.minor < 8:
        print("❌ Python版本过低，需要3.8+")
        return False
    return True

def check_node_version():
    """检查Node.js版本"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"📦 Node.js版本: {version}")
            return True
        else:
            print("❌ Node.js未安装")
            return False
    except FileNotFoundError:
        print("❌ Node.js未找到")
        return False

def check_file_structure():
    """检查项目文件结构"""
    required_files = [
        'README.md',
        'requirements.txt',
        'start.ps1',
        'start.sh',
        'backend/manage.py',
        'backend/edu/settings.py',
        'frontend/package.json',
        'frontend/vite.config.js',
        'frontend/src/main.jsx',
    ]
    
    print("📁 检查项目文件结构...")
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print("❌ 缺失文件:")
        for file_path in missing_files:
            print(f"  🔍 {file_path}")
        return False
    
    return True

def check_dependencies():
    """检查依赖安装状态"""
    print("📦 检查Python依赖...")
    try:
        import django
        import pandas
        import numpy
        import sklearn
        print(f"  ✅ Django: {django.VERSION}")
        print(f"  ✅ pandas: {pandas.__version__}")
        print(f"  ✅ numpy: {numpy.__version__}")
        print(f"  ✅ scikit-learn: {sklearn.__version__}")
    except ImportError as e:
        print(f"  ❌ 缺失Python依赖: {e}")
        return False
    
    print("📦 检查前端依赖...")
    if os.path.exists('frontend/node_modules'):
        print("  ✅ 前端依赖已安装")
    else:
        print("  ❌ 前端依赖未安装，请运行: cd frontend && npm install")
        return False
    
    return True

def check_database():
    """检查数据库状态"""
    print("💾 检查数据库...")
    if os.path.exists('backend/db.sqlite3'):
        print("  ✅ SQLite数据库存在")
        return True
    else:
        print("  ⚠️ 数据库未初始化，请运行: cd backend && python manage.py migrate")
        return False

def main():
    """主检查函数"""
    print("🔌 电力知识库与AI预测平台 - 项目状态检查")
    print("=" * 50)
    
    checks = [
        ("Python版本", check_python_version),
        ("Node.js版本", check_node_version),
        ("文件结构", check_file_structure),
        ("依赖安装", check_dependencies),
        ("数据库状态", check_database),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 {name}检查...")
        result = check_func()
        results.append((name, result))
        print(f"{'✅ 通过' if result else '❌ 失败'}")
    
    print("\n" + "=" * 50)
    print("📊 检查结果总结:")
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 项目状态良好，可以启动！")
        print("🚀 运行启动脚本: .\\start.ps1 (Windows) 或 ./start.sh (Linux/Mac)")
    else:
        print("\n⚠️ 项目存在问题，请根据上述检查结果进行修复。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
