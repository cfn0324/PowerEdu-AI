#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知识库应用数据模式定义
"""

from typing import List, Optional, Dict, Any
from ninja import Schema, Field, ModelSchema
from datetime import datetime
from .models import (
    KnowledgeBase, Document, QASession, QARecord, 
    ModelConfig, EmbeddingConfig
)


class KnowledgeBaseSchema(ModelSchema):
    class Meta:
        model = KnowledgeBase
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'is_active']


class KnowledgeBaseCreateSchema(Schema):
    name: str = Field(..., description="知识库名称")
    description: str = Field("", description="知识库描述")
    documents_dir: Optional[str] = Field(None, description="初始文档目录路径")


class DocumentSchema(ModelSchema):
    class Meta:
        model = Document
        fields = ['id', 'title', 'file_type', 'file_size', 'status', 'uploaded_at', 'chunk_count']


class DocumentUploadSchema(Schema):
    title: Optional[str] = Field(None, description="文档标题（可选，默认使用文件名）")
    chunk_size: int = Field(1000, description="分块大小", ge=100, le=5000)
    chunk_overlap: int = Field(200, description="分块重叠", ge=0, le=500)


class QASessionSchema(ModelSchema):
    class Meta:
        model = QASession
        fields = ['id', 'session_id', 'title', 'created_at', 'updated_at']


class QARecordSchema(ModelSchema):
    class Meta:
        model = QARecord
        fields = ['id', 'question', 'answer', 'model_used', 'response_time', 'created_at', 'feedback_score']


class QARequestSchema(Schema):
    kb_id: int = Field(..., description="知识库ID")
    question: str = Field(..., description="用户问题", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="会话ID（可选，不提供则创建新会话）")
    model_config_id: Optional[int] = Field(None, description="模型配置ID（可选，使用默认配置）")
    top_k: Optional[int] = Field(5, description="检索文档数量", ge=1, le=20)
    threshold: Optional[float] = Field(0.5, description="相似度阈值", ge=0.0, le=1.0)


class AnswerSchema(Schema):
    answer: str = Field(..., description="AI回答")
    session_id: str = Field(..., description="会话ID")
    model_used: str = Field(..., description="使用的模型")
    response_time: float = Field(..., description="响应时间")
    retrieved_chunks: List[dict] = Field([], description="检索到的文档块")
    sources: List[dict] = Field([], description="来源文档")


class FeedbackSchema(Schema):
    qa_record_id: int = Field(..., description="问答记录ID")
    score: int = Field(..., ge=1, le=5, description="评分(1-5)")
    comment: str = Field("", description="评论")


class ModelConfigSchema(ModelSchema):
    class Meta:
        model = ModelConfig
        fields = ['id', 'name', 'model_type', 'provider', 'model_name', 'is_active', 'is_default']


class ModelConfigCreateSchema(Schema):
    name: str = Field(..., description="配置名称")
    model_type: str = Field(..., description="模型类型")
    provider: str = Field(..., description="模型提供商")
    model_name: str = Field(..., description="模型名称")
    api_key: str = Field("", description="API密钥")
    api_base_url: str = Field("", description="API基础URL")
    model_path: str = Field("", description="本地模型路径")
    max_tokens: int = Field(4096, description="最大Token数")
    temperature: float = Field(0.7, description="温度参数")


class EmbeddingConfigSchema(ModelSchema):
    class Meta:
        model = EmbeddingConfig
        fields = ['id', 'name', 'embedding_type', 'model_name', 'dimension', 'is_active', 'is_default']


class EmbeddingConfigCreateSchema(Schema):
    name: str = Field(..., description="配置名称")
    embedding_type: str = Field(..., description="嵌入类型")
    model_name: str = Field(..., description="模型名称")
    api_key: str = Field("", description="API密钥")
    api_base_url: str = Field("", description="API基础URL")
    model_path: str = Field("", description="本地模型路径")
    dimension: int = Field(1536, description="向量维度")


class ProcessDocumentSchema(Schema):
    document_id: int = Field(..., description="文档ID")
    chunk_size: int = Field(1000, description="分块大小")
    chunk_overlap: int = Field(200, description="分块重叠")


class SearchSchema(Schema):
    query: str = Field(..., description="搜索查询")
    knowledge_base_id: int = Field(..., description="知识库ID")
    top_k: int = Field(5, description="返回结果数量")
    threshold: float = Field(0.5, description="相似度阈值")


class SearchResultSchema(Schema):
    content: str = Field(..., description="文档内容")
    score: float = Field(..., description="相似度分数")
    metadata: dict = Field({}, description="元数据")
    document_title: str = Field(..., description="文档标题")
    chunk_index: int = Field(..., description="分块索引")


class SystemStatusSchema(Schema):
    knowledge_bases: int = Field(..., description="知识库数量")
    documents: int = Field(..., description="文档数量")
    total_chunks: int = Field(..., description="总分块数")
    active_sessions: int = Field(..., description="活跃会话数")
    total_questions: int = Field(..., description="总问题数")
    available_models: List[str] = Field([], description="可用模型列表")
    system_ready: bool = Field(..., description="系统是否就绪")
