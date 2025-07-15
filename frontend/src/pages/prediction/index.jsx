import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Select, Alert, Spin, message, Row, Col, Space } from 'antd';
import api from '../../service/req';
import './index.css';

const { Option } = Select;

const PredictionPage = () => {
  const [loading, setLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [initializing, setInitializing] = useState(false);
  const [singleResult, setSingleResult] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    console.log('🔌 AI预测页面已加载');
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      console.log('🔍 检查系统状态...');
      const response = await api.get('/prediction/system/status');
      console.log('📊 状态响应:', response.data);
      
      if (response.data && response.data.success) {
        setSystemStatus(response.data.data);
        console.log(`✅ 系统状态获取成功: initialized=${response.data.data.initialized}`);
      } else {
        console.log('❌ 状态检查失败');
        setSystemStatus({ initialized: false, error: '状态检查失败' });
      }
    } catch (error) {
      console.log(`❌ 检查系统状态异常: ${error.message}`);
      setSystemStatus({ initialized: false, error: error.message });
    }
  };

  const initializeSystem = async () => {
    try {
      setInitializing(true);
      console.log('🚀 开始初始化AI系统...');
      
      const response = await api.get('/prediction/system/initialize');
      console.log('🔍 初始化响应:', response.data);
      
      if (response.data && response.data.success) {
        console.log('✅ 初始化API调用成功');
        message.success('AI系统初始化成功！');
        
        // 等待几秒后检查状态
        setTimeout(() => {
          console.log('🔄 检查初始化后的系统状态...');
          checkSystemStatus();
        }, 3000);
      } else {
        console.log(`❌ 初始化失败: ${response.data?.message || '未知错误'}`);
        message.error(`初始化失败: ${response.data?.message || '未知错误'}`);
      }
    } catch (error) {
      console.log(`❌ 初始化系统异常: ${error.message}`);
      message.error(`初始化系统异常: ${error.message}`);
    } finally {
      setInitializing(false);
    }
  };

  const handleSinglePredict = async (values) => {
    try {
      setLoading(true);
      console.log('🎯 开始单点预测:', values);
      
      const response = await api.post('/prediction/predict/single', {
        model: values.model,
        features: {
          temperature: parseFloat(values.temperature),
          humidity: parseFloat(values.humidity),
          hour: parseInt(values.hour),
          day_of_week: parseInt(values.day_of_week),
          month: parseInt(values.month)
        }
      });
      
      if (response.data.success) {
        setSingleResult(response.data.data);
        console.log('✅ 预测成功:', response.data.data);
        message.success('预测完成！');
      } else {
        message.error(`预测失败: ${response.data?.message || '未知错误'}`);
      }
    } catch (error) {
      console.error('❌ 单点预测失败:', error);
      message.error(`预测异常: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prediction-page">
      <div className="page-header">
        <h1>🔌 电力负荷AI预测系统</h1>
        <p>基于机器学习的智能电力负荷预测平台</p>
      </div>

      {/* 系统状态检查 */}
      {systemStatus === null && (
        <Alert
          message="正在检查系统状态..."
          type="info"
          showIcon
          style={{ marginBottom: '20px' }}
        />
      )}

      {systemStatus && systemStatus.initialized && (
        <Alert
          message="系统已就绪"
          description={`AI预测系统已成功初始化。最佳模型: ${systemStatus.best_model || '未知'}`}
          type="success"
          showIcon
          style={{ marginBottom: '20px' }}
        />
      )}

      {systemStatus && !systemStatus.initialized && (
        <Alert
          message="系统未初始化"
          description="AI预测系统尚未初始化，请点击初始化按钮。"
          type="warning"
          showIcon
          action={
            <Button 
              size="small" 
              type="primary" 
              onClick={initializeSystem}
              loading={initializing}
            >
              {initializing ? '正在初始化...' : '初始化系统'}
            </Button>
          }
          style={{ marginBottom: '20px' }}
        />
      )}

      {initializing && (
        <Alert
          message="正在初始化AI预测系统..."
          description="这可能需要1-2分钟时间，请耐心等待。系统正在生成训练数据和训练机器学习模型。"
          type="info"
          showIcon
          icon={<Spin />}
          style={{ marginBottom: '20px' }}
        />
      )}

      {/* 主要内容 - 只有系统初始化后才显示 */}
      {systemStatus && systemStatus.initialized && (
        <Row gutter={[24, 24]}>
          {/* 单点预测 */}
          <Col span={16}>
            <Card title="🎯 单点预测" className="prediction-card">
              <Form
                form={form}
                layout="vertical"
                onFinish={handleSinglePredict}
              >
                <Form.Item
                  name="model"
                  label="选择模型"
                  rules={[{ required: true, message: '请选择预测模型' }]}
                >
                  <Select placeholder="请选择预测模型">
                    <Option value="linear_regression">线性回归</Option>
                    <Option value="random_forest">随机森林</Option>
                    <Option value="gradient_boosting">梯度提升</Option>
                    <Option value="xgboost">XGBoost</Option>
                    <Option value="svr">支持向量回归</Option>
                  </Select>
                </Form.Item>

                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      name="temperature"
                      label="温度 (°C)"
                      rules={[{ required: true, message: '请输入温度' }]}
                    >
                      <Input type="number" placeholder="25" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name="humidity"
                      label="湿度 (%)"
                      rules={[{ required: true, message: '请输入湿度' }]}
                    >
                      <Input type="number" placeholder="60" />
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  <Col span={8}>
                    <Form.Item
                      name="hour"
                      label="小时"
                      rules={[{ required: true, message: '请输入小时' }]}
                    >
                      <Input type="number" min="0" max="23" placeholder="12" />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item
                      name="day_of_week"
                      label="星期"
                      rules={[{ required: true, message: '请选择星期' }]}
                    >
                      <Select placeholder="选择星期">
                        <Option value="1">星期一</Option>
                        <Option value="2">星期二</Option>
                        <Option value="3">星期三</Option>
                        <Option value="4">星期四</Option>
                        <Option value="5">星期五</Option>
                        <Option value="6">星期六</Option>
                        <Option value="7">星期日</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item
                      name="month"
                      label="月份"
                      rules={[{ required: true, message: '请输入月份' }]}
                    >
                      <Input type="number" min="1" max="12" placeholder="6" />
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading} block>
                    开始预测
                  </Button>
                </Form.Item>
              </Form>

              {singleResult && (
                <Alert
                  message="预测结果"
                  description={
                    <div>
                      <p><strong>预测负荷:</strong> {singleResult.predicted_load?.toFixed(2)} MW</p>
                      <p><strong>使用模型:</strong> {singleResult.model_used}</p>
                      <p><strong>预测时间:</strong> {new Date().toLocaleString()}</p>
                    </div>
                  }
                  type="success"
                  showIcon
                  style={{ marginTop: 16 }}
                />
              )}
            </Card>
          </Col>

          {/* 功能说明 */}
          <Col span={8}>
            <Card title="🏆 功能介绍">
              <div style={{ marginBottom: 16 }}>
                <h4>🎯 单点预测</h4>
                <p>输入环境参数，预测特定时间点的电力负荷</p>
              </div>
              <div style={{ marginBottom: 16 }}>
                <h4>🤖 多模型支持</h4>
                <p>支持线性回归、随机森林、XGBoost等多种机器学习模型</p>
              </div>
              <div style={{ marginBottom: 16 }}>
                <h4>⚡ 实时预测</h4>
                <p>快速响应，实时计算预测结果</p>
              </div>
              <div>
                <h4>📊 智能分析</h4>
                <p>基于历史数据训练的AI模型，提供准确可靠的预测</p>
              </div>
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
};

export default PredictionPage;
