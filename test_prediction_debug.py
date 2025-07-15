#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI预测系统快速测试脚本
用于诊断参数传递问题
"""

import os
import sys
import django

# 设置Django环境
sys.path.append('d:/xm/PowerEdu-AI/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu.settings')
django.setup()

def test_prediction_methods():
    """测试预测方法的参数传递"""
    try:
        from ai_prediction.model_manager import ModelManager
        from ai_prediction.data_preprocessor import DataPreprocessor
        from ai_prediction.predictor import LoadPredictor
        from ai_prediction.data_generator import DataGenerator
        
        print("📊 开始测试AI预测系统...")
        
        # 1. 生成测试数据
        print("1. 生成测试数据...")
        data_generator = DataGenerator()
        train_data = data_generator.generate_training_data(days=1)  # 少量数据
        print(f"   ✅ 训练数据: {len(train_data)} 条")
        
        # 2. 数据预处理
        print("2. 数据预处理...")
        preprocessor = DataPreprocessor()
        X_train, X_test, y_train, y_test = preprocessor.fit_transform(train_data)
        print(f"   ✅ 预处理完成: 训练集 {X_train.shape}, 测试集 {X_test.shape}")
        
        # 3. 训练模型
        print("3. 训练模型...")
        model_manager = ModelManager()
        success = model_manager.train_core_models(X_train, y_train, X_test, y_test)
        if not success:
            print("   ❌ 模型训练失败")
            return False
        print(f"   ✅ 模型训练完成，最佳模型: {model_manager.best_model_name}")
        
        # 4. 测试预测方法
        print("4. 测试预测方法...")
        
        # 测试 predict 方法（最佳模型）
        print("   测试 predict 方法...")
        test_X = X_test[:1]  # 取一个样本测试
        result1 = model_manager.predict(test_X)
        print(f"   ✅ predict 方法成功: {result1}")
        
        # 测试 predict_with_model 方法
        print("   测试 predict_with_model 方法...")
        available_models = model_manager.get_available_models()
        print(f"   可用模型: {available_models}")
        
        if available_models:
            test_model = available_models[0]
            print(f"   使用模型: {test_model}")
            result2 = model_manager.predict_with_model(test_X, test_model)
            print(f"   ✅ predict_with_model 方法成功: {result2}")
        
        # 5. 测试LoadPredictor
        print("5. 测试LoadPredictor...")
        predictor = LoadPredictor(model_manager, preprocessor)
        
        # 测试单点预测
        print("   测试单点预测...")
        from datetime import datetime
        single_result = predictor.predict_single_point(
            timestamp=datetime(2024, 1, 1, 12, 0),
            temperature=25.0,
            humidity=60.0,
            wind_speed=3.0,
            rainfall=0.0
        )
        print(f"   ✅ 单点预测成功: {single_result}")
        
        print("🎉 所有测试通过！")
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ 测试失败: {str(e)}")
        print(f"详细错误:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_prediction_methods()
