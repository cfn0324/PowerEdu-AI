from django.db import models
from apps.user.models import User
from django.core.validators import FileExtensionValidator
import json


class KnowledgeBase(models.Model):
    """知识库基础信息"""
    name = models.CharField(max_length=200, verbose_name="知识库名称")
    description = models.TextField(blank=True, verbose_name="知识库描述")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    vector_store_path = models.CharField(max_length=500, blank=True, verbose_name="向量库路径")
    
    class Meta:
        verbose_name = "知识库"
        verbose_name_plural = "知识库"
        
    def __str__(self):
        return self.name


class Document(models.Model):
    """文档模型"""
    DOCUMENT_TYPES = [
        ('md', 'Markdown'),
        ('pdf', 'PDF'),
        ('txt', 'Text'),
        ('docx', 'Word'),
        ('html', 'HTML'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=500, verbose_name="文档标题")
    file_path = models.CharField(max_length=1000, verbose_name="文件路径")
    file_name = models.CharField(max_length=255, default="", verbose_name="文件名")
    file_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES, verbose_name="文件类型")
    file_size = models.IntegerField(default=0, verbose_name="文件大小(bytes)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="处理状态")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="上传者")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="处理时间")
    chunk_count = models.IntegerField(default=0, verbose_name="分块数量")
    metadata = models.JSONField(default=dict, verbose_name="元数据")
    
    class Meta:
        verbose_name = "文档"
        verbose_name_plural = "文档"
        
    def __str__(self):
        return self.title


class DocumentChunk(models.Model):
    """文档分块"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField(verbose_name="分块索引")
    content = models.TextField(verbose_name="分块内容")
    embedding = models.JSONField(null=True, blank=True, verbose_name="向量嵌入")
    metadata = models.JSONField(default=dict, verbose_name="分块元数据")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "文档分块"
        verbose_name_plural = "文档分块"
        unique_together = ['document', 'chunk_index']
        
    def __str__(self):
        return f"{self.document.title} - 块{self.chunk_index}"


class QASession(models.Model):
    """问答会话"""
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='qa_sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    session_id = models.CharField(max_length=100, unique=True, verbose_name="会话ID")
    title = models.CharField(max_length=500, blank=True, verbose_name="会话标题")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "问答会话"
        verbose_name_plural = "问答会话"
        
    def __str__(self):
        return f"{self.user.username} - {self.title or self.session_id}"


class QARecord(models.Model):
    """问答记录"""
    session = models.ForeignKey(QASession, on_delete=models.CASCADE, related_name='qa_records')
    question = models.TextField(verbose_name="问题")
    answer = models.TextField(verbose_name="回答")
    retrieved_chunks = models.JSONField(default=list, verbose_name="检索到的文档块")
    model_used = models.CharField(max_length=100, verbose_name="使用的模型")
    response_time = models.FloatField(verbose_name="响应时间(秒)")
    tokens_used = models.IntegerField(default=0, verbose_name="使用的Token数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    feedback_score = models.IntegerField(null=True, blank=True, verbose_name="反馈评分(1-5)")
    feedback_comment = models.TextField(blank=True, verbose_name="反馈评论")
    
    class Meta:
        verbose_name = "问答记录"
        verbose_name_plural = "问答记录"
        
    def __str__(self):
        return f"Q: {self.question[:50]}..."


class ModelConfig(models.Model):
    """模型配置"""
    MODEL_TYPES = [
        ('api', 'API模式'),
        ('local', '本地模式'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="配置名称")
    description = models.TextField(blank=True, verbose_name="配置描述")
    model_type = models.CharField(max_length=10, choices=MODEL_TYPES, verbose_name="模型类型")
    model_name = models.CharField(max_length=100, verbose_name="模型名称")
    api_key = models.CharField(max_length=500, verbose_name="API密钥")
    api_base_url = models.URLField(verbose_name="API基础URL")
    model_path = models.CharField(max_length=1000, blank=True, verbose_name="本地模型路径")
    max_tokens = models.IntegerField(default=4096, verbose_name="最大Token数")
    temperature = models.FloatField(default=0.7, verbose_name="温度参数")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    is_default = models.BooleanField(default=False, verbose_name="是否默认")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "模型配置"
        verbose_name_plural = "模型配置"
        
    def __str__(self):
        return f"{self.name} ({self.model_name})"


class EmbeddingConfig(models.Model):
    """嵌入模型配置"""
    EMBEDDING_TYPES = [
        ('api', 'API模式'),
        ('local', '本地模式'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="配置名称")
    embedding_type = models.CharField(max_length=10, choices=EMBEDDING_TYPES, verbose_name="嵌入类型")
    model_name = models.CharField(max_length=100, verbose_name="模型名称")
    api_key = models.CharField(max_length=500, blank=True, verbose_name="API密钥")
    api_base_url = models.URLField(blank=True, verbose_name="API基础URL")
    model_path = models.CharField(max_length=1000, blank=True, verbose_name="本地模型路径")
    dimension = models.IntegerField(default=1536, verbose_name="向量维度")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    is_default = models.BooleanField(default=False, verbose_name="是否默认")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "嵌入模型配置"
        verbose_name_plural = "嵌入模型配置"
        
    def __str__(self):
        return f"{self.name} (dim: {self.dimension})"
