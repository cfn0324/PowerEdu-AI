import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Table,
  Upload,
  Space,
  Typography,
  Row,
  Col,
  Statistic,
  Select,
  message,
  Modal,
  Alert,
  Spin
} from 'antd';
import {
  UploadOutlined,
  DownloadOutlined,
  BarChartOutlined,
  FileExcelOutlined,
  DeleteOutlined,
  PlusOutlined
} from '@ant-design/icons';
import { predictionApi } from '../../service/prediction';

const { Title, Text } = Typography;
const { Option } = Select;

const BatchPrediction = () => {
  const [loading, setLoading] = useState(false);
  const [predicting, setPredicting] = useState(false);
  const [dataSource, setDataSource] = useState([]);
  const [results, setResults] = useState(null);
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);

  useEffect(() => {
    loadModels();
    generateSampleData();
  }, []);

  const loadModels = async () => {
    try {
      const response = await predictionApi.getModels();
      if (response.success) {
        setModels(response.data);
      }
    } catch (error) {
      message.error('加载模型列表失败');
    }
  };

  const generateSampleData = () => {
    const sampleData = [];
    const baseTime = new Date();
    
    for (let i = 0; i < 24; i++) {
      const timestamp = new Date(baseTime.getTime() + i * 60 * 60 * 1000);
      const hour = timestamp.getHours();
      
      // 根据时间生成合理的气象数据
      let baseTemp = 20 + 10 * Math.sin((hour - 6) * Math.PI / 12);
      baseTemp += (Math.random() - 0.5) * 4; // 添加随机变化
      
      const temperature = Math.round(baseTemp * 10) / 10;
      const humidity = Math.round((60 + (Math.random() - 0.5) * 30) * 10) / 10;
      const wind_speed = Math.round((5 + Math.random() * 5) * 10) / 10;
      const rainfall = Math.random() > 0.8 ? Math.round(Math.random() * 5 * 10) / 10 : 0;

      sampleData.push({
        key: i + 1,
        timestamp: timestamp.toISOString(),
        temperature,
        humidity,
        wind_speed,
        rainfall
      });
    }
    
    setDataSource(sampleData);
    message.success('已生成24小时示例数据');
  };

  const handlePredict = async () => {
    if (dataSource.length === 0) {
      message.warning('请先添加预测数据');
      return;
    }

    try {
      setPredicting(true);
      
      const predictData = {
        data_points: dataSource.map(item => ({
          timestamp: item.timestamp,
          temperature: item.temperature,
          humidity: item.humidity,
          wind_speed: item.wind_speed,
          rainfall: item.rainfall
        })),
        model_name: selectedModel
      };

      const response = await predictionApi.predictBatch(predictData);
      
      if (response.success) {
        setResults(response.data);
        message.success(`批量预测完成！共预测 ${response.data.predictions.length} 个时间点`);
      } else {
        message.error(response.error || '批量预测失败');
      }
    } catch (error) {
      console.error('批量预测失败:', error);
      message.error('预测请求失败，请稍后重试');
    } finally {
      setPredicting(false);
    }
  };

  const handleUpload = (file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        if (Array.isArray(data)) {
          const processedData = data.map((item, index) => ({
            key: index + 1,
            timestamp: item.timestamp || new Date().toISOString(),
            temperature: parseFloat(item.temperature) || 20,
            humidity: parseFloat(item.humidity) || 60,
            wind_speed: parseFloat(item.wind_speed) || 5,
            rainfall: parseFloat(item.rainfall) || 0
          }));
          setDataSource(processedData);
          message.success(`成功导入 ${processedData.length} 条数据`);
        } else {
          message.error('文件格式错误，请上传JSON数组格式');
        }
      } catch (error) {
        message.error('文件解析失败，请检查文件格式');
      }
    };
    reader.readAsText(file);
    return false; // 阻止自动上传
  };

  const handleExport = () => {
    if (!results) {
      message.warning('暂无预测结果可导出');
      return;
    }

    const exportData = results.predictions.map(pred => ({
      timestamp: pred.timestamp,
      predicted_load: pred.predicted_load,
      model_used: pred.model_used
    }));

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `batch_prediction_${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
    
    message.success('预测结果已导出');
  };

  const addDataRow = () => {
    const newRow = {
      key: dataSource.length + 1,
      timestamp: new Date().toISOString(),
      temperature: 25,
      humidity: 60,
      wind_speed: 5,
      rainfall: 0
    };
    setDataSource([...dataSource, newRow]);
  };

  const deleteDataRow = (key) => {
    setDataSource(dataSource.filter(item => item.key !== key));
  };

  const updateDataRow = (key, field, value) => {
    setDataSource(dataSource.map(item => 
      item.key === key ? { ...item, [field]: value } : item
    ));
  };

  const columns = [
    {
      title: '序号',
      dataIndex: 'key',
      width: 60,
      align: 'center'
    },
    {
      title: '时间',
      dataIndex: 'timestamp',
      width: 180,
      render: (text) => new Date(text).toLocaleString()
    },
    {
      title: '温度 (°C)',
      dataIndex: 'temperature',
      width: 100,
      render: (text, record) => (
        <input
          type="number"
          value={text}
          step="0.1"
          style={{ width: '100%', border: 'none' }}
          onChange={(e) => updateDataRow(record.key, 'temperature', parseFloat(e.target.value))}
        />
      )
    },
    {
      title: '湿度 (%)',
      dataIndex: 'humidity',
      width: 100,
      render: (text, record) => (
        <input
          type="number"
          value={text}
          step="1"
          style={{ width: '100%', border: 'none' }}
          onChange={(e) => updateDataRow(record.key, 'humidity', parseFloat(e.target.value))}
        />
      )
    },
    {
      title: '风速 (m/s)',
      dataIndex: 'wind_speed',
      width: 100,
      render: (text, record) => (
        <input
          type="number"
          value={text}
          step="0.1"
          style={{ width: '100%', border: 'none' }}
          onChange={(e) => updateDataRow(record.key, 'wind_speed', parseFloat(e.target.value))}
        />
      )
    },
    {
      title: '降雨量 (mm)',
      dataIndex: 'rainfall',
      width: 100,
      render: (text, record) => (
        <input
          type="number"
          value={text}
          step="0.1"
          style={{ width: '100%', border: 'none' }}
          onChange={(e) => updateDataRow(record.key, 'rainfall', parseFloat(e.target.value))}
        />
      )
    },
    {
      title: '操作',
      width: 80,
      render: (_, record) => (
        <Button
          type="text"
          icon={<DeleteOutlined />}
          onClick={() => deleteDataRow(record.key)}
          danger
          size="small"
        />
      )
    }
  ];

  const resultColumns = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      render: (text) => new Date(text).toLocaleString()
    },
    {
      title: '预测负荷 (MW)',
      dataIndex: 'predicted_load',
      render: (text) => text.toFixed(2),
      sorter: (a, b) => a.predicted_load - b.predicted_load
    },
    {
      title: '使用模型',
      dataIndex: 'model_used'
    }
  ];

  return (
    <div>
      <Row gutter={24}>
        <Col span={24}>
          <Card 
            title={
              <Space>
                <BarChartOutlined />
                <span>批量负荷预测</span>
              </Space>
            }
            extra={
              <Space>
                <Select
                  placeholder="选择预测模型"
                  value={selectedModel}
                  onChange={setSelectedModel}
                  style={{ width: 150 }}
                  allowClear
                >
                  {models.map((model) => (
                    <Option key={model.name} value={model.name}>
                      {model.name} {model.is_best && '(最佳)'}
                    </Option>
                  ))}
                </Select>
                <Upload
                  beforeUpload={handleUpload}
                  showUploadList={false}
                  accept=".json"
                >
                  <Button icon={<UploadOutlined />}>
                    导入数据
                  </Button>
                </Upload>
                <Button 
                  icon={<FileExcelOutlined />}
                  onClick={generateSampleData}
                >
                  生成示例
                </Button>
                <Button
                  type="primary"
                  icon={<BarChartOutlined />}
                  onClick={handlePredict}
                  loading={predicting}
                  disabled={dataSource.length === 0}
                >
                  批量预测
                </Button>
              </Space>
            }
          >
            <div style={{ marginBottom: 16 }}>
              <Alert
                type="info"
                message="批量预测说明"
                description="可以通过编辑表格直接修改数据，或者上传JSON格式的数据文件。支持同时预测多个时间点的电力负荷。"
                showIcon
              />
            </div>

            <div style={{ marginBottom: 16 }}>
              <Space>
                <Button icon={<PlusOutlined />} onClick={addDataRow}>
                  添加数据行
                </Button>
                <Text>当前数据点数：{dataSource.length}</Text>
              </Space>
            </div>

            <Table
              columns={columns}
              dataSource={dataSource}
              pagination={false}
              scroll={{ y: 300 }}
              size="small"
              bordered
            />
          </Card>
        </Col>
      </Row>

      {/* 预测结果 */}
      {predicting && (
        <Row gutter={24} style={{ marginTop: 24 }}>
          <Col span={24}>
            <Card>
              <div style={{ textAlign: 'center', padding: '50px 0' }}>
                <Spin size="large" />
                <div style={{ marginTop: 16 }}>
                  <Text>正在进行批量预测计算...</Text>
                </div>
              </div>
            </Card>
          </Col>
        </Row>
      )}

      {results && (
        <Row gutter={24} style={{ marginTop: 24 }}>
          <Col span={24}>
            <Card 
              title="预测结果"
              extra={
                <Button 
                  icon={<DownloadOutlined />}
                  onClick={handleExport}
                >
                  导出结果
                </Button>
              }
            >
              {/* 统计信息 */}
              <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={6}>
                  <Statistic
                    title="总预测点数"
                    value={results.summary.total_points}
                    suffix="个"
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="平均负荷"
                    value={results.visualization?.statistics?.average_load || 0}
                    precision={2}
                    suffix="MW"
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="峰值负荷"
                    value={results.visualization?.statistics?.peak_load || 0}
                    precision={2}
                    suffix="MW"
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="使用模型"
                    value={results.summary.model_used || 'N/A'}
                  />
                </Col>
              </Row>

              {/* 可视化图表 */}
              {results.visualization && (
                <div style={{ marginBottom: 16 }}>
                  <Title level={4}>负荷预测曲线</Title>
                  <div 
                    dangerouslySetInnerHTML={{ 
                      __html: results.visualization.html 
                    }}
                    style={{ 
                      border: '1px solid #d9d9d9',
                      borderRadius: '6px',
                      overflow: 'hidden'
                    }}
                  />
                </div>
              )}

              {/* 详细结果表格 */}
              <Title level={4}>详细预测结果</Title>
              <Table
                columns={resultColumns}
                dataSource={results.predictions}
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total) => `共 ${total} 条记录`
                }}
                scroll={{ y: 400 }}
                size="small"
              />
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
};

export default BatchPrediction;
