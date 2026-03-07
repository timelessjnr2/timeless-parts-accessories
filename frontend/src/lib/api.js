import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

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
};

// Customers API
export const customersApi = {
  getAll: (params) => api.get("/customers", { params }),
  getById: (id) => api.get(`/customers/${id}`),
  create: (data) => api.post("/customers", data),
  update: (id, data) => api.put(`/customers/${id}`, data),
  delete: (id) => api.delete(`/customers/${id}`),
};

// Invoices API
export const invoicesApi = {
  getAll: (params) => api.get("/invoices", { params }),
  getById: (id) => api.get(`/invoices/${id}`),
  create: (data) => api.post("/invoices", data),
  update: (id, data) => api.put(`/invoices/${id}`, data),
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
