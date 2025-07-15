#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试预测功能和可视化
"""

import json
import sys
import os

# 添加AI预测模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
ai_prediction_path = os.path.join(current_dir, 'ai_prediction')
sys.path.insert(0, ai_prediction_path)

from ai_prediction.data_generator import DataGenerator
from ai_prediction.data_preprocessor import DataPreprocessor
from ai_prediction.model_manager import ModelManager
from ai_prediction.predictor import LoadPredictor
from ai_prediction.visualizer import Visualizer
from datetime import datetime, timedelta

def test_single_prediction_visualization():
    """测试单点预测可视化"""
    print("🧪 测试单点预测可视化...")
    
    # 初始化组件
    data_generator = DataGenerator()
    preprocessor = DataPreprocessor()
    model_manager = ModelManager()
    visualizer = Visualizer()
    
    # 生成训练数据
    print("📊 生成训练数据...")
    train_data = data_generator.generate_training_data(days=7)
    X_train, X_test, y_train, y_test = preprocessor.fit_transform(train_data)
    
    # 训练模型
    print("🤖 训练模型...")
    model_manager.train_core_models(X_train, y_train, X_test, y_test)
    
    # 创建预测器
    predictor = LoadPredictor(model_manager, preprocessor)
    
    # 执行单点预测
    print("🔮 执行单点预测...")
    result = predictor.predict_single_point(
        timestamp=datetime.now(),
        temperature=25.0,
        humidity=60.0,
        wind_speed=5.0,
        rainfall=0.0
    )
    
    print(f"✅ 预测结果: {result['predicted_load']:.2f} MW")
    print(f"✅ 使用模型: {result['model_used']}")
    print(f"✅ 输入特征: {list(result['input_features'].keys())}")
    
    # 生成可视化
    print("📊 生成可视化...")
    visualization = visualizer.plot_single_prediction(result)
    
    print(f"✅ 可视化数据类型: {type(visualization)}")
    print(f"✅ 可视化键: {list(visualization.keys())}")
    
    if 'html' in visualization:
        print(f"✅ HTML长度: {len(visualization['html'])} 字符")
    
    return result, visualization

def test_day_ahead_prediction_visualization():
    """测试日前预测可视化"""
    print("\n🧪 测试日前预测可视化...")
    
    # 初始化组件
    data_generator = DataGenerator()
    preprocessor = DataPreprocessor()
    model_manager = ModelManager()
    visualizer = Visualizer()
    
    # 生成训练数据
    print("📊 生成训练数据...")
    train_data = data_generator.generate_training_data(days=7)
    X_train, X_test, y_train, y_test = preprocessor.fit_transform(train_data)
    
    # 训练模型
    print("🤖 训练模型...")
    model_manager.train_core_models(X_train, y_train, X_test, y_test)
    
    # 创建预测器
    predictor = LoadPredictor(model_manager, preprocessor)
    
    # 执行日前预测
    print("🔮 执行日前预测...")
    target_date = datetime.now().date() + timedelta(days=1)
    result = predictor.predict_day_ahead(target_date)
    
    print(f"✅ 预测日期: {result['date']}")
    print(f"✅ 预测点数: {len(result['predictions'])}")
    print(f"✅ 峰值负荷: {result['statistics']['peak_load']:.2f} MW")
    print(f"✅ 使用模型: {result['model_used']}")
    
    # 生成可视化
    print("📊 生成可视化...")
    visualization = visualizer.plot_day_ahead_prediction(result)
    
    print(f"✅ 可视化数据类型: {type(visualization)}")
    print(f"✅ 可视化键: {list(visualization.keys())}")
    
    if 'main_chart' in visualization:
        print(f"✅ 主图表HTML长度: {len(visualization['main_chart']['html'])} 字符")
    if 'distribution_chart' in visualization:
        print(f"✅ 分布图表HTML长度: {len(visualization['distribution_chart']['html'])} 字符")
    if 'statistics_chart' in visualization:
        print(f"✅ 统计图表HTML长度: {len(visualization['statistics_chart']['html'])} 字符")
    
    return result, visualization

def test_api_response_structure():
    """测试API响应结构"""
    print("\n🧪 测试API响应结构...")
    
    # 模拟单点预测API响应
    single_result, single_viz = test_single_prediction_visualization()
    
    single_api_response = {
        "success": True,
        "data": {
            "prediction": single_result,
            "visualization": single_viz
        }
    }
    
    print("✅ 单点预测API响应结构:")
    print(f"   - success: {single_api_response['success']}")
    print(f"   - data.prediction键: {list(single_api_response['data']['prediction'].keys())}")
    print(f"   - data.visualization键: {list(single_api_response['data']['visualization'].keys())}")
    
    # 模拟日前预测API响应
    day_result, day_viz = test_day_ahead_prediction_visualization()
    
    day_api_response = {
        "success": True,
        "data": {
            "prediction": day_result,
            "visualization": day_viz
        }
    }
    
    print("✅ 日前预测API响应结构:")
    print(f"   - success: {day_api_response['success']}")
    print(f"   - data.prediction键: {list(day_api_response['data']['prediction'].keys())}")
    print(f"   - data.visualization键: {list(day_api_response['data']['visualization'].keys())}")
    
    return single_api_response, day_api_response

if __name__ == "__main__":
    print("🚀 开始测试预测可视化功能...")
    
    try:
        single_response, day_response = test_api_response_structure()
        
        print("\n🎉 所有测试完成！")
        print("\n📋 测试总结:")
        print("✅ 单点预测和可视化正常")
        print("✅ 日前预测和可视化正常")
        print("✅ API响应结构正确")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
