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
  message,
  Tag
} from 'antd';
import {
  ThunderboltOutlined,
  CalculatorOutlined,
  ExperimentOutlined,
  UserOutlined,
  LoginOutlined
} from '@ant-design/icons';
import moment from 'moment';
import { predictionApi } from '../../service/prediction';
import useAISystem from '../../hooks/useAISystem';
import AISystemStatus from '../../components/common/AISystemStatus';
import SafeVisualization from '../../components/common/SafeVisualization';
import { useTokenStore } from '../../stores';

const { Title, Text } = Typography;
const { Option } = Select;

const SinglePrediction = () => {
  const [form] = Form.useForm();
  const [predicting, setPredicting] = useState(false);
  const [result, setResult] = useState(null);
  
  // 获取用户登录状态
  const { auth } = useTokenStore();
  const isLoggedIn = !!auth?.token;
  
  // 使用AI系统管理hook
  const {
    systemStatus,
    models,
    loading,
    initializing,
    initializeSystem,
    loadModels,
    isSystemReady
  } = useAISystem();

  useEffect(() => {
    // 设置默认值
    form.setFieldsValue({
      timestamp: moment(),
      temperature: 25,
      humidity: 60,
      wind_speed: 5.0,
      rainfall: 0.0
    });
  }, []);

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

      console.log('🔮 发送预测请求:', predictData);
      const response = await predictionApi.predictSingle(predictData);
      console.log('📊 预测响应:', response.data);
      
      if (response.data && response.data.success) {
        setResult(response.data.data);
        if (isLoggedIn) {
          message.success('预测完成！历史记录已保存');
        } else {
          message.success('预测完成！登录后可保存历史记录');
        }
        console.log('✅ 预测结果:', response.data.data);
      } else {
        console.log('❌ 预测失败:', response.data);
        const errorMsg = response.data?.error || '预测失败';
        message.error(`预测失败: ${errorMsg}`);
        // 显示详细错误信息供调试
        console.error('详细错误信息:', response.data);
      }
    } catch (error) {
      console.error('❌ 预测异常:', error);
      let errorMessage = '预测请求失败，请稍后重试';
      
      if (error.response) {
        // 服务器响应错误
        console.error('服务器响应错误:', error.response.data);
        errorMessage = `服务器错误: ${error.response.data?.error || error.response.statusText}`;
      } else if (error.request) {
        // 网络错误
        console.error('网络请求错误:', error.request);
        errorMessage = '网络连接失败，请检查服务器状态';
      } else {
        // 其他错误
        console.error('其他错误:', error.message);
        errorMessage = `请求错误: ${error.message}`;
      }
      
      message.error(errorMessage);
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
            {/* 系统状态检查 */}
            <AISystemStatus
              systemStatus={systemStatus}
              models={models}
              loading={loading}
              initializing={initializing}
              onInitialize={initializeSystem}
              onLoadModels={loadModels}
            />

            {/* 登录状态提示 */}
            {!isLoggedIn && (
              <Alert
                type="info"
                message="历史记录提示"
                description={
                  <div>
                    <span>💡 登录后可自动保存预测历史记录 </span>
                    <Tag color="green" style={{ marginLeft: 8 }}>
                      <UserOutlined /> 建议登录
                    </Tag>
                  </div>
                }
                style={{ marginBottom: 16 }}
                showIcon
                action={
                  <Button size="small" icon={<LoginOutlined />} onClick={() => window.location.reload()}>
                    去登录
                  </Button>
                }
              />
            )}

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

              <Form.Item 
                label="选择模型" 
                name="model_name"
                extra={
                  models.length === 0 && systemStatus?.initialized 
                    ? "暂无可用模型，请刷新页面或重新初始化系统" 
                    : `共有 ${models.length} 个模型可选，留空将使用最佳模型`
                }
              >
                <Select 
                  placeholder={
                    loading ? "正在加载模型..." : 
                    models.length === 0 ? "暂无可用模型" : 
                    "选择预测模型（留空使用最佳模型）"
                  }
                  allowClear
                  loading={loading}
                  disabled={!systemStatus?.initialized || models.length === 0}
                  notFoundContent={
                    !systemStatus?.initialized ? "请先初始化系统" : "暂无可用模型"
                  }
                >
                  {models.map((model) => (
                    <Option key={model.name} value={model.name}>
                      <Space>
                        <span>{model.name}</span>
                        {model.is_best && (
                          <span style={{ color: '#52c41a', fontSize: '12px' }}>
                            (最佳)
                          </span>
                        )}
                        {model.performance && (
                          <span style={{ color: '#999', fontSize: '12px' }}>
                            R²: {model.performance.r2?.toFixed(3)}
                          </span>
                        )}
                      </Space>
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
                  disabled={!isSystemReady || initializing}
                  icon={<CalculatorOutlined />}
                  size="large"
                >
                  {!systemStatus?.initialized ? '请先初始化系统' : 
                   models.length === 0 ? '暂无可用模型' : '开始预测'}
                </Button>
                <Button 
                  onClick={handleReset} 
                  size="large"
                  disabled={predicting || initializing}
                >
                  重置
                </Button>
                {systemStatus?.initialized && (
                  <Button 
                    onClick={loadModels} 
                    size="large"
                    loading={loading}
                    disabled={predicting || initializing}
                  >
                    刷新模型
                  </Button>
                )}
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
                {result.visualization && result.visualization.html ? (
                  <div>
                    <Title level={4}>预测分析</Title>
                    <SafeVisualization
                      html={result.visualization.html}
                      height="400px"
                      title="单点负荷预测分析"
                      errorTitle="图表加载失败"
                      errorDescription="预测分析图表生成失败或数据为空"
                    />
                  </div>
                ) : result.visualization && result.visualization.error ? (
                  <div>
                    <Title level={4}>预测分析</Title>
                    <Alert
                      type="warning"
                      message="可视化生成失败"
                      description={`错误信息: ${result.visualization.error}`}
                      showIcon
                    />
                  </div>
                ) : (
                  <div>
                    <Title level={4}>预测分析</Title>
                    <Alert
                      type="info"
                      message="暂无可视化数据"
                      description="预测完成，但可视化图表生成中..."
                      showIcon
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
