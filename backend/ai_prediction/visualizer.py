#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
可视化工具 - 生成预测结果图表
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import base64
import io
import time
from datetime import datetime, timedelta

class Visualizer:
    """可视化工具类"""
    
    def __init__(self):
        """初始化可视化工具"""
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'warning': '#ff9800',
            'error': '#f44336',
            'info': '#2196f3',
            'purple': '#9c27b0',
            'teal': '#009688'
        }
    
    def plot_single_prediction(self, prediction_result):
        """绘制单点预测结果
        
        Args:
            prediction_result: 预测结果字典
            
        Returns:
            dict: 包含图表HTML和相关信息
        """
        try:
            prediction_value = prediction_result.get('predicted_load', 0)
            input_features = prediction_result.get('input_features', {})
            
            # 创建子图
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('预测负荷', '环境参数', '时间特征分析', '负荷影响因子'),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "pie"}, {"type": "scatter"}]]
            )
            
            # 1. 预测负荷柱状图
            fig.add_trace(
                go.Bar(
                    x=['预测负荷'],
                    y=[prediction_value],
                    text=[f'{prediction_value:.2f} MW'],
                    textposition='auto',
                    marker_color=self.colors['primary'],
                    name='预测负荷'
                ),
                row=1, col=1
            )
            
            # 2. 环境参数对比
            if input_features:
                feature_names = ['温度(°C)', '湿度(%)', '风速(m/s)', '降雨量(mm)']
                feature_keys = ['temperature', 'humidity', 'wind_speed', 'rainfall']
                feature_values = [input_features.get(key, 0) for key in feature_keys]
                
                fig.add_trace(
                    go.Bar(
                        x=feature_names,
                        y=feature_values,
                        text=[f'{v:.1f}' for v in feature_values],
                        textposition='auto',
                        marker_color=[self.colors['error'], self.colors['info'], 
                                     self.colors['success'], self.colors['secondary']],
                        name='环境参数'
                    ),
                    row=1, col=2
                )
            
            # 3. 时间特征饼图
            time_labels = []
            time_values = []
            
            hour = input_features.get('hour', 12)
            if 6 <= hour <= 8:
                time_labels.extend(['早高峰', '其他时段'])
                time_values.extend([60, 40])
            elif 18 <= hour <= 20:
                time_labels.extend(['晚高峰', '其他时段'])
                time_values.extend([65, 35])
            elif 9 <= hour <= 17:
                time_labels.extend(['日间', '其他时段'])
                time_values.extend([70, 30])
            else:
                time_labels.extend(['夜间', '其他时段'])
                time_values.extend([30, 70])
                
            is_weekend = input_features.get('is_weekend', 0)
            if is_weekend:
                time_labels.append('周末')
                time_values.append(20)
            else:
                time_labels.append('工作日')
                time_values.append(80)
                
            fig.add_trace(
                go.Pie(
                    labels=time_labels,
                    values=time_values,
                    name="时间特征",
                    hole=0.3
                ),
                row=2, col=1
            )
        
            # 4. 负荷影响因子分析
            temp = input_features.get('temperature', 20)
            humidity = input_features.get('humidity', 60)
            
            # 计算影响因子
            temp_effect = max(0, abs(temp - 22) * 0.02)  # 温度偏离22度的影响
            time_effect = 0.3 if 18 <= hour <= 20 else 0.1  # 时间影响
            weather_effect = max(0, (humidity - 50) * 0.001)  # 湿度影响
            base_load = 0.6  # 基础负荷
            
            factors = ['基础负荷', '温度影响', '时间影响', '湿度影响']
            effects = [base_load, temp_effect, time_effect, weather_effect]
            
            fig.add_trace(
                go.Scatter(
                    x=factors,
                    y=effects,
                    mode='lines+markers',
                    line=dict(color=self.colors['purple'], width=3),
                    marker=dict(size=10, color=self.colors['purple']),
                    name='影响因子'
                ),
                row=2, col=2
            )
        
            # 更新布局
            fig.update_layout(
                title=f"电力负荷预测分析 - {prediction_result.get('model_used', '未知模型')}",
                height=800,
                showlegend=False,
                font=dict(size=12)
            )
            
            # 更新子图标题
            fig.update_yaxes(title_text="负荷 (MW)", row=1, col=1)
            fig.update_yaxes(title_text="数值", row=1, col=2)
            fig.update_yaxes(title_text="影响权重", row=2, col=2)
            
            return {
                'html': fig.to_html(include_plotlyjs='cdn', div_id=f"plot_{int(time.time())}", 
                                   config={'displayModeBar': False, 'responsive': True}),
                'json': fig.to_json(),
                'plot_div': fig.to_html(include_plotlyjs=False, div_id=f"plot_{int(time.time())}", 
                                       config={'displayModeBar': False, 'responsive': True}),
                'summary': {
                    'predicted_load': prediction_value,
                    'model_used': prediction_result.get('model_used', '未知'),
                    'prediction_time': prediction_result.get('prediction_time', datetime.now().isoformat()),
                    'input_summary': {
                        'temperature': input_features.get('temperature', 0),
                        'humidity': input_features.get('humidity', 0),
                        'wind_speed': input_features.get('wind_speed', 0),
                        'rainfall': input_features.get('rainfall', 0),
                        'hour': input_features.get('hour', 0)
                    }
                }
            }
            
        except Exception as e:
            print(f"❌ 单点预测可视化生成失败: {str(e)}")
            # 返回简单的备用可视化
            simple_fig = go.Figure(data=[
                go.Bar(x=['预测负荷'], y=[prediction_result.get('predicted_load', 0)])
            ])
            simple_fig.update_layout(title="预测结果")
            
            return {
                'html': simple_fig.to_html(include_plotlyjs='cdn', div_id=f"plot_error_{int(time.time())}", 
                                           config={'displayModeBar': False, 'responsive': True}),
                'json': simple_fig.to_json(),
                'plot_div': simple_fig.to_html(include_plotlyjs=False, div_id=f"plot_error_{int(time.time())}", 
                                               config={'displayModeBar': False, 'responsive': True}),
                'summary': {
                    'predicted_load': prediction_result.get('predicted_load', 0),
                    'model_used': prediction_result.get('model_used', '未知'),
                    'error': str(e)
                }
            }
    
    def plot_batch_predictions(self, prediction_results):
        """绘制批量预测结果
        
        Args:
            prediction_results: 预测结果列表
            
        Returns:
            dict: 包含图表和统计信息
        """
        if not prediction_results:
            return None
        
        # 提取数据
        timestamps = [pd.to_datetime(r['timestamp']) for r in prediction_results]
        loads = [r['predicted_load'] for r in prediction_results]
        
        # 创建主图表
        fig = go.Figure()
        
        # 添加负荷曲线
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=loads,
            mode='lines+markers',
            name='预测负荷',
            line=dict(color=self.colors['primary'], width=2),
            marker=dict(size=6)
        ))
        
        # 添加统计信息
        avg_load = np.mean(loads)
        max_load = np.max(loads)
        min_load = np.min(loads)
        
        fig.add_hline(y=avg_load, line_dash="dash", line_color=self.colors['success'],
                     annotation_text=f"平均负荷: {avg_load:.2f} MW")
        
        # 标记峰值
        peak_idx = loads.index(max_load)
        fig.add_annotation(
            x=timestamps[peak_idx],
            y=max_load,
            text=f"峰值: {max_load:.2f} MW",
            showarrow=True,
            arrowhead=2,
            arrowcolor=self.colors['error']
        )
        
        # 更新布局
        fig.update_layout(
            title="批量电力负荷预测结果",
            xaxis_title="时间",
            yaxis_title="负荷 (MW)",
            hovermode='x unified'
        )
        
        return {
            'html': fig.to_html(include_plotlyjs='cdn', div_id=f"batch_plot_{int(time.time())}", 
                               config={'displayModeBar': False, 'responsive': True}),
            'json': fig.to_json(),
            'plot_div': fig.to_html(include_plotlyjs=False, div_id=f"batch_plot_{int(time.time())}", 
                                   config={'displayModeBar': False, 'responsive': True}),
            'statistics': {
                'total_points': len(loads),
                'average_load': avg_load,
                'peak_load': max_load,
                'min_load': min_load,
                'load_range': max_load - min_load,
                'peak_time': timestamps[peak_idx].isoformat()
            }
        }
    
    def plot_day_ahead_prediction(self, day_prediction_result):
        """绘制日前预测结果
        
        Args:
            day_prediction_result: 日前预测结果
            
        Returns:
            dict: 包含多个图表的字典
        """
        try:
            predictions = day_prediction_result['predictions']
            statistics = day_prediction_result['statistics']
            load_distribution = day_prediction_result['load_distribution']
            
            # 提取数据
            timestamps = [pd.to_datetime(r['timestamp']) for r in predictions]
            loads = [r['predicted_load'] for r in predictions]
            
            # 创建主图表 - 24小时负荷曲线
            main_fig = go.Figure()
            
            # 添加负荷曲线
            main_fig.add_trace(go.Scatter(
                x=timestamps,
                y=loads,
                mode='lines+markers',
                name='预测负荷',
                line=dict(color=self.colors['primary'], width=3),
                marker=dict(size=4),
                hovertemplate='<b>时间</b>: %{x}<br><b>负荷</b>: %{y:.2f} MW<extra></extra>'
            ))
            
            # 添加时段背景色
            for i in range(0, len(timestamps), 24):  # 每6小时一个时段
                if i + 23 < len(timestamps):
                    hour = timestamps[i].hour
                    start_time = timestamps[i]
                    end_time = timestamps[min(i + 23, len(timestamps) - 1)]
                    
                    # 不同时段使用不同颜色
                    if 6 <= hour <= 8 or 18 <= hour <= 20:  # 高峰时段
                        color = 'rgba(255, 99, 71, 0.1)'
                        text = '高峰时段'
                    elif 22 <= hour or hour <= 5:  # 夜间时段
                        color = 'rgba(70, 130, 180, 0.1)'
                        text = '夜间时段'
                    else:  # 正常时段
                        color = 'rgba(144, 238, 144, 0.1)'
                        text = '日间时段'
                    
                    main_fig.add_vrect(
                        x0=start_time, x1=end_time,
                        fillcolor=color,
                        layer="below",
                        line_width=0,
                        annotation_text=text,
                        annotation_position="top left"
                    )
            
            # 标记峰值点
            peak_time = pd.to_datetime(statistics['peak_time'])
            main_fig.add_annotation(
                x=peak_time,
                y=statistics['peak_load'],
                text=f"峰值: {statistics['peak_load']:.2f} MW<br>{peak_time.strftime('%H:%M')}",
                showarrow=True,
                arrowhead=2,
                arrowcolor=self.colors['error'],
                bgcolor="white",
                bordercolor=self.colors['error'],
                borderwidth=2
            )
            
            main_fig.update_layout(
                title=f"日前电力负荷预测曲线 - {day_prediction_result['date']}",
                xaxis_title="时间",
                yaxis_title="负荷 (MW)",
                hovermode='x unified',
                height=500
            )
            
            # 负荷分布饼图
            distribution_fig = go.Figure(data=[
                go.Pie(
                    labels=['夜间 (00-06)', '上午 (06-12)', '下午 (12-18)', '晚间 (18-24)'],
                    values=[load_distribution['night'], load_distribution['morning'],
                           load_distribution['afternoon'], load_distribution['evening']],
                    hole=0.4,
                    marker_colors=[self.colors['info'], self.colors['success'],
                                  self.colors['warning'], self.colors['error']],
                    textinfo='label+percent+value',
                    texttemplate='%{label}<br>%{value:.2f} MW<br>(%{percent})'
                )
            ])
            
            distribution_fig.update_layout(
                title="时段平均负荷分布",
                annotations=[dict(text='负荷分布', x=0.5, y=0.5, font_size=16, showarrow=False)],
                height=500
            )
            
            # 统计指标条形图
            stats_fig = go.Figure()
            
            stats_labels = ['峰值负荷', '最小负荷', '平均负荷', '负荷系数']
            stats_values = [statistics['peak_load'], statistics['min_load'],
                           statistics['average_load'], statistics['load_factor']]
            stats_colors = [self.colors['error'], self.colors['success'],
                           self.colors['primary'], self.colors['purple']]
            
            stats_fig.add_trace(go.Bar(
                x=stats_labels,
                y=stats_values,
                marker_color=stats_colors,
                text=[f"{statistics['peak_load']:.2f} MW",
                      f"{statistics['min_load']:.2f} MW",
                      f"{statistics['average_load']:.2f} MW",
                      f"{statistics['load_factor']:.3f}"],
                textposition='auto'
            ))
            
            stats_fig.update_layout(
                title="关键统计指标",
                yaxis_title="数值",
                height=500
            )
            
            return {
                'main_chart': {
                    'html': main_fig.to_html(include_plotlyjs='cdn', div_id=f"main_chart_{int(time.time())}", 
                                           config={'displayModeBar': False, 'responsive': True}),
                    'json': main_fig.to_json()
                },
                'distribution_chart': {
                    'html': distribution_fig.to_html(include_plotlyjs='cdn', div_id=f"distribution_chart_{int(time.time())}", 
                                                    config={'displayModeBar': False, 'responsive': True}),
                    'json': distribution_fig.to_json()
                },
                'statistics_chart': {
                    'html': stats_fig.to_html(include_plotlyjs='cdn', div_id=f"statistics_chart_{int(time.time())}", 
                                             config={'displayModeBar': False, 'responsive': True}),
                    'json': stats_fig.to_json()
                },
                'summary': {
                    'date': day_prediction_result['date'],
                    'total_points': len(predictions),
                    'model_used': day_prediction_result['model_used'],
                    'statistics': statistics,
                    'load_distribution': load_distribution
                }
            }
            
        except Exception as e:
            print(f"❌ 日前预测可视化生成失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 返回简单的备用可视化
            simple_fig = go.Figure(data=[
                go.Scatter(x=list(range(96)), y=[0] * 96, mode='lines', name='预测失败')
            ])
            simple_fig.update_layout(title="日前预测 - 数据生成失败")
            
            return {
                'main_chart': {
                    'html': simple_fig.to_html(include_plotlyjs='cdn', div_id=f"main_chart_error_{int(time.time())}", 
                                              config={'displayModeBar': False, 'responsive': True}),
                    'json': simple_fig.to_json()
                },
                'distribution_chart': {
                    'html': simple_fig.to_html(include_plotlyjs='cdn', div_id=f"distribution_chart_error_{int(time.time())}", 
                                              config={'displayModeBar': False, 'responsive': True}),
                    'json': simple_fig.to_json()
                },
                'statistics_chart': {
                    'html': simple_fig.to_html(include_plotlyjs='cdn', div_id=f"statistics_chart_error_{int(time.time())}", 
                                              config={'displayModeBar': False, 'responsive': True}),
                    'json': simple_fig.to_json()
                },
                'summary': {
                    'error': str(e),
                    'total_points': 0
                }
            }
    
    def plot_model_comparison(self, model_performance):
        """绘制模型性能比较图
        
        Args:
            model_performance: 模型性能字典
            
        Returns:
            dict: 包含比较图表
        """
        if not model_performance:
            return {
                'html': '<div style="text-align: center; padding: 50px;">暂无模型性能数据</div>',
                'json': None,
                'best_model': None,
                'performance_summary': {
                    'best_r2': 0,
                    'best_rmse': 0,
                    'model_count': 0
                }
            }
        
        try:
            models = list(model_performance.keys())
            
            # 创建子图
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('R² 决定系数', '均方根误差 (RMSE)', '平均绝对误差 (MAE)', '平均绝对百分比误差 (MAPE)'),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "bar"}]]
            )
            
            # R² 分数
            r2_scores = [model_performance[model].get('r2', 0) for model in models]
            fig.add_trace(
                go.Bar(x=models, y=r2_scores, name='R²', marker_color=self.colors['success']),
                row=1, col=1
            )
            
            # RMSE
            rmse_values = [model_performance[model].get('rmse', 0) for model in models]
            fig.add_trace(
                go.Bar(x=models, y=rmse_values, name='RMSE', marker_color=self.colors['error']),
                row=1, col=2
            )
            
            # MAE
            mae_values = [model_performance[model].get('mae', 0) for model in models]
            fig.add_trace(
                go.Bar(x=models, y=mae_values, name='MAE', marker_color=self.colors['warning']),
                row=2, col=1
            )
            
            # MAPE
            mape_values = [model_performance[model].get('mape', 0) for model in models]
            fig.add_trace(
                go.Bar(x=models, y=mape_values, name='MAPE (%)', marker_color=self.colors['info']),
                row=2, col=2
            )
            
            fig.update_layout(
                title="模型性能比较",
                height=600,
                showlegend=False
            )
            
            # 找到最佳模型
            best_model = max(models, key=lambda x: model_performance[x].get('r2', 0))
            
            return {
                'html': fig.to_html(include_plotlyjs=True),
                'json': fig.to_json(),
                'best_model': best_model,
                'performance_summary': {
                    'best_r2': model_performance[best_model].get('r2', 0),
                    'best_rmse': model_performance[best_model].get('rmse', 0),
                    'model_count': len(models)
                }
            }
        except Exception as e:
            print(f"❌ 生成模型对比图表时出错: {e}")
            return {
                'html': f'<div style="text-align: center; padding: 50px; color: red;">图表生成失败: {str(e)}</div>',
                'json': None,
                'best_model': None,
                'performance_summary': {
                    'best_r2': 0,
                    'best_rmse': 0,
                    'model_count': 0
                },
                'error': str(e)
            }
    
    def plot_prediction_error_analysis(self, predictions, actual_values):
        """绘制预测误差分析图
        
        Args:
            predictions: 预测值列表
            actual_values: 实际值列表
            
        Returns:
            dict: 误差分析图表
        """
        if len(predictions) != len(actual_values):
            raise ValueError("预测值和实际值数量不匹配")
        
        predictions = np.array(predictions)
        actual_values = np.array(actual_values)
        errors = predictions - actual_values
        relative_errors = errors / actual_values * 100
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('预测值 vs 实际值', '误差分布', '相对误差 (%)', '误差时间序列'),
            specs=[[{"type": "scatter"}, {"type": "histogram"}],
                   [{"type": "histogram"}, {"type": "scatter"}]]
        )
        
        # 1. 预测值 vs 实际值散点图
        fig.add_trace(
            go.Scatter(
                x=actual_values, y=predictions,
                mode='markers',
                name='预测vs实际',
                marker=dict(color=self.colors['primary'], size=6)
            ),
            row=1, col=1
        )
        
        # 添加理想线 y=x
        min_val = min(min(predictions), min(actual_values))
        max_val = max(max(predictions), max(actual_values))
        fig.add_trace(
            go.Scatter(
                x=[min_val, max_val], y=[min_val, max_val],
                mode='lines',
                name='理想预测',
                line=dict(color='red', dash='dash')
            ),
            row=1, col=1
        )
        
        # 2. 误差分布直方图
        fig.add_trace(
            go.Histogram(
                x=errors,
                name='误差分布',
                marker_color=self.colors['secondary'],
                nbinsx=30
            ),
            row=1, col=2
        )
        
        # 3. 相对误差分布
        fig.add_trace(
            go.Histogram(
                x=relative_errors,
                name='相对误差分布',
                marker_color=self.colors['success'],
                nbinsx=30
            ),
            row=2, col=1
        )
        
        # 4. 误差时间序列
        fig.add_trace(
            go.Scatter(
                y=errors,
                mode='lines+markers',
                name='误差序列',
                line=dict(color=self.colors['error'], width=2),
                marker=dict(size=4)
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title="预测误差分析",
            height=700,
            showlegend=False
        )
        
        # 计算统计指标
        mae = np.mean(np.abs(errors))
        mse = np.mean(errors**2)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs(relative_errors))
        r2 = 1 - mse / np.var(actual_values)
        
        return {
            'html': fig.to_html(include_plotlyjs=True),
            'json': fig.to_json(),
            'error_statistics': {
                'mae': float(mae),
                'mse': float(mse),
                'rmse': float(rmse),
                'mape': float(mape),
                'r2': float(r2),
                'max_error': float(np.max(np.abs(errors))),
                'mean_error': float(np.mean(errors))
            }
        }
    
    def create_dashboard_summary(self, prediction_results, model_performance=None):
        """创建仪表板摘要
        
        Args:
            prediction_results: 预测结果
            model_performance: 模型性能数据
            
        Returns:
            dict: 仪表板数据
        """
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'prediction_summary': {},
            'model_summary': {},
            'charts': {}
        }
        
        # 预测摘要
        if isinstance(prediction_results, list):
            loads = [r['predicted_load'] for r in prediction_results]
            dashboard['prediction_summary'] = {
                'total_predictions': len(loads),
                'average_load': np.mean(loads),
                'peak_load': np.max(loads),
                'min_load': np.min(loads),
                'load_range': np.max(loads) - np.min(loads)
            }
        elif isinstance(prediction_results, dict):
            dashboard['prediction_summary'] = {
                'single_prediction': prediction_results['predicted_load'],
                'model_used': prediction_results.get('model_used', 'unknown'),
                'prediction_time': prediction_results.get('prediction_time', 'unknown')
            }
        
        # 模型摘要
        if model_performance:
            best_r2 = max(perf.get('r2', 0) for perf in model_performance.values())
            best_model = max(model_performance.keys(), 
                           key=lambda x: model_performance[x].get('r2', 0))
            
            dashboard['model_summary'] = {
                'available_models': len(model_performance),
                'best_model': best_model,
                'best_r2_score': best_r2,
                'average_r2': np.mean([perf.get('r2', 0) for perf in model_performance.values()])
            }
        
        return dashboard
