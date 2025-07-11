import React, { useState } from 'react';
import { Card, Form, Input, Button, Select, Row, Col, Statistic, Alert, message } from 'antd';
import './index.css';

const { Option } = Select;

const PredictionPage = () => {
  const [loading, setLoading] = useState(false);
  const [singleResult, setSingleResult] = useState(null);
  const [form] = Form.useForm();

  const handleSinglePredict = async (values) => {
    try {
      setLoading(true);
      // 模拟预测结果
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockResult = {
        prediction: (Math.random() * 500 + 300).toFixed(2),
        confidence_interval: [
          (Math.random() * 500 + 250).toFixed(2),
          (Math.random() * 500 + 350).toFixed(2)
        ],
        model: values.model
      };
      
      setSingleResult(mockResult);
      message.success('预测完成！');
    } catch (error) {
      console.error('预测失败:', error);
      message.error('预测失败，请重试');
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

      <Row gutter={[24, 24]} justify="center">
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
                    <p><strong>预测负荷:</strong> {singleResult.prediction} MW</p>
                    <p><strong>置信区间:</strong> [{singleResult.confidence_interval[0]}, {singleResult.confidence_interval[1]}] MW</p>
                    <p><strong>使用模型:</strong> {singleResult.model}</p>
                  </div>
                }
                type="success"
                showIcon
              />
            )}
          </Card>
        </Col>

        {/* 功能说明 */}
        <Col span={24}>
          <Card title="🏆 功能介绍" style={{marginTop: 24}}>
            <Row gutter={16}>
              <Col span={6}>
                <Card size="small" title="单点预测">
                  <p>输入环境参数，预测特定时间点的电力负荷</p>
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small" title="多模型支持">
                  <p>支持线性回归、随机森林、XGBoost等多种机器学习模型</p>
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small" title="实时预测">
                  <p>快速响应，实时计算预测结果</p>
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small" title="置信区间">
                  <p>提供预测结果的置信区间，评估预测可靠性</p>
                </Card>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default PredictionPage;
