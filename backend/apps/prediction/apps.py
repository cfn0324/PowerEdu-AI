from django.apps import AppConfig


class PredictionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prediction'
    verbose_name = '电力负荷预测'
