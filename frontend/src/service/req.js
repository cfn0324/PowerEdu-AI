import { message } from "antd";
import axios from "axios";
import { host } from "../tools";

function getToken() {
  const authStorage = localStorage.getItem("auth-storage");
  const storage = JSON.parse(authStorage);
  return storage?.state?.auth?.token;
}

// 创建axios实例
const api = axios.create({
  baseURL: `${host}/api`,
});

// 请求拦截器：在请求头中添加token
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：处理token过期等情况
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API请求错误:', error);
    
    if (error.response) {
      // 服务器响应了错误状态码
      if (error.response.status === 401) {
        if (getToken()) {
          localStorage.clear();
          location.reload();
        }
        message.error("凭证已过期，请登录");
      } else if (error.response.status === 500) {
        message.error("服务器内部错误，请稍后重试");
      } else if (error.response.status === 404) {
        message.error("请求的资源不存在");
      } else {
        message.error(`请求失败: ${error.response.status}`);
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      message.error("网络连接失败，请检查后端服务是否启动");
    } else {
      // 其他错误
      message.error(`请求配置错误: ${error.message}`);
    }
    
    return Promise.reject(error);
  }
);

export default api;
