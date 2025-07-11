import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Select, DatePicker, Row, Col, Statistic, Alert, Spin } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import './index.css';

const { Option } = Select;
const { RangePicker } = DatePicker;

const PredictionPage = () => {
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState([]);
  const [singleResult, setSingleResult] = useState(null);
  const [batchResult, setBatchResult] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchModels();
    fetchPerformance();
  }, []);

  const fetchModels = async () => {
    try {
      const response = await axios.get('/api/prediction/models');
      if (response.data.success) {
        setModels(response.data.data);
      }
    } catch (error) {
      console.error('获取模型列表失败:', error);
    }
  };

  const fetchPerformance = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/prediction/performance');
      if (response.data.success) {
        setPerformance(response.data.data);
      }
    } catch (error) {
      console.error('获取性能数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSinglePredict = async (values) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/prediction/predict/single', {
        model: values.model,
        features: {
          temperature: values.temperature,
          humidity: values.humidity,
          hour: values.hour,
          day_of_week: values.day_of_week,
          month: values.month
        }
      });
      
      if (response.data.success) {
        setSingleResult(response.data.data);
      }
    } catch (error) {
      console.error('单点预测失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchPredict = async (values) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/prediction/predict/batch', {
        model: values.batchModel,
        start_date: values.dateRange[0].format('YYYY-MM-DD'),
        end_date: values.dateRange[1].format('YYYY-MM-DD')
      });
      
      if (response.data.success) {
        setBatchResult(response.data.data);
      }
    } catch (error) {
      console.error('批量预测失败:', error);
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

      <Row gutter={[24, 24]}>
        {/* 单点预测 */}
        <Col span={12}>
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
                    <p><strong>预测负荷:</strong> {singleResult.prediction?.toFixed(2)} MW</p>
                    <p><strong>置信区间:</strong> [{singleResult.confidence_interval?.[0]?.toFixed(2)}, {singleResult.confidence_interval?.[1]?.toFixed(2)}] MW</p>
                    <p><strong>使用模型:</strong> {singleResult.model}</p>
                  </div>
                }
                type="success"
                showIcon
              />
            )}
          </Card>
        </Col>

        {/* 批量预测 */}
        <Col span={12}>
          <Card title="📊 批量预测" className="prediction-card">
            <Form layout="vertical" onFinish={handleBatchPredict}>
              <Form.Item
                name="batchModel"
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

              <Form.Item
                name="dateRange"
                label="预测时间范围"
                rules={[{ required: true, message: '请选择时间范围' }]}
              >
                <RangePicker style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading} block>
                  批量预测
                </Button>
              </Form.Item>
            </Form>

            {batchResult && (
              <div className="batch-result">
                <h4>预测结果趋势图</h4>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={batchResult.predictions}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="datetime" />
                    <YAxis />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="prediction" 
                      stroke="#1890ff" 
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </Card>
        </Col>

        {/* 模型性能对比 */}
        <Col span={24}>
          <Card title="🏆 模型性能对比" loading={loading}>
            {performance && (
              <Row gutter={16}>
                {Object.entries(performance).map(([model, metrics]) => (
                  <Col span={6} key={model}>
                    <Card size="small" title={model}>
                      <Statistic
                        title="R² 得分"
                        value={metrics.r2_score}
                        precision={4}
                        suffix=""
                      />
                      <Statistic
                        title="均方根误差"
                        value={metrics.rmse}
                        precision={2}
                        suffix="MW"
                      />
                      <Statistic
                        title="平均绝对误差"
                        value={metrics.mae}
                        precision={2}
                        suffix="MW"
                      />
                    </Card>
                  </Col>
                ))}
              </Row>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default PredictionPage;
