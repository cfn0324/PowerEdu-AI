#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试模型API的脚本
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8000/api/prediction"
    
    print("🔍 测试AI预测系统API...")
    
    # 1. 测试系统状态
    print("\n1. 检查系统状态...")
    try:
        response = requests.get(f"{base_url}/system/status")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试调试信息
    print("\n2. 检查调试信息...")
    try:
        response = requests.get(f"{base_url}/debug/info")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"调试信息: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 3. 测试模型列表
    print("\n3. 获取模型列表...")
    try:
        response = requests.get(f"{base_url}/models")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"模型列表: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_api()
