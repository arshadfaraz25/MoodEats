import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Set auth token for requests
export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

// User API calls
export const userAPI = {
  register: (userData) => api.post('/users/register', userData),
  login: (userData) => api.post('/users/login', userData),
  logout: () => api.post('/users/logout'),
  getProfile: () => api.get('/users/profile'),
  updateProfile: (userData) => api.put('/users/profile', userData),
  getPreferences: () => api.get('/users/preferences'),
  updatePreferences: (preferences) => api.put('/users/preferences', preferences),
  getFavorites: () => api.get('/users/favorites'),
  addFavorite: (mealId) => api.post(`/users/favorites/${mealId}`),
  removeFavorite: (mealId) => api.delete(`/users/favorites/${mealId}`)
};

// Meal API calls
export const mealAPI = {
  getMeals: (params) => api.get('/meals', { params }),
  getMeal: (id) => api.get(`/meals/${id}`),
  addFeedback: (id, feedback) => api.post(`/meals/${id}/feedback`, feedback),
  searchMeals: (query) => api.get('/meals/search', { params: { q: query } }),
  getRandomMeals: (limit = 10) => api.get('/meals/random', { params: { limit } })
};

// Mood API calls
export const moodAPI = {
  logMood: (moodData) => api.post('/moods/log', moodData),
  getMoodHistory: (limit = 10) => api.get('/moods/history', { params: { limit } }),
  getRecommendations: (mood, limit = 10) => api.get('/moods/recommendations', { params: { mood, limit } }),
  getAvailableMoods: () => api.get('/moods/moods')
};

// Admin API calls
export const adminAPI = {
  getUsers: (limit = 100) => api.get('/admin/users', { params: { limit } }),
  getUser: (id) => api.get(`/admin/users/${id}`),
  deleteUser: (id) => api.delete(`/admin/users/${id}`),
  getMeals: () => api.get('/admin/meals'),
  createMeal: (mealData) => api.post('/admin/meals', mealData),
  updateMeal: (id, mealData) => api.put(`/admin/meals/${id}`, mealData),
  deleteMeal: (id) => api.delete(`/admin/meals/${id}`),
  bulkUploadMeals: (formData) => api.post('/admin/meals/bulk', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  getUserAnalytics: (timeRange = 'week') => api.get('/admin/analytics/users', { params: { time_range: timeRange } }),
  getMealAnalytics: (timeRange = 'week') => api.get('/admin/analytics/meals', { params: { time_range: timeRange } }),
  getMoodAnalytics: (timeRange = 'week') => api.get('/admin/analytics/moods', { params: { time_range: timeRange } })
};

export default api;
