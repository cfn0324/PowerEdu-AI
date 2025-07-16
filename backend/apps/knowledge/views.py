#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知识库应用视图 - 大模型知识库问答系统 API
"""

from ninja import Router, UploadedFile, File
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from typing import List, Dict, Optional
import json
import os
import sys
import traceback
import asyncio
import logging

logger = logging.getLogger(__name__)
import uuid
from datetime import datetime

from apps.core import auth, R
from .models import (
    KnowledgeBase, Document, QASession, QARecord, 
    ModelConfig, EmbeddingConfig
)
from .schemas import (
    KnowledgeBaseSchema, DocumentSchema, QASessionSchema, 
    QARecordSchema, ModelConfigSchema, QARequestSchema,
    DocumentUploadSchema, KnowledgeBaseCreateSchema
)

# 导入RAG系统
from .rag_system_simple import RAGSystem

# 创建路由器
router = Router()

# 全局RAG系统实例
_rag_system = None

def get_rag_system():
    """获取RAG系统实例"""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
    return _rag_system


@router.get("/", summary="知识库系统概览")
def knowledge_root(request):
    """知识库系统根端点"""
    return {
        "success": True,
        "message": "欢迎使用PowerEdu-AI大模型知识库系统",
        "version": "1.0.0",
        "features": [
            "基于RAG技术的智能问答",
            "支持多种文档格式处理",
            "多模型配置支持",
            "向量化存储与检索",
            "会话式交互体验"
        ],
        "endpoints": {
            "knowledge_bases": "/api/knowledge/knowledge-bases",
            "documents": "/api/knowledge/documents", 
            "qa": "/api/knowledge/qa",
            "models": "/api/knowledge/models",
            "upload": "/api/knowledge/upload"
        },
        "timestamp": datetime.now().isoformat()
    }


# ==================== 知识库管理 ====================

@router.get("/knowledge-bases", summary="获取知识库列表")
def get_knowledge_bases(request, page: int = 1, size: int = 10):
    """获取知识库列表"""
    try:
        knowledge_bases = KnowledgeBase.objects.filter(is_active=True).order_by('-created_at')
        paginator = Paginator(knowledge_bases, size)
        page_obj = paginator.get_page(page)
        
        # 手动序列化知识库对象
        items = []
        for kb in page_obj:
            items.append({
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "status": kb.status,
                "document_count": kb.documents.count(),
                "created_at": kb.created_at.isoformat() if kb.created_at else None,
                "updated_at": kb.updated_at.isoformat() if kb.updated_at else None,
                "embedding_config_name": kb.embedding_config.name if kb.embedding_config else None,
                "model_config_name": kb.model_config.name if kb.model_config else None,
            })
        
        return {
            "success": True,
            "data": {
                "items": items,
                "total": paginator.count,
                "page": page,
                "size": size,
                "pages": paginator.num_pages
            }
        }
    except Exception as e:
        logger.error(f"获取知识库列表失败: {e}")
        return {"success": False, "error": str(e)}


@router.post("/knowledge-bases", summary="创建知识库", **auth)
def create_knowledge_base(request, data: KnowledgeBaseCreateSchema):
    """创建新的知识库"""
    try:
        # 创建数据库记录
        user = User.objects.get(id=request.auth)
        kb = KnowledgeBase.objects.create(
            name=data.name,
            description=data.description,
            created_by=user
        )
        
        # 初始化RAG系统中的知识库
        rag_system = get_rag_system()
        success = rag_system.create_knowledge_base(kb.id, data.documents_dir)
        
        if success:
            return {"success": True, "data": {"id": kb.id, "name": kb.name}}
        else:
            kb.delete()
            return {"success": False, "error": "RAG系统初始化失败"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/knowledge-bases/{kb_id}", summary="获取知识库详情")
def get_knowledge_base(request, kb_id: int):
    """获取知识库详情"""
    try:
        kb = KnowledgeBase.objects.get(id=kb_id, is_active=True)
        
        # 获取统计信息
        rag_system = get_rag_system()
        stats = rag_system.get_knowledge_base_stats(kb_id)
        
        return {
            "success": True,
            "data": {
                "knowledge_base": kb,
                "stats": stats,
                "document_count": kb.documents.count(),
                "qa_session_count": kb.qa_sessions.count()
            }
        }
    except KnowledgeBase.DoesNotExist:
        return {"success": False, "error": "知识库不存在"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== 文档管理 ====================

@router.get("/documents", summary="获取文档列表")
def get_documents(request, kb_id: int, page: int = 1, size: int = 10):
    """获取文档列表"""
    try:
        documents = Document.objects.filter(
            knowledge_base_id=kb_id
        ).order_by('-uploaded_at')
        
        paginator = Paginator(documents, size)
        page_obj = paginator.get_page(page)
        
        # 手动序列化文档对象
        items = []
        for doc in page_obj:
            items.append({
                "id": doc.id,
                "title": doc.title,
                "file_name": doc.file_name,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "status": doc.status,
                "processed_at": doc.processed_at.isoformat() if doc.processed_at else None,
                "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
            })
        
        return {
            "success": True,
            "data": {
                "items": items,
                "total": paginator.count,
                "page": page,
                "size": size,
                "pages": paginator.num_pages
            }
        }
    except Exception as e:
        logger.error(f"获取文档列表失败: {e}")
        return {"success": False, "error": str(e)}


@router.post("/documents/upload", summary="上传文档", **auth)
def upload_document(request, kb_id: int, file: UploadedFile = File(...)):
    """上传文档到知识库"""
    try:
        # 检查知识库是否存在
        kb = KnowledgeBase.objects.get(id=kb_id, is_active=True)
        user = User.objects.get(id=request.auth)
        
        # 检查文件类型
        allowed_extensions = ['.md', '.pdf', '.txt', '.docx', '.html']
        file_extension = os.path.splitext(file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return {"success": False, "error": f"不支持的文件类型: {file_extension}"}
        
        # 保存文件
        upload_dir = f"media/knowledge_bases/{kb_id}/documents"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.name)
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        
        # 创建文档记录
        document = Document.objects.create(
            knowledge_base=kb,
            title=os.path.splitext(file.name)[0],
            file_path=file_path,
            file_type=file_extension[1:],  # 去掉点号
            file_size=file.size,
            uploaded_by=user,
            status='pending'
        )
        
        # 异步处理文档
        try:
            rag_system = get_rag_system()
            result = rag_system.process_document(kb_id, file_path)
            
            # 更新文档状态
            document.status = 'completed'
            document.chunk_count = result['chunk_count']
            document.processed_at = datetime.now()
            document.save()
            
            return {
                "success": True,
                "data": {
                    "document_id": document.id,
                    "chunk_count": result['chunk_count'],
                    "status": "completed"
                }
            }
            
        except Exception as e:
            document.status = 'failed'
            document.save()
            return {"success": False, "error": f"文档处理失败: {str(e)}"}
            
    except KnowledgeBase.DoesNotExist:
        return {"success": False, "error": "知识库不存在"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== 问答功能 ====================

@router.post("/qa/ask", summary="智能问答", **auth)
def ask_question(request, data: QARequestSchema):
    """智能问答接口"""
    try:
        # 检查知识库
        kb = KnowledgeBase.objects.get(id=data.kb_id, is_active=True)
        user = User.objects.get(id=request.auth)
        
        # 获取或创建会话
        if data.session_id:
            try:
                session = QASession.objects.get(session_id=data.session_id, user=user)
            except QASession.DoesNotExist:
                session = QASession.objects.create(
                    knowledge_base=kb,
                    user=user,
                    session_id=data.session_id,
                    title=data.question[:50] + "..." if len(data.question) > 50 else data.question
                )
        else:
            # 创建新会话
            session_id = str(uuid.uuid4())
            session = QASession.objects.create(
                knowledge_base=kb,
                user=user,
                session_id=session_id,
                title=data.question[:50] + "..." if len(data.question) > 50 else data.question
            )
        
        # 调用RAG系统进行问答
        rag_system = get_rag_system()
        
        # 配置LLM（如果指定了配置ID）
        if data.model_config_id:
            try:
                model_config = ModelConfig.objects.get(id=data.model_config_id, is_active=True)
                llm_config = {
                    'model_type': model_config.model_type,
                    'provider': model_config.provider,
                    'model_name': model_config.model_name,
                    'api_key': model_config.api_key,
                    'api_base_url': model_config.api_base_url,
                    'max_tokens': model_config.max_tokens,
                    'temperature': model_config.temperature
                }
                rag_system.configure_llm(data.model_config_id, llm_config)
            except ModelConfig.DoesNotExist:
                pass
        
        # 执行问答
        async def run_qa():
            return await rag_system.ask_question(
                kb_id=data.kb_id,
                question=data.question,
                config_id=data.model_config_id,
                top_k=data.top_k or 5,
                threshold=data.threshold or 0.5
            )
        
        # 在同步环境中运行异步函数
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(run_qa())
        
        # 保存问答记录
        qa_record = QARecord.objects.create(
            session=session,
            question=data.question,
            answer=result['answer'],
            retrieved_chunks=result['retrieved_chunks'],
            model_used=result['model_used'],
            response_time=result['response_time'],
            tokens_used=result.get('tokens_used', 0)
        )
        
        return {
            "success": True,
            "data": {
                "session_id": session.session_id,
                "answer": result['answer'],
                "sources": result['sources'],
                "model_used": result['model_used'],
                "response_time": result['response_time'],
                "qa_record_id": qa_record.id
            }
        }
        
    except KnowledgeBase.DoesNotExist:
        return {"success": False, "error": "知识库不存在"}
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"问答异常: {error_trace}")
        return {"success": False, "error": str(e)}


@router.get("/qa/sessions", summary="获取问答会话列表", **auth)
def get_qa_sessions(request, kb_id: int = None, page: int = 1, size: int = 10):
    """获取用户的问答会话列表"""
    try:
        user = User.objects.get(id=request.auth)
        
        sessions = QASession.objects.filter(user=user)
        if kb_id:
            sessions = sessions.filter(knowledge_base_id=kb_id)
        
        sessions = sessions.order_by('-updated_at')
        
        paginator = Paginator(sessions, size)
        page_obj = paginator.get_page(page)
        
        # 手动序列化会话对象
        items = []
        for session in page_obj:
            items.append({
                "id": session.id,
                "session_id": session.session_id,
                "title": session.title,
                "knowledge_base_name": session.knowledge_base.name if session.knowledge_base else None,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None,
            })
        
        return {
            "success": True,
            "data": {
                "items": items,
                "total": paginator.count,
                "page": page,
                "size": size,
                "pages": paginator.num_pages
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/qa/sessions/{session_id}/records", summary="获取会话问答记录")
def get_qa_records(request, session_id: str, page: int = 1, size: int = 20):
    """获取指定会话的问答记录"""
    try:
        session = QASession.objects.get(session_id=session_id)
        records = QARecord.objects.filter(session=session).order_by('created_at')
        
        paginator = Paginator(records, size)
        page_obj = paginator.get_page(page)
        
        # 手动序列化QA记录对象
        record_items = []
        for record in page_obj:
            record_items.append({
                "id": record.id,
                "question": record.question,
                "answer": record.answer,
                "confidence": float(record.confidence) if record.confidence else 0.0,
                "feedback_score": record.feedback_score,
                "feedback_comment": record.feedback_comment,
                "created_at": record.created_at.isoformat() if record.created_at else None,
            })
        
        return {
            "success": True,
            "data": {
                "session": {
                    "id": session.id,
                    "session_id": session.session_id,
                    "title": session.title,
                    "created_at": session.created_at.isoformat() if session.created_at else None,
                },
                "records": record_items,
                "total": paginator.count,
                "page": page,
                "size": size,
                "pages": paginator.num_pages
            }
        }
    except QASession.DoesNotExist:
        return {"success": False, "error": "会话不存在"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/qa/feedback", summary="问答反馈", **auth)
def submit_feedback(request, qa_record_id: int, score: int, comment: str = ""):
    """提交问答反馈"""
    try:
        qa_record = QARecord.objects.get(id=qa_record_id)
        
        # 验证评分范围
        if not (1 <= score <= 5):
            return {"success": False, "error": "评分必须在1-5之间"}
        
        qa_record.feedback_score = score
        qa_record.feedback_comment = comment
        qa_record.save()
        
        return {"success": True, "message": "反馈提交成功"}
        
    except QARecord.DoesNotExist:
        return {"success": False, "error": "问答记录不存在"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== 模型配置管理 ====================

@router.get("/models/configs", summary="获取模型配置列表")
def get_model_configs(request):
    """获取模型配置列表"""
    try:
        configs = ModelConfig.objects.filter(is_active=True).order_by('-created_at')
        
        # 手动序列化模型配置对象
        items = []
        for config in configs:
            items.append({
                "id": config.id,
                "name": config.name,
                "description": config.description,
                "model_type": config.model_type,
                "model_name": config.model_name,
                "api_base": config.api_base,
                "is_default": config.is_default,
                "created_at": config.created_at.isoformat() if config.created_at else None,
            })
        
        return {"success": True, "data": items}
    except Exception as e:
        logger.error(f"获取模型配置列表失败: {e}")
        return {"success": False, "error": str(e)}


@router.post("/models/configs", summary="创建模型配置", **auth)
def create_model_config(request, data: ModelConfigSchema):
    """创建模型配置"""
    try:
        # 如果设置为默认，先取消其他默认配置
        if data.is_default:
            ModelConfig.objects.filter(is_default=True).update(is_default=False)
        
        config = ModelConfig.objects.create(**data.dict())
        return {"success": True, "data": {"id": config.id, "name": config.name}}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/models/test", summary="测试模型配置")
def test_model_config(request, config_id: int):
    """测试模型配置"""
    try:
        config = ModelConfig.objects.get(id=config_id, is_active=True)
        
        # 创建测试用的RAG系统实例
        rag_system = get_rag_system()
        
        # 配置LLM
        llm_config = {
            'model_type': config.model_type,
            'provider': config.provider,
            'model_name': config.model_name,
            'api_key': config.api_key,
            'api_base_url': config.api_base_url,
            'max_tokens': config.max_tokens,
            'temperature': config.temperature
        }
        
        rag_system.configure_llm(config_id, llm_config)
        
        # 发送测试问题
        async def test_llm():
            return await rag_system.llm_configs[config_id].generate_response(
                "你好，请简单介绍一下你自己。", ""
            )
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(test_llm())
        
        return {
            "success": True,
            "data": {
                "test_result": "连接成功",
                "response": result['answer'][:100] + "..." if len(result['answer']) > 100 else result['answer'],
                "response_time": result['response_time']
            }
        }
        
    except ModelConfig.DoesNotExist:
        return {"success": False, "error": "模型配置不存在"}
    except Exception as e:
        return {"success": False, "error": f"测试失败: {str(e)}"}


# ==================== 系统状态和统计 ====================

@router.get("/stats", summary="获取系统统计信息")
def get_system_stats(request):
    """获取系统统计信息"""
    try:
        stats = {
            "knowledge_bases": KnowledgeBase.objects.filter(is_active=True).count(),
            "documents": Document.objects.filter(status='completed').count(),
            "qa_sessions": QASession.objects.count(),
            "qa_records": QARecord.objects.count(),
            "model_configs": ModelConfig.objects.filter(is_active=True).count(),
        }
        
        # 获取最近的问答记录
        recent_qa = QARecord.objects.order_by('-created_at')[:5]
        
        return {
            "success": True,
            "data": {
                "stats": stats,
                "recent_qa": [
                    {
                        "question": qa.question[:50] + "..." if len(qa.question) > 50 else qa.question,
                        "model_used": qa.model_used,
                        "response_time": qa.response_time,
                        "created_at": qa.created_at
                    } for qa in recent_qa
                ]
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/health", summary="系统健康检查")
def health_check(request):
    """系统健康检查"""
    try:
        # 检查RAG系统
        rag_system = get_rag_system()
        
        # 检查数据库连接
        db_status = "ok"
        try:
            KnowledgeBase.objects.first()
        except Exception:
            db_status = "error"
        
        # 检查模型配置
        active_models = ModelConfig.objects.filter(is_active=True).count()
        
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "database": db_status,
                "rag_system": "initialized" if rag_system else "not_initialized",
                "active_models": active_models,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": "unhealthy"
        }
