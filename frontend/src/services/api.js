import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token: newRefreshToken } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', newRefreshToken);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
};

// Chat API
export const chatAPI = {
  createSession: () => api.post('/chat/sessions'),
  getUserSessions: (limit = 10) => api.get(`/chat/sessions?limit=${limit}`),
  getSessionMessages: (sessionId) => api.get(`/chat/sessions/${sessionId}/messages`),
  sendMessage: (sessionId, content) => api.post(`/chat/sessions/${sessionId}/messages`, { content }),
  getSessionRiskHistory: (sessionId) => api.get(`/chat/sessions/${sessionId}/risk-history`),
  getInterventions: (riskLevel = 'low') => api.get(`/chat/interventions?risk_level=${riskLevel}`),
};

// Counsellor API
export const counsellorAPI = {
  getHighRiskSessions: (assignedOnly = false) => 
    api.get(`/counsellor/dashboard/high-risk?assigned_only=${assignedOnly}`),
  getMyAssignments: (statusFilter) => 
    api.get(`/counsellor/dashboard/assignments${statusFilter ? `?status_filter=${statusFilter}` : ''}`),
  createAssignment: (assignmentData) => api.post('/counsellor/assignments', assignmentData),
  updateAssignmentStatus: (assignmentId, status, notes) => 
    api.put(`/counsellor/assignments/${assignmentId}/status`, { status, notes }),
  getStudentRiskTrend: (studentId) => api.get(`/counsellor/students/${studentId}/risk-trend`),
  getCounsellorStats: () => api.get('/counsellor/dashboard/stats'),
  // Admin endpoints
  getAllAssignments: (limit = 50) => api.get(`/counsellor/admin/all-assignments?limit=${limit}`),
  getSystemStats: () => api.get('/counsellor/admin/system-stats'),
};

// Risk API
export const riskAPI = {
  assessMessage: (message, context = []) => api.post('/risk/assess', { message, context }),
  getInterventionsByRisk: (riskLevel) => api.get(`/risk/interventions/${riskLevel}`),
  getUserRiskTrend: (userId, limit = 10) => api.get(`/risk/user/${userId}/trend?limit=${limit}`),
  getCrisisKeywords: () => api.get('/risk/crisis-keywords'),
  initInterventions: () => api.post('/risk/init-interventions'),
};

export default api;