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
        """初始化机器学习模型"""
        
        # 线性回归
        self.models['LinearRegression'] = LinearRegression()
        
        # 随机森林
        self.models['RandomForest'] = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        
        # 梯度提升 - 使用更保守的参数设置
        try:
            self.models['GradientBoosting'] = GradientBoostingRegressor(
                n_estimators=20,  # 进一步减少估计器数量
                max_depth=2,      # 更小的树深度
                learning_rate=0.2, # 稍高的学习率以补偿较少的估计器
                random_state=42,
                subsample=0.9,    # 稍高的子采样比例
                min_samples_split=5,  # 最小分割样本数
                min_samples_leaf=3    # 最小叶子样本数
            )

        except Exception as e:
            print(f"   ⚠️ GradientBoosting 初始化失败: {e}")
            # 如果初始化失败，从模型字典中移除
            if 'GradientBoosting' in self.models:
                del self.models['GradientBoosting']
        
        # 支持向量回归 - 使用更安全的参数
        try:
            self.models['SVR'] = SVR(
                kernel='rbf', 
                C=0.5,           # 进一步降低正则化参数
                gamma='scale',   # 使用自动缩放
                epsilon=0.2,     # 更大的容错范围
                cache_size=500,  # 增加缓存大小
                max_iter=1000    # 限制最大迭代次数
            )

        except Exception as e:
            print(f"   ⚠️ SVR 初始化失败: {e}")
            # 如果初始化失败，从模型字典中移除
            if 'SVR' in self.models:
                del self.models['SVR']
        
        # XGBoost (如果可用) - 使用兼容性更好的参数
        if XGBOOST_AVAILABLE:
            try:
                self.models['XGBoost'] = XGBRegressor(
                    n_estimators=20,      # 减少估计器数量
                    max_depth=2,          # 更小的树深度
                    learning_rate=0.2,    # 稍高的学习率
                    random_state=42,
                    subsample=0.9,        # 子采样比例
                    colsample_bytree=0.8, # 特征采样比例
                    reg_alpha=0.1,        # L1正则化
                    reg_lambda=0.1,       # L2正则化
                    objective='reg:squarederror',  # 明确指定目标函数
                    eval_metric='rmse',   # 评估指标
                    verbosity=0,          # 关闭详细输出
                    n_jobs=1              # 单线程运行避免冲突
                )

            except Exception as e:
                print(f"   ⚠️ XGBoost 初始化失败: {e}")
                # 如果初始化失败，从模型字典中移除
                if 'XGBoost' in self.models:
                    del self.models['XGBoost']
        else:
            print("   ⚠️ XGBoost 不可用，请安装: pip install xgboost")
        

    
    def train_all_models(self, X_train, y_train, X_test, y_test):
        """训练所有模型
        
        Args:
            X_train: 训练特征
            y_train: 训练目标
            X_test: 测试特征
            y_test: 测试目标
        """

        
        for name, model in self.models.items():
            try:
                # 训练模型
                model.fit(X_train, y_train)
                
                # 预测
                y_pred = model.predict(X_test)
                
                # 评估性能
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mse)
                
                # 计算MAE和MAPE
                mae = np.mean(np.abs(y_test - y_pred))
                mape = np.mean(np.abs((y_test - y_pred) / np.maximum(np.abs(y_test), 1e-8))) * 100
                
                self.performance[name] = {
                    'mse': mse,
                    'r2': r2,
                    'rmse': rmse,
                    'mae': mae,
                    'mape': mape,
                    'training_time': 0
                }
                

                
            except Exception as e:
                print(f"    ❌ {name} 训练失败: {e}")
                # 从模型字典中移除失败的模型
                if name in self.models:
                    try:
                        del self.models[name]

                    except:
                        pass
        
        # 选择最佳模型
        if self.performance:
            self.best_model_name = min(self.performance.keys(), 
                                     key=lambda x: self.performance[x]['mse'])
            print(f"🏆 最佳模型: {self.best_model_name}")
            self.is_trained = True
        else:
            print("❌ 所有模型训练失败")
    
    def train_core_models(self, X_train, y_train, X_test, y_test):
        """训练核心模型 - 快速版本，只训练关键模型
        
        Args:
            X_train: 训练特征
            y_train: 训练目标
            X_test: 测试特征
            y_test: 测试目标
        """
        print("🚀 快速训练核心模型...")
        
        # 按优先级排序的模型列表
        model_priority = [
            'LinearRegression',    # 最稳定
            'RandomForest',        # 通常很可靠
            'GradientBoosting',    # 可能有问题的模型
            'SVR',                 # 可能有问题的模型
            'XGBoost'              # 可能有问题的模型
        ]
        
        successful_models = []
        
        for name in model_priority:
            if name in self.models:
                print(f"  训练 {name}...")
                try:
                    model = self.models[name]
                    
                    # 训练模型
                    model.fit(X_train, y_train)
                    
                    # 预测
                    y_pred = model.predict(X_test)
                    
                    # 验证预测结果
                    if np.any(np.isnan(y_pred)) or np.any(np.isinf(y_pred)):
                        raise ValueError("预测结果包含NaN或无穷值")
                    
                    # 评估性能
                    mse = mean_squared_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                    rmse = np.sqrt(mse)
                    
                    # 计算MAE和MAPE
                    mae = np.mean(np.abs(y_test - y_pred))
                    mape = np.mean(np.abs((y_test - y_pred) / np.maximum(np.abs(y_test), 1e-8))) * 100
                    
                    # 验证性能指标
                    if np.isnan(mse) or np.isnan(r2) or mse < 0:
                        raise ValueError("性能指标异常")
                    
                    self.performance[name] = {
                        'mse': mse,
                        'r2': r2,
                        'rmse': rmse,
                        'mae': mae,
                        'mape': mape,
                        'training_time': 0  # 可以后续添加计时功能
                    }
                    
                    successful_models.append(name)
                    print(f"    ✅ {name}: MSE={mse:.6f}, R²={r2:.6f}")
                    
                except Exception as e:
                    print(f"    ❌ {name} 训练失败: {e}")
                    # 从模型字典中移除失败的模型
                    if name in self.models:
                        try:
                            del self.models[name]
                            print(f"    🗑️ 已移除故障模型: {name}")
                        except:
                            pass
                    continue
        
        # 检查是否有成功的模型
        if successful_models:
            # 选择最佳模型
            self.best_model_name = min(self.performance.keys(), 
                                     key=lambda k: self.performance[k]['mse'])
            print(f"✅ 训练完成，成功模型: {successful_models}")
            print(f"🏆 最佳模型: {self.best_model_name}")
            self.is_trained = True
        else:
            print("❌ 所有模型训练失败")
            self.is_trained = False
        
        return self.is_trained

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
    
    def get_model_comparison(self):
        """获取模型性能对比数据，按R²分数排序
        
        Returns:
            list: 排序后的模型性能对比数据
        """
        if not self.performance:
            return []
        
        comparison_data = []
        for model_name, metrics in self.performance.items():
            # 计算额外的指标
            mae = metrics.get('mae', metrics.get('rmse', 0) * 0.8)  # 如果没有MAE，用RMSE估算
            mape = metrics.get('mape', abs(1 - metrics.get('r2', 0)) * 100)  # 如果没有MAPE，用R²估算
            
            comparison_data.append({
                'model': model_name,
                'r2': metrics.get('r2', 0),
                'rmse': metrics.get('rmse', 0),
                'mae': mae,
                'mape': mape,
                'mse': metrics.get('mse', 0),
                'training_time': metrics.get('training_time', 0)
            })
        
        # 按R²分数降序排序
        comparison_data.sort(key=lambda x: x['r2'], reverse=True)
        
        return comparison_data

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
