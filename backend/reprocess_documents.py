#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查文档处理状态并重新处理
"""
import os
import sys
import django
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu.settings')
django.setup()

from apps.knowledge.models import KnowledgeBase, Document, DocumentChunk
from apps.knowledge.rag_system_simple import RAGSystem
import asyncio

def reprocess_documents():
    """重新处理文档"""
    print("=" * 60)
    print("重新处理文档")
    print("=" * 60)
    
    # 获取已完成但没有DocumentChunk的文档
    docs_without_chunks = Document.objects.filter(
        status='completed',
        chunks__isnull=True
    ).distinct()
    
    print(f"找到 {docs_without_chunks.count()} 个需要重新处理的文档")
    
    rag_system = RAGSystem()
    
    for doc in docs_without_chunks:
        print(f"\n处理文档: {doc.title}")
        print(f"文档ID: {doc.id}")
        print(f"文件路径: {doc.file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(doc.file_path):
            print(f"文件不存在: {doc.file_path}")
            continue
        
        # 重新处理文档
        try:
            result = rag_system.process_document(
                kb_id=doc.knowledge_base.id,
                file_path=doc.file_path,
                document_id=doc.id
            )
            
            print(f"处理结果: {result}")
            
            if result.get('success', False):
                # 更新文档状态
                doc.chunk_count = result.get('chunk_count', 0)
                doc.processed_at = datetime.now()
                doc.save()
                
                # 检查是否创建了DocumentChunk
                chunks = DocumentChunk.objects.filter(document=doc)
                print(f"创建的DocumentChunk数量: {chunks.count()}")
                
                if chunks.exists():
                    first_chunk = chunks.first()
                    print(f"第一个块内容预览: {first_chunk.content[:100]}...")
                
            else:
                print(f"处理失败: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"处理异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("重新处理完成")
    print("=" * 60)

if __name__ == "__main__":
    reprocess_documents()
