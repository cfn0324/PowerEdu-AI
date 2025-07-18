import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Typography,
  Tag,
  Tooltip,
  Empty,
  Spin,
  message,
  Modal,
  Alert
} from 'antd';
import {
  HistoryOutlined,
  EyeOutlined,
  DeleteOutlined,
  ReloadOutlined,
  DownloadOutlined,
  LoginOutlined,
  UserOutlined
} from '@ant-design/icons';
import moment from 'moment';
import { predictionApi } from '../../service/prediction';
import { useTokenStore } from '../../stores';

const { Title, Text } = Typography;

const PredictionHistory = () => {
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);
  
  // 获取用户登录状态
  const { auth } = useTokenStore();
  const isLoggedIn = !!auth?.token;

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      console.log('🔍 开始加载预测历史...');
      console.log('🔍 当前登录状态:', isLoggedIn);
      console.log('🔍 Token:', auth?.token ? '存在' : '不存在');
      
      const response = await predictionApi.getPredictionHistory();
      console.log('🔍 历史记录API响应:', response);
      
      if (response.data && response.data.success) {
        const historyData = response.data.data || [];
        console.log('🔍 获取到历史记录数量:', historyData.length);
        setHistory(historyData);
        
        if (historyData.length > 0) {
          message.success(`成功加载 ${historyData.length} 条预测历史记录`);
        }
      } else {
        console.error('🔍 历史记录加载失败:', response.data);
        message.error('预测历史加载失败: ' + (response.data?.error || '未知错误'));
      }
    } catch (error) {
      console.error('🔍 历史记录请求异常:', error);
      if (error.response) {
        console.error('🔍 错误响应状态:', error.response.status);
        console.error('🔍 错误响应数据:', error.response.data);
      }
      message.error('加载预测历史失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = (record) => {
    setSelectedRecord(record);
    setDetailVisible(true);
  };

  const handleExportHistory = () => {
    if (history.length === 0) {
      message.warning('暂无历史记录可导出');
      return;
    }

    const exportData = history.map(record => ({
      id: record.id,
      model_name: record.model_name,
      prediction_type: record.prediction_type,
      created_at: record.created_at,
      input_summary: record.input_summary,
      prediction_summary: record.prediction_summary
    }));

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `prediction_history_${moment().format('YYYY-MM-DD')}.json`;
    link.click();
    URL.revokeObjectURL(url);
    
    message.success('历史记录已导出');
  };

  const getPredictionTypeTag = (type) => {
    const typeMap = {
      'single': { color: 'blue', text: '单点预测' },
      'batch': { color: 'green', text: '批量预测' },
      'day_ahead': { color: 'purple', text: '日前预测' }
    };
    const config = typeMap[type] || { color: 'default', text: type };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const columns = [
    {
      title: '序号',
      render: (_, __, index) => index + 1,
      width: 60,
      align: 'center'
    },
    {
      title: '预测时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => (
        <Tooltip title={moment(text).format('YYYY-MM-DD HH:mm:ss')}>
          {moment(text).fromNow()}
        </Tooltip>
      ),
      sorter: (a, b) => moment(a.created_at).unix() - moment(b.created_at).unix(),
      defaultSortOrder: 'descend'
    },
    {
      title: '预测类型',
      dataIndex: 'prediction_type',
      key: 'prediction_type',
      render: getPredictionTypeTag,
      filters: [
        { text: '单点预测', value: 'single' },
        { text: '批量预测', value: 'batch' },
        { text: '日前预测', value: 'day_ahead' }
      ],
      onFilter: (value, record) => record.prediction_type === value,
      width: 120
    },
    {
      title: '使用模型',
      dataIndex: 'model_name',
      key: 'model_name',
      ellipsis: true,
      width: 150
    },
    {
      title: '输入参数',
      dataIndex: 'input_summary',
      key: 'input_summary',
      render: (summary, record) => (
        <div>
          {record.prediction_type === 'day_ahead' ? (
            <div>
              <div>
                <Text type="secondary">目标日期: </Text>
                <Text>{summary.target_date !== 'N/A' ? moment(summary.target_date).format('YYYY-MM-DD') : 'N/A'}</Text>
              </div>
              <div>
                <Text type="secondary">温度: </Text>
                <Text>{summary.temperature !== 'N/A' ? `${summary.temperature}°C` : '自动生成'}</Text>
              </div>
            </div>
          ) : (
            <div>
              <div>
                <Text type="secondary">时间: </Text>
                <Text>{summary.timestamp !== 'N/A' ? moment(summary.timestamp).format('MM-DD HH:mm') : 'N/A'}</Text>
              </div>
              <div>
                <Text type="secondary">温度: </Text>
                <Text>{summary.temperature !== 'N/A' ? `${summary.temperature}°C` : 'N/A'}</Text>
              </div>
            </div>
          )}
        </div>
      ),
      width: 220
    },
    {
      title: '预测结果',
      dataIndex: 'prediction_summary',
      key: 'prediction_summary',
      render: (summary, record) => (
        <div>
          {record.prediction_type === 'single' ? (
            // 单点预测显示具体数值
            summary.predicted_load !== 'N/A' && typeof summary.predicted_load === 'number' ? (
              <Text strong>{summary.predicted_load.toFixed(2)} MW</Text>
            ) : (
              <Text strong>{summary.predicted_load}</Text>
            )
          ) : (
            // 批量预测和日前预测显示概要信息
            <Text>{summary.predicted_load}</Text>
          )}
        </div>
      ),
      width: 120
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
            size="small"
          >
            详情
          </Button>
        </Space>
      ),
      width: 100
    }
  ];

  return (
    <div>
      <Card 
        title={
          <Space>
            <HistoryOutlined />
            <span>预测历史记录</span>
            {isLoggedIn && (
              <Tag color="green" icon={<UserOutlined />}>
                已登录用户
              </Tag>
            )}
          </Space>
        }
        extra={
          <Space>
            <Button 
              icon={<DownloadOutlined />}
              onClick={handleExportHistory}
              disabled={history.length === 0}
            >
              导出记录
            </Button>
            <Button 
              icon={<ReloadOutlined />}
              onClick={loadHistory}
              loading={loading}
            >
              刷新
            </Button>
          </Space>
        }
      >
        {!isLoggedIn && (
          <Alert
            type="info"
            message="登录提示"
            description={
              <div>
                <p>🔐 预测历史记录功能需要登录账户才能使用</p>
                <p>💡 登录后，系统会自动保存您的预测记录，方便查看和管理</p>
                <p>📊 支持单点预测、批量预测、日前预测等所有类型的记录</p>
              </div>
            }
            action={
              <Button type="primary" icon={<LoginOutlined />} onClick={() => window.location.reload()}>
                前往登录
              </Button>
            }
            style={{ marginBottom: 16 }}
            showIcon
          />
        )}
        
        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px 0' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>
              <Text>正在加载历史记录...</Text>
            </div>
          </div>
        ) : isLoggedIn && history.length > 0 ? (
          <Table
            columns={columns}
            dataSource={history}
            rowKey="id"
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条记录`
            }}
            scroll={{ x: 800 }}
            size="middle"
          />
        ) : (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={
              isLoggedIn ? 
                "暂无预测历史记录" : 
                "请登录账户查看预测历史记录"
            }
          />
        )}
      </Card>

      {/* 详情模态框 */}
      <Modal
        title="预测记录详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {selectedRecord && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Title level={4}>基本信息</Title>
              <div style={{ background: '#fafafa', padding: '12px', borderRadius: '6px' }}>
                <div style={{ marginBottom: 8 }}>
                  <Text strong>预测ID: </Text>
                  <Text>{selectedRecord.id}</Text>
                </div>
                <div style={{ marginBottom: 8 }}>
                  <Text strong>预测时间: </Text>
                  <Text>{moment(selectedRecord.created_at).format('YYYY-MM-DD HH:mm:ss')}</Text>
                </div>
                <div style={{ marginBottom: 8 }}>
                  <Text strong>预测类型: </Text>
                  {getPredictionTypeTag(selectedRecord.prediction_type)}
                </div>
                <div>
                  <Text strong>使用模型: </Text>
                  <Text>{selectedRecord.model_name}</Text>
                </div>
              </div>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Title level={4}>输入参数</Title>
              <div style={{ background: '#fafafa', padding: '12px', borderRadius: '6px' }}>
                <pre style={{ margin: 0, fontFamily: 'Monaco, monospace', fontSize: '12px' }}>
                  {JSON.stringify(selectedRecord.input_summary, null, 2)}
                </pre>
              </div>
            </div>

            <div>
              <Title level={4}>预测结果</Title>
              <div style={{ background: '#fafafa', padding: '12px', borderRadius: '6px' }}>
                <pre style={{ margin: 0, fontFamily: 'Monaco, monospace', fontSize: '12px' }}>
                  {JSON.stringify(selectedRecord.prediction_summary, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default PredictionHistory;
