#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
预测器 - 执行电力负荷预测
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class LoadPredictor:
    """电力负荷预测器"""
    
    def __init__(self, model_manager, data_preprocessor):
        """初始化预测器
        
        Args:
            model_manager: 模型管理器实例
            data_preprocessor: 数据预处理器实例
        """
        self.model_manager = model_manager
        self.preprocessor = data_preprocessor
        
        if not model_manager.is_trained:
            raise ValueError("模型管理器未训练，请先训练模型")
        
        if not data_preprocessor.is_fitted:
            raise ValueError("数据预处理器未拟合，请先拟合数据")
    
    def predict_single_point(self, timestamp, temperature, humidity, 
                           wind_speed=5.0, rainfall=0.0):
        """预测单个时间点的负荷
        
        Args:
            timestamp: 时间戳
            temperature: 温度
            humidity: 湿度
            wind_speed: 风速
            rainfall: 降雨量
            
        Returns:
            float: 预测的负荷值
        """
        # 构建输入数据
        input_data = {
            'hour': timestamp.hour,
            'minute': timestamp.minute,
            'weekday': timestamp.weekday(),
            'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
            'is_holiday': self._is_holiday(timestamp),
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'rainfall': rainfall
        }
        
        # 转换为DataFrame
        df = pd.DataFrame([input_data])
        
        # 数据预处理
        X_scaled = self.preprocessor.transform(df)
        
        # 预测
        y_pred_scaled = self.model_manager.predict(X_scaled)
        
        # 反标准化
        y_pred = self.preprocessor.inverse_transform_target(y_pred_scaled)
        
        return float(y_pred[0])
    
    def predict_with_parameters(self, hour, minute, temperature, humidity, is_weekend=False, is_holiday=False):
        """使用参数进行单点预测"""
        timestamp = datetime.now().replace(hour=hour, minute=minute)
        
        input_data = {
            'hour': hour,
            'minute': minute,
            'weekday': timestamp.weekday(),
            'is_weekend': 1 if is_weekend else 0,
            'is_holiday': 1 if is_holiday else 0,
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': 5.0,  # 使用默认值
            'rainfall': 0.0      # 使用默认值
        }
        
        df = pd.DataFrame([input_data])
        X_scaled = self.preprocessor.transform(df)
        y_pred_scaled = self.model_manager.predict(X_scaled)
        y_pred = self.preprocessor.inverse_transform_target(y_pred_scaled)
        
        return float(y_pred[0])

    def predict_batch(self, start_time, periods=96, default_temp=25.0, 
                     default_humidity=60.0):
        """批量预测多个时间点
        
        Args:
            start_time: 开始时间
            periods: 预测点数
            default_temp: 默认温度
            default_humidity: 默认湿度
            
        Returns:
            pandas.DataFrame: 预测结果
        """
        print(f"🔮 批量预测 {periods} 个时间点...")
        
        # 生成时间序列
        time_points = pd.date_range(start=start_time, periods=periods, freq='15T')
        
        predictions = []
        for timestamp in time_points:
            # 模拟气象数据（实际应用中应使用真实气象预报）
            temp = self._simulate_temperature(timestamp, default_temp)
            humidity = self._simulate_humidity(temp, default_humidity)
            
            # 预测负荷
            load = self.predict_single_point(
                timestamp, temp, humidity,
                wind_speed=np.random.uniform(3, 8),
                rainfall=np.random.exponential(0.1) if np.random.random() < 0.2 else 0
            )
            
            predictions.append({
                'timestamp': timestamp,
                'predicted_load': load,
                'temperature': temp,
                'humidity': humidity
            })
        
        df = pd.DataFrame(predictions)
        print("✅ 批量预测完成")
        return df

    def get_prediction_summary(self, predictions_df):
        """获取预测摘要统计"""
        summary = {
            'mean': predictions_df['predicted_load'].mean(),
            'max': predictions_df['predicted_load'].max(),
            'min': predictions_df['predicted_load'].min(),
            'std': predictions_df['predicted_load'].std(),
            'max_time': predictions_df.loc[predictions_df['predicted_load'].idxmax()]['timestamp'],
            'min_time': predictions_df.loc[predictions_df['predicted_load'].idxmin()]['timestamp']
        }
        return summary
    
    def _is_holiday(self, timestamp):
        """判断是否为节假日（简化版）"""
        # 简化的节假日判断
        if (timestamp.month == 1 and timestamp.day <= 3) or \
           (timestamp.month == 5 and timestamp.day == 1) or \
           (timestamp.month == 10 and timestamp.day <= 3):
            return 1
        return 0
    
    def _simulate_temperature(self, timestamp, base_temp):
        """模拟温度数据"""
        hour = timestamp.hour
        
        # 日内温度变化
        if 6 <= hour <= 12:
            temp_adj = (hour - 6) * 1.5
        elif 13 <= hour <= 18:
            temp_adj = 9 - (hour - 12) * 0.5
        else:
            temp_adj = -3
        
        temperature = base_temp + temp_adj + np.random.normal(0, 1)
        return max(-5, min(35, temperature))
    
    def _simulate_humidity(self, temperature, base_humidity):
        """模拟湿度数据"""
        # 温度越高，湿度相对越低
        humidity_adj = (25 - temperature) * 0.8
        humidity = base_humidity + humidity_adj + np.random.normal(0, 5)
        return max(30, min(90, humidity))
    
    def validate_prediction(self, prediction):
        """验证预测结果的合理性
        
        Args:
            prediction: 预测值
            
        Returns:
            dict: 验证结果
        """
        validation = {
            'is_valid': True,
            'warnings': []
        }
        
        # 检查预测值范围
        if prediction < 20:
            validation['warnings'].append('预测负荷过低')
        elif prediction > 300:
            validation['warnings'].append('预测负荷过高')
        
        # 检查预测值是否为数值
        if not isinstance(prediction, (int, float)) or np.isnan(prediction):
            validation['is_valid'] = False
            validation['warnings'].append('预测结果无效')
        
        return validation
