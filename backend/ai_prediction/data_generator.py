#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据生成器 - 生成电力负荷训练数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class DataGenerator:
    """电力负荷数据生成器"""
    
    def __init__(self, seed=42):
        """初始化数据生成器"""
        np.random.seed(seed)
        random.seed(seed)
        
    def generate_training_data(self, days=30):
        """生成训练数据
        
        Args:
            days: 生成数据的天数
            
        Returns:
            pandas.DataFrame: 训练数据
        """

        
        # 生成时间序列
        start_date = datetime(2024, 1, 1)
        end_date = start_date + timedelta(days=days)
        
        # 15分钟间隔的时间点
        time_points = pd.date_range(start=start_date, end=end_date, freq='15T')
        
        data = []
        for timestamp in time_points:
            # 基础负荷模式
            hour = timestamp.hour
            minute = timestamp.minute
            weekday = timestamp.weekday()  # 0=Monday, 6=Sunday
            
            # 负荷基准值（考虑时段特征）
            if 6 <= hour <= 8 or 18 <= hour <= 20:  # 早晚高峰
                base_load = 120 + np.random.normal(0, 10)
            elif 9 <= hour <= 17:  # 日间
                base_load = 90 + np.random.normal(0, 8)
            else:  # 夜间
                base_load = 60 + np.random.normal(0, 5)
            
            # 周末调整
            if weekday >= 5:  # 周末
                base_load *= 0.8
            
            # 气象参数
            temperature = self._generate_temperature(timestamp)
            humidity = self._generate_humidity(temperature)
            wind_speed = np.random.uniform(0, 15)
            rainfall = np.random.exponential(0.1) if np.random.random() < 0.3 else 0
            
            # 温度对负荷的影响
            if temperature > 25:  # 高温增加空调负荷
                base_load += (temperature - 25) * 2
            elif temperature < 10:  # 低温增加取暖负荷
                base_load += (10 - temperature) * 1.5
            
            # 湿度影响
            if humidity > 80:
                base_load += 5
            
            # 添加随机噪声
            load = max(20, base_load + np.random.normal(0, 3))
            
            # 节假日判断（简化）
            is_holiday = 1 if (timestamp.month == 1 and timestamp.day <= 3) or \
                            (timestamp.month == 5 and timestamp.day == 1) or \
                            (timestamp.month == 10 and timestamp.day <= 3) else 0
            
            data.append({
                'timestamp': timestamp,
                'hour': hour,
                'minute': minute,
                'weekday': weekday,
                'is_weekend': 1 if weekday >= 5 else 0,
                'is_holiday': is_holiday,
                'temperature': round(temperature, 1),
                'humidity': round(humidity, 1),
                'wind_speed': round(wind_speed, 1),
                'rainfall': round(rainfall, 1),
                'load': round(load, 2)
            })
        
        df = pd.DataFrame(data)

        return df
    
    def _generate_temperature(self, timestamp):
        """生成温度数据"""
        # 基于月份的季节性温度
        month = timestamp.month
        hour = timestamp.hour
        
        # 月份基准温度
        monthly_temp = {
            1: 5, 2: 8, 3: 12, 4: 18, 5: 23, 6: 28,
            7: 32, 8: 31, 9: 27, 10: 21, 11: 14, 12: 7
        }
        
        base_temp = monthly_temp[month]
        
        # 日内温度变化
        if 6 <= hour <= 14:  # 白天升温
            temp_adj = (hour - 6) * 2
        elif 15 <= hour <= 18:  # 下午高温
            temp_adj = 16 - (hour - 14) * 2
        else:  # 夜间降温
            temp_adj = -5
        
        temperature = base_temp + temp_adj + np.random.normal(0, 2)
        return max(-10, min(40, temperature))
    
    def _generate_humidity(self, temperature):
        """生成湿度数据（与温度相关）"""
        # 高温低湿，低温高湿
        base_humidity = 80 - (temperature - 10) * 1.5
        humidity = base_humidity + np.random.normal(0, 10)
        return max(20, min(100, humidity))
    
    def generate_test_data(self, start_time, periods=96):
        """生成测试数据
        
        Args:
            start_time: 开始时间
            periods: 生成的时间点数量
            
        Returns:
            pandas.DataFrame: 测试数据
        """
        time_points = pd.date_range(start=start_time, periods=periods, freq='15T')
        
        data = []
        for timestamp in time_points:
            data.append({
                'timestamp': timestamp,
                'hour': timestamp.hour,
                'minute': timestamp.minute,
                'weekday': timestamp.weekday(),
                'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
                'is_holiday': 0,  # 简化
                'temperature': self._generate_temperature(timestamp),
                'humidity': self._generate_humidity(self._generate_temperature(timestamp)),
                'wind_speed': np.random.uniform(0, 15),
                'rainfall': 0
            })
        
        return pd.DataFrame(data)
