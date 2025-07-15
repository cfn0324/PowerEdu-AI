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
  Modal
} from 'antd';
import {
  HistoryOutlined,
  EyeOutlined,
  DeleteOutlined,
  ReloadOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import moment from 'moment';
import { predictionApi } from '../../service/prediction';

const { Title, Text } = Typography;

const PredictionHistory = () => {
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const response = await predictionApi.getPredictionHistory();
      if (response.success) {
        setHistory(response.data);
      }
    } catch (error) {
      message.error('加载预测历史失败');
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
      render: (summary) => (
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
      ),
      width: 200
    },
    {
      title: '预测结果',
      dataIndex: 'prediction_summary',
      key: 'prediction_summary',
      render: (summary) => (
        <div>
          {summary.predicted_load !== 'N/A' ? (
            <Text strong>{summary.predicted_load} MW</Text>
          ) : (
            <Text>批量结果</Text>
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
        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px 0' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>
              <Text>正在加载历史记录...</Text>
            </div>
          </div>
        ) : history.length > 0 ? (
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
            description="暂无预测历史记录"
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
