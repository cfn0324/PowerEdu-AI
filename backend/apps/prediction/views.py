from ninja import Router
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import sys
import os
from datetime import datetime

# 添加AI预测模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
ai_prediction_path = os.path.join(current_dir, '../../ai_prediction')
sys.path.insert(0, ai_prediction_path)

try:
    from predictor import Predictor
    from data_generator import DataGenerator
    from model_manager import ModelManager
    from visualizer import Visualizer
except ImportError as e:
    print(f"AI预测模块导入失败: {e}")
    # 定义备用类
    class Predictor:
        def train_models(self, data): pass
        def predict_single(self, **kwargs): return {"prediction": 100, "model": "backup"}
        def predict_batch(self, **kwargs): return {"predictions": []}
        def evaluate_models(self, data): return {}
    
    class DataGenerator:
        def generate_load_data(self, **kwargs): return []
    
    class ModelManager:
        def get_available_models(self): return ["linear_regression", "random_forest"]

from .models import PredictionHistory, PredictionModel, ModelPerformance

router = Router()


@router.get("/models")
def get_models(request):
    """获取可用模型列表"""
    try:
        model_manager = ModelManager()
        models = model_manager.get_available_models()
        return {"success": True, "data": models}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/predict/single")
def single_predict(request):
    """单点预测"""
    try:
        data = json.loads(request.body)
        model_name = data.get('model', 'linear_regression')
        input_features = data.get('features', {})
        
        # 初始化预测器
        predictor = Predictor()
        
        # 生成测试数据并训练模型
        data_generator = DataGenerator()
        train_data = data_generator.generate_load_data(days=30)
        predictor.train_models(train_data)
        
        # 进行预测
        result = predictor.predict_single(
            temperature=input_features.get('temperature', 25),
            humidity=input_features.get('humidity', 60),
            hour=input_features.get('hour', 12),
            day_of_week=input_features.get('day_of_week', 1),
            month=input_features.get('month', 6),
            model_name=model_name
        )
        
        # 保存预测历史
        if request.user.is_authenticated:
            try:
                model_obj, _ = PredictionModel.objects.get_or_create(
                    name=model_name,
                    defaults={'model_type': model_name, 'description': f'{model_name}模型'}
                )
                PredictionHistory.objects.create(
                    user=request.user,
                    model=model_obj,
                    input_data=input_features,
                    prediction_result=result,
                    prediction_type='single'
                )
            except Exception as db_error:
                print(f"数据库保存错误: {db_error}")
        
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/predict/batch")
def batch_predict(request):
    """批量预测"""
    try:
        data = json.loads(request.body)
        model_name = data.get('model', 'linear_regression')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # 初始化预测器
        predictor = Predictor()
        
        # 生成测试数据并训练模型
        data_generator = DataGenerator()
        train_data = data_generator.generate_load_data(days=30)
        predictor.train_models(train_data)
        
        # 进行批量预测
        result = predictor.predict_batch(
            start_date=start_date,
            end_date=end_date,
            model_name=model_name
        )
        
        # 保存预测历史
        if request.user.is_authenticated:
            try:
                model_obj, _ = PredictionModel.objects.get_or_create(
                    name=model_name,
                    defaults={'model_type': model_name, 'description': f'{model_name}模型'}
                )
                PredictionHistory.objects.create(
                    user=request.user,
                    model=model_obj,
                    input_data={'start_date': start_date, 'end_date': end_date},
                    prediction_result=result,
                    prediction_type='batch'
                )
            except Exception as db_error:
                print(f"数据库保存错误: {db_error}")
        
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/performance")
def get_model_performance(request):
    """获取模型性能对比"""
    try:
        # 初始化组件
        data_generator = DataGenerator()
        predictor = Predictor()
        
        # 生成训练数据
        train_data = data_generator.generate_load_data(days=30)
        test_data = data_generator.generate_load_data(days=7, start_date='2024-07-01')
        
        # 训练模型
        predictor.train_models(train_data)
        
        # 获取性能指标
        performance = predictor.evaluate_models(test_data)
        
        return {"success": True, "data": performance}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/history")
def get_prediction_history(request):
    """获取用户预测历史"""
    if not request.user.is_authenticated:
        return {"success": False, "error": "用户未登录"}
    
    try:
        history = PredictionHistory.objects.filter(user=request.user).order_by('-created_at')[:20]
        data = []
        for record in history:
            data.append({
                'id': record.id,
                'model': record.model.name,
                'prediction_type': record.get_prediction_type_display(),
                'input_data': record.input_data,
                'prediction_result': record.prediction_result,
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}
