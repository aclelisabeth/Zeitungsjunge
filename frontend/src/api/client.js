// API Service for backend communication
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth on 401
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication APIs
export const authAPI = {
  register: (userData) => 
    apiClient.post('/auth/register', userData),
  login: (credentials) => 
    apiClient.post('/auth/login', credentials),
  getMe: () => 
    apiClient.get('/auth/me'),
  refreshToken: () => 
    apiClient.post('/auth/refresh')
};

// News APIs
export const newsAPI = {
  getNews: (timeRange = 'today', region = null, limit = 20, offset = 0) => 
    apiClient.get('/news/', {
      params: { time_range: timeRange, region, limit, offset }
    }),
  searchNews: (query, region = null, days = 30, limit = 20, offset = 0) => 
    apiClient.get('/news/search', {
      params: { query, region, days, limit, offset }
    }),
  getTrendingNews: (days = 7, limit = 20) => 
    apiClient.get('/news/trending', {
      params: { days, limit }
    }),
  getArticle: (id) => 
    apiClient.get(`/news/${id}`),
  summarizeArticle: (id) => 
    apiClient.post(`/news/${id}/summarize`)
};

// Bookmark APIs
export const bookmarkAPI = {
  addBookmark: (articleId) => 
    apiClient.post(`/bookmarks/${articleId}`),
  removeBookmark: (articleId) => 
    apiClient.delete(`/bookmarks/${articleId}`),
  getBookmarks: (limit = 20, offset = 0) => 
    apiClient.get('/bookmarks/', {
      params: { limit, offset }
    }),
  checkBookmark: (articleId) => 
    apiClient.get(`/bookmarks/check/${articleId}`),
  clearBookmarks: () => 
    apiClient.delete('/bookmarks/')
};

// User APIs
export const userAPI = {
  getProfile: () => 
    apiClient.get('/users/profile'),
  updateProfile: (userData) => 
    apiClient.put('/users/profile', userData),
  deleteProfile: () => 
    apiClient.delete('/users/profile'),
  getPreferences: () => 
    apiClient.get('/users/preferences'),
  updatePreferences: (preferences) => 
    apiClient.put('/users/preferences', preferences)
};

export default apiClient;
