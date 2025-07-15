#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试预测系统修复效果
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime

# 添加AI预测模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
ai_prediction_path = os.path.join(current_dir, 'ai_prediction')
sys.path.insert(0, ai_prediction_path)

from ai_prediction.data_generator import DataGenerator
from ai_prediction.data_preprocessor import DataPreprocessor
from ai_prediction.model_manager import ModelManager
from ai_prediction.predictor import LoadPredictor

def test_prediction_fix():
    """测试预测系统修复效果"""
    print("🧪 开始测试预测系统修复效果...")
    
    try:
        # 1. 初始化系统
        print("📊 初始化数据生成器...")
        data_generator = DataGenerator()
        
        print("📊 生成测试数据...")
        train_data = data_generator.generate_training_data(days=7)  # 少量数据用于测试
        print(f"✅ 生成数据完成，数据量: {len(train_data)}")
        
        print("🔧 初始化数据预处理器...")
        data_preprocessor = DataPreprocessor()
        X_train, X_test, y_train, y_test = data_preprocessor.fit_transform(train_data)
        print(f"✅ 数据预处理完成，训练集: {X_train.shape}, 测试集: {X_test.shape}")
        
        print("🤖 初始化模型管理器...")
        model_manager = ModelManager()
        
        print("📚 训练核心模型...")
        training_success = model_manager.train_core_models(X_train, y_train, X_test, y_test)
        
        if not training_success:
            print("❌ 模型训练失败")
            return False
        
        print(f"✅ 模型训练完成，最佳模型: {model_manager.best_model_name}")
        print(f"可用模型: {list(model_manager.models.keys())}")
        
        # 2. 初始化预测器
        print("🔮 初始化预测器...")
        predictor = LoadPredictor(model_manager, data_preprocessor)
        
        # 3. 测试不同的预测方式
        print("\n🧪 测试1: 使用默认模型预测...")
        test_data = {
            'timestamp': '2024-07-15 14:30:00',
            'temperature': 25.5,
            'humidity': 65,
            'wind_speed': 5.2,
            'rainfall': 0.0,
            'model_name': None  # 使用默认模型
        }
        
        result1 = predictor.predict_single_point(
            timestamp=test_data['timestamp'],
            temperature=test_data['temperature'],
            humidity=test_data['humidity'],
            wind_speed=test_data['wind_speed'],
            rainfall=test_data['rainfall'],
            model_name=test_data['model_name']
        )
        print(f"✅ 默认模型预测成功: {result1['predicted_load']:.2f} MW, 使用模型: {result1['model_used']}")
        
        # 4. 测试指定模型预测
        available_models = list(model_manager.models.keys())
        if len(available_models) > 0:
            specific_model = available_models[0]
            print(f"\n🧪 测试2: 使用指定模型 {specific_model} 预测...")
            
            result2 = predictor.predict_single_point(
                timestamp=test_data['timestamp'],
                temperature=test_data['temperature'],
                humidity=test_data['humidity'],
                wind_speed=test_data['wind_speed'],
                rainfall=test_data['rainfall'],
                model_name=specific_model
            )
            print(f"✅ 指定模型预测成功: {result2['predicted_load']:.2f} MW, 使用模型: {result2['model_used']}")
        
        # 5. 测试批量预测
        print(f"\n🧪 测试3: 批量预测...")
        batch_data = [
            {
                'timestamp': '2024-07-15 15:00:00',
                'temperature': 26.0,
                'humidity': 60,
                'wind_speed': 4.8,
                'rainfall': 0.0
            },
            {
                'timestamp': '2024-07-15 15:15:00',
                'temperature': 26.2,
                'humidity': 58,
                'wind_speed': 5.0,
                'rainfall': 0.0
            }
        ]
        
        batch_results = predictor.predict_batch(batch_data, model_name=None)
        print(f"✅ 批量预测成功: {len(batch_results)} 个预测结果")
        for i, result in enumerate(batch_results):
            print(f"   时间点 {i+1}: {result['predicted_load']:.2f} MW")
        
        print(f"\n🎉 所有测试通过！修复成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_prediction_fix()
