import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Input,
  Button,
  Space,
  Typography,
  List,
  Avatar,
  Tag,
  Spin,
  message,
  Rate,
  Modal,
  Form,
  Select,
  Tooltip,
  Divider,
  Alert
} from 'antd';
import {
  SendOutlined,
  MessageOutlined,
  RobotOutlined,
  UserOutlined,
  LikeOutlined,
  DislikeOutlined,
  SettingOutlined,
  DatabaseOutlined,
  ClockCircleOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import { knowledgeApi } from '../../service/knowledge';
import { useTokenStore } from '../../stores';
import { useParams } from 'react-router-dom';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const KnowledgeChat = () => {
  const { kbId } = useParams();
  const [loading, setLoading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [knowledgeBase, setKnowledgeBase] = useState(null);
  const [modelConfigs, setModelConfigs] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [question, setQuestion] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [feedbackModalVisible, setFeedbackModalVisible] = useState(false);
  const [currentQARecord, setCurrentQARecord] = useState(null);
  const [form] = Form.useForm();
  const chatContainerRef = useRef(null);
  
  // 获取用户登录状态
  const { auth } = useTokenStore();
  const isLoggedIn = !!auth?.token;

  useEffect(() => {
    if (kbId && isLoggedIn) {
      loadInitialData();
    }
  }, [kbId, isLoggedIn]);

  useEffect(() => {
    // 自动滚动到底部
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // 并行加载知识库信息和模型配置
      const [kbResponse, modelsResponse] = await Promise.all([
        knowledgeApi.getKnowledgeBase(kbId),
        knowledgeApi.getModelConfigs()
      ]);

      if (kbResponse.data?.success) {
        setKnowledgeBase(kbResponse.data.data.knowledge_base);
      } else {
        message.error('知识库不存在或已被删除');
        return;
      }

      if (modelsResponse.data?.success) {
        const configs = modelsResponse.data.data || [];
        setModelConfigs(configs);
        
        // 自动选择默认模型
        const defaultModel = configs.find(config => config.is_default);
        if (defaultModel) {
          setSelectedModel(defaultModel.id);
        }
      }
    } catch (error) {
      console.error('加载初始数据失败:', error);
      message.error('加载数据失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!question.trim()) {
      message.warning('请输入问题');
      return;
    }

    try {
      setAsking(true);
      
      // 添加用户问题到聊天历史
      const userMessage = {
        id: Date.now(),
        type: 'user',
        content: question,
        timestamp: new Date()
      };
      
      setChatHistory(prev => [...prev, userMessage]);
      const currentQuestion = question;
      setQuestion('');

      // 调用问答API
      const response = await knowledgeApi.askQuestion({
        kb_id: parseInt(kbId),
        question: currentQuestion,
        session_id: sessionId,
        model_config_id: selectedModel,
        top_k: 5,
        threshold: 0.5
      });

      if (response.data?.success) {
        const { session_id, answer, sources, model_used, response_time, qa_record_id } = response.data.data;
        
        // 更新会话ID
        if (!sessionId) {
          setSessionId(session_id);
        }

        // 添加AI回答到聊天历史
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: answer,
          sources: sources || [],
          model_used,
          response_time,
          qa_record_id,
          timestamp: new Date()
        };
        
        setChatHistory(prev => [...prev, aiMessage]);
      } else {
        const errorMsg = response.data?.error || '问答失败';
        console.error('问答失败:', errorMsg);
        
        // 提供更详细的错误信息
        let userFriendlyError = '抱歉，我现在无法回答您的问题，请稍后再试。';
        if (errorMsg.includes('model_used')) {
          userFriendlyError = '系统配置错误，请联系管理员检查模型配置。';
        } else if (errorMsg.includes('知识库')) {
          userFriendlyError = '知识库访问失败，请检查知识库是否存在。';
        } else if (errorMsg.includes('权限')) {
          userFriendlyError = '没有访问权限，请重新登录。';
        }
        
        message.error(userFriendlyError);
        
        // 添加错误消息
        const errorMessage = {
          id: Date.now() + 1,
          type: 'error',
          content: userFriendlyError,
          timestamp: new Date()
        };
        
        setChatHistory(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('问答失败:', error);
      message.error('问答失败: ' + error.message);
      
      // 添加错误消息
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: '网络错误，请检查连接后重试。',
        timestamp: new Date()
      };
      
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setAsking(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAskQuestion();
    }
  };

  const handleFeedback = (qaRecordId, isPositive) => {
    setCurrentQARecord(qaRecordId);
    setFeedbackModalVisible(true);
    form.setFieldsValue({
      score: isPositive ? 5 : 2
    });
  };

  const submitFeedback = async (values) => {
    try {
      const response = await knowledgeApi.submitFeedback(
        currentQARecord,
        values.score,
        values.comment || ''
      );

      if (response.data?.success) {
        message.success('反馈提交成功');
        setFeedbackModalVisible(false);
        form.resetFields();
      } else {
        message.error(response.data?.error || '反馈提交失败');
      }
    } catch (error) {
      console.error('提交反馈失败:', error);
      message.error('提交反馈失败: ' + error.message);
    }
  };

  const clearChat = () => {
    setChatHistory([]);
    setSessionId(null);
    message.success('聊天记录已清空');
  };

  if (!isLoggedIn) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Title level={3}>请先登录</Title>
        <Text type="secondary">您需要登录后才能使用智能问答功能</Text>
        <div style={{ marginTop: 16 }}>
          <Button type="primary" onClick={() => window.location.href = '/login'}>
            前往登录
          </Button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text>正在加载知识库...</Text>
        </div>
      </div>
    );
  }

  if (!knowledgeBase) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Title level={3}>知识库不存在</Title>
        <Text type="secondary">请检查知识库ID是否正确</Text>
        <div style={{ marginTop: 16 }}>
          <Button type="primary" onClick={() => window.location.href = '/knowledge'}>
            返回知识库列表
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
      {/* 页面标题 */}
      <Card style={{ marginBottom: 16, flexShrink: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Title level={3} style={{ margin: 0 }}>
              <MessageOutlined style={{ marginRight: 8 }} />
              {knowledgeBase.name} - 智能问答
            </Title>
            <Text type="secondary">{knowledgeBase.description}</Text>
          </div>
          <Space>
            <Select
              placeholder="选择模型"
              value={selectedModel}
              onChange={setSelectedModel}
              style={{ width: 200 }}
              allowClear
            >
              {modelConfigs.map(config => (
                <Option key={config.id} value={config.id}>
                  {config.name} {config.is_default && '(默认)'}
                </Option>
              ))}
            </Select>
            <Button onClick={clearChat}>清空对话</Button>
            <Button 
              icon={<SettingOutlined />}
              onClick={() => window.location.href = '/knowledge/settings'}
            >
              模型配置
            </Button>
          </Space>
        </div>
      </Card>

      {/* 聊天区域 */}
      <Card 
        style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
        bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0 }}
      >
        {/* 聊天历史 */}
        <div 
          ref={chatContainerRef}
          style={{ 
            flex: 1, 
            overflowY: 'auto', 
            padding: '16px',
            backgroundColor: '#fafafa'
          }}
        >
          {chatHistory.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
              <RobotOutlined style={{ fontSize: 48, marginBottom: 16 }} />
              <div>
                <Title level={4} type="secondary">开始与AI助手对话</Title>
                <Text type="secondary">
                  您可以询问关于 "{knowledgeBase.name}" 知识库中的任何问题
                </Text>
              </div>
              <div style={{ marginTop: 24 }}>
                <Space direction="vertical">
                  <Text type="secondary">💡 建议询问：</Text>
                  <Tag style={{ cursor: 'pointer' }} onClick={() => setQuestion('请介绍一下这个知识库的主要内容')}>
                    请介绍一下这个知识库的主要内容
                  </Tag>
                  <Tag style={{ cursor: 'pointer' }} onClick={() => setQuestion('有哪些重要的概念和术语？')}>
                    有哪些重要的概念和术语？
                  </Tag>
                </Space>
              </div>
            </div>
          ) : (
            <List
              dataSource={chatHistory}
              renderItem={(item) => (
                <List.Item style={{ border: 'none', padding: '8px 0' }}>
                  <div style={{ width: '100%' }}>
                    {item.type === 'user' ? (
                      // 用户消息
                      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                        <div style={{ 
                          maxWidth: '70%',
                          backgroundColor: '#1890ff',
                          color: 'white',
                          padding: '12px 16px',
                          borderRadius: '18px',
                          borderTopRightRadius: '4px'
                        }}>
                          <Text style={{ color: 'white' }}>{item.content}</Text>
                          <div style={{ textAlign: 'right', marginTop: 4 }}>
                            <Text style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '12px' }}>
                              {item.timestamp.toLocaleTimeString()}
                            </Text>
                          </div>
                        </div>
                        <Avatar icon={<UserOutlined />} style={{ marginLeft: 8 }} />
                      </div>
                    ) : item.type === 'ai' ? (
                      // AI回答
                      <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                        <Avatar icon={<RobotOutlined />} style={{ marginRight: 8, backgroundColor: '#52c41a' }} />
                        <div style={{ 
                          maxWidth: '70%',
                          backgroundColor: 'white',
                          border: '1px solid #d9d9d9',
                          padding: '12px 16px',
                          borderRadius: '18px',
                          borderTopLeftRadius: '4px'
                        }}>
                          <Paragraph style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                            {item.content}
                          </Paragraph>
                          
                          {/* 来源文档 */}
                          {item.sources && item.sources.length > 0 && (
                            <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #f0f0f0' }}>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                <FileTextOutlined style={{ marginRight: 4 }} />
                                参考来源：
                              </Text>
                              <div style={{ marginTop: 4 }}>
                                {item.sources.slice(0, 3).map((source, index) => (
                                  <Tag key={index} size="small" style={{ margin: '2px' }}>
                                    {source.document_title}
                                  </Tag>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {/* 底部信息 */}
                          <div style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            alignItems: 'center',
                            marginTop: 8,
                            paddingTop: 8,
                            borderTop: '1px solid #f0f0f0'
                          }}>
                            <Space size="small">
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                <ClockCircleOutlined style={{ marginRight: 2 }} />
                                {item.timestamp.toLocaleTimeString()}
                              </Text>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                {item.model_used}
                              </Text>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                {item.response_time?.toFixed(2)}s
                              </Text>
                            </Space>
                            <Space>
                              <Tooltip title="回答有帮助">
                                <Button 
                                  type="text" 
                                  size="small"
                                  icon={<LikeOutlined />}
                                  onClick={() => handleFeedback(item.qa_record_id, true)}
                                />
                              </Tooltip>
                              <Tooltip title="回答有问题">
                                <Button 
                                  type="text" 
                                  size="small"
                                  icon={<DislikeOutlined />}
                                  onClick={() => handleFeedback(item.qa_record_id, false)}
                                />
                              </Tooltip>
                            </Space>
                          </div>
                        </div>
                      </div>
                    ) : (
                      // 错误消息
                      <div style={{ display: 'flex', justifyContent: 'center' }}>
                        <Alert
                          message={item.content}
                          type="error"
                          style={{ maxWidth: '70%' }}
                        />
                      </div>
                    )}
                  </div>
                </List.Item>
              )}
            />
          )}
        </div>

        {/* 输入区域 */}
        <div style={{ padding: '16px', borderTop: '1px solid #f0f0f0', backgroundColor: 'white' }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <TextArea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入您的问题... (Shift+Enter换行，Enter发送)"
              autoSize={{ minRows: 1, maxRows: 4 }}
              disabled={asking}
              style={{ flex: 1 }}
            />
            <Button 
              type="primary"
              icon={<SendOutlined />}
              onClick={handleAskQuestion}
              loading={asking}
              disabled={!question.trim() || asking}
            >
              发送
            </Button>
          </div>
          {!selectedModel && (
            <Alert
              message="提示：未选择模型配置，将使用默认配置"
              type="warning"
              style={{ marginTop: 8 }}
              showIcon
              closable
            />
          )}
        </div>
      </Card>

      {/* 反馈弹窗 */}
      <Modal
        title="问答反馈"
        open={feedbackModalVisible}
        onCancel={() => {
          setFeedbackModalVisible(false);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={submitFeedback}
        >
          <Form.Item
            name="score"
            label="评分"
            rules={[{ required: true, message: '请给出评分' }]}
          >
            <Rate />
          </Form.Item>

          <Form.Item
            name="comment"
            label="详细反馈"
          >
            <TextArea 
              rows={3}
              placeholder="请详细描述您的意见和建议（可选）"
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => {
                setFeedbackModalVisible(false);
                form.resetFields();
              }}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                提交反馈
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default KnowledgeChat;
