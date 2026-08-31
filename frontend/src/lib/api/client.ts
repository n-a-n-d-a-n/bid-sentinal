import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('procurex_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'API Request failed';
    return Promise.reject(new Error(message));
  }
);

// Helper API Methods
export const api = {
  // Auth
  login: async (username: string, password: string) => {
    // Form data login
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const res: any = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    if (res.data?.access_token && typeof window !== 'undefined') {
      localStorage.setItem('procurex_token', res.data.access_token);
    }
    return res.data;
  },
  getCurrentUser: async () => apiClient.get('/auth/me'),

  // Tenders
  getTenders: async () => apiClient.get('/tenders'),
  getTender: async (id: string) => apiClient.get(`/tenders/${id}`),

  // Bidders
  getBidders: async () => apiClient.get('/bidders'),
  getBidder: async (id: string) => apiClient.get(`/bidders/${id}`),
  getBidderGraph: async (id: string) => apiClient.get(`/bidders/${id}/graph`),
  getBidderAnomalies: async (id: string) => apiClient.get(`/bidders/${id}/anomalies`),

  // Bids
  getBids: async () => apiClient.get('/bids'),
  getBid: async (id: string) => apiClient.get(`/bids/${id}`),
  getBidCompliance: async (id: string) => apiClient.get(`/bids/${id}/compliance`),
  getBidVerification: async (id: string) => apiClient.get(`/bids/${id}/verification`),
  getVerificationAdapters: async () => apiClient.get('/verification/adapters'),
  getBidDecisionReadiness: async (id: string) => apiClient.get(`/bids/${id}/decision-readiness`),
  getBidConsistency: async (id: string) => apiClient.get(`/bids/${id}/consistency`),
  getBidRisk: async (id: string) => apiClient.get(`/bids/${id}/risk`),
  calculateBidRisk: async (id: string) => apiClient.post(`/risk/bids/${id}/calculate`),
  getBidAudit: async (id: string) => apiClient.get(`/bids/${id}/audit`),


  // Graph
  getBidGraph: async (bidId: string) => apiClient.get(`/graph/bids/${bidId}`),
  getConnections: async (src: string, target: string) => apiClient.get(`/graph/bidders/${src}/connections/${target}`),

  // Policy RAG
  queryPolicy: async (question: string, sourceFilters?: string[], versionFilter?: string) =>
    apiClient.post('/policy/query', { question, source_filters: sourceFilters, version_filter: versionFilter }),
  getPolicySources: async () => apiClient.get('/policy/sources'),
  getBidPolicyExplanation: async (bidId: string, reqName: string, extVal: string, reqVal: string, result: string) =>
    apiClient.post(`/policy/bids/${bidId}/explanation`, {
      requirement_name: reqName,
      extracted_value: extVal,
      required_value: reqVal,
      compliance_result: result,
    }),

  // Decisions
  submitDecision: async (bidId: string, payload: any) => apiClient.post(`/bids/${bidId}/decision`, payload),
  getDecisionHistory: async (bidId: string) => apiClient.get(`/bids/${bidId}/decision-history`),

  // Audit
  listAuditEvents: async () => apiClient.get('/audit'),
  verifyAuditChain: async (entityType?: string, entityId?: string) =>
    entityType && entityId ? apiClient.get(`/audit/verify/${entityType}/${entityId}`) : apiClient.get('/audit/verify'),

  // Demo Center
  getDemoHealth: async () => apiClient.get('/demo/health'),
  listDemoScenarios: async () => apiClient.get('/demo/scenarios'),
  runDemoScenario: async (code: string, mode: string = 'FULL_RUN') => apiClient.post(`/demo/scenarios/${code}/run`, { mode }),
  resetDemo: async () => apiClient.post('/demo/reset'),
};
