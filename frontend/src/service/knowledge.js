import api from './req';

const API_BASE = '/knowledge';

export const knowledgeApi = {
  // 系统概览
  getSystemInfo: () => api.get(`${API_BASE}/`),
  getSystemStats: () => api.get(`${API_BASE}/stats`),
  getHealthCheck: () => api.get(`${API_BASE}/health`),

  // 知识库管理
  getKnowledgeBases: (params = {}) => api.get(`${API_BASE}/knowledge-bases`, { params }),
  createKnowledgeBase: (data) => api.post(`${API_BASE}/knowledge-bases`, data),
  getKnowledgeBase: (kbId) => api.get(`${API_BASE}/knowledge-bases/${kbId}`),
  updateKnowledgeBase: (kbId, data) => api.put(`${API_BASE}/knowledge-bases/${kbId}`, data),
  deleteKnowledgeBase: (kbId) => api.delete(`${API_BASE}/knowledge-bases/${kbId}`),

  // 文档管理
  getDocuments: (kbId, params = {}) => api.get(`${API_BASE}/documents`, { 
    params: { kb_id: kbId, ...params } 
  }),
  uploadDocument: (kbId, formData) => api.post(`${API_BASE}/documents/upload`, formData, {
    params: { kb_id: kbId },
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  batchUploadDocuments: (kbId, formData, config = {}) => api.post(`${API_BASE}/documents/${kbId}/batch-upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    ...config
  }),
  deleteDocument: (documentId) => api.delete(`${API_BASE}/documents/${documentId}`),
  processDocument: (documentId, options = {}) => api.post(`${API_BASE}/documents/${documentId}/process`, options),

  // 智能问答
  askQuestion: (data) => api.post(`${API_BASE}/qa/ask`, data),
  getQAHistory: (params = {}) => api.get(`${API_BASE}/qa/sessions`, { params }),
  getSessionRecords: (sessionId, params = {}) => api.get(`${API_BASE}/qa/sessions/${sessionId}/records`, { params }),
  submitFeedback: (qaRecordId, score, comment = '') => api.post(`${API_BASE}/qa/feedback`, {
    qa_record_id: qaRecordId,
    score,
    comment
  }),

  // 模型配置管理
  getModelConfigs: () => api.get(`${API_BASE}/models/configs`),
  createModelConfig: (data) => api.post(`${API_BASE}/models/configs`, data),
  updateModelConfig: (configId, data) => api.put(`${API_BASE}/models/configs/${configId}`, data),
  deleteModelConfig: (configId) => api.delete(`${API_BASE}/models/configs/${configId}`),
  testModelConfig: (configId) => api.get(`${API_BASE}/models/test`, { params: { config_id: configId } }),

  // 搜索功能
  searchDocuments: (data) => api.post(`${API_BASE}/search`, data)
};
