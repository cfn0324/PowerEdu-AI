import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// 电力知识库与AI预测平台 - 生产环境配置
export default defineConfig({
  plugins: [react()],
  
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
    },
    // 资源内联阈值
    assetsInlineLimit: 4096,
    // 块大小警告限制
    chunkSizeWarningLimit: 1000
  },
  
  // 路径别名
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  
  // 基础路径（如果部署在子目录下）
  base: '/',
  
  // 预览配置（用于生产环境预览）
  preview: {
    port: 4173,
    host: true
  }
});
