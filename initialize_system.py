#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速初始化AI系统的脚本
"""

import requests
import time
import json

def initialize_system():
    base_url = "http://localhost:8000/api/prediction"
    
    print("🚀 初始化AI系统...")
    
    try:
        # 调用初始化API
        response = requests.get(f"{base_url}/system/initialize", timeout=60)
        print(f"初始化状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"初始化响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('success'):
                print("✅ 系统初始化成功！")
                
                # 等待3秒后检查模型列表
                print("⏳ 等待3秒后检查模型列表...")
                time.sleep(3)
                
                # 检查模型列表
                model_response = requests.get(f"{base_url}/models")
                print(f"模型列表状态码: {model_response.status_code}")
                
                if model_response.status_code == 200:
                    model_data = model_response.json()
                    print(f"模型列表: {json.dumps(model_data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"获取模型列表失败: {model_response.text}")
            else:
                print(f"❌ 初始化失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ 初始化请求失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 初始化异常: {e}")

if __name__ == "__main__":
    initialize_system()
