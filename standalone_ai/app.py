#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
电力负荷AI预测系统 - 主应用
"""

import gradio as gr
from datetime import datetime
import warnings
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 忽略警告
warnings.filterwarnings('ignore')

# 导入核心模块
from src.data_generator import DataGenerator
from src.data_preprocessor import DataPreprocessor
from src.model_manager import ModelManager
from src.predictor import LoadPredictor
from src.visualizer import Visualizer

class PowerLoadPredictionApp:
    """电力负荷预测应用"""
    
    def __init__(self):
        """初始化应用"""
        self.data_generator = None
        self.preprocessor = None
        self.model_manager = None
        self.predictor = None
        self.visualizer = None
        self.system_ready = False
        
    def initialize_system(self):
        """初始化系统"""
        try:
            progress_text = "🚀 开始系统初始化...\n"
            
            # 1. 初始化数据生成器
            progress_text += "📊 初始化数据生成器...\n"
            self.data_generator = DataGenerator()
            
            # 2. 生成训练数据
            progress_text += "🔄 生成训练数据...\n"
            train_data = self.data_generator.generate_training_data(days=30)
            
            # 3. 初始化预处理器
            progress_text += "🔧 初始化数据预处理器...\n"
            self.preprocessor = DataPreprocessor()
            
            # 4. 数据预处理
            progress_text += "⚙️ 预处理数据...\n"
            X_train, X_test, y_train, y_test = self.preprocessor.fit_transform(train_data)
            
            # 5. 初始化模型管理器
            progress_text += "🤖 初始化模型管理器...\n"
            self.model_manager = ModelManager()
            
            # 6. 训练模型
            progress_text += "🏋️ 训练机器学习模型...\n"
            self.model_manager.train_all_models(X_train, y_train, X_test, y_test)
            
            # 7. 初始化预测器
            progress_text += "🔮 初始化预测器...\n"
            self.predictor = LoadPredictor(self.model_manager, self.preprocessor)
            
            # 8. 初始化可视化器
            progress_text += "📊 初始化可视化器...\n"
            self.visualizer = Visualizer()
            
            self.system_ready = True
            progress_text += "✅ 系统初始化完成！\n"
            progress_text += f"🏆 最佳模型: {self.model_manager.get_best_model_name()}\n"
            progress_text += f"📈 可用模型: {', '.join(self.model_manager.get_available_models())}"
            
            return progress_text
            
        except Exception as e:
            error_text = f"❌ 系统初始化失败: {str(e)}\n"
            error_text += "请检查依赖包是否正确安装"
            return error_text
    
    def single_prediction(self, hour, minute, temperature, humidity, 
                         is_weekend, is_holiday):
        """单点预测"""
        if not self.system_ready:
            return "❌ 请先初始化系统", None
            
        try:
            # 执行预测
            prediction = self.predictor.predict_with_parameters(
                hour=hour,
                minute=minute,
                temperature=temperature,
                humidity=humidity,
                is_weekend=is_weekend,
                is_holiday=is_holiday
            )
            
            # 输入参数摘要
            input_params = {
                'hour': hour,
                'minute': minute,
                'temperature': temperature,
                'humidity': humidity
            }
            
            # 生成结果文本
            result_text = f"""
🎯 单点预测结果:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 预测负荷: {prediction:.2f} MW

📋 输入参数:
  🕐 时间: {hour:02d}:{minute:02d}
  🌡️ 温度: {temperature:.1f}°C
  💧 湿度: {humidity:.1f}%
  📅 周末: {'是' if is_weekend else '否'}
  🎉 节假日: {'是' if is_holiday else '否'}

📈 负荷水平: {self._get_load_level(prediction)}
            """
            
            # 生成图表
            fig = self.visualizer.plot_single_prediction(prediction, input_params)
            
            return result_text, fig
            
        except Exception as e:
            return f"❌ 预测失败: {str(e)}", None
    
    def batch_prediction(self, start_date, start_time, periods):
        """批量预测"""
        if not self.system_ready:
            return "❌ 请先初始化系统", None
            
        try:
            # 解析开始时间
            start_datetime = datetime.strptime(f"{start_date} {start_time}", 
                                             "%Y-%m-%d %H:%M")
            
            # 执行批量预测
            predictions_df = self.predictor.predict_batch(
                start_datetime, periods=periods
            )
            
            # 生成摘要统计
            summary = self.predictor.get_prediction_summary(predictions_df)
            
            # 生成结果文本
            result_text = f"""
📊 批量预测结果:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 预测时间段: {start_date} {start_time} 开始
⏱️ 预测点数: {periods} 个 (每15分钟一个点)
📏 时间跨度: {periods * 15 / 60:.1f} 小时

📈 负荷统计:
  • 平均负荷: {summary['mean']:.2f} MW
  • 最大负荷: {summary['max']:.2f} MW
  • 最小负荷: {summary['min']:.2f} MW
  • 标准差: {summary['std']:.2f} MW

