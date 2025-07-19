import React from 'react';
import { Empty, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { UserOutlined } from '@ant-design/icons';

/**
 * 登录提示组件 - 用于显示需要登录的提示
 * @param {Object} props - 组件属性
 * @param {string} props.title - 提示标题
 * @param {string} props.description - 提示描述
 * @param {string} props.redirectTo - 点击按钮后重定向的路径
 * @param {string} props.buttonText - 按钮文本
 * @param {React.ReactNode} props.extra - 额外的操作组件
 */
const LoginPrompt = ({
  title = '需要登录',
  description = '请先登录后访问此页面',
  redirectTo = '/',
  buttonText = '返回首页',
  extra = null
}) => {
  const navigate = useNavigate();

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '60vh', 
      flexDirection: 'column',
      padding: '20px'
    }}>
      <Empty 
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        imageStyle={{
          height: 60,
        }}
        description={
          <div>
            <h3 style={{ margin: '16px 0 8px', color: '#595959' }}>
              <UserOutlined style={{ marginRight: '8px' }} />
              {title}
            </h3>
            <p style={{ color: '#8c8c8c', margin: 0 }}>
              {description}
            </p>
          </div>
        }
      >
        <div style={{ marginTop: '16px' }}>
          <Button 
            type="primary" 
            onClick={() => navigate(redirectTo)}
            style={{ marginRight: '8px' }}
          >
            {buttonText}
          </Button>
          {extra}
        </div>
      </Empty>
    </div>
  );
};

export default LoginPrompt;
