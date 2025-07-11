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
            'info': '#2196f3'
        }
    
    def plot_single_prediction(self, prediction_value, input_params=None):
        """绘制单点预测结果
        
        Args:
            prediction_value: 预测值
            input_params: 输入参数字典
            
        Returns:
            plotly.graph_objects.Figure: 图表对象
        """
        fig = go.Figure()
        
        # 添加预测值柱状图
        fig.add_trace(go.Bar(
            x=['预测负荷'],
            y=[prediction_value],
            text=[f'{prediction_value:.2f} MW'],
            textposition='auto',
            marker_color=self.colors['primary'],
            name='预测负荷'
        ))
        
        # 添加参考线
        fig.add_hline(y=100, line_dash="dash", line_color="gray", 
                     annotation_text="平均负荷参考")
        
        # 更新布局
        fig.update_layout(
            title='单点负荷预测结果',
            yaxis_title='负荷 (MW)',
            height=400,
            showlegend=False
        )
        
        # 如果有输入参数，添加到标题
        if input_params:
            subtitle = f"时间: {input_params.get('hour', 'N/A')}:{input_params.get('minute', 'N/A'):02d} | " \
                      f"温度: {input_params.get('temperature', 'N/A')}°C | " \
                      f"湿度: {input_params.get('humidity', 'N/A')}%"
            fig.update_layout(title=f'单点负荷预测结果<br><sub>{subtitle}</sub>')
        
        return fig
    
    def plot_batch_predictions(self, predictions_df):
        """绘制批量预测结果
        
        Args:
            predictions_df: 预测结果DataFrame
            
        Returns:
            plotly.graph_objects.Figure: 图表对象
        """
        fig = go.Figure()
        
        # 添加负荷预测曲线
        fig.add_trace(go.Scatter(
            x=predictions_df['timestamp'],
            y=predictions_df['predicted_load'],
            mode='lines+markers',
            name='预测负荷',
            line=dict(color=self.colors['primary'], width=2),
            marker=dict(size=4),
            hovertemplate='<b>时间</b>: %{x}<br>' +
                         '<b>预测负荷</b>: %{y:.2f} MW<br>' +
                         '<extra></extra>'
        ))
        
        # 添加温度曲线（右Y轴）
        if 'temperature' in predictions_df.columns:
            fig.add_trace(go.Scatter(
                x=predictions_df['timestamp'],
                y=predictions_df['temperature'],
                mode='lines',
                name='温度',
                line=dict(color=self.colors['secondary'], width=1),
                yaxis='y2',
                hovertemplate='<b>时间</b>: %{x}<br>' +
                             '<b>温度</b>: %{y:.1f}°C<br>' +
                             '<extra></extra>'
            ))
        
        # 更新布局
        fig.update_layout(
            title='批量负荷预测结果',
            xaxis_title='时间',
            yaxis_title='负荷 (MW)',
            yaxis2=dict(
                title='温度 (°C)',
                overlaying='y',
                side='right'
            ),
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_model_performance(self, performance_dict):
        """绘制模型性能对比
        
        Args:
            performance_dict: 模型性能字典
            
        Returns:
            plotly.graph_objects.Figure: 图表对象
        """
        if not performance_dict:
            # 空数据图表
            fig = go.Figure()
            fig.add_annotation(
                text="无模型性能数据",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(title="模型性能对比")
            return fig
        
        models = list(performance_dict.keys())
        mse_values = [performance_dict[model]['mse'] for model in models]
        r2_values = [performance_dict[model]['r2'] for model in models]
        
        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('均方误差 (MSE)', '决定系数 (R²)'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # MSE柱状图
        fig.add_trace(
            go.Bar(
                name='MSE',
                x=models,
                y=mse_values,
                marker_color=self.colors['warning'],
                text=[f'{mse:.6f}' for mse in mse_values],
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # R²柱状图
        fig.add_trace(
            go.Bar(
                name='R²',
                x=models,
                y=r2_values,
                marker_color=self.colors['success'],
                text=[f'{r2:.4f}' for r2 in r2_values],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        # 更新布局
        fig.update_layout(
            title='模型性能对比',
            height=500,
            showlegend=False
        )
        
        # 更新Y轴标签
        fig.update_yaxes(title_text="MSE", row=1, col=1)
        fig.update_yaxes(title_text="R²", row=1, col=2)
        
        return fig
    
    def plot_load_distribution(self, predictions_df):
        """绘制负荷分布直方图
        
        Args:
            predictions_df: 预测结果DataFrame
            
        Returns:
            plotly.graph_objects.Figure: 图表对象
        """
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=predictions_df['predicted_load'],
            nbinsx=30,
            name='负荷分布',
            marker_color=self.colors['info'],
            opacity=0.7
        ))
        
        # 添加平均值线
        mean_load = predictions_df['predicted_load'].mean()
        fig.add_vline(
            x=mean_load,
            line_dash="dash",
            line_color="red",
            annotation_text=f"平均值: {mean_load:.2f} MW"
        )
        
        fig.update_layout(
            title='负荷分布直方图',
            xaxis_title='负荷 (MW)',
            yaxis_title='频次',
            height=400
        )
        
        return fig
    
    def plot_hourly_pattern(self, predictions_df):
        """绘制小时负荷模式
        
        Args:
            predictions_df: 预测结果DataFrame
            
        Returns:
            plotly.graph_objects.Figure: 图表对象
        """
        # 按小时分组统计
        hourly_stats = predictions_df.groupby(
            predictions_df['timestamp'].dt.hour
        )['predicted_load'].agg(['mean', 'std']).reset_index()
        
        fig = go.Figure()
        
        # 添加平均值线
        fig.add_trace(go.Scatter(
            x=hourly_stats['timestamp'],
            y=hourly_stats['mean'],
            mode='lines+markers',
            name='平均负荷',
            line=dict(color=self.colors['primary'], width=2),
            error_y=dict(
                type='data',
                array=hourly_stats['std'],
                visible=True
            )
        ))
        
        fig.update_layout(
            title='小时负荷模式',
            xaxis_title='小时',
            yaxis_title='负荷 (MW)',
            height=400
        )
        
        return fig
    
    def create_summary_table(self, summary_stats):
        """创建摘要统计表格
        
        Args:
            summary_stats: 统计摘要字典
            
        Returns:
            plotly.graph_objects.Figure: 表格对象
        """
        if not summary_stats:
            return None
        
        # 准备表格数据
        headers = ['指标', '数值']
        values = []
        
        for key, value in summary_stats.items():
            if key in ['max_time', 'min_time']:
                values.append([key, str(value)])
            else:
                values.append([key, f'{value:.2f}'])
        
        fig = go.Figure(data=[go.Table(
            header=dict(values=headers, fill_color='lightblue'),
            cells=dict(values=[[row[0] for row in values], [row[1] for row in values]],
                      fill_color='white')
        )])
        
        fig.update_layout(
            title='预测结果摘要',
            height=300
        )
        
        return fig
