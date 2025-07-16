import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  DatePicker,
  Select,
  Space,
  Typography,
  Row,
  Col,
  Statistic,
  Alert,
  Spin,
  Tabs,
  message,
  Tag
} from 'antd';
import {
  CalendarOutlined,
  BarChartOutlined,
  ThunderboltOutlined,
  DownloadOutlined,
  ExperimentOutlined,
  UserOutlined,
  LoginOutlined
} from '@ant-design/icons';
import moment from 'moment';
import { predictionApi } from '../../service/prediction';
import useAISystem from '../../hooks/useAISystem';
import AISystemStatus from '../../components/common/AISystemStatus';
import { useTokenStore } from '../../stores';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const DayAheadPrediction = () => {
  const [predicting, setPredicting] = useState(false);
  const [selectedModel, setSelectedModel] = useState(null);
  const [targetDate, setTargetDate] = useState(moment().add(1, 'day'));
  const [results, setResults] = useState(null);
  
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

  const handlePredict = async () => {
    try {
      setPredicting(true);
      
      const predictData = {
        target_date: targetDate.format('YYYY-MM-DD'),
        model_name: selectedModel
      };

      console.log('🔮 发送日前预测请求:', predictData);
      const response = await predictionApi.predictDayAhead(predictData);
      console.log('📊 日前预测响应完整数据:', response.data);
      
      if (response.data && response.data.success) {
        const resultData = response.data.data;
        console.log('✅ 预测成功，分析结果数据:', resultData);
        
        // 验证数据结构
        if (!resultData.predictions || !Array.isArray(resultData.predictions)) {
          console.error('❌ 预测数据格式错误:', resultData);
          message.error('预测数据格式错误');
          return;
        }
        
        if (!resultData.visualization) {
          console.warn('⚠️ 没有可视化数据');
        } else {
          console.log('📈 可视化数据结构:', resultData.visualization);
          console.log('📈 主图表数据:', resultData.visualization.main_chart);
        }
        
        setResults(resultData);
        const pointCount = resultData.predictions.length;
        if (isLoggedIn) {
          message.success(`日前预测完成！共生成${pointCount}个时间点的预测结果，历史记录已保存`);
        } else {
          message.success(`日前预测完成！共生成${pointCount}个时间点的预测结果，登录后可保存历史记录`);
        }
      } else {
        console.error('❌ 日前预测失败:', response.data);
        message.error(response.data?.error || '日前预测失败');
      }
    } catch (error) {
      console.error('❌ 日前预测请求失败:', error);
      message.error('预测请求失败，请稍后重试');
    } finally {
      setPredicting(false);
    }
  };

  const handleExport = () => {
    if (!results) {
      message.warning('暂无预测结果可导出');
      return;
    }

    const exportData = {
      date: results.prediction.date,
      model_used: results.prediction.model_used,
      statistics: results.prediction.statistics,
      predictions: results.prediction.predictions.map(pred => ({
        timestamp: pred.timestamp,
        predicted_load: pred.predicted_load
      }))
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `day_ahead_prediction_${results.prediction.date}.json`;
    link.click();
    URL.revokeObjectURL(url);
    
    message.success('预测结果已导出');
  };

  const generateQuickPredict = async (days) => {
    const quickDate = moment().add(days, 'day');
    setTargetDate(quickDate);
    
    // 延迟一下让日期选择器更新
    setTimeout(() => {
      handlePredict();
    }, 100);
  };

  return (
    <div>
      <Row gutter={24}>
        {/* 配置面板 */}
        <Col span={8}>
          <Card 
            title={
              <Space>
                <CalendarOutlined />
                <span>日前预测配置</span>
              </Space>
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
                    <span>💡 登录后可自动保存日前预测历史记录 </span>
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

            <div style={{ marginBottom: 16 }}>
              <Alert
                type="info"
                message="日前预测说明"
                description="预测指定日期未来24小时（96个15分钟间隔）的电力负荷变化。系统将自动生成气象预报数据进行预测。"
                showIcon
              />
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>预测日期：</Text>
              <DatePicker
                value={targetDate}
                onChange={setTargetDate}
                style={{ width: '100%', marginTop: 8 }}
                placeholder="选择预测日期"
                disabledDate={(current) => {
                  // 不能选择过去的日期
                  return current && current < moment().startOf('day');
                }}
              />
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>预测模型：</Text>
              <Select
                value={selectedModel}
                onChange={setSelectedModel}
                style={{ width: '100%', marginTop: 8 }}
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
                    {model.name} {model.is_best && '(最佳)'}
                  </Option>
                ))}
              </Select>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>快速选择：</Text>
              <div style={{ marginTop: 8 }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Button 
                    block 
                    onClick={() => generateQuickPredict(1)}
                    disabled={predicting || !isSystemReady || initializing}
                  >
                    明天预测
                  </Button>
                  <Button 
                    block 
                    onClick={() => generateQuickPredict(2)}
                    disabled={predicting || !isSystemReady || initializing}
                  >
                    后天预测
                  </Button>
                  <Button 
                    block 
                    onClick={() => generateQuickPredict(7)}
                    disabled={predicting || !isSystemReady || initializing}
                  >
                    一周后预测
                  </Button>
                </Space>
              </div>
            </div>

            <Button
              type="primary"
              icon={<ThunderboltOutlined />}
              onClick={handlePredict}
              loading={predicting}
              disabled={!isSystemReady || initializing}
              block
              size="large"
            >
              {!systemStatus?.initialized ? '请先初始化系统' : 
               models.length === 0 ? '暂无可用模型' : '开始预测'}
            </Button>
          </Card>
        </Col>

        {/* 预测结果 */}
        <Col span={16}>
          <Card 
            title={
              <Space>
                <BarChartOutlined />
                <span>预测结果</span>
              </Space>
            }
            extra={
              results && (
                <Button 
                  icon={<DownloadOutlined />}
                  onClick={handleExport}
                >
                  导出结果
                </Button>
              )
            }
          >
            {predicting ? (
              <div style={{ textAlign: 'center', padding: '100px 0' }}>
                <Spin size="large" />
                <div style={{ marginTop: 16 }}>
                  <Text>正在进行日前预测计算...</Text>
                  <br />
                  <Text type="secondary">预测96个时间点，请稍候...</Text>
                </div>
              </div>
            ) : results ? (
              <div>
                {/* 统计概览 */}
                <Row gutter={16} style={{ marginBottom: 24 }}>
                  <Col span={6}>
                    <Statistic
                      title="预测日期"
                      value={results.prediction.date}
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic
                      title="峰值负荷"
                      value={results.prediction.statistics.peak_load}
                      precision={2}
                      suffix="MW"
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic
                      title="平均负荷"
                      value={results.prediction.statistics.average_load}
                      precision={2}
                      suffix="MW"
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic
                      title="峰值时间"
                      value={moment(results.prediction.statistics.peak_time).format('HH:mm')}
                    />
                  </Col>
                </Row>

                <Row gutter={16} style={{ marginBottom: 24 }}>
                  <Col span={6}>
                    <Statistic
                      title="最小负荷"
                      value={results.prediction.statistics.min_load}
                      precision={2}
                      suffix="MW"
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic
                      title="总用电量"
                      value={results.prediction.statistics.total_energy}
                      precision={2}
                      suffix="MWh"
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic
                      title="负荷系数"
                      value={results.prediction.statistics.load_factor}
                      precision={3}
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic
                      title="使用模型"
                      value={results.prediction.model_used}
                    />
                  </Col>
                </Row>

                {/* 可视化图表 */}
                <Tabs defaultActiveKey="main">
                  <TabPane 
                    tab={
                      <span>
                        <BarChartOutlined />
                        负荷曲线
                      </span>
                    } 
                    key="main"
                  >
                    {results.visualization && results.visualization.main_chart && results.visualization.main_chart.html ? (
                      <div 
                        dangerouslySetInnerHTML={{ 
                          __html: results.visualization.main_chart.html 
                        }}
                        style={{ 
                          border: '1px solid #d9d9d9',
                          borderRadius: '6px',
                          overflow: 'hidden',
                          minHeight: '400px'
                        }}
                      />
                    ) : (
                      <Alert
                        type="warning"
                        message="图表加载失败"
                        description="负荷曲线图表生成失败或数据为空"
                        showIcon
                      />
                    )}
                  </TabPane>
                  
                  <TabPane 
                    tab={
                      <span>
                        <ExperimentOutlined />
                        负荷分布
                      </span>
                    } 
                    key="distribution"
                  >
                    {results.visualization.distribution_chart && (
                      <div>
                        <div style={{ marginBottom: 16 }}>
                          <Title level={4}>时段负荷分布</Title>
                          <Row gutter={16}>
                            <Col span={6}>
                              <Statistic
                                title="夜间 (00:00-06:00)"
                                value={results.prediction.load_distribution.night}
                                precision={2}
                                suffix="MW"
                              />
                            </Col>
                            <Col span={6}>
                              <Statistic
                                title="上午 (06:00-12:00)"
                                value={results.prediction.load_distribution.morning}
                                precision={2}
                                suffix="MW"
                              />
                            </Col>
                            <Col span={6}>
                              <Statistic
                                title="下午 (12:00-18:00)"
                                value={results.prediction.load_distribution.afternoon}
                                precision={2}
                                suffix="MW"
                              />
                            </Col>
                            <Col span={6}>
                              <Statistic
                                title="晚间 (18:00-24:00)"
                                value={results.prediction.load_distribution.evening}
                                precision={2}
                                suffix="MW"
                              />
                            </Col>
                          </Row>
                        </div>
                        
                        <div 
                          dangerouslySetInnerHTML={{ 
                            __html: results.visualization.distribution_chart.html 
                          }}
                          style={{ 
                            border: '1px solid #d9d9d9',
                            borderRadius: '6px',
                            overflow: 'hidden'
                          }}
                        />
                      </div>
                    )}
                  </TabPane>
                  
                  <TabPane 
                    tab={
                      <span>
                        <BarChartOutlined />
                        统计指标
                      </span>
                    } 
                    key="statistics"
                  >
                    {results.visualization.statistics_chart && (
                      <div 
                        dangerouslySetInnerHTML={{ 
                          __html: results.visualization.statistics_chart.html 
                        }}
                        style={{ 
                          border: '1px solid #d9d9d9',
                          borderRadius: '6px',
                          overflow: 'hidden'
                        }}
                      />
                    )}
                  </TabPane>
                </Tabs>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '100px 0', color: '#999' }}>
                <CalendarOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                <div>
                  <Text>请选择预测日期并点击"开始预测"</Text>
                  <br />
                  <Text type="secondary">将生成96个时间点的详细负荷预测</Text>
                </div>
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DayAheadPrediction;
