#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
预测器 - 执行电力负荷预测
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

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
                           wind_speed=5.0, rainfall=0.0, model_name=None):
        """预测单个时间点的负荷
        
        Args:
            timestamp: 时间戳字符串或datetime对象
            temperature: 温度
            humidity: 湿度
            wind_speed: 风速
            rainfall: 降雨量
            model_name: 指定使用的模型名称
            
        Returns:
            dict: 包含预测值和相关信息的字典
        """
        # 处理时间戳
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        
        # 构建输入数据
        input_data = {
            'timestamp': timestamp,
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'rainfall': rainfall,
            'hour': timestamp.hour,
            'minute': timestamp.minute,  # 添加缺失的minute字段
            'weekday': timestamp.weekday(),
            'day_of_week': timestamp.weekday(),  # 保持兼容性
            'month': timestamp.month,
            'is_holiday': self._is_holiday(timestamp),
            'is_weekend': 1 if timestamp.weekday() >= 5 else 0
        }
        
        # 转换为DataFrame
        df = pd.DataFrame([input_data])
        
        # 预处理
        X = self.preprocessor.transform(df)
        
        # 预测
        if model_name is None:
            prediction = self.model_manager.predict(X)
            model_name = self.model_manager.best_model_name
        else:
            prediction = self.model_manager.predict_with_model(X, model_name)
        
        return {
            'timestamp': timestamp.isoformat(),
            'predicted_load': float(prediction[0]),
            'model_used': model_name,
            'input_features': input_data,
            'prediction_time': datetime.now().isoformat()
        }
    
    def predict_batch(self, prediction_data, model_name=None):
        """批量预测
        
        Args:
            prediction_data: 包含预测输入的DataFrame或字典列表
            model_name: 指定使用的模型名称
            
        Returns:
            list: 预测结果列表
        """
        if isinstance(prediction_data, list):
            df = pd.DataFrame(prediction_data)
        else:
            df = prediction_data.copy()
        
        # 确保包含所需的时间特征
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['minute'] = df['timestamp'].dt.minute  # 添加缺失的minute字段
            df['weekday'] = df['timestamp'].dt.weekday  # 添加weekday字段
            df['day_of_week'] = df['timestamp'].dt.weekday  # 保持兼容性
            df['month'] = df['timestamp'].dt.month
            df['is_holiday'] = df['timestamp'].apply(self._is_holiday)
            df['is_weekend'] = (df['timestamp'].dt.weekday >= 5).astype(int)
        
        # 预处理
        X = self.preprocessor.transform(df)
        
        # 预测
        if model_name is None:
            predictions = self.model_manager.predict(X)
            model_name = self.model_manager.best_model_name
        else:
            predictions = self.model_manager.predict_with_model(X, model_name)
        
        # 构建结果
        results = []
        for i, row in df.iterrows():
            result = {
                'timestamp': row['timestamp'].isoformat() if 'timestamp' in row else f'point_{i}',
                'predicted_load': float(predictions[i]),
                'model_used': model_name,
                'prediction_time': datetime.now().isoformat()
            }
            results.append(result)
        
        return results
    
    def predict_day_ahead(self, target_date, weather_forecast=None, model_name=None):
        """预测未来一天96个时间点的负荷
        
        Args:
            target_date: 目标日期字符串或datetime对象
            weather_forecast: 天气预报数据，如果为None则使用模拟数据
            model_name: 指定使用的模型名称
            
        Returns:
            dict: 包含预测结果和分析的字典
        """
        # 处理目标日期
        if isinstance(target_date, str):
            try:
                # 确保日期字符串格式正确
                target_date = pd.to_datetime(target_date, format='%Y-%m-%d').date()
            except Exception as e:
                raise ValueError(f"日期格式错误: {target_date}，应为YYYY-MM-DD格式")
        elif isinstance(target_date, datetime):
            target_date = target_date.date()
        
        print(f"🗓️  预测目标日期: {target_date}")
        
        # 生成24小时96个时间点
        start_time = datetime.combine(target_date, datetime.min.time())
        time_points = pd.date_range(start=start_time, periods=96, freq='15T')
        
        print(f"⏰ 生成时间点: {len(time_points)}个，从 {time_points[0]} 到 {time_points[-1]}")
        
        # 构建预测数据
        prediction_data = []
        for i, timestamp in enumerate(time_points):
            if weather_forecast and i < len(weather_forecast):
                # 使用提供的天气预报
                weather = weather_forecast[i]
                temp = weather.get('temperature', 20)
                humidity = weather.get('humidity', 60)
                wind_speed = weather.get('wind_speed', 5)
                rainfall = weather.get('rainfall', 0)
            else:
                # 使用模拟天气数据
                hour = timestamp.hour
                minute = timestamp.minute
                
                # 模拟日温度变化
                temp_seasonal = 20 + 15 * np.sin(2 * np.pi * (timestamp.dayofyear - 80) / 365)
                temp_daily = 5 * np.sin(2 * np.pi * (hour * 60 + minute) / (24 * 60))
                temp = temp_seasonal + temp_daily + np.random.normal(0, 1)
                
                humidity = max(30, min(90, 70 - 0.5 * temp + np.random.normal(0, 5)))
                wind_speed = max(0, np.random.normal(8, 2))
                rainfall = 0  # 假设无降雨
            
            prediction_data.append({
                'timestamp': timestamp,
                'temperature': temp,
                'humidity': humidity,
                'wind_speed': wind_speed,
                'rainfall': rainfall,
                'hour': timestamp.hour,
                'minute': timestamp.minute,  # 添加缺失的minute字段
                'weekday': timestamp.weekday(),  # 添加weekday字段
                'day_of_week': timestamp.weekday(),  # 保持兼容性
                'month': timestamp.month,
                'is_holiday': self._is_holiday(timestamp),
                'is_weekend': 1 if timestamp.weekday() >= 5 else 0
            })
        
        # 批量预测
        results = self.predict_batch(prediction_data, model_name)
        
        # 计算统计信息
        predictions = [r['predicted_load'] for r in results]
        peak_load = max(predictions)
        min_load = min(predictions)
        avg_load = np.mean(predictions)
        
        # 找到峰值时间
        peak_time_idx = predictions.index(peak_load)
        peak_time = time_points[peak_time_idx]
        
        # 计算负荷分布
        load_distribution = {
            'night': np.mean([p for i, p in enumerate(predictions) if 0 <= time_points[i].hour < 6]),
            'morning': np.mean([p for i, p in enumerate(predictions) if 6 <= time_points[i].hour < 12]),
            'afternoon': np.mean([p for i, p in enumerate(predictions) if 12 <= time_points[i].hour < 18]),
            'evening': np.mean([p for i, p in enumerate(predictions) if 18 <= time_points[i].hour < 24])
        }
        
        return {
            'date': target_date.isoformat(),
            'predictions': results,
            'statistics': {
                'peak_load': peak_load,
                'min_load': min_load,
                'average_load': avg_load,
                'peak_time': peak_time.isoformat(),
                'total_energy': sum(predictions) * 0.25,  # 15分钟 = 0.25小时
                'load_factor': avg_load / peak_load
            },
            'load_distribution': load_distribution,
            'model_used': model_name or self.model_manager.best_model_name,
            'prediction_time': datetime.now().isoformat()
        }
    
    def predict_with_uncertainty(self, input_data, n_samples=100):
        """使用不确定性分析进行预测
        
        Args:
            input_data: 输入数据
            n_samples: 采样次数
            
        Returns:
            dict: 包含预测均值、标准差和置信区间的结果
        """
        predictions = []
        
        # 使用不同模型进行预测
        for model_name in self.model_manager.models.keys():
            try:
                if isinstance(input_data, list):
                    result = self.predict_batch(input_data, model_name)
                    pred_values = [r['predicted_load'] for r in result]
                else:
                    result = self.predict_single_point(**input_data, model_name=model_name)
                    pred_values = [result['predicted_load']]
                
                predictions.append(pred_values)
            except:
                continue
        
        if not predictions:
            raise ValueError("无可用模型进行预测")
        
        # 计算统计信息
        predictions = np.array(predictions)
        mean_pred = np.mean(predictions, axis=0)
        std_pred = np.std(predictions, axis=0)
        
        # 计算置信区间
        confidence_95 = {
            'lower': mean_pred - 1.96 * std_pred,
            'upper': mean_pred + 1.96 * std_pred
        }
        
        return {
            'mean_prediction': mean_pred.tolist(),
            'std_prediction': std_pred.tolist(),
            'confidence_interval_95': confidence_95,
            'model_predictions': {f'model_{i}': pred.tolist() for i, pred in enumerate(predictions)},
            'prediction_time': datetime.now().isoformat()
        }
    
    def analyze_prediction_factors(self, prediction_result, actual_load=None):
        """分析预测因素和可能的误差原因
        
        Args:
            prediction_result: 预测结果
            actual_load: 实际负荷值（可选）
            
        Returns:
            dict: 分析结果
        """
        analysis = {
            'prediction_quality': 'unknown',
            'key_factors': [],
            'potential_issues': [],
            'recommendations': []
        }
        
        # 如果有实际值，计算误差
        if actual_load is not None:
            if isinstance(prediction_result, list):
                predicted_values = [r['predicted_load'] for r in prediction_result]
                if isinstance(actual_load, list) and len(predicted_values) == len(actual_load):
                    errors = np.abs(np.array(predicted_values) - np.array(actual_load))
                    mape = np.mean(errors / np.array(actual_load)) * 100
                    
                    if mape < 5:
                        analysis['prediction_quality'] = 'excellent'
                    elif mape < 10:
                        analysis['prediction_quality'] = 'good'
                    elif mape < 20:
                        analysis['prediction_quality'] = 'fair'
                    else:
                        analysis['prediction_quality'] = 'poor'
                        
                    analysis['mape'] = mape
                    analysis['max_error'] = float(np.max(errors))
                    analysis['mean_error'] = float(np.mean(errors))
            else:
                error = abs(prediction_result['predicted_load'] - actual_load)
                relative_error = error / actual_load * 100
                analysis['absolute_error'] = error
                analysis['relative_error'] = relative_error
                
                if relative_error < 5:
                    analysis['prediction_quality'] = 'excellent'
                elif relative_error < 10:
                    analysis['prediction_quality'] = 'good'
                elif relative_error < 20:
                    analysis['prediction_quality'] = 'fair'
                else:
                    analysis['prediction_quality'] = 'poor'
        
        # 分析关键因素
        if isinstance(prediction_result, dict) and 'input_features' in prediction_result:
            features = prediction_result['input_features']
            
            # 温度因素
            temp = features.get('temperature', 20)
            if temp > 30:
                analysis['key_factors'].append('高温驱动空调负荷增加')
            elif temp < 5:
                analysis['key_factors'].append('低温驱动取暖负荷增加')
            
            # 时间因素
            hour = features.get('hour', 12)
            if 6 <= hour <= 8 or 18 <= hour <= 20:
                analysis['key_factors'].append('用电高峰时段')
            elif 22 <= hour or hour <= 5:
                analysis['key_factors'].append('夜间低负荷时段')
            
            # 节假日因素
            if features.get('is_holiday', 0):
                analysis['key_factors'].append('节假日负荷模式')
            
            # 周末因素
            if features.get('is_weekend', 0):
                analysis['key_factors'].append('周末负荷模式')
        
        # 预测质量建议
        if analysis['prediction_quality'] == 'poor':
            analysis['potential_issues'] = [
                '极端天气条件可能影响预测准确性',
                '特殊事件（如大型活动）可能改变负荷模式',
                '模型可能需要重新训练以适应新的负荷特征',
                '数据质量问题可能影响预测结果'
            ]
            analysis['recommendations'] = [
                '增加更多历史数据进行模型训练',
                '考虑加入更多外部因素（如经济指标、特殊事件）',
                '使用集成学习方法提高预测稳定性',
                '建立实时数据校验机制'
            ]
        elif analysis['prediction_quality'] == 'fair':
            analysis['recommendations'] = [
                '优化特征工程，提取更有效的特征',
                '调整模型参数以提高预测精度',
                '考虑使用深度学习模型处理复杂非线性关系'
            ]
        
        analysis['analysis_time'] = datetime.now().isoformat()
        return analysis
    
    def _is_holiday(self, timestamp):
        """判断是否为节假日（简化实现）"""
        month = timestamp.month
        day = timestamp.day
        
        # 元旦
        if month == 1 and day <= 3:
            return 1
        # 劳动节
        elif month == 5 and day == 1:
            return 1
        # 国庆节
        elif month == 10 and day <= 7:
            return 1
        # 春节（简化，假设2月第一周）
        elif month == 2 and day <= 7:
            return 1
        
        return 0
    
    def get_model_performance_summary(self):
        """获取模型性能摘要"""
        if not self.model_manager.performance:
            return None
        
        return {
            'available_models': list(self.model_manager.models.keys()),
            'best_model': self.model_manager.best_model_name,
            'performance_metrics': self.model_manager.performance,
            'model_comparison': self.model_manager.get_model_comparison()
        }
