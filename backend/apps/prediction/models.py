from django.db import models
from apps.user.models import User  # 使用自定义User模型


class PredictionModel(models.Model):
    """预测模型管理"""
    name = models.CharField(max_length=100, verbose_name='模型名称')
    model_type = models.CharField(max_length=50, verbose_name='模型类型')
    description = models.TextField(verbose_name='模型描述', blank=True)
    accuracy = models.FloatField(verbose_name='模型精度', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    class Meta:
        db_table = 'prediction_model'
        verbose_name = '预测模型'
        verbose_name_plural = '预测模型'

    def __str__(self):
        return self.name


class PredictionHistory(models.Model):
    """预测历史记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    model = models.ForeignKey(PredictionModel, on_delete=models.CASCADE, verbose_name='使用模型')
    input_data = models.JSONField(verbose_name='输入数据')
    prediction_result = models.JSONField(verbose_name='预测结果')
    prediction_type = models.CharField(max_length=20, choices=[
        ('single', '单点预测'),
        ('batch', '批量预测'),
        ('day_ahead', '日前预测')
    ], verbose_name='预测类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='预测时间')

    class Meta:
        db_table = 'prediction_history'
        verbose_name = '预测历史'
        verbose_name_plural = '预测历史'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.model.name} - {self.created_at}'


class ModelPerformance(models.Model):
    """模型性能指标"""
    model = models.OneToOneField(PredictionModel, on_delete=models.CASCADE, verbose_name='模型')
    mae = models.FloatField(verbose_name='平均绝对误差', null=True, blank=True)
    mse = models.FloatField(verbose_name='均方误差', null=True, blank=True)
    rmse = models.FloatField(verbose_name='均方根误差', null=True, blank=True)
    r2_score = models.FloatField(verbose_name='R²决定系数', null=True, blank=True)
    training_time = models.FloatField(verbose_name='训练时间(秒)', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'model_performance'
        verbose_name = '模型性能'
        verbose_name_plural = '模型性能'

    def __str__(self):
        return f'{self.model.name} - 性能指标'
