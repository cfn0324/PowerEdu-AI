import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTokenStore } from "../stores";
import { message } from "antd";

/**
 * 认证守卫Hook - 用于保护需要登录的页面
 * @param {Object} options - 配置选项
 * @param {string} options.redirectTo - 未登录时重定向的路径，默认为 '/'
 * @param {string} options.message - 未登录时显示的消息
 * @param {boolean} options.silent - 是否静默模式，不显示消息
 * @returns {Object} - 返回认证状态和用户信息
 */
function useAuthGuard(options = {}) {
  const {
    redirectTo = '/',
    message: customMessage = '请先登录后访问此页面',
    silent = false
  } = options;

  const { auth } = useTokenStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (!auth?.token) {
      if (!silent) {
        message.warning(customMessage);
      }
      navigate(redirectTo);
    }
  }, [auth, navigate, redirectTo, customMessage, silent]);

  return {
    isAuthenticated: !!auth?.token,
    user: auth?.user || null,
    token: auth?.token || null
  };
}

/**
 * 登录检查Hook - 仅检查登录状态，不执行重定向
 * @returns {Object} - 返回认证状态和用户信息
 */
export const useAuth = () => {
  const { auth } = useTokenStore();

  return {
    isAuthenticated: !!auth?.token,
    user: auth?.user || null,
    token: auth?.token || null,
    isLoading: false
  };
};

export default useAuthGuard;
