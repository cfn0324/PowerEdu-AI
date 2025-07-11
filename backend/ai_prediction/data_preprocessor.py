#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据预处理器 - 处理和准备机器学习数据
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split

class DataPreprocessor:
    """数据预处理器"""
    
    def __init__(self):
        """初始化预处理器"""
        self.scaler = StandardScaler()
        self.target_scaler = MinMaxScaler()
        self.feature_columns = [
            'hour', 'minute', 'weekday', 'is_weekend', 'is_holiday',
            'temperature', 'humidity', 'wind_speed', 'rainfall'
        ]
        self.is_fitted = False
    
    def prepare_features(self, df):
        """准备特征数据
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            tuple: (特征矩阵X, 目标向量y)
        """
        # 确保所有必需列存在
        for col in self.feature_columns:
            if col not in df.columns:
                if col in ['is_weekend', 'is_holiday']:
                    df[col] = 0
                else:
                    print(f"⚠️ 缺少特征列: {col}")
                    return None, None
        
        # 提取特征
        X = df[self.feature_columns].copy()
        
        # 处理缺失值
        X = X.fillna(X.mean())
        
        # 提取目标变量
        y = df['load'].values if 'load' in df.columns else None
        
        return X, y
    
    def fit_transform(self, df):
        """拟合并转换训练数据
        
        Args:
            df: 训练数据DataFrame
            
        Returns:
            tuple: (X_train, X_test, y_train, y_test)
        """
        print("🔧 预处理训练数据...")
        
        # 准备特征
        X, y = self.prepare_features(df)
        if X is None:
            return None, None, None, None
        
        # 标准化特征
        X_scaled = self.scaler.fit_transform(X)
        
        # 标准化目标变量
        y_scaled = self.target_scaler.fit_transform(y.reshape(-1, 1)).flatten()
        
        # 分割训练和测试数据
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_scaled, test_size=0.2, random_state=42
        )
        
        self.is_fitted = True
        print(f"✅ 训练数据: {X_train.shape}, 测试数据: {X_test.shape}")
        
        return X_train, X_test, y_train, y_test
    
    def transform(self, df):
        """转换新数据
        
        Args:
            df: 新数据DataFrame
            
        Returns:
            numpy.ndarray: 转换后的特征矩阵
        """
        if not self.is_fitted:
            raise ValueError("预处理器未训练，请先调用fit_transform")
        
        X, _ = self.prepare_features(df)
        if X is None:
            return None
        
        return self.scaler.transform(X)
    
    def inverse_transform_target(self, y_scaled):
        """反转换目标变量
        
        Args:
            y_scaled: 标准化的目标变量
            
        Returns:
            numpy.ndarray: 原始尺度的目标变量
        """
        if not self.is_fitted:
            raise ValueError("预处理器未训练")
        
        return self.target_scaler.inverse_transform(y_scaled.reshape(-1, 1)).flatten()
    
    def get_feature_names(self):
        """获取特征名称"""
        return self.feature_columns
    
    def summary(self):
        """打印预处理器摘要"""
        if not self.is_fitted:
            print("❌ 预处理器未训练")
            return
        
        print("📋 预处理器摘要:")
        print(f"  - 特征数量: {len(self.feature_columns)}")
        print(f"  - 特征列: {', '.join(self.feature_columns)}")
        print(f"  - 特征缩放: StandardScaler")
        print(f"  - 目标缩放: MinMaxScaler")
        print(f"  - 状态: {'已训练' if self.is_fitted else '未训练'}")
