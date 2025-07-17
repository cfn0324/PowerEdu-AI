import React, { useState, useEffect } from 'react';
import { Card, Button, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTokenStore } from '../../stores';
import LoginModal from '../../components/login';
import './Login.css';

const Login = () => {
  const [showLogin, setShowLogin] = useState(true);
  const { auth, loginAct, registerAct } = useTokenStore();
  const navigate = useNavigate();

  // 如果已经登录，重定向到首页
  useEffect(() => {
    if (auth) {
      navigate('/');
    }
  }, [auth, navigate]);

  const handleLogin = async (values) => {
    const result = await loginAct(values);
    if (result) {
      setShowLogin(false);
      message.success('登录成功！');
      // 延迟跳转，让用户看到成功消息
      setTimeout(() => {
        navigate('/');
      }, 1000);
    }
  };

  const handleRegister = async (values) => {
    if (values.password !== values.confirmPassword) {
      message.error("两次输入的密码不一致！");
      return;
    }
    const result = await registerAct({
      username: values.username,
      password: values.password,
    });
    
    if (result) {
      message.success("注册成功！请登录");
      setShowLogin(false);
      setTimeout(() => {
        setShowLogin(true);
      }, 500);
    } else {
      message.error("注册失败，请重试！");
    }
  };

  const handleCancel = () => {
    navigate(-1); // 返回上一页
  };

  return (
    <div className="login-page">
      <div className="login-background">
        <div className="login-content">
          <Card 
            className="login-card"
            title={
              <div className="login-title">
                <UserOutlined style={{ marginRight: 8 }} />
                欢迎使用 PowerEdu-AI
              </div>
            }
          >
            <div className="login-description">
              <h3>🚀 智能电力教育平台</h3>
              <p>• 📚 在线知识库学习</p>
              <p>• 🤖 AI 智能问答</p>
              <p>• 📊 负荷预测分析</p>
              <p>• 📈 学习进度跟踪</p>
            </div>
            
            <div className="login-actions">
              <Button 
                type="primary" 
                size="large" 
                icon={<UserOutlined />}
                onClick={() => setShowLogin(true)}
                block
              >
                立即登录
              </Button>
              <Button 
                size="large" 
                onClick={handleCancel}
                style={{ marginTop: 16 }}
                block
              >
                返回上页
              </Button>
            </div>
          </Card>
        </div>
      </div>

      <LoginModal
        open={showLogin}
        close={() => setShowLogin(false)}
        login={handleLogin}
        register={handleRegister}
      />
    </div>
  );
};

export default Login;
