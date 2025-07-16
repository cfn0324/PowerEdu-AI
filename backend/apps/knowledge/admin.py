from django.contrib import admin
from .models import (
    KnowledgeBase, Document, DocumentChunk, 
    QASession, QARecord, ModelConfig, EmbeddingConfig
)


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'knowledge_base', 'file_type', 'status', 'uploaded_at']
    list_filter = ['file_type', 'status', 'uploaded_at']
    search_fields = ['title', 'file_path']
    readonly_fields = ['uploaded_at', 'processed_at', 'file_size', 'chunk_count']


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['document', 'chunk_index', 'created_at']
    list_filter = ['created_at']
    search_fields = ['document__title', 'content']
    readonly_fields = ['created_at']


@admin.register(QASession)
class QASessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'knowledge_base', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'session_id', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(QARecord)
class QARecordAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'session', 'model_used', 'response_time', 'created_at']
    list_filter = ['model_used', 'created_at', 'feedback_score']
    search_fields = ['question', 'answer']
    readonly_fields = ['created_at', 'response_time', 'tokens_used']
    
    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_preview.short_description = "问题预览"


@admin.register(ModelConfig)
class ModelConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'model_type', 'is_active', 'is_default']
    list_filter = ['model_type', 'provider', 'is_active', 'is_default']
    search_fields = ['name', 'model_name']
    readonly_fields = ['created_at']


@admin.register(EmbeddingConfig)
class EmbeddingConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_name', 'embedding_type', 'dimension', 'is_active', 'is_default']
    list_filter = ['embedding_type', 'is_active', 'is_default']
    search_fields = ['name', 'model_name']
    readonly_fields = ['created_at']
