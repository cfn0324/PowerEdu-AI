import React, { useState, useEffect } from 'react';
import {
  Form,
  Input,
  InputNumber,
  Button,
  Card,
  Row,
  Col,
  Select,
  DatePicker,
  TimePicker,
  Space,
  Divider,
  Alert,
  Spin,
  Typography,
  message
} from 'antd';
import {
  ThunderboltOutlined,
  CalculatorOutlined,
  ExperimentOutlined
} from '@ant-design/icons';
import moment from 'moment';
import { predictionApi } from '../../service/prediction';

const { Title, Text } = Typography;
const { Option } = Select;

const SinglePrediction = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [predicting, setPredicting] = useState(false);
  const [models, setModels] = useState([]);
  const [result, setResult] = useState(null);

  useEffect(() => {
    loadModels();
    // 设置默认值
    form.setFieldsValue({
      timestamp: moment(),
      temperature: 25,
      humidity: 60,
      wind_speed: 5.0,
      rainfall: 0.0
    });
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      const response = await predictionApi.getModels();
      if (response.success) {
        setModels(response.data);
      }
    } catch (error) {
      message.error('加载模型列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = async (values) => {
    try {
      setPredicting(true);
      
      // 格式化时间戳
      const timestamp = values.timestamp.format('YYYY-MM-DD HH:mm:ss');
      
      const predictData = {
        timestamp,
        temperature: values.temperature,
        humidity: values.humidity,
        wind_speed: values.wind_speed,
        rainfall: values.rainfall,
        model_name: values.model_name
      };

      const response = await predictionApi.predictSingle(predictData);
      
      if (response.success) {
        setResult(response.data);
        message.success('预测完成！');
      } else {
        message.error(response.error || '预测失败');
      }
    } catch (error) {
      console.error('预测失败:', error);
      message.error('预测请求失败，请稍后重试');
    } finally {
      setPredicting(false);
    }
  };

  const handleReset = () => {
    form.resetFields();
    setResult(null);
    // 重新设置默认值
    form.setFieldsValue({
      timestamp: moment(),
      temperature: 25,
      humidity: 60,
      wind_speed: 5.0,
      rainfall: 0.0
    });
  };

  const generateRandomData = () => {
    const randomTemp = Math.round((Math.random() * 30 + 10) * 10) / 10; // 10-40°C
    const randomHumidity = Math.round((Math.random() * 50 + 30) * 10) / 10; // 30-80%
    const randomWind = Math.round((Math.random() * 10 + 2) * 10) / 10; // 2-12 m/s
    const randomRain = Math.round((Math.random() * 5) * 10) / 10; // 0-5 mm
    
    form.setFieldsValue({
      temperature: randomTemp,
      humidity: randomHumidity,
      wind_speed: randomWind,
      rainfall: randomRain
    });
    
    message.info('已生成随机气象数据');
  };

  return (
    <div>
      <Row gutter={24}>
        {/* 输入表单 */}
        <Col span={12}>
          <Card 
            title={
              <Space>
                <ThunderboltOutlined />
                <span>单点负荷预测</span>
              </Space>
            }
            extra={
              <Button onClick={generateRandomData} size="small">
                随机数据
              </Button>
            }
          >
            <Form
              form={form}
              layout="vertical"
              onFinish={handlePredict}
              autoComplete="off"
            >
              <Form.Item
                label="预测时间"
                name="timestamp"
                rules={[{ required: true, message: '请选择预测时间' }]}
              >
                <DatePicker
                  showTime
                  format="YYYY-MM-DD HH:mm:ss"
                  style={{ width: '100%' }}
                  placeholder="选择预测时间"
                />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    label="温度 (°C)"
                    name="temperature"
                    rules={[
                      { required: true, message: '请输入温度' },
                      { type: 'number', min: -20, max: 50, message: '温度范围：-20°C 到 50°C' }
                    ]}
                  >
                    <InputNumber
                      style={{ width: '100%' }}
                      placeholder="温度"
                      step={0.1}
                      precision={1}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label="湿度 (%)"
                    name="humidity"
                    rules={[
                      { required: true, message: '请输入湿度' },
                      { type: 'number', min: 0, max: 100, message: '湿度范围：0% 到 100%' }
                    ]}
                  >
                    <InputNumber
                      style={{ width: '100%' }}
                      placeholder="相对湿度"
                      step={1}
                      precision={1}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    label="风速 (m/s)"
                    name="wind_speed"
                    rules={[
                      { type: 'number', min: 0, max: 50, message: '风速范围：0 到 50 m/s' }
                    ]}
                  >
                    <InputNumber
                      style={{ width: '100%' }}
                      placeholder="风速"
                      step={0.1}
                      precision={1}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label="降雨量 (mm)"
                    name="rainfall"
                    rules={[
                      { type: 'number', min: 0, max: 200, message: '降雨量范围：0 到 200 mm' }
                    ]}
                  >
                    <InputNumber
                      style={{ width: '100%' }}
                      placeholder="降雨量"
                      step={0.1}
                      precision={1}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label="选择模型" name="model_name">
                <Select placeholder="选择预测模型（留空使用最佳模型）" allowClear>
                  {models.map((model) => (
                    <Option key={model.name} value={model.name}>
                      {model.name} {model.is_best && '(最佳)'}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Divider />

              <Space>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={predicting}
                  icon={<CalculatorOutlined />}
                  size="large"
                >
                  开始预测
                </Button>
                <Button onClick={handleReset} size="large">
                  重置
                </Button>
              </Space>
            </Form>
          </Card>
        </Col>

        {/* 预测结果 */}
        <Col span={12}>
          <Card 
            title={
              <Space>
                <ExperimentOutlined />
                <span>预测结果</span>
              </Space>
            }
          >
            {predicting ? (
              <div style={{ textAlign: 'center', padding: '50px 0' }}>
                <Spin size="large" />
                <div style={{ marginTop: 16 }}>
                  <Text>正在进行预测计算...</Text>
                </div>
              </div>
            ) : result ? (
              <div>
                <Alert
                  type="success"
                  message={`预测负荷: ${result.prediction.predicted_load.toFixed(2)} MW`}
                  description={`使用模型: ${result.prediction.model_used}`}
                  showIcon
                  style={{ marginBottom: 16 }}
                />

                <div style={{ marginBottom: 16 }}>
                  <Title level={4}>输入参数</Title>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Text strong>时间：</Text>
                      <Text>{moment(result.prediction.timestamp).format('YYYY-MM-DD HH:mm:ss')}</Text>
                    </Col>
                    <Col span={12}>
                      <Text strong>温度：</Text>
                      <Text>{result.prediction.input_features.temperature}°C</Text>
                    </Col>
                    <Col span={12}>
                      <Text strong>湿度：</Text>
                      <Text>{result.prediction.input_features.humidity}%</Text>
                    </Col>
                    <Col span={12}>
                      <Text strong>风速：</Text>
                      <Text>{result.prediction.input_features.wind_speed} m/s</Text>
                    </Col>
                  </Row>
                </div>

                {/* 可视化图表 */}
                {result.visualization && (
                  <div>
                    <Title level={4}>预测分析</Title>
                    <div 
                      dangerouslySetInnerHTML={{ 
                        __html: result.visualization.html 
                      }}
                      style={{ 
                        border: '1px solid #d9d9d9',
                        borderRadius: '6px',
                        overflow: 'hidden'
                      }}
                    />
                  </div>
                )}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '50px 0', color: '#999' }}>
                <ExperimentOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                <div>
                  <Text>请填写参数并点击"开始预测"查看结果</Text>
                </div>
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SinglePrediction;
