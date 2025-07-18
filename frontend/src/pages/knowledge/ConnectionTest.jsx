import React, { useState, useEffect } from 'react';
import { Card, Button, Typography, Space, Alert, Spin } from 'antd';
import { useNavigate } from 'react-router-dom';
import { knowledgeApi } from '../../service/knowledge';
import { useTokenStore } from '../../stores';

const { Title, Text } = Typography;

const ConnectionTest = () => {
  const [testResults, setTestResults] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { auth } = useTokenStore();
  const isLoggedIn = !!auth?.token;

  const runTests = async () => {
    setLoading(true);
    const results = {};

    try {
      // 测试1: 系统基础信息
      try {
        const systemInfo = await knowledgeApi.getSystemInfo();
        results.systemInfo = {
          status: 'success',
          data: systemInfo.data
        };
      } catch (error) {
        results.systemInfo = {
          status: 'error',
          error: error.message
        };
      }

      // 测试2: 模型配置列表
      try {
        const modelConfigs = await knowledgeApi.getModelConfigs();
        results.modelConfigs = {
          status: 'success',
          data: modelConfigs.data
        };
      } catch (error) {
        results.modelConfigs = {
          status: 'error',
          error: error.message,
          statusCode: error.response?.status
        };
      }

      // 测试3: 知识库列表
      try {
        const knowledgeBases = await knowledgeApi.getKnowledgeBases();
        results.knowledgeBases = {
          status: 'success',
          data: knowledgeBases.data
        };
      } catch (error) {
        results.knowledgeBases = {
          status: 'error',
          error: error.message,
          statusCode: error.response?.status
        };
      }

      setTestResults(results);
    } catch (error) {
      console.error('测试失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderTestResult = (testName, result) => {
    if (!result) return null;

    const { status, data, error, statusCode } = result;

    return (
      <Card 
        title={testName} 
        type="inner" 
        style={{ marginBottom: 16 }}
      >
        {status === 'success' ? (
          <Alert
            type="success"
            message="测试通过"
            description={
              <div>
                <Text>数据获取成功</Text>
                <br />
                <Text type="secondary">
                  {JSON.stringify(data, null, 2).slice(0, 200)}...
                </Text>
              </div>
            }
          />
        ) : (
          <Alert
            type="error"
            message="测试失败"
            description={
              <div>
                <Text>错误信息: {error}</Text>
                <br />
                {statusCode && <Text type="secondary">状态码: {statusCode}</Text>}
              </div>
            }
          />
        )}
      </Card>
    );
  };

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto' }}>
      <Card
        title={
          <Space>
            <Title level={3} style={{ margin: 0 }}>
              API 连接测试
            </Title>
          </Space>
        }
        extra={
          <Button onClick={() => navigate('/knowledge')}>
            返回知识库
          </Button>
        }
      >
        <div style={{ marginBottom: 24 }}>
          <Alert
            type="info"
            message="此页面用于测试知识库API的连接状态"
            description={
              <div>
                <Text>用户登录状态: {isLoggedIn ? '已登录' : '未登录'}</Text>
                <br />
                <Text>Token: {auth?.token ? `${auth.token.slice(0, 20)}...` : '无'}</Text>
              </div>
            }
          />
        </div>

        <div style={{ marginBottom: 24 }}>
          <Button 
            type="primary" 
            onClick={runTests}
            loading={loading}
            disabled={!isLoggedIn}
          >
            {loading ? '测试中...' : '开始测试'}
          </Button>
        </div>

        {loading && (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>
              <Text>正在测试API连接...</Text>
            </div>
          </div>
        )}

        {Object.keys(testResults).length > 0 && !loading && (
          <div>
            <Title level={4}>测试结果</Title>
            {renderTestResult('系统基础信息', testResults.systemInfo)}
            {renderTestResult('模型配置列表', testResults.modelConfigs)}
            {renderTestResult('知识库列表', testResults.knowledgeBases)}
          </div>
        )}

        {!isLoggedIn && (
          <Alert
            type="warning"
            message="请先登录"
            description="需要登录后才能进行API测试"
            action={
              <Button type="primary" onClick={() => navigate('/login')}>
                前往登录
              </Button>
            }
          />
        )}
      </Card>
    </div>
  );
};

export default ConnectionTest;
