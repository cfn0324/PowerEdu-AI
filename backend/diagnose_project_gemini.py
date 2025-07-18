#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断项目中的Gemini API调用问题
"""
import os
import sys
import django
import asyncio
import json
import logging

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu.settings')
django.setup()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from apps.knowledge.rag_system_simple import RAGSystem, LLMInterface
from apps.knowledge.models import ModelConfig

async def test_project_gemini_api():
    """测试项目中的Gemini API调用"""
    print("====== 测试项目中的Gemini API调用 ======")
    
    try:
        # 1. 获取Gemini配置
        print("1. 获取Gemini配置...")
        gemini_config = ModelConfig.objects.filter(
            model_name__icontains='gemini',
            is_active=True
        ).first()
        
        if not gemini_config:
            print("❌ 未找到激活的Gemini配置")
            return False
        
        print(f"✅ 找到Gemini配置:")
        print(f"   ID: {gemini_config.id}")
        print(f"   名称: {gemini_config.name}")
        print(f"   模型: {gemini_config.model_name}")
        print(f"   API URL: {gemini_config.api_base_url}")
        print(f"   API Key: {gemini_config.api_key[:20]}...")
        print(f"   Max Tokens: {gemini_config.max_tokens}")
        print(f"   Temperature: {gemini_config.temperature}")
        
        # 2. 创建LLM配置字典
        print("\n2. 创建LLM配置...")
        llm_config = {
            'model_type': gemini_config.model_type,
            'model_name': gemini_config.model_name,
            'api_key': gemini_config.api_key,
            'api_base_url': gemini_config.api_base_url,
            'max_tokens': gemini_config.max_tokens,
            'temperature': gemini_config.temperature
        }
        
        print(f"✅ LLM配置: {json.dumps(llm_config, indent=2, ensure_ascii=False)}")
        
        # 3. 创建LLM接口
        print("\n3. 创建LLM接口...")
        llm = LLMInterface(llm_config)
        print(f"✅ LLM接口创建成功")
        print(f"   模型类型: {llm.model_type}")
        print(f"   模型名称: {llm.model_name}")
        print(f"   配置: {llm.model_config}")
        
        # 4. 测试generate方法
        print("\n4. 测试generate方法...")
        try:
            result = await llm.generate("你好，请简单介绍一下你自己。")
            print(f"✅ generate方法调用成功")
            print(f"   结果: {result[:200]}...")
        except Exception as e:
            print(f"❌ generate方法调用失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 5. 测试generate_response方法
        print("\n5. 测试generate_response方法...")
        try:
            result = await llm.generate_response("你好，请简单介绍一下你自己。")
            print(f"✅ generate_response方法调用成功")
            print(f"   结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"❌ generate_response方法调用失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 6. 测试RAG系统
        print("\n6. 测试RAG系统...")
        try:
            rag_system = RAGSystem()
            rag_system.configure_llm(gemini_config.id, llm_config)
            print(f"✅ RAG系统配置成功")
            print(f"   LLM配置: {list(rag_system.llm_configs.keys())}")
            
            # 测试ask_question
            result = await rag_system.ask_question(
                kb_id=1,
                question="你好，请简单介绍一下你自己。",
                config_id=gemini_config.id,
                top_k=5,
                threshold=0.5
            )
            print(f"✅ ask_question调用成功")
            print(f"   结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
        except Exception as e:
            print(f"❌ RAG系统测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始诊断项目中的Gemini API调用问题...")
    success = asyncio.run(test_project_gemini_api())
    
    if success:
        print("\n✅ 所有测试通过！项目中的Gemini API调用正常")
    else:
        print("\n❌ 测试失败，发现问题")

if __name__ == "__main__":
    main()