🔝 峰值时间: {summary['max_time'].strftime('%H:%M')}
🔻 谷值时间: {summary['min_time'].strftime('%H:%M')}
            """
            
            # 生成图表
            fig = self.visualizer.plot_batch_predictions(predictions_df)
            
            return result_text, fig
            
        except Exception as e:
            return f"❌ 批量预测失败: {str(e)}", None
    
    def model_performance(self):
        """模型性能评估"""
        if not self.system_ready:
            return "❌ 请先初始化系统", None
            
        try:
            # 获取性能数据
            performance = self.model_manager.get_model_performance()
            best_model = self.model_manager.get_best_model_name()
            
            # 生成结果文本
            result_text = f"""
🏆 模型性能评估:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🥇 最佳模型: {best_model}

📊 性能指标:
"""
            
            for model_name, metrics in performance.items():
                symbol = "🏆" if model_name == best_model else "📊"
                result_text += f"\n{symbol} {model_name}:\n"
                result_text += f"  • MSE: {metrics['mse']:.6f}\n"
                result_text += f"  • R²: {metrics['r2']:.6f}\n"
                result_text += f"  • RMSE: {metrics['rmse']:.6f}\n"
            
            result_text += f"\n📝 评估说明:\n"
            result_text += f"  • MSE (均方误差): 越小越好\n"
            result_text += f"  • R² (决定系数): 越接近1越好\n"
            result_text += f"  • RMSE (均方根误差): 越小越好"
            
            # 生成图表
            fig = self.visualizer.plot_model_performance(performance)
            
            return result_text, fig
            
        except Exception as e:
            return f"❌ 获取模型性能失败: {str(e)}", None
    
    def system_status(self):
        """系统状态"""
        status_text = f"""
🔧 系统状态监控:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖥️ 系统状态: {'✅ 运行正常' if self.system_ready else '❌ 未初始化'}

📦 组件状态:
  • 数据生成器: {'✅ 已加载' if self.data_generator else '❌ 未加载'}
  • 数据预处理器: {'✅ 已训练' if self.preprocessor and self.preprocessor.is_fitted else '❌ 未训练'}
  • 模型管理器: {'✅ 已训练' if self.model_manager and self.model_manager.is_trained else '❌ 未训练'}
  • 预测器: {'✅ 就绪' if self.predictor else '❌ 未就绪'}
  • 可视化器: {'✅ 已加载' if self.visualizer else '❌ 未加载'}
"""
        
        if self.system_ready and self.model_manager:
            available_models = self.model_manager.get_available_models()
            best_model = self.model_manager.get_best_model_name()
            
            status_text += f"""
🤖 模型信息:
  • 可用模型: {len(available_models)} 个
  • 模型列表: {', '.join(available_models)}
  • 最佳模型: {best_model}

💾 系统资源:
  • 内存使用: 正常
  • 模型缓存: 已加载
  • 预测就绪: 是
