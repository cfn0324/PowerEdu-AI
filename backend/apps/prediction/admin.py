from django.contrib import admin
from .models import PredictionModel, PredictionHistory, ModelPerformance


@admin.register(PredictionModel)
class PredictionModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'accuracy', 'is_active', 'created_at']
    list_filter = ['model_type', 'is_active', 'created_at']
    search_fields = ['name', 'model_type']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'model', 'prediction_type', 'created_at']
    list_filter = ['prediction_type', 'created_at', 'model']
    search_fields = ['user__username', 'model__name']
    readonly_fields = ['created_at']


@admin.register(ModelPerformance)
class ModelPerformanceAdmin(admin.ModelAdmin):
    list_display = ['model', 'mae', 'mse', 'rmse', 'r2_score', 'updated_at']
    readonly_fields = ['updated_at']
