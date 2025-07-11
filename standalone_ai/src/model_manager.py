#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型管理器 - 管理多种机器学习模型
"""

import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

class ModelManager:
    """机器学习模型管理器"""
    
    def __init__(self):
        """初始化模型管理器"""
        self.models = {}
        self.performance = {}
        self.best_model_name = None
        self.is_trained = False
        
        # 初始化模型
        self._init_models()
    
    def _init_models(self):
        """初始化所有模型"""
        print("🤖 初始化机器学习模型...")
        
        # 线性回归
        self.models['LinearRegression'] = LinearRegression()
        
        # 随机森林
        self.models['RandomForest'] = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        
        # 梯度提升
        self.models['GradientBoosting'] = GradientBoostingRegressor(
            n_estimators=100,
            random_state=42
        )
        
        # 支持向量回归
        self.models['SVR'] = SVR(kernel='rbf', C=100, gamma=0.1)
        
        # XGBoost (如果可用)
        if XGBOOST_AVAILABLE:
            self.models['XGBoost'] = XGBRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
        
        print(f"✅ 初始化完成，共 {len(self.models)} 个模型")
    
    def train_all_models(self, X_train, y_train, X_test, y_test):
        """训练所有模型
        
        Args:
            X_train: 训练特征
            y_train: 训练目标
            X_test: 测试特征
            y_test: 测试目标
        """
        print("🏋️ 开始训练所有模型...")
        
        for name, model in self.models.items():
            print(f"  训练 {name}...")
            try:
                # 训练模型
                model.fit(X_train, y_train)
                
                # 预测
                y_pred = model.predict(X_test)
                
                # 评估性能
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                self.performance[name] = {
                    'mse': mse,
                    'r2': r2,
                    'rmse': np.sqrt(mse)
                }
                
                print(f"    {name}: MSE={mse:.6f}, R²={r2:.6f}")
                
            except Exception as e:
                print(f"    ❌ {name} 训练失败: {e}")
                # 从模型字典中移除失败的模型
                if name in self.models:
                    del self.models[name]
        
        # 选择最佳模型
        if self.performance:
            self.best_model_name = min(self.performance.keys(), 
                                     key=lambda x: self.performance[x]['mse'])
            print(f"🏆 最佳模型: {self.best_model_name}")
            self.is_trained = True
        else:
            print("❌ 所有模型训练失败")
    
    def predict(self, X):
        """使用最佳模型进行预测
        
        Args:
            X: 输入特征
            
        Returns:
            numpy.ndarray: 预测结果
        """
        if not self.is_trained:
            raise ValueError("模型未训练，请先调用train_all_models")
        
        if self.best_model_name is None:
            raise ValueError("没有可用的训练模型")
        
        best_model = self.models[self.best_model_name]
        return best_model.predict(X)
    
    def predict_with_model(self, X, model_name):
        """使用指定模型进行预测
        
        Args:
            X: 输入特征
            model_name: 模型名称
            
        Returns:
            numpy.ndarray: 预测结果
        """
        if model_name not in self.models:
            raise ValueError(f"模型 {model_name} 不存在")
        
        return self.models[model_name].predict(X)
    
    def get_model_performance(self):
        """获取所有模型的性能指标"""
        return self.performance.copy()
    
    def get_best_model_name(self):
        """获取最佳模型名称"""
        return self.best_model_name
    
    def get_available_models(self):
        """获取可用模型列表"""
        return list(self.models.keys())
    
    def save_models(self, filepath='models.pkl'):
        """保存模型到文件
        
        Args:
            filepath: 保存路径
        """
        if not self.is_trained:
            print("❌ 模型未训练，无法保存")
            return False
        
        try:
            model_data = {
                'models': self.models,
                'performance': self.performance,
                'best_model_name': self.best_model_name,
                'is_trained': self.is_trained
            }
            joblib.dump(model_data, filepath)
            print(f"💾 模型已保存到: {filepath}")
            return True
        except Exception as e:
            print(f"❌ 保存模型失败: {e}")
            return False
    
    def load_models(self, filepath='models.pkl'):
        """从文件加载模型
        
        Args:
            filepath: 模型文件路径
            
        Returns:
            bool: 加载是否成功
        """
        try:
            model_data = joblib.load(filepath)
            self.models = model_data['models']
            self.performance = model_data['performance']
            self.best_model_name = model_data['best_model_name']
            self.is_trained = model_data['is_trained']
            print(f"📂 模型已从 {filepath} 加载")
            return True
        except Exception as e:
            print(f"❌ 加载模型失败: {e}")
            return False
    
    def summary(self):
        """打印模型管理器摘要"""
        print("📋 模型管理器摘要:")
        print(f"  - 可用模型: {len(self.models)}")
        print(f"  - 模型列表: {', '.join(self.models.keys())}")
        print(f"  - 训练状态: {'已训练' if self.is_trained else '未训练'}")
        print(f"  - 最佳模型: {self.best_model_name or '未确定'}")
        
        if self.performance:
            print("  - 性能指标:")
            for name, metrics in self.performance.items():
                print(f"    {name}: MSE={metrics['mse']:.6f}, R²={metrics['r2']:.6f}")
