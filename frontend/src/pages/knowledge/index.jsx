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
  Statistic,
  Tag,
  Tooltip,
  Popconfirm
} from 'antd';
import {
  PlusOutlined,
  DatabaseOutlined,
  FileTextOutlined,
  MessageOutlined,
  SettingOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { knowledgeApi } from '../../service/knowledge';
import { useTokenStore } from '../../stores';

const { Title, Text, Paragraph } = Typography;

const KnowledgeHome = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [knowledgeBases, setKnowledgeBases] = useState([]);
  const [stats, setStats] = useState({});
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [form] = Form.useForm();
  
  // 获取用户登录状态
  const { auth } = useTokenStore();
  const isLoggedIn = !!auth?.token;

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // 并行加载知识库列表和统计信息
      const [kbResponse, statsResponse] = await Promise.all([
        knowledgeApi.getKnowledgeBases({ page: 1, size: 50 }),
        knowledgeApi.getSystemStats()
      ]);

      if (kbResponse.data?.success) {
        setKnowledgeBases(kbResponse.data.data?.items || []);
      }

      if (statsResponse.data?.success) {
        setStats(statsResponse.data.data?.stats || {});
      }
    } catch (error) {
      console.error('加载数据失败:', error);
      message.error('加载数据失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKnowledgeBase = async (values) => {
    try {
      const response = await knowledgeApi.createKnowledgeBase(values);
      
      if (response.data?.success) {
        message.success('知识库创建成功');
        setCreateModalVisible(false);
        form.resetFields();
        
        // 创建成功后跳转到文档管理页面进行文档上传
        const kbId = response.data.data.id;
        message.info('请上传初始文档到知识库', 3);
        setTimeout(() => {
          navigate(`/knowledge/documents/${kbId}`);
        }, 1000);
      } else {
        message.error(response.data?.error || '创建失败');
      }
    } catch (error) {
      console.error('创建知识库失败:', error);
      message.error('创建失败: ' + error.message);
    }
  };

  const handleDeleteKnowledgeBase = async (kbId) => {
    try {
      const response = await knowledgeApi.deleteKnowledgeBase(kbId);
      
      if (response.data?.success) {
        message.success('知识库删除成功');
        loadData();
      } else {
        message.error(response.data?.error || '删除失败');
      }
    } catch (error) {
      console.error('删除知识库失败:', error);
      message.error('删除失败: ' + error.message);
    }
  };

  const columns = [
    {
      title: '知识库名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <DatabaseOutlined style={{ color: '#1890ff' }} />
          <Text strong>{text}</Text>
        </Space>
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text) => (
        <Tooltip title={text}>
          <Text type="secondary">{text || '暂无描述'}</Text>
        </Tooltip>
      )
    },
    {
      title: '创建者',
      dataIndex: 'created_by',
      key: 'created_by',
      width: 120
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (text) => new Date(text).toLocaleString()
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (active) => (
        <Tag color={active ? 'green' : 'red'}>
          {active ? '激活' : '禁用'}
        </Tag>
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space>
          <Tooltip title="查看详情">
            <Button 
              type="text" 
              icon={<EyeOutlined />} 
              onClick={() => navigate(`/knowledge/detail/${record.id}`)}
            />
          </Tooltip>
          <Tooltip title="管理文档">
            <Button 
              type="text" 
              icon={<FileTextOutlined />} 
              onClick={() => navigate(`/knowledge/documents/${record.id}`)}
            />
          </Tooltip>
          <Tooltip title="智能问答">
            <Button 
              type="text" 
              icon={<MessageOutlined />} 
              onClick={() => navigate(`/knowledge/chat/${record.id}`)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button type="text" icon={<EditOutlined />} />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个知识库吗？"
            description="删除后将无法恢复，包括其中的所有文档和问答记录。"
            onConfirm={() => handleDeleteKnowledgeBase(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ];

  if (!isLoggedIn) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Title level={3}>请先登录</Title>
        <Text type="secondary">您需要登录后才能使用大模型知识库功能</Text>
        <div style={{ marginTop: 16 }}>
          <Button type="primary" onClick={() => navigate('/login')}>
            前往登录
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <DatabaseOutlined style={{ marginRight: 8 }} />
          大模型知识库
        </Title>
        <Paragraph type="secondary">
          基于检索增强生成（RAG）技术，为电力知识库提供智能问答能力。
          支持多种文档格式处理，提供精准的基于知识库的回答。
        </Paragraph>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="知识库数量"
              value={stats.knowledge_bases || 0}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="文档数量"
              value={stats.documents || 0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="问答会话"
              value={stats.qa_sessions || 0}
              prefix={<MessageOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="问答记录"
              value={stats.qa_records || 0}
              prefix={<MessageOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 知识库列表 */}
      <Card
        title={
          <Space>
            <DatabaseOutlined />
            <span>我的知识库</span>
          </Space>
        }
        extra={
          <Space>
            <Button 
              type="default" 
              icon={<SettingOutlined />}
              onClick={() => navigate('/knowledge/test')}
            >
              连接测试
            </Button>
            <Button 
              type="primary" 
              icon={<SettingOutlined />}
              onClick={() => navigate('/knowledge/settings')}
            >
              模型配置
            </Button>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              创建知识库
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={knowledgeBases}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个知识库`
          }}
          locale={{
            emptyText: (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <DatabaseOutlined style={{ fontSize: 48, color: '#ccc', marginBottom: 16 }} />
                <div>
                  <Text type="secondary">还没有创建知识库</Text>
                  <div style={{ marginTop: 8 }}>
                    <Button 
                      type="primary" 
                      icon={<PlusOutlined />}
                      onClick={() => setCreateModalVisible(true)}
                    >
                      创建第一个知识库
                    </Button>
                  </div>
                </div>
              </div>
            )
          }}
        />
      </Card>

      {/* 创建知识库弹窗 */}
      <Modal
        title="创建知识库"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateKnowledgeBase}
        >
          <Form.Item
            name="name"
            label="知识库名称"
            rules={[
              { required: true, message: '请输入知识库名称' },
              { max: 200, message: '名称不能超过200个字符' }
            ]}
          >
            <Input placeholder="请输入知识库名称，如：电力设备维护手册" />
          </Form.Item>

          <Form.Item
            name="description"
            label="知识库描述"
            rules={[
              { max: 1000, message: '描述不能超过1000个字符' }
            ]}
          >
            <Input.TextArea 
              rows={4}
              placeholder="请输入知识库描述，简要说明知识库的用途和内容范围"
            />
          </Form.Item>

          <div style={{ background: '#f6ffed', border: '1px solid #b7eb8f', borderRadius: 6, padding: 12, marginBottom: 16 }}>
            <Text type="secondary">
              📝 提示：知识库创建完成后，系统将跳转到文档管理页面，您可以上传知识库文档。
              支持格式：MD、PDF、TXT、DOCX、HTML
            </Text>
          </div>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => {
                setCreateModalVisible(false);
                form.resetFields();
              }}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                创建
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default KnowledgeHome;
