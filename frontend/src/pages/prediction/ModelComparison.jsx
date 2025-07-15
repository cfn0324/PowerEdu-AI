import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Typography,
  Row,
  Col,
  Statistic,
  Spin,
  Alert,
  message
} from 'antd';
import {
  ExperimentOutlined,
  BarChartOutlined,
  TrophyOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { predictionApi } from '../../service/prediction';

const { Title, Text } = Typography;

const ModelComparison = () => {
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState([]);
  const [performance, setPerformance] = useState(null);

  useEffect(() => {
    loadModelPerformance();
  }, []);

  const loadModelPerformance = async () => {
    try {
      setLoading(true);
      const response = await predictionApi.getModelPerformance();
      if (response.success) {
        setModels(response.data.comparison);
        setPerformance(response.data);
      }
    } catch (error) {
      message.error('加载模型性能数据失败');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: '排名',
      render: (_, __, index) => (
        <Space>
          {index === 0 && <TrophyOutlined style={{ color: '#faad14' }} />}
          <span>{index + 1}</span>
        </Space>
      ),
      width: 80,
      align: 'center'
    },
    {
      title: '模型名称',
      dataIndex: 'model',
      key: 'model',
      render: (text, record, index) => (
        <Space>
          <span style={{ fontWeight: index === 0 ? 'bold' : 'normal' }}>
            {text}
          </span>
          {index === 0 && (
            <span style={{ color: '#52c41a', fontSize: '12px' }}>
              (最佳)
            </span>
          )}
        </Space>
      )
    },
    {
      title: 'R² 决定系数',
      dataIndex: 'r2',
      key: 'r2',
      render: (value) => (
        <span style={{ 
          color: value > 0.9 ? '#52c41a' : value > 0.8 ? '#faad14' : '#ff4d4f' 
        }}>
          {value.toFixed(4)}
        </span>
      ),
      sorter: (a, b) => a.r2 - b.r2,
      defaultSortOrder: 'descend'
    },
    {
      title: '均方根误差 (RMSE)',
      dataIndex: 'rmse',
      key: 'rmse',
      render: (value) => value.toFixed(4),
      sorter: (a, b) => a.rmse - b.rmse
    },
    {
      title: '平均绝对误差 (MAE)',
      dataIndex: 'mae',
      key: 'mae',
      render: (value) => value.toFixed(4),
      sorter: (a, b) => a.mae - b.mae
    },
    {
      title: '平均绝对百分比误差 (MAPE)',
      dataIndex: 'mape',
      key: 'mape',
      render: (value) => `${value.toFixed(2)}%`,
      sorter: (a, b) => a.mape - b.mape
    },
    {
      title: '训练时间 (秒)',
      dataIndex: 'training_time',
      key: 'training_time',
      render: (value) => value.toFixed(2),
      sorter: (a, b) => a.training_time - b.training_time
    }
  ];

  const getPerformanceLevel = (r2) => {
    if (r2 > 0.9) return { level: '优秀', color: '#52c41a' };
    if (r2 > 0.8) return { level: '良好', color: '#faad14' };
    if (r2 > 0.7) return { level: '一般', color: '#ff7a45' };
    return { level: '需改进', color: '#ff4d4f' };
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text>正在加载模型性能数据...</Text>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* 性能概览 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="参与对比模型数"
              value={models.length}
              prefix={<ExperimentOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="最佳模型"
              value={performance?.best_model || 'N/A'}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="最高 R² 分数"
              value={models.length > 0 ? models[0].r2 : 0}
              precision={4}
              prefix={<BarChartOutlined />}
              valueStyle={{ 
                color: models.length > 0 ? getPerformanceLevel(models[0].r2).color : '#999' 
              }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="性能等级"
              value={models.length > 0 ? getPerformanceLevel(models[0].r2).level : 'N/A'}
              valueStyle={{ 
                color: models.length > 0 ? getPerformanceLevel(models[0].r2).color : '#999' 
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* 模型性能对比表 */}
      <Card 
        title={
          <Space>
            <ExperimentOutlined />
            <span>模型性能对比</span>
          </Space>
        }
        extra={
          <Button 
            icon={<ReloadOutlined />}
            onClick={loadModelPerformance}
            loading={loading}
          >
            刷新数据
          </Button>
        }
      >
        {models.length > 0 ? (
          <>
            <Alert
              type="info"
              message="性能指标说明"
              description={
                <div>
                  <p><strong>R² 决定系数：</strong>越接近1越好，表示模型解释数据变异的能力</p>
                  <p><strong>RMSE/MAE：</strong>误差指标，越小越好</p>
                  <p><strong>MAPE：</strong>平均绝对百分比误差，越小越好</p>
                </div>
              }
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Table
              columns={columns}
              dataSource={models}
              rowKey="model"
              pagination={false}
              size="middle"
              rowClassName={(record, index) => 
                index === 0 ? 'best-model-row' : ''
              }
            />

            {/* 性能可视化图表 */}
            {performance?.visualization && (
              <div style={{ marginTop: 24 }}>
                <Title level={4}>性能可视化对比</Title>
                <div 
                  dangerouslySetInnerHTML={{ 
                    __html: performance.visualization.html 
                  }}
                  style={{ 
                    border: '1px solid #d9d9d9',
                    borderRadius: '6px',
                    overflow: 'hidden'
                  }}
                />
              </div>
            )}
          </>
        ) : (
          <div style={{ textAlign: 'center', padding: '50px 0', color: '#999' }}>
            <ExperimentOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
            <div>
              <Text>暂无模型性能数据</Text>
              <br />
              <Text type="secondary">请确保系统已初始化并训练了模型</Text>
            </div>
          </div>
        )}
      </Card>

      <style jsx>{`
        .best-model-row {
          background-color: #f6ffed;
        }
        .best-model-row:hover {
          background-color: #f6ffed !important;
        }
      `}</style>
    </div>
  );
};

export default ModelComparison;