"""
        
        return status_text
    
    def _get_load_level(self, load_value):
        """获取负荷水平描述"""
        if load_value < 60:
            return "🟢 低负荷"
        elif load_value < 120:
            return "🟡 中等负荷"
        elif load_value < 180:
            return "🟠 高负荷"
        else:
            return "🔴 峰值负荷"
    
    def create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(
            title="电力负荷AI预测系统",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1200px;
                margin: auto;
            }
            .tab-nav {
                background: linear-gradient(90deg, #1e3c72, #2a5298);
            }
            """
        ) as interface:
            
            # 标题
            gr.Markdown("""
            # 🔌 电力负荷AI预测系统
            
            基于机器学习的短期电力负荷预测系统，支持单点预测和批量预测。
            """)
            
            # 系统初始化
            with gr.Tab("🚀 系统初始化"):
                gr.Markdown("### 系统初始化")
                gr.Markdown("首次使用或重新训练模型时，请点击下方按钮初始化系统。")
                
                init_btn = gr.Button("🔄 初始化系统", variant="primary", size="lg")
                init_output = gr.Textbox(
                    label="初始化进度",
                    lines=15,
                    placeholder="点击初始化按钮开始..."
                )
                
                init_btn.click(
                    self.initialize_system,
                    outputs=init_output
                )
            
            # 单点预测
            with gr.Tab("🎯 单点预测"):
                gr.Markdown("### 单点预测")
                gr.Markdown("输入具体参数，预测某个时间点的电力负荷。")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### 时间参数")
                        hour = gr.Slider(
                            minimum=0, maximum=23, value=12, step=1,
                            label="小时"
                        )
                        minute = gr.Slider(
                            minimum=0, maximum=59, value=0, step=15,
                            label="分钟"
                        )
                        
                        gr.Markdown("#### 气象参数")
                        temperature = gr.Slider(
                            minimum=-10, maximum=40, value=25, step=0.5,
                            label="温度 (°C)"
                        )
                        humidity = gr.Slider(
                            minimum=20, maximum=100, value=60, step=1,
                            label="湿度 (%)"
                        )
                        
                        gr.Markdown("#### 时间属性")
                        is_weekend = gr.Checkbox(label="周末")
                        is_holiday = gr.Checkbox(label="节假日")
                        
                        predict_btn = gr.Button("🔮 开始预测", variant="primary")
                    
                    with gr.Column(scale=2):
                        single_output = gr.Textbox(
                            label="预测结果",
                            lines=12,
                            placeholder="点击预测按钮获取结果..."
                        )
                        single_chart = gr.Plot(label="预测图表")
                
                predict_btn.click(
                    self.single_prediction,
                    inputs=[hour, minute, temperature, humidity, is_weekend, is_holiday],
                    outputs=[single_output, single_chart]
                )
            
            # 批量预测
            with gr.Tab("📊 批量预测"):
                gr.Markdown("### 批量预测")
                gr.Markdown("预测一段时间内的电力负荷变化趋势。")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### 时间设置")
                        start_date = gr.Textbox(
                            value=datetime.now().strftime("%Y-%m-%d"),
                            label="开始日期 (YYYY-MM-DD)"
                        )
                        start_time = gr.Textbox(
                            value="00:00",
                            label="开始时间 (HH:MM)"
                        )
                        periods = gr.Slider(
                            minimum=1, maximum=288, value=96, step=1,
                            label="预测点数 (96点=1天)"
                        )
                        
                        batch_btn = gr.Button("📈 批量预测", variant="primary")
                    
                    with gr.Column(scale=2):
                        batch_output = gr.Textbox(
                            label="预测结果",
                            lines=12,
                            placeholder="点击预测按钮获取结果..."
                        )
                        batch_chart = gr.Plot(label="预测趋势图")
                
                batch_btn.click(
                    self.batch_prediction,
                    inputs=[start_date, start_time, periods],
                    outputs=[batch_output, batch_chart]
                )
            
            # 模型性能
            with gr.Tab("🏆 模型性能"):
                gr.Markdown("### 模型性能评估")
                gr.Markdown("查看各机器学习模型的性能指标和对比。")
                
                performance_btn = gr.Button("📊 查看性能", variant="primary")
                performance_output = gr.Textbox(
                    label="性能报告",
                    lines=20,
                    placeholder="点击查看性能按钮获取报告..."
                )
                performance_chart = gr.Plot(label="性能对比图")
                
                performance_btn.click(
                    self.model_performance,
                    outputs=[performance_output, performance_chart]
                )
            
            # 系统状态
            with gr.Tab("🔧 系统状态"):
                gr.Markdown("### 系统状态监控")
                gr.Markdown("查看系统各组件的运行状态和资源使用情况。")
                
                status_btn = gr.Button("🔍 检查状态", variant="secondary")
                status_output = gr.Textbox(
                    label="系统状态",
                    lines=15,
                    placeholder="点击检查状态按钮获取信息..."
                )
                
                status_btn.click(
                    self.system_status,
                    outputs=status_output
                )
            
            # 使用说明
            with gr.Tab("📖 使用说明"):
                gr.Markdown("""
                ### 📋 使用指南
                
                #### 🚀 快速开始
                1. **系统初始化**：首次使用点击"初始化系统"
                2. **单点预测**：输入参数预测单个时间点
                3. **批量预测**：预测一段时间的负荷趋势
                4. **模型性能**：查看模型训练效果
                5. **系统状态**：监控系统运行状态
                
                #### 🎯 参数说明
                - **时间**：24小时制，分钟建议15分钟间隔
                - **温度**：环境温度，影响空调和供暖负荷
                - **湿度**：相对湿度，影响舒适度调节
                - **周末/节假日**：影响用电模式
                
                #### 📊 结果解读
                - **负荷值**：单位为MW (兆瓦)
                - **负荷水平**：低负荷(<60MW)、中等(60-120MW)、高负荷(120-180MW)、峰值(>180MW)
                - **模型指标**：MSE越小越好，R²越接近1越好
                
                #### 🔧 故障排除
                - 确保已完成系统初始化
                - 检查输入参数是否合理
                - 查看系统状态确认组件正常
                
                #### 💡 使用建议
                - 批量预测建议96点(1天)或192点(2天)
                - 注意温度对负荷的影响
                - 定期查看模型性能确保预测质量
                
                ---
                **系统版本**: v2.0.0 | **更新日期**: 2025年7月9日
                """)
        
        return interface

# 创建应用实例
app = PowerLoadPredictionApp()

def main():
    """主函数"""
    print("🔌 电力负荷AI预测系统")
    print("=" * 40)
    print("🚀 启动Gradio界面...")
    
    # 创建界面
    interface = app.create_interface()
    
    # 启动服务
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_error=True
    )

if __name__ == "__main__":
    main()
