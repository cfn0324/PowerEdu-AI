import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Button,
  Tabs,
  Alert,
  Spin,
  Typography,
  Space,
  message
} from 'antd';
import {
  ThunderboltOutlined,
  BarChartOutlined,
  ExperimentOutlined,
  HistoryOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import SinglePrediction from './SinglePrediction';
import BatchPrediction from './BatchPrediction';
import DayAheadPrediction from './DayAheadPrediction';
import ModelComparison from './ModelComparison';
import PredictionHistory from './PredictionHistory';
import api from '../../service/req';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

const PredictionDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [systemStatus, setSystemStatus] = useState(null);
  const [initializing, setInitializing] = useState(false);
  const [activeTab, setActiveTab] = useState('single');

  useEffect(() => {
    initializeSystem();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const response = await api.get('/prediction/system/status');
      
      if (response.data && response.data.success) {
        setSystemStatus(response.data.data);
        return response.data.data;
      } else {
        setSystemStatus({ initialized: false, error: '状态检查失败' });
        return { initialized: false, error: '状态检查失败' };
      }
    } catch (error) {
      setSystemStatus({ initialized: false, error: error.message });
      return { initialized: false, error: error.message };
    }
  };

  const initializeSystemAPI = async () => {
    try {
      setInitializing(true);
      
      const response = await api.get('/prediction/system/initialize');
      
      if (response.data && response.data.success) {
        message.success('AI系统初始化成功！');
        
        // 等待几秒后检查状态
        setTimeout(() => {
          checkSystemStatus();
        }, 3000);
        return true;
      } else {
        message.error(`初始化失败: ${response.data?.message || '未知错误'}`);
        return false;
      }
    } catch (error) {
      message.error(`初始化系统异常: ${error.message}`);
      return false;
    } finally {
      setInitializing(false);
    }
  };

  const initializeSystem = async () => {
    try {
      setLoading(true);
      
      // 首先检查系统状态
      const status = await checkSystemStatus();
      
      if (!status.initialized) {
        // 如果系统未初始化，先初始化
        message.info('正在初始化AI预测系统，请稍候...');
        await initializeSystemAPI();
      }
      
    } catch (error) {
      console.error('初始化失败:', error);
      message.error('系统初始化失败，请刷新页面重试');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    initializeSystem();
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text>正在初始化AI预测系统...</Text>
        </div>
      </div>
    );
  }

  if (!systemStatus?.initialized) {
    return (
      <div style={{ padding: '20px' }}>
        <Alert
          type="warning"
          message="系统未初始化"
          description="AI预测系统尚未初始化，请点击下方按钮进行初始化。"
          action={
            <Button 
              type="primary" 
              onClick={initializeSystemAPI}
              loading={initializing}
            >
              {initializing ? '正在初始化...' : '初始化系统'}
            </Button>
          }
          showIcon
        />
        
        {initializing && (
          <Alert
            message="正在初始化AI预测系统..."
            description="这可能需要1-2分钟时间，请耐心等待。系统正在生成训练数据和训练机器学习模型。"
            type="info"
            showIcon
            icon={<Spin />}
            style={{ marginTop: 16 }}
          />
        )}
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: '20px' }}>
        <Space align="center">
          <ThunderboltOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
          <Title level={2} style={{ margin: 0 }}>电力负荷AI预测系统</Title>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh}>
            刷新
          </Button>
        </Space>
      </div>

      {/* 系统状态概览 */}
      <Row gutter={16} style={{ marginBottom: '20px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="可用模型数量"
              value={systemStatus?.available_models?.length || 0}
              prefix={<ExperimentOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="最佳模型"
              value={systemStatus?.best_model || 'N/A'}
              prefix={<BarChartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="系统状态"
              value={systemStatus?.models_trained ? '已训练' : '未训练'}
              prefix={<ThunderboltOutlined />}
              valueStyle={{ 
                color: systemStatus?.models_trained ? '#3f8600' : '#cf1322' 
              }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="最后更新"
              value={new Date(systemStatus?.timestamp || Date.now()).toLocaleTimeString()}
              prefix={<HistoryOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 功能标签页 */}
      <Card>
        <Tabs 
          activeKey={activeTab} 
          onChange={setActiveTab}
          tabPosition="top"
          size="large"
        >
          <TabPane
            tab={
              <span>
                <ThunderboltOutlined />
                单点预测
              </span>
            }
            key="single"
          >
            <SinglePrediction />
          </TabPane>
          
          <TabPane
            tab={
              <span>
                <BarChartOutlined />
                批量预测
              </span>
            }
            key="batch"
          >
            <BatchPrediction />
          </TabPane>
          
          <TabPane
            tab={
              <span>
                <ExperimentOutlined />
                日前预测
              </span>
            }
            key="dayahead"
          >
            <DayAheadPrediction />
          </TabPane>
          
          <TabPane
            tab={
              <span>
                <BarChartOutlined />
                模型对比
              </span>
            }
            key="comparison"
          >
            <ModelComparison />
          </TabPane>
          
          <TabPane
            tab={
              <span>
                <HistoryOutlined />
                预测历史
              </span>
            }
            key="history"
          >
            <PredictionHistory />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default PredictionDashboard;
