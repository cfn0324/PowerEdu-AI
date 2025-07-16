#!/usr/bin/env python
"""
创建测试数据
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu.settings')
django.setup()

from apps.knowledge.models import KnowledgeBase, ModelConfig, EmbeddingConfig

def create_test_data():
    """创建测试数据"""
    try:
        print("🔄 创建测试数据...")
        
        # 1. 创建嵌入配置
        embedding_config, created = EmbeddingConfig.objects.get_or_create(
            name="测试嵌入模型",
            defaults={
                'description': '用于测试的简单嵌入模型',
                'model_type': 'simple',
                'config': {'dimension': 768}
            }
        )
        print(f"✅ 嵌入配置: {embedding_config.name}")
        
        # 2. 创建模型配置
        model_config, created = ModelConfig.objects.get_or_create(
            name="测试模型",
            defaults={
                'description': '用于测试的模拟模型',
                'model_type': 'mock',
                'api_base': '',
                'api_key': '',
                'model_name': 'mock-model',
                'config': {
                    'temperature': 0.7,
                    'max_tokens': 1000
                }
            }
        )
        print(f"✅ 模型配置: {model_config.name}")
        
        # 3. 创建知识库
        kb, created = KnowledgeBase.objects.get_or_create(
            name="电力系统基础知识库",
            defaults={
                'description': '包含电力系统基础知识的测试知识库',
                'embedding_config': embedding_config,
                'model_config': model_config,
                'status': 'active'
            }
        )
        print(f"✅ 知识库: {kb.name} (ID: {kb.id})")
        
        # 4. 统计信息
        print(f"\n📊 数据库统计:")
        print(f"  - 知识库: {KnowledgeBase.objects.count()} 个")
        print(f"  - 模型配置: {ModelConfig.objects.count()} 个")
        print(f"  - 嵌入配置: {EmbeddingConfig.objects.count()} 个")
        
        print("\n✅ 测试数据创建成功!")
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_data()
