import { InfoCircleOutlined } from "@ant-design/icons";
import "./index.css";

import { Button, Modal, Form, Input, Tooltip } from "antd";
import React, { useState } from "react";

const LoginForm = ({ isRegister, handleLogin, handleRegister }) => {
  const [form] = Form.useForm();

  const onFinish = (values) => {
    console.log("Success:", values);
    if (isRegister) {
      handleRegister(values); // 调用注册函数
    } else {
      handleLogin(values); // 调用登录函数
    }
  };

  const onFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo);
  };

  return (
    <Form
      form={form}
      name="basic"
      onFinish={onFinish}
      onFinishFailed={onFinishFailed}
      autoComplete="off"
    >
      <Form.Item
        name="username"
        rules={[
          {
            required: true,
            message: "请输入用户名！",
          },
        ]}
      >
        <Input placeholder="用户名" />
      </Form.Item>

      <Form.Item
        name="password"
        rules={[
          {
            required: true,
            message: "请输入密码！",
          },
        ]}
      >
        <Input type="password" placeholder="密码" />
      </Form.Item>

      {isRegister && (
        <Form.Item
          name="confirmPassword"
          dependencies={["password"]}
          rules={[
            {
              required: true,
              message: "请确认密码！",
            },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue("password") === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error("两次输入的密码不一致！"));
              },
            }),
          ]}
        >
          <Input type="password" placeholder="确认密码" />
        </Form.Item>
      )}

      <Form.Item>
        <Button type="primary" htmlType="submit" style={{ width: "100%" }}>
          {isRegister ? "注册" : "登录"}
        </Button>
      </Form.Item>
    </Form>
  );
};

const LoginModal = ({ open, close, login, register }) => {
  const [isRegister, setIsRegister] = useState(false);

  const ModalTitle = (
    <div>
      <span>{isRegister ? "用户注册" : "用户登录"}</span>
      <Tooltip title={isRegister ? "填写信息完成注册" : "填写信息完成登录"}>
        <InfoCircleOutlined style={{ marginLeft: "5px" }} />
      </Tooltip>
    </div>
  );

  return (
    <Modal
      width={384}
      open={open}
      onCancel={close}
      footer={null}
      destroyOnClose={true}
      title={ModalTitle}
    >
      <div className="login-form">
        <LoginForm
          isRegister={isRegister}
          handleLogin={login} // 登录函数
          handleRegister={register} // 注册函数
        />
      </div>
      <Button type="link" onClick={() => setIsRegister(!isRegister)}>
        {isRegister ? "已有账号？去登录" : "没有账号？去注册"}
      </Button>
    </Modal>
  );
};

export default LoginModal;
