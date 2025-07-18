#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断LLM配置问题
"""
import os
import sys
import django
import asyncio
import json

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu.settings')
django.setup()

from apps.knowledge.rag_system_simple import RAGSystem
from apps.knowledge.models import ModelConfig

def diagnose_llm_config():
    """诊断LLM配置问题"""
    print("====== 诊断LLM配置问题 ======")
    
    try:
        # 1. 检查数据库中的模型配置
        print("1. 检查数据库中的模型配置...")
        configs = ModelConfig.objects.all()
        print(f"总共有 {configs.count()} 个模型配置")
        
        gemini_config = None
        for config in configs:
            print(f"- ID: {config.id}, 名称: {config.model_name}, 激活: {config.is_active}")
            if 'gemini' in config.model_name.lower():
                gemini_config = config
                print(f"  ✅ 找到Gemini配置: {config.model_name}")
                print(f"  API Key: {config.api_key[:10]}...")
                print(f"  API Base: {config.api_base_url}")
        
        if not gemini_config:
            print("❌ 未找到Gemini配置")
            return False
        
        # 2. 检查RAG系统中的LLM配置
        print("\n2. 检查RAG系统中的LLM配置...")
        rag_system = RAGSystem()
        print(f"RAG系统中已配置的LLM数量: {len(rag_system.llm_configs)}")
        
        for config_id, llm in rag_system.llm_configs.items():
            print(f"- 配置ID: {config_id}, 模型类型: {llm.model_type}")
        
        # 3. 手动配置LLM
        print("\n3. 手动配置LLM...")
        llm_config = {
            'model_type': gemini_config.model_type,
            'model_name': gemini_config.model_name,
            'api_key': gemini_config.api_key,
            'api_base_url': gemini_config.api_base_url,
            'max_tokens': gemini_config.max_tokens,
            'temperature': gemini_config.temperature
        }
        
        rag_system.configure_llm(gemini_config.id, llm_config)
        print(f"✅ 手动配置完成，现在有 {len(rag_system.llm_configs)} 个LLM配置")
        
        # 4. 测试LLM直接调用
        print("\n4. 测试LLM直接调用...")
        llm = rag_system.llm_configs.get(gemini_config.id)
        if llm:
            print(f"✅ 找到LLM配置: {llm.model_name}")
            
            # 测试generate方法
            async def test_generate():
                return await llm.generate("你好，请简单介绍一下你自己。")
            
            try:
                result = asyncio.run(test_generate())
                print(f"✅ LLM直接调用成功: {result}")
            except Exception as e:
                print(f"❌ LLM直接调用失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ 未找到LLM配置")
        
        # 5. 测试问答系统
        print("\n5. 测试问答系统...")
        
        async def test_ask_question():
            return await rag_system.ask_question(
                kb_id=1,
                question="你好，请简单介绍一下你自己。",
                config_id=gemini_config.id,
                top_k=5,
                threshold=0.5
            )
        
        try:
            result = asyncio.run(test_ask_question())
            print(f"✅ 问答系统结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"❌ 问答系统失败: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ 诊断失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = diagnose_llm_config()
    if success:
        print("\n✅ 诊断完成")
    else:
        print("\n❌ 诊断失败")
