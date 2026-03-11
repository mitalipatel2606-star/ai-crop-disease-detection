/**
 * api.js
 * ======
 * Axios API client for the FastAPI backend.
 * All requests go through this single module.
 */

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000,  // 60s — model inference can take time
});

// ── Request interceptor (logs in dev) ─────────────────────────────────────
api.interceptors.request.use((config) => {
  if (process.env.NODE_ENV === 'development') {
    console.log(`→ ${config.method?.toUpperCase()} ${config.url}`);
  }
  return config;
});

// ── Response interceptor (normalise errors) ──────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';
    return Promise.reject(new Error(message));
  }
);


/**
 * POST /predict
 * Upload a leaf image and get disease prediction.
 *
 * @param {File} imageFile - The uploaded image file
 * @returns {Promise<PredictionResponse>}
 */
export const predictDisease = async (imageFile) => {
  const formData = new FormData();
  formData.append('file', imageFile);

  const response = await api.post('/predict', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};


/**
 * GET /diseases
 * Fetch the complete disease knowledge base.
 *
 * @returns {Promise<DiseasesResponse>}
 */
export const fetchDiseases = async () => {
  const response = await api.get('/diseases');
  return response.data;
};


/**
 * GET /history
 * Fetch prediction history.
 *
 * @param {number} limit  - Records per page (default: 20)
 * @param {number} offset - Pagination offset
 * @returns {Promise<HistoryResponse>}
 */
export const fetchHistory = async (limit = 20, offset = 0) => {
  const response = await api.get('/history', { params: { limit, offset } });
  return response.data;
};


/**
 * GET /health
 * Check API health and model status.
 *
 * @returns {Promise<HealthResponse>}
 */
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
