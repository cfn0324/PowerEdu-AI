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
import SafeVisualization from '../../components/common/SafeVisualization';
import { useTokenStore } from '../../stores';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const DayAheadPrediction = () => {
  const [predicting, setPredicting] = useState(false);
  const [selectedModel, setSelectedModel] = useState(null);
  const [targetDate, setTargetDate] = useState(() => {
    // 确保初始值是明天的日期
    return moment().add(1, 'day').startOf('day');
  });
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
      
      // 验证日期
      if (!targetDate || !targetDate.isValid()) {
        message.error('请选择有效的预测日期');
        return;
      }
      
      // 确保日期不是今天或过去的日期
      const today = moment().startOf('day');
      if (targetDate.isSameOrBefore(today)) {
        message.error('只能预测明天及以后的日期');
        return;
      }
      
      const predictData = {
        target_date: targetDate.format('YYYY-MM-DD'),
        model_name: selectedModel
      };

      console.log('发送预测请求:', predictData);
      console.log('目标日期对象:', targetDate.toISOString());
      
      const response = await predictionApi.predictDayAhead(predictData);
      
      if (response.data && response.data.success) {
        const resultData = response.data.data;
        
        // 验证数据结构
        if (!resultData.prediction || !resultData.prediction.predictions || !Array.isArray(resultData.prediction.predictions)) {
          message.error('预测数据格式错误');
          return;
        }
        
        setResults(resultData);
        const pointCount = resultData.prediction.predictions.length;
        if (isLoggedIn) {
          message.success(`日前预测完成！共生成${pointCount}个时间点的预测结果，历史记录已保存`);
        } else {
          message.success(`日前预测完成！共生成${pointCount}个时间点的预测结果，登录后可保存历史记录`);
        }
      } else {
        message.error(response.data?.error || '日前预测失败');
      }
    } catch (error) {
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
    if (predicting) {
      message.warning('正在预测中，请稍候...');
      return;
    }
    
    // 从今天开始计算，确保日期正确
    const today = moment().startOf('day');
    const quickDate = today.clone().add(days, 'day');
    
    // 验证生成的日期
    if (!quickDate.isValid()) {
      message.error('生成的日期无效');
      return;
    }
    
    console.log(`快速选择: 今天+${days}天 = ${quickDate.format('YYYY-MM-DD')}`);
    
    // 更新状态
    setTargetDate(quickDate);
    
    // 等待状态更新
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // 直接调用预测
    try {
      setPredicting(true);
      
      const predictData = {
        target_date: quickDate.format('YYYY-MM-DD'),
        model_name: selectedModel
      };

      console.log('快速预测请求:', predictData);
      const response = await predictionApi.predictDayAhead(predictData);
      
      if (response.data && response.data.success) {
        const resultData = response.data.data;
        
        if (!resultData.prediction || !resultData.prediction.predictions || !Array.isArray(resultData.prediction.predictions)) {
          message.error('预测数据格式错误');
          return;
        }
        
        setResults(resultData);
        const pointCount = resultData.prediction.predictions.length;
        if (isLoggedIn) {
          message.success(`快速预测完成！共生成${pointCount}个时间点的预测结果，历史记录已保存`);
        } else {
          message.success(`快速预测完成！共生成${pointCount}个时间点的预测结果，登录后可保存历史记录`);
        }
      } else {
        message.error(response.data?.error || '快速预测失败');
      }
    } catch (error) {
      console.error('快速预测错误:', error);
      message.error('快速预测请求失败，请稍后重试');
    } finally {
      setPredicting(false);
    }
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
                onChange={(date) => {
                  console.log('原始日期对象:', date);
                  if (date) {
                    const formattedDate = date.format('YYYY-MM-DD');
                    console.log('格式化日期:', formattedDate);
                    setTargetDate(date);
                  } else {
                    console.log('日期被清空');
                    setTargetDate(null);
                  }
                }}
                style={{ width: '100%', marginTop: 8 }}
                placeholder="请选择预测日期"
                format="YYYY-MM-DD"
                allowClear={true}
                disabledDate={(current) => {
                  if (!current) return false;
                  // 禁用今天及之前的日期
                  const today = moment().startOf('day');
                  return current.isSameOrBefore(today);
                }}
                showToday={false}
                getPopupContainer={(trigger) => trigger.parentElement}
              />
              {targetDate && targetDate.isValid() && (
                <div style={{ marginTop: 4, color: '#666', fontSize: '12px' }}>
                  已选择: {targetDate.format('YYYY-MM-DD')} (星期{['日','一','二','三','四','五','六'][targetDate.day()]})
                </div>
              )}
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
                      <SafeVisualization
                        html={results.visualization.main_chart.html}
                        height="400px"
                        title="日前负荷预测曲线"
                        errorTitle="图表加载失败"
                        errorDescription="负荷曲线图表生成失败或数据为空"
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
                    {results.visualization.distribution_chart && results.visualization.distribution_chart.html ? (
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
                        
                        <SafeVisualization
                          html={results.visualization.distribution_chart.html}
                          height="400px"
                          title="负荷分布饼图"
                          errorTitle="图表加载失败"
                          errorDescription="负荷分布图表生成失败或数据为空"
                        />
                      </div>
                    ) : (
                      <Alert
                        type="warning"
                        message="图表加载失败"
                        description="负荷分布图表生成失败或数据为空"
                        showIcon
                      />
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
                    {results.visualization.statistics_chart && results.visualization.statistics_chart.html ? (
                      <SafeVisualization
                        html={results.visualization.statistics_chart.html}
                        height="400px"
                        title="统计指标图表"
                        errorTitle="图表加载失败"
                        errorDescription="统计指标图表生成失败或数据为空"
                      />
                    ) : (
                      <Alert
                        type="warning"
                        message="图表加载失败"
                        description="统计指标图表生成失败或数据为空"
                        showIcon
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
