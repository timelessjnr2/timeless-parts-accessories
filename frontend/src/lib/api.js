import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && window.location.pathname !== '/login') {
      // Token expired or invalid - redirect to login
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      // Don't redirect for password verification endpoints
      if (!error.config?.url?.includes('verify-password')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// User Auth API
export const userAuthApi = {
  login: (username, password) => api.post("/auth/login", { username, password }),
  logout: () => api.post("/auth/logout"),
  register: (data) => api.post("/auth/register", data),
  getCurrentUser: () => api.get("/auth/me"),
  getAllUsers: () => api.get("/auth/users"),
  getActivityLogs: (limit = 50, userId = null) => 
    api.get(`/auth/activity?limit=${limit}${userId ? `&user_id=${userId}` : ''}`),
  toggleUserActive: (userId) => api.put(`/auth/users/${userId}/toggle-active`),
  deleteUser: (userId, password) => api.delete(`/auth/users/${userId}?password=${encodeURIComponent(password)}`),
};

// Parts API
export const partsApi = {
  getAll: (params) => api.get("/parts", { params }),
  getById: (id) => api.get(`/parts/${id}`),
  create: (data) => api.post("/parts", data),
  update: (id, data) => api.put(`/parts/${id}`, data),
  delete: (id) => api.delete(`/parts/${id}`),
  adjustStock: (id, adjustment) =>
    api.post(`/parts/${id}/adjust-stock?adjustment=${adjustment}`),
  getCategories: () => api.get("/parts/categories/list"),
  getFrequentlyUsed: (limit = 6) => api.get(`/parts/frequently-used?limit=${limit}`),
};

// Customers API
export const customersApi = {
  getAll: (params) => api.get("/customers", { params }),
  getById: (id) => api.get(`/customers/${id}`),
  create: (data) => api.post("/customers", data),
  update: (id, data) => api.put(`/customers/${id}`, data),
  delete: (id) => api.delete(`/customers/${id}`),
  getInvoices: (id) => api.get(`/customers/${id}/invoices`),
};

// Invoices API
export const invoicesApi = {
  getAll: (params) => api.get("/invoices", { params }),
  getById: (id) => api.get(`/invoices/${id}`),
  create: (data) => api.post("/invoices", data),
  update: (id, data) => api.put(`/invoices/${id}`, data),
  delete: (id, password) => api.delete(`/invoices/${id}?password=${encodeURIComponent(password)}`),
  cancel: (id, password) => api.put(`/invoices/${id}/cancel?password=${encodeURIComponent(password)}`),
  uncancel: (id, password) => api.put(`/invoices/${id}/uncancel?password=${encodeURIComponent(password)}`),
  refund: (id, password, reason = '') => api.put(`/invoices/${id}/refund?password=${encodeURIComponent(password)}${reason ? `&reason=${encodeURIComponent(reason)}` : ''}`),
  markPaid: (id, amount) => api.put(`/invoices/${id}/mark-paid${amount ? `?amount=${amount}` : ''}`),
  addPayment: (id, amount) => api.put(`/invoices/${id}/add-payment?amount=${amount}`),
};

// Sales Journal API
export const salesJournalApi = {
  getJournal: (date) => api.get(`/sales-journal${date ? `?date=${date}` : ''}`),
  getDates: (limit = 30) => api.get(`/sales-journal/dates?limit=${limit}`),
  toggleCheckOff: (invoiceId) => api.put(`/sales-journal/check-off/${invoiceId}`),
};

// Auth API (legacy password verification)
export const authApi = {
  verifyPassword: (password) => api.post("/verify-password", { password }),
  verifyInvoicePassword: (password) => api.post("/verify-invoice-password", { password }),
};

// Settings API
export const settingsApi = {
  get: () => api.get("/settings"),
  updateCompany: (data) => api.put("/settings/company", data),
  updatePolicies: (data) => api.put("/settings/policies", data),
  updateTax: (taxRate, taxName) =>
    api.put(`/settings/tax?tax_rate=${taxRate}&tax_name=${taxName}`),
};

// Vehicles API
export const vehiclesApi = {
  getAll: () => api.get("/vehicles"),
  create: (data) => api.post("/vehicles", data),
  delete: (id) => api.delete(`/vehicles/${id}`),
  getMakes: () => api.get("/vehicles/makes"),
  getModels: (make) => api.get(`/vehicles/models/${make}`),
};

// Dashboard API
export const dashboardApi = {
  getStats: () => api.get("/dashboard/stats"),
  getLowStock: () => api.get("/dashboard/low-stock"),
  getRecentInvoices: (limit = 10) =>
    api.get(`/dashboard/recent-invoices?limit=${limit}`),
};

// Reports API
export const reportsApi = {
  getSales: (params) => api.get("/reports/sales", { params }),
  getInventory: () => api.get("/reports/inventory"),
};

// Upload API
export const uploadApi = {
  uploadImage: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/upload/image", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default api;
