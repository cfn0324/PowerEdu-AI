import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Space,
  Typography,
  Descriptions,
  Tag,
  Spin,
  message,
  Breadcrumb,
  Row,
  Col,
  Divider,
  Statistic,
  Alert
} from 'antd';
import {
  ArrowLeftOutlined,
  FileTextOutlined,
  DatabaseOutlined,
  HomeOutlined,
  DownloadOutlined,
  EditOutlined,
  DeleteOutlined,
  CloudOutlined,
  CalendarOutlined,
  UserOutlined,
  FileOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { knowledgeApi } from '../../service/knowledge';
import { useTokenStore } from '../../stores';

const { Title, Text, Paragraph } = Typography;

const DocumentDetail = () => {
  const { docId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [document, setDocument] = useState(null);
  
  // 获取用户登录状态
  const { auth } = useTokenStore();
  const isLoggedIn = !!auth?.token;

  useEffect(() => {
    if (docId) {
      fetchDocumentDetail();
    }
  }, [docId]);

  const fetchDocumentDetail = async () => {
    try {
      setLoading(true);
      const response = await knowledgeApi.getDocument(docId);
      
      if (response.data?.success) {
        setDocument(response.data.data);
      } else {
        message.error(response.data?.error || '文档不存在');
        navigate('/knowledge');
      }
    } catch (error) {
      console.error('获取文档详情失败:', error);
      message.error('获取文档详情失败');
      navigate('/knowledge');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    message.info('下载功能待开发');
  };

  const handleEdit = () => {
    message.info('编辑功能待开发');
  };

  const handleDelete = async () => {
    try {
      const response = await knowledgeApi.deleteDocument(docId);
      
      if (response.data?.success) {
        message.success('文档删除成功');
        navigate(`/knowledge/documents/${document.knowledge_base.id}`);
      } else {
        message.error(response.data?.error || '删除失败');
      }
    } catch (error) {
      console.error('删除文档失败:', error);
      message.error('删除失败: ' + error.message);
    }
  };

  const getStatusConfig = (status) => {
    const statusMap = {
      'pending': { 
        color: 'orange', 
        text: '处理中', 
        icon: <ClockCircleOutlined />, 
        description: '文档正在处理中，请稍候...' 
      },
      'processing': { 
        color: 'blue', 
        text: '处理中', 
        icon: <ClockCircleOutlined />, 
        description: '文档正在处理中，请稍候...' 
      },
      'completed': { 
        color: 'green', 
        text: '已完成', 
        icon: <CheckCircleOutlined />, 
        description: '文档已成功处理并完成分块' 
      },
      'failed': { 
        color: 'red', 
        text: '失败', 
        icon: <ExclamationCircleOutlined />, 
        description: '文档处理失败，请重新上传' 
      }
    };
    return statusMap[status] || { color: 'default', text: status, icon: null, description: '' };
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (!isLoggedIn) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Title level={3}>请先登录</Title>
        <Text type="secondary">您需要登录后才能查看文档详情</Text>
        <div style={{ marginTop: 16 }}>
          <Button type="primary" onClick={() => navigate('/login')}>
            前往登录
          </Button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!document) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Typography.Text type="secondary">文档不存在</Typography.Text>
        </div>
      </Card>
    );
  }

  const statusConfig = getStatusConfig(document.status);

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
          <span onClick={() => navigate(`/knowledge/documents/${document.knowledge_base.id}`)} style={{ cursor: 'pointer' }}>
            {document.knowledge_base.name}
          </span>
        </Breadcrumb.Item>
        <Breadcrumb.Item>{document.title}</Breadcrumb.Item>
      </Breadcrumb>

      {/* 返回按钮 */}
      <div style={{ marginBottom: '20px' }}>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate(`/knowledge/documents/${document.knowledge_base.id}`)}
        >
          返回文档列表
        </Button>
      </div>

      {/* 文档基本信息 */}
      <Card style={{ marginBottom: '20px' }}>
        <Row justify="space-between" align="top">
          <Col span={18}>
            <Title level={2} style={{ marginBottom: '16px' }}>
              <FileTextOutlined style={{ marginRight: '8px' }} />
              {document.title}
            </Title>
            <Paragraph type="secondary" style={{ fontSize: '16px' }}>
              所属知识库：{document.knowledge_base.name}
            </Paragraph>
          </Col>
          <Col span={6} style={{ textAlign: 'right' }}>
            <Space direction="vertical" size="middle">
              <Button 
                type="primary" 
                icon={<DownloadOutlined />}
                onClick={handleDownload}
              >
                下载文档
              </Button>
              <Button 
                icon={<EditOutlined />}
                onClick={handleEdit}
              >
                编辑文档
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 文档详细信息 */}
      <Row gutter={[20, 20]}>
        <Col span={16}>
          <Card title="文档信息">
            <Descriptions column={2} bordered>
              <Descriptions.Item label="文档标题" span={2}>
                {document.title}
              </Descriptions.Item>
              <Descriptions.Item label="原文件名" span={2}>
                {document.file_name}
              </Descriptions.Item>
              <Descriptions.Item label="文件类型">
                <Tag color="blue">{document.file_type?.toUpperCase()}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="文件大小">
                {formatFileSize(document.file_size)}
              </Descriptions.Item>
              <Descriptions.Item label="处理状态">
                <Tag color={statusConfig.color} icon={statusConfig.icon}>
                  {statusConfig.text}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="分块数量">
                {document.chunk_count || 0} 个
              </Descriptions.Item>
              <Descriptions.Item label="上传者">
                <UserOutlined style={{ marginRight: 4 }} />
                {document.uploaded_by || '未知'}
              </Descriptions.Item>
              <Descriptions.Item label="上传时间">
                <CalendarOutlined style={{ marginRight: 4 }} />
                {document.uploaded_at ? new Date(document.uploaded_at).toLocaleString() : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="处理时间" span={2}>
                <CalendarOutlined style={{ marginRight: 4 }} />
                {document.processed_at ? new Date(document.processed_at).toLocaleString() : '-'}
              </Descriptions.Item>
            </Descriptions>

            {/* 状态说明 */}
            {statusConfig.description && (
              <div style={{ marginTop: '16px' }}>
                <Alert
                  message={statusConfig.description}
                  type={document.status === 'completed' ? 'success' : 
                        document.status === 'failed' ? 'error' : 'info'}
                  showIcon
                />
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
                  title="文档分块数"
                  value={document.chunk_count || 0}
                  prefix={<FileOutlined />}
                  suffix="个"
                />
              </Col>
              <Col span={24}>
                <Statistic
                  title="文件大小"
                  value={formatFileSize(document.file_size)}
                  prefix={<CloudOutlined />}
                />
              </Col>
            </Row>
          </Card>

          {/* 操作区域 */}
          <Card title="操作">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button 
                type="primary" 
                icon={<DownloadOutlined />} 
                block
                onClick={handleDownload}
              >
                下载文档
              </Button>
              <Button 
                icon={<EditOutlined />} 
                block
                onClick={handleEdit}
              >
                编辑文档
              </Button>
              <Divider />
              <Button 
                danger 
                icon={<DeleteOutlined />} 
                block
                onClick={handleDelete}
              >
                删除文档
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DocumentDetail;
