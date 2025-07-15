import { useState, useEffect } from 'react';
import { message } from 'antd';
import { predictionApi } from '../service/prediction';

/**
 * AI系统状态管理Hook
 * 统一管理系统状态、模型加载和初始化
 */
export const useAISystem = () => {
  const [systemStatus, setSystemStatus] = useState(null);
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(false);

  // 检查系统状态
  const checkSystemStatus = async () => {
    try {
      console.log('🔍 检查系统状态...');
      const response = await predictionApi.getSystemStatus();
      console.log('📊 系统状态响应:', response.data);
      
      if (response.data && response.data.success) {
        setSystemStatus(response.data.data);
        if (response.data.data.initialized) {
          // 系统已初始化，加载模型
          loadModels();
        }
        return response.data.data;
      } else {
        console.log('❌ 系统状态检查失败:', response.data);
        const status = { initialized: false };
        setSystemStatus(status);
        return status;
      }
    } catch (error) {
      console.error('❌ 系统状态检查异常:', error);
      const status = { initialized: false };
      setSystemStatus(status);
      return status;
    }
  };

  // 加载模型列表
  const loadModels = async () => {
    try {
      setLoading(true);
      console.log('🔍 正在加载模型列表...');
      const response = await predictionApi.getModels();
      console.log('📊 模型响应:', response.data);
      
      if (response.data && response.data.success) {
        setModels(response.data.data || []);
        console.log('✅ 模型加载成功:', response.data.data);
        if (response.data.data && response.data.data.length === 0) {
          message.warning('暂无可用模型，请先初始化系统');
        }
        return response.data.data || [];
      } else {
        console.log('❌ 模型加载失败:', response.data);
        setModels([]);
        const errorMsg = response.data?.error || '未知错误';
        if (errorMsg.includes('系统未初始化') || errorMsg.includes('模型未训练')) {
          message.warning('系统未初始化，请先点击"初始化系统"按钮');
        } else {
          message.error('模型加载失败: ' + errorMsg);
        }
        return [];
      }
    } catch (error) {
      console.error('❌ 加载模型列表异常:', error);
      setModels([]);
      message.error('加载模型列表失败: ' + error.message);
      return [];
    } finally {
      setLoading(false);
    }
  };

  // 初始化系统
  const initializeSystem = async () => {
    try {
      setInitializing(true);
      console.log('🚀 开始初始化系统...');
      message.info('正在初始化AI预测系统，请稍候...');
      
      const response = await predictionApi.initializeSystem();
      console.log('📊 初始化响应:', response.data);
      
      if (response.data && response.data.success) {
        message.success('系统初始化完成！');
        // 重新检查系统状态和加载模型
        const status = await checkSystemStatus();
        return status;
      } else {
        console.log('❌ 系统初始化失败:', response.data);
        const error = response.data?.error || '未知错误';
        message.error('系统初始化失败: ' + error);
        return false;
      }
    } catch (error) {
      console.error('❌ 系统初始化异常:', error);
      message.error('系统初始化失败: ' + error.message);
      return false;
    } finally {
      setInitializing(false);
    }
  };

  // 重置系统状态
  const resetSystemStatus = () => {
    setSystemStatus(null);
    setModels([]);
    setLoading(false);
    setInitializing(false);
  };

  // 组件挂载时检查系统状态
  useEffect(() => {
    checkSystemStatus();
  }, []);

  return {
    // 状态
    systemStatus,
    models,
    loading,
    initializing,
    
    // 方法
    checkSystemStatus,
    loadModels,
    initializeSystem,
    resetSystemStatus,
    
    // 计算属性
    isSystemReady: systemStatus?.initialized && models.length > 0,
    hasModels: models.length > 0,
    isLoading: loading || initializing
  };
};

export default useAISystem;
