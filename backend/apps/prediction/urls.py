from django.urls import path
from ninja import NinjaAPI
from .views import router

# 创建API实例
api = NinjaAPI(title="电力负荷预测API")

# 添加路由
api.add_router("/prediction", router)

urlpatterns = [
    path("api/", api.urls),
]
