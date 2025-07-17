import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Space,
  Typography,
  Table,
  Modal,
  Upload,
  message,
  Tag,
  Tooltip,
  Popconfirm,
  Progress,
  Divider,
  Alert
} from 'antd';
import {
  UploadOutlined,
  FileTextOutlined,
  DeleteOutlined,
  DownloadOutlined,
  EyeOutlined,
  CloudUploadOutlined,
  InboxOutlined,
  ArrowLeftOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { knowledgeApi } from '../../service/knowledge';
import { useTokenStore } from '../../stores';

const { Title, Text } = Typography;
const { Dragger } = Upload;

const DocumentManage = () => {
  const { kbId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [knowledgeBase, setKnowledgeBase] = useState(null);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [fileList, setFileList] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  // 获取用户登录状态
  const { auth } = useTokenStore();
  const isLoggedIn = !!auth?.token;

  useEffect(() => {
    if (kbId) {
      loadData();
    }
  }, [kbId]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // 并行加载知识库信息和文档列表
      const [kbResponse, docsResponse] = await Promise.all([
        knowledgeApi.getKnowledgeBase(kbId),
        knowledgeApi.getDocuments(kbId, { page: 1, size: 50 })
      ]);

      if (kbResponse.data?.success) {
        setKnowledgeBase(kbResponse.data.data?.knowledge_base);
      }

      if (docsResponse.data?.success) {
        setDocuments(docsResponse.data.data?.items || []);
      }
    } catch (error) {
      console.error('加载数据失败:', error);
      message.error('加载数据失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning('请选择要上传的文件');
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);

      const formData = new FormData();
      fileList.forEach(file => {
        formData.append('files', file.originFileObj);
      });

      // 使用批量上传接口
      const response = await knowledgeApi.batchUploadDocuments(kbId, formData, {
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        }
      });
      
      if (response.data?.success) {
        const { summary, results } = response.data.data;
        
        if (summary.failed > 0) {
          // 显示部分失败的详细信息
          const failedFiles = results.filter(r => !r.success);
          message.warning(`上传完成：成功 ${summary.success} 个，失败 ${summary.failed} 个`);
          console.log('失败文件:', failedFiles);
        } else {
          message.success(`成功上传 ${summary.success} 个文件`);
        }
        
        setUploadModalVisible(false);
        setFileList([]);
        setUploadProgress(0);
        loadData();
      } else {
        message.error(response.data?.error || '上传失败');
      }
    } catch (error) {
      console.error('上传文件失败:', error);
      message.error('上传失败: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDocument = async (docId) => {
    try {
      const response = await knowledgeApi.deleteDocument(docId);
      
      if (response.data?.success) {
        message.success('文档删除成功');
        loadData();
      } else {
        message.error(response.data?.error || '删除失败');
      }
    } catch (error) {
      console.error('删除文档失败:', error);
      message.error('删除失败: ' + error.message);
    }
  };

  const uploadProps = {
    multiple: true,
    fileList,
    beforeUpload: (file) => {
      // 检查文件类型
      const allowedTypes = ['.md', '.pdf', '.txt', '.docx', '.html'];
      const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
      
      if (!allowedTypes.includes(fileExtension)) {
        message.error(`不支持的文件类型: ${fileExtension}`);
        return false;
      }
      
      // 检查文件大小 (限制为10MB)
      if (file.size > 10 * 1024 * 1024) {
        message.error('文件大小不能超过10MB');
        return false;
      }
      
      return false; // 阻止自动上传
    },
    onChange: ({ fileList: newFileList }) => {
      setFileList(newFileList);
    },
    onRemove: (file) => {
      const index = fileList.indexOf(file);
      const newFileList = fileList.slice();
      newFileList.splice(index, 1);
      setFileList(newFileList);
    }
  };

  const columns = [
    {
      title: '文档名称',
      dataIndex: 'title',
      key: 'title',
      render: (text, record) => (
        <Space>
          <FileTextOutlined style={{ color: '#1890ff' }} />
          <div>
            <div><Text strong>{text}</Text></div>
            <div><Text type="secondary" size="small">{record.file_name}</Text></div>
          </div>
        </Space>
      )
    },
    {
      title: '文件类型',
      dataIndex: 'file_type',
      key: 'file_type',
      width: 100,
      render: (type) => (
        <Tag color="blue">{type?.toUpperCase()}</Tag>
      )
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 120,
      render: (size) => {
        if (size < 1024) return `${size} B`;
        if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
        return `${(size / (1024 * 1024)).toFixed(1)} MB`;
      }
    },
    {
      title: '处理状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => {
        const statusMap = {
          'pending': { color: 'orange', text: '处理中' },
          'completed': { color: 'green', text: '已完成' },
          'failed': { color: 'red', text: '失败' }
        };
        const statusInfo = statusMap[status] || { color: 'default', text: status };
        return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>;
      }
    },
    {
      title: '分块数量',
      dataIndex: 'chunk_count',
      key: 'chunk_count',
      width: 100,
      render: (count) => count || '-'
    },
    {
      title: '上传时间',
      dataIndex: 'uploaded_at',
      key: 'uploaded_at',
      width: 160,
      render: (text) => new Date(text).toLocaleString()
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Tooltip title="查看详情">
            <Button type="text" icon={<EyeOutlined />} size="small" />
          </Tooltip>
          <Tooltip title="下载文件">
            <Button type="text" icon={<DownloadOutlined />} size="small" />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个文档吗？"
            description="删除后将无法恢复，同时会从向量数据库中移除相关数据。"
            onConfirm={() => handleDeleteDocument(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="text" danger icon={<DeleteOutlined />} size="small" />
          </Popconfirm>
        </Space>
      )
    }
  ];

  if (!isLoggedIn) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Title level={3}>请先登录</Title>
        <Text type="secondary">您需要登录后才能管理知识库文档</Text>
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
        <Space style={{ marginBottom: 16 }}>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={() => navigate('/knowledge')}
          >
            返回知识库
          </Button>
        </Space>
        
        <Title level={2}>
          <FileTextOutlined style={{ marginRight: 8 }} />
          文档管理
        </Title>
        
        {knowledgeBase && (
          <div>
            <Text strong style={{ fontSize: 16 }}>{knowledgeBase.name}</Text>
            <br />
            <Text type="secondary">{knowledgeBase.description}</Text>
          </div>
        )}
      </div>

      {/* 上传提示 */}
      {documents.length === 0 && (
        <Alert
          message="知识库为空"
          description="请上传文档来构建您的知识库。支持 MD、PDF、TXT、DOCX、HTML 格式的文件。"
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
          action={
            <Button 
              type="primary" 
              icon={<UploadOutlined />}
              onClick={() => setUploadModalVisible(true)}
            >
              立即上传
            </Button>
          }
        />
      )}

      {/* 文档列表 */}
      <Card
        title={
          <Space>
            <FileTextOutlined />
            <span>文档列表</span>
            <Text type="secondary">({documents.length} 个文档)</Text>
          </Space>
        }
        extra={
          <Button 
            type="primary" 
            icon={<UploadOutlined />}
            onClick={() => setUploadModalVisible(true)}
          >
            上传文档
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={documents}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个文档`
          }}
          locale={{
            emptyText: (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <FileTextOutlined style={{ fontSize: 48, color: '#ccc', marginBottom: 16 }} />
                <div>
                  <Text type="secondary">还没有上传文档</Text>
                  <div style={{ marginTop: 8 }}>
                    <Button 
                      type="primary" 
                      icon={<UploadOutlined />}
                      onClick={() => setUploadModalVisible(true)}
                    >
                      上传第一个文档
                    </Button>
                  </div>
                </div>
              </div>
            )
          }}
        />
      </Card>

      {/* 上传文档弹窗 */}
      <Modal
        title="上传文档"
        open={uploadModalVisible}
        onCancel={() => {
          setUploadModalVisible(false);
          setFileList([]);
          setUploadProgress(0);
        }}
        footer={null}
        width={600}
      >
        <div style={{ marginBottom: 16 }}>
          <Text type="secondary">
            支持格式：MD、PDF、TXT、DOCX、HTML，单个文件不超过10MB
          </Text>
        </div>
        
        <Dragger {...uploadProps} style={{ marginBottom: 16 }}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持单个或批量上传。严禁上传公司数据或其他禁止文件。
          </p>
        </Dragger>

        {uploading && (
          <div style={{ marginBottom: 16 }}>
            <Text>上传进度:</Text>
            <Progress percent={uploadProgress} />
          </div>
        )}

        <div style={{ textAlign: 'right' }}>
          <Space>
            <Button 
              onClick={() => {
                setUploadModalVisible(false);
                setFileList([]);
                setUploadProgress(0);
              }}
              disabled={uploading}
            >
              取消
            </Button>
            <Button 
              type="primary" 
              onClick={handleUpload}
              loading={uploading}
              disabled={fileList.length === 0}
              icon={<CloudUploadOutlined />}
            >
              {uploading ? '上传中...' : `上传 (${fileList.length})`}
            </Button>
          </Space>
        </div>
      </Modal>
    </div>
  );
};

export default DocumentManage;
