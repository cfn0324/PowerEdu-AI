import api from './req';

const API_BASE = '/prediction';

export const predictionApi = {
  // 系统管理
  getSystemStatus: () => api.get(`${API_BASE}/system/status`),
  initializeSystem: () => api.get(`${API_BASE}/system/initialize`),
  
  // 模型管理
  getModels: () => api.get(`${API_BASE}/models`),
  getModelPerformance: () => api.get(`${API_BASE}/models/performance`),
  
  // 预测功能
  predictSingle: (data) => api.post(`${API_BASE}/predict/single`, data),
  predictBatch: (data) => api.post(`${API_BASE}/predict/batch`, data),
  predictDayAhead: (data) => api.post(`${API_BASE}/predict/day-ahead`, data),
  predictWithUncertainty: (data) => api.post(`${API_BASE}/predict/uncertainty`, data),
  
  // 分析功能
  analyzePredictionFactors: (data) => api.post(`${API_BASE}/analysis/factors`, data),
  analyzePredictionError: (data) => api.post(`${API_BASE}/analysis/error`, data),
  
  // 历史记录
  getPredictionHistory: () => api.get(`${API_BASE}/history`),
  
  // 仪表板
  getDashboardData: () => api.get(`${API_BASE}/dashboard`),
  
  // 数据生成
  generateSampleData: (data) => api.post(`${API_BASE}/data/generate`, data)
};
