import React from 'react';
import { Alert, Button, Spin } from 'antd';

/**
 * AI系统状态显示组件
 * 显示系统初始化状态、模型加载状态等
 */
const AISystemStatus = ({ 
  systemStatus, 
  models, 
  loading, 
  initializing, 
  onInitialize, 
  onLoadModels,
  showModelCount = true 
}) => {
  // 正在检查系统状态
  if (systemStatus === null) {
    return (
      <Alert
        message="正在检查系统状态..."
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
    );
  }

  // 系统未初始化
  if (!systemStatus.initialized) {
    return (
      <Alert
        message="系统未初始化"
        description="AI预测系统尚未初始化，请先点击下方按钮初始化系统以训练机器学习模型。"
        type="warning"
        showIcon
        action={
          <Button 
            size="small" 
            type="primary" 
            onClick={onInitialize}
            loading={initializing}
          >
            {initializing ? '正在初始化...' : '初始化系统'}
          </Button>
        }
        style={{ marginBottom: 16 }}
      />
    );
  }

  // 系统正在初始化
  if (initializing) {
    return (
      <Alert
        message="正在初始化AI预测系统..."
        description="这可能需要1-2分钟时间，请耐心等待。系统正在生成训练数据和训练机器学习模型。"
        type="info"
        showIcon
        icon={<Spin />}
        style={{ marginBottom: 16 }}
      />
    );
  }

  // 模型加载中
  if (models.length === 0 && loading) {
    return (
      <Alert
        message="模型加载中"
        description="系统已初始化，正在加载可用模型..."
        type="info"
        showIcon
        action={
          <Button 
            size="small" 
            onClick={onLoadModels}
            loading={loading}
          >
            重试加载
          </Button>
        }
        style={{ marginBottom: 16 }}
      />
    );
  }

  // 无可用模型
  if (models.length === 0) {
    return (
      <Alert
        message="暂无可用模型"
        description="系统已初始化但未找到可用模型，请重新加载或重新初始化系统。"
        type="warning"
        showIcon
        action={
          <Button 
            size="small" 
            onClick={onLoadModels}
            loading={loading}
          >
            重新加载
          </Button>
        }
        style={{ marginBottom: 16 }}
      />
    );
  }

  // 系统就绪
  return (
    <Alert
      message="系统已就绪"
      description={
        showModelCount 
          ? `已加载 ${models.length} 个预测模型，可以开始预测。` 
          : "AI预测系统已就绪，可以开始预测。"
      }
      type="success"
      showIcon
      style={{ marginBottom: 16 }}
    />
  );
};

export default AISystemStatus;
