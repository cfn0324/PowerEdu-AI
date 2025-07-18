import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Space,
  Typography,
  Table,
  Modal,
  Form,
  Input,
  message,
  Select,
  InputNumber,
  Switch,
  Tag,
  Tooltip,
  Popconfirm,
  Breadcrumb
} from 'antd';
import {
  HomeOutlined,
  DatabaseOutlined,
  SettingOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { knowledgeApi } from '../../service/knowledge';

const { Title, Paragraph } = Typography;
const { Option } = Select;

const ModelSettings = () => {
  const [modelConfigs, setModelConfigs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [currentConfig, setCurrentConfig] = useState(null);
  const [testLoading, setTestLoading] = useState({});
  const [form] = Form.useForm();
  const navigate = useNavigate();

  // 模型类型选项
  const modelTypes = [
    { value: 'api', label: 'API模式' },
    { value: 'local', label: '本地模式' }
  ];

  useEffect(() => {
    fetchModelConfigs();
  }, []);

  const fetchModelConfigs = async () => {
    setLoading(true);
    try {
      const response = await knowledgeApi.getModelConfigs();
      
      let configs = [];
      if (response.data?.success) {
        configs = response.data.data || [];
      } else if (Array.isArray(response.data)) {
        configs = response.data;
      } else if (response.data?.data && Array.isArray(response.data.data)) {
        configs = response.data.data;
      }
      
      setModelConfigs(Array.isArray(configs) ? configs : []);
    } catch (error) {
      console.error('获取模型配置失败:', error);
      message.error('获取模型配置失败');
      setModelConfigs([]); // 确保设置为空数组
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (values) => {
    try {
      const response = await knowledgeApi.createModelConfig(values);
      if (response.data?.success) {
        message.success('模型配置创建成功');
        setCreateModalVisible(false);
        form.resetFields();
        fetchModelConfigs();
      } else {
        message.error(response.data?.error || '创建失败');
      }
    } catch (error) {
      console.error('创建模型配置失败:', error);
      message.error('创建模型配置失败');
    }
  };

  const handleEdit = (config) => {
    setCurrentConfig(config);
    form.setFieldsValue(config);
    setEditModalVisible(true);
  };

  const handleUpdate = async (values) => {
    try {
      const response = await knowledgeApi.updateModelConfig(currentConfig.id, values);
      if (response.data?.success) {
        message.success('模型配置更新成功');
        setEditModalVisible(false);
        form.resetFields();
        setCurrentConfig(null);
        fetchModelConfigs();
      } else {
        message.error(response.data?.error || '更新失败');
      }
    } catch (error) {
      console.error('更新模型配置失败:', error);
      message.error('更新模型配置失败');
    }
  };

  const handleDelete = async (configId) => {
    try {
      const response = await knowledgeApi.deleteModelConfig(configId);
      if (response.data?.success) {
        message.success('模型配置删除成功');
        fetchModelConfigs();
      } else {
        message.error(response.data?.error || '删除失败');
      }
    } catch (error) {
      console.error('删除模型配置失败:', error);
      message.error('删除模型配置失败');
    }
  };

  const handleTest = async (configId) => {
    setTestLoading(prev => ({ ...prev, [configId]: true }));
    try {
      const response = await knowledgeApi.testModelConfig(configId);
      if (response.data?.success) {
        message.success('模型测试成功');
        Modal.success({
          title: '模型测试结果',
          content: (
            <div>
              <p><strong>状态：</strong>{response.data.data.test_result}</p>
              <p><strong>响应时间：</strong>{response.data.data.response_time}ms</p>
              <p><strong>响应内容：</strong>{response.data.data.response}</p>
            </div>
          ),
        });
      } else {
        message.error(response.data?.error || '测试失败');
      }
    } catch (error) {
      console.error('测试模型配置失败:', error);
      message.error('测试模型配置失败');
    } finally {
      setTestLoading(prev => ({ ...prev, [configId]: false }));
    }
  };

  const columns = [
    {
      title: '配置名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <span>{text}</span>
          {record.is_default && <Tag color="gold">默认</Tag>}
        </Space>
      )
    },
    {
      title: '模型类型',
      dataIndex: 'model_type',
      key: 'model_type',
      render: (text) => {
        const type = modelTypes.find(t => t.value === text);
        return type ? type.label : text;
      }
    },
    {
      title: '模型名称',
      dataIndex: 'model_name',
      key: 'model_name'
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '启用' : '禁用'}
        </Tag>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => text ? new Date(text).toLocaleString() : '-'
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Tooltip title="测试连接">
            <Button
              type="text"
              icon={<PlayCircleOutlined />}
              loading={testLoading[record.id]}
              onClick={() => handleTest(record.id)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个模型配置吗？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Tooltip title="删除">
              <Button
                type="text"
                icon={<DeleteOutlined />}
                danger
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ];

  const modalForm = (
    <Form
      form={form}
      layout="vertical"
      onFinish={editModalVisible ? handleUpdate : handleCreate}
    >
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="name"
            label="配置名称"
            rules={[{ required: true, message: '请输入配置名称' }]}
          >
            <Input placeholder="请输入配置名称" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name="model_type"
            label="模型类型"
            rules={[{ required: true, message: '请选择模型类型' }]}
          >
            <Select placeholder="请选择模型类型">
              {modelTypes.map(type => (
                <Option key={type.value} value={type.value}>
                  {type.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
      </Row>

      <Form.Item
        name="description"
        label="配置描述"
      >
        <Input.TextArea rows={2} placeholder="请输入配置描述（可选）" />
      </Form.Item>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="model_name"
            label="模型名称"
            rules={[{ required: true, message: '请输入模型名称' }]}
          >
            <Input placeholder="如：gpt-3.5-turbo" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name="model_path"
            label="本地模型路径"
          >
            <Input placeholder="本地模型文件路径（可选）" />
          </Form.Item>
        </Col>
      </Row>

      <Form.Item
        name="api_key"
        label="API密钥"
        rules={[{ required: true, message: '请输入API密钥' }]}
      >
        <Input.Password placeholder="请输入API密钥" />
      </Form.Item>

      <Form.Item
        name="api_base_url"
        label="API基础URL"
        rules={[{ required: true, message: '请输入API基础URL' }]}
      >
        <Input placeholder="请输入API基础URL" />
      </Form.Item>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item
            name="max_tokens"
            label="最大Token数"
            initialValue={4096}
          >
            <InputNumber min={100} max={32768} style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item
            name="temperature"
            label="温度参数"
            initialValue={0.7}
          >
            <InputNumber min={0} max={2} step={0.1} style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item
            name="is_default"
            label="设为默认"
            valuePropName="checked"
            initialValue={false}
          >
            <Switch />
          </Form.Item>
        </Col>
      </Row>
    </Form>
  );

  return (
    <div style={{ padding: '20px' }}>
      {/* 面包屑导航 */}
      <Breadcrumb style={{ marginBottom: '20px' }}>
        <Breadcrumb.Item>
          <HomeOutlined />
          <span onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>首页</span>
        </Breadcrumb.Item>
        <Breadcrumb.Item>
          <DatabaseOutlined />
          <span onClick={() => navigate('/knowledge')} style={{ cursor: 'pointer' }}>知识库</span>
        </Breadcrumb.Item>
        <Breadcrumb.Item>
          <SettingOutlined />
          模型配置
        </Breadcrumb.Item>
      </Breadcrumb>

      {/* 页面标题和说明 */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <SettingOutlined style={{ marginRight: '8px' }} />
          模型配置管理
        </Title>
        <Paragraph type="secondary">
          配置和管理大语言模型，支持OpenAI、Claude、ChatGLM等多种模型。
        </Paragraph>
      </div>

      {/* 模型配置列表 */}
      <Card
        title="模型配置列表"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              form.resetFields();
              setCreateModalVisible(true);
            }}
          >
            新增配置
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={Array.isArray(modelConfigs) ? modelConfigs : []}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`
          }}
        />
      </Card>

      {/* 创建模型配置弹窗 */}
      <Modal
        title="新增模型配置"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          form.resetFields();
        }}
        footer={[
          <Button key="cancel" onClick={() => setCreateModalVisible(false)}>
            取消
          </Button>,
          <Button key="submit" type="primary" onClick={() => form.submit()}>
            创建
          </Button>
        ]}
        width={800}
        destroyOnClose
      >
        {modalForm}
      </Modal>

      {/* 编辑模型配置弹窗 */}
      <Modal
        title="编辑模型配置"
        open={editModalVisible}
        onCancel={() => {
          setEditModalVisible(false);
          form.resetFields();
          setCurrentConfig(null);
        }}
        footer={[
          <Button key="cancel" onClick={() => setEditModalVisible(false)}>
            取消
          </Button>,
          <Button key="submit" type="primary" onClick={() => form.submit()}>
            更新
          </Button>
        ]}
        width={800}
        destroyOnClose
      >
        {modalForm}
      </Modal>
    </div>
  );
};

export default ModelSettings;
