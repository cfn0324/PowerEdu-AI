import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// 电力知识库与AI预测平台 - 服务器部署专用配置
export default defineConfig({
  plugins: [react()],
  
  // 开发服务器配置（服务器部署）
  server: {
    host: "0.0.0.0",  // 允许外部访问
    port: 5173,
    open: false,      // 禁用自动打开浏览器
    strictPort: true, // 端口被占用时不自动尝试下一个端口
    
    // 不使用代理，直接让前端请求后端API
    // 这样可以避免代理配置问题
  },
  
  // 定义环境变量
  define: {
    'process.env.NODE_ENV': '"development"',
    '__SERVER_DEPLOY__': 'true'  // 标识这是服务器部署模式
  },
  
  // 构建配置
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          antd: ['antd'],
          charts: ['echarts', 'echarts-for-react']
        }
      }
    }
  },
  
  // 路径别名
  resolve: {
    alias: {
      '@': '/src'
    }
  }
});
