import React, { useEffect, useRef, useState } from 'react';
import { Alert, Spin } from 'antd';

/**
 * 安全的可视化图表组件
 * 使用iframe沙盒来安全渲染Plotly HTML内容
 */
const SafeVisualization = ({ 
  html, 
  height = '400px', 
  width = '100%',
  title = '图表加载中...',
  errorTitle = '图表加载失败',
  errorDescription = '图表生成失败或数据为空'
}) => {
  const iframeRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!html) {
      setError(true);
      setLoading(false);
      return;
    }

    const iframe = iframeRef.current;
    if (!iframe) return;

    try {
      setLoading(true);
      setError(false);

      // 创建一个安全的HTML文档
      const safeHtml = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>${title}</title>
          <style>
            body {
              margin: 0;
              padding: 8px;
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
              background: white;
            }
            .plotly-graph-div {
              width: 100% !important;
              height: calc(100vh - 16px) !important;
            }
          </style>
        </head>
        <body>
          ${html}
        </body>
        </html>
      `;

      // 使用Blob URL方式安全加载内容
      const blob = new Blob([safeHtml], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      
      iframe.src = url;
      
      const handleLoad = () => {
        setLoading(false);
        // 清理Blob URL
        setTimeout(() => {
          URL.revokeObjectURL(url);
        }, 1000);
      };

      const handleError = () => {
        setError(true);
        setLoading(false);
        URL.revokeObjectURL(url);
      };

      iframe.addEventListener('load', handleLoad);
      iframe.addEventListener('error', handleError);

      return () => {
        iframe.removeEventListener('load', handleLoad);
        iframe.removeEventListener('error', handleError);
        URL.revokeObjectURL(url);
      };
    } catch (err) {
      console.error('可视化加载失败:', err);
      setError(true);
      setLoading(false);
    }
  }, [html, title]);

  if (error || !html) {
    return (
      <Alert
        type="warning"
        message={errorTitle}
        description={errorDescription}
        showIcon
        style={{ height, display: 'flex', alignItems: 'center' }}
      />
    );
  }

  return (
    <div style={{ position: 'relative', width, height }}>
      {loading && (
        <div 
          style={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            right: 0, 
            bottom: 0, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            background: 'rgba(255, 255, 255, 0.8)',
            zIndex: 1
          }}
        >
          <Spin size="large" />
        </div>
      )}
      <iframe
        ref={iframeRef}
        style={{
          width: '100%',
          height: '100%',
          border: '1px solid #d9d9d9',
          borderRadius: '6px'
        }}
        sandbox="allow-scripts allow-same-origin"
        title={title}
      />
    </div>
  );
};

export default SafeVisualization;
