import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// 电力知识库与AI预测平台 - Vite配置
export default defineConfig({
  plugins: [react()],
  
  // 开发服务器配置
  server: {
    host: "localhost",
    port: 5173,
    open: false,  // 禁用自动打开浏览器（解决服务器环境问题）
    
    // API代理配置
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
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
