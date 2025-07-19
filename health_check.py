#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PowerEdu-AI 项目健康检查脚本
检查项目的配置、依赖和基本功能
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, cwd=None):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, 
                              capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令超时"
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """检查Python版本"""
    print("1. 检查Python版本...")
    success, stdout, stderr = run_command("python --version")
    if success:
        version = stdout.strip()
        print(f"   ✓ {version}")
        return True
    else:
        print(f"   ✗ Python检查失败: {stderr}")
        return False

def check_node_version():
    """检查Node.js版本"""
    print("2. 检查Node.js版本...")
    success, stdout, stderr = run_command("node --version")
    if success:
        version = stdout.strip()
        print(f"   ✓ Node.js {version}")
        return True
    else:
        print(f"   ✗ Node.js检查失败: {stderr}")
        return False

def check_django_config():
    """检查Django配置"""
    print("3. 检查Django配置...")
    os.chdir("backend")
    success, stdout, stderr = run_command("python manage.py check")
    os.chdir("..")
    
    if success:
        if "System check identified no issues" in stdout or "check" in stdout:
            print("   ✓ Django配置正常")
            return True
        else:
            print(f"   ⚠ Django检查输出: {stdout}")
            return True
    else:
        print(f"   ✗ Django检查失败: {stderr}")
        return False

def check_requirements():
    """检查Python依赖"""
    print("4. 检查Python依赖...")
    if not os.path.exists("requirements.txt"):
        print("   ✗ 未找到requirements.txt文件")
        return False
    
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = f.read()
    
    essential_packages = [
        "Django", "django-cors-headers", "django-ninja",
        "numpy", "pandas", "scikit-learn", "requests"
    ]
    
    missing = []
    for pkg in essential_packages:
        if pkg.lower() not in requirements.lower():
            missing.append(pkg)
    
    if missing:
        print(f"   ⚠ 可能缺少依赖: {', '.join(missing)}")
    else:
        print("   ✓ 核心依赖包含在requirements.txt中")
    
    return True

def check_frontend_deps():
    """检查前端依赖"""
    print("5. 检查前端依赖...")
    package_json_path = "frontend/package.json"
    
    if not os.path.exists(package_json_path):
        print("   ✗ 未找到frontend/package.json文件")
        return False
    
    try:
        with open(package_json_path, "r", encoding="utf-8") as f:
            package_data = json.load(f)
        
        deps = package_data.get("dependencies", {})
        essential_frontend = ["react", "antd", "axios", "react-router-dom"]
        
        missing = []
        for pkg in essential_frontend:
            if pkg not in deps:
                missing.append(pkg)
        
        if missing:
            print(f"   ⚠ 缺少前端依赖: {', '.join(missing)}")
        else:
            print("   ✓ 核心前端依赖完整")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 检查前端依赖失败: {e}")
        return False

def check_file_structure():
    """检查文件结构"""
    print("6. 检查项目结构...")
    
    required_files = [
        "README.md", "requirements.txt", "start.ps1", "start.sh",
        "backend/manage.py", "backend/edu/settings.py",
        "frontend/package.json", "frontend/src/main.jsx"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"   ⚠ 缺少文件: {', '.join(missing_files)}")
    else:
        print("   ✓ 核心文件结构完整")
    
    return len(missing_files) == 0

def check_env_example():
    """检查环境变量配置"""
    print("7. 检查环境配置...")
    
    if os.path.exists(".env.example"):
        print("   ✓ 找到.env.example配置模板")
        
        with open(".env.example", "r", encoding="utf-8") as f:
            env_content = f.read()
        
        if "GEMINI_API_KEY" in env_content:
            print("   ✓ 包含AI模型配置")
        else:
            print("   ⚠ 建议添加AI模型API配置")
        
        return True
    else:
        print("   ⚠ 未找到.env.example文件")
        return False

def main():
    """主检查函数"""
    print("="*50)
    print("PowerEdu-AI 项目健康检查")
    print("="*50)
    
    checks = [
        check_python_version,
        check_node_version,
        check_django_config,
        check_requirements,
        check_frontend_deps,
        check_file_structure,
        check_env_example,
    ]
    
    passed = 0
    total = len(checks)
    
    for check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"   ✗ 检查异常: {e}")
    
    print("\n" + "="*50)
    print(f"检查完成: {passed}/{total} 项通过")
    
    if passed == total:
        print("✓ 项目配置完整，可以正常启动！")
        return True
    elif passed >= total - 2:
        print("⚠ 项目基本配置正常，存在少量改进建议")
        return True
    else:
        print("✗ 项目存在配置问题，请检查并修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
