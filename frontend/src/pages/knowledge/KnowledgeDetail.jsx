import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Space,
  Typography,
  Descriptions,
  Tag,
  Statistic,
  Breadcrumb,
  message,
  Spin
} from 'antd';
import {
  HomeOutlined,
  DatabaseOutlined,
  FileTextOutlined,
  MessageOutlined,
  CalendarOutlined,
  UserOutlined,
  EditOutlined
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { knowledgeApi } from '../../service/knowledge';

const { Title, Paragraph } = Typography;

const KnowledgeDetail = () => {
  const [knowledgeBase, setKnowledgeBase] = useState(null);
  const [kbStats, setKbStats] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { kbId } = useParams();

  useEffect(() => {
    fetchKnowledgeBaseDetail();
    fetchDocuments();
  }, [kbId]);

  const fetchKnowledgeBaseDetail = async () => {
    try {
      const response = await knowledgeApi.getKnowledgeBase(kbId);
      console.log('获取知识库详情响应:', response.data);
      if (response.data?.success) {
        setKnowledgeBase(response.data.data.knowledge_base);
        setKbStats(response.data.data);
      } else {
        message.error(response.data?.error || '知识库不存在');
        navigate('/knowledge');
      }
    } catch (error) {
      console.error('获取知识库详情失败:', error);
      message.error('获取知识库详情失败');
      navigate('/knowledge');
    } finally {
      setLoading(false);
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await knowledgeApi.getDocuments(kbId);
      console.log('获取文档列表响应:', response.data);
      if (response.data?.success) {
        setDocuments(response.data.data.items || []);
      } else {
        console.error('获取文档列表失败:', response.data?.error);
        setDocuments([]);
      }
    } catch (error) {
      console.error('获取文档列表失败:', error);
      setDocuments([]);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!knowledgeBase) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Typography.Text type="secondary">知识库不存在</Typography.Text>
        </div>
      </Card>
    );
  }

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
        <Breadcrumb.Item>{knowledgeBase.name}</Breadcrumb.Item>
      </Breadcrumb>

      {/* 知识库基本信息 */}
      <Card style={{ marginBottom: '20px' }}>
        <Row justify="space-between" align="top">
          <Col span={18}>
            <Title level={2} style={{ marginBottom: '16px' }}>
              <DatabaseOutlined style={{ marginRight: '8px' }} />
              {knowledgeBase.name}
            </Title>
            <Paragraph 
              style={{ fontSize: '16px', color: '#666', marginBottom: '24px' }}
            >
              {knowledgeBase.description || '暂无描述'}
            </Paragraph>
          </Col>
          <Col span={6} style={{ textAlign: 'right' }}>
            <Space direction="vertical" size="large">
              <Button 
                type="primary" 
                icon={<EditOutlined />}
                onClick={() => {
                  // 这里可以添加编辑功能
                  message.info('编辑功能待开发');
                }}
              >
                编辑知识库
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 知识库详细信息 */}
      <Row gutter={[16, 16]}>
        <Col span={16}>
          <Card title="知识库信息" style={{ marginBottom: '20px' }}>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="知识库名称" span={2}>
                {knowledgeBase.name}
              </Descriptions.Item>
              <Descriptions.Item label="描述" span={2}>
                {knowledgeBase.description || '暂无描述'}
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={knowledgeBase.is_active ? 'green' : 'red'}>
                  {knowledgeBase.is_active ? '启用' : '禁用'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                <CalendarOutlined style={{ marginRight: '4px' }} />
                {new Date(knowledgeBase.created_at).toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label="更新时间" span={2}>
                {new Date(knowledgeBase.updated_at).toLocaleString()}
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* 文档列表预览 */}
          <Card 
            title="文档列表" 
            extra={
              <Button 
                type="link" 
                onClick={() => navigate(`/knowledge/documents/${kbId}`)}
              >
                查看全部
              </Button>
            }
          >
            {documents.length > 0 ? (
              <div>
                {documents.slice(0, 5).map((doc, index) => (
                  <div 
                    key={doc.id} 
                    style={{ 
                      padding: '12px 0', 
                      borderBottom: index < Math.min(4, documents.length - 1) ? '1px solid #f0f0f0' : 'none' 
                    }}
                  >
                    <Space>
                      <FileTextOutlined />
                      <span>{doc.file_name || `文档${doc.id}`}</span>
                      <Tag size="small">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </Tag>
                    </Space>
                  </div>
                ))}
                {documents.length > 5 && (
                  <div style={{ textAlign: 'center', marginTop: '16px' }}>
                    <Typography.Text type="secondary">
                      还有 {documents.length - 5} 个文档...
                    </Typography.Text>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '20px' }}>
                <Typography.Text type="secondary">暂无文档</Typography.Text>
              </div>
            )}
          </Card>
        </Col>

        <Col span={8}>
          {/* 统计信息 */}
          <Card title="统计信息" style={{ marginBottom: '20px' }}>
            <Row gutter={16}>
              <Col span={24} style={{ marginBottom: '16px' }}>
                <Statistic
                  title="文档数量"
                  value={kbStats?.document_count || 0}
                  prefix={<FileTextOutlined />}
                  suffix="个"
                />
              </Col>
              <Col span={24} style={{ marginBottom: '16px' }}>
                <Statistic
                  title="向量块数量"
                  value={kbStats?.stats?.total_chunks || 0}
                  prefix={<DatabaseOutlined />}
                  suffix="个"
                />
              </Col>
              <Col span={24}>
                <Statistic
                  title="知识库状态"
                  value={knowledgeBase?.is_active ? '正常运行' : '已禁用'}
                  valueStyle={{ 
                    color: knowledgeBase?.is_active ? '#3f8600' : '#cf1322' 
                  }}
                />
              </Col>
            </Row>
          </Card>

          {/* 快速操作 */}
          <Card title="快速操作">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button 
                type="primary" 
                icon={<FileTextOutlined />} 
                block
                onClick={() => navigate(`/knowledge/documents/${kbId}`)}
              >
                管理文档
              </Button>
              <Button 
                icon={<MessageOutlined />} 
                block
                onClick={() => navigate(`/knowledge/chat/${kbId}`)}
              >
                智能问答
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default KnowledgeDetail;
