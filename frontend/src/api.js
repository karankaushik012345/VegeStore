
import axios from 'axios';

const API = axios.create({ baseURL: process.env.REACT_APP_API_URL || '/api' });

API.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const authAPI = {
  login: (data) => API.post('/auth/login', data),
  register: (data) => API.post('/auth/register', data),
  me: () => API.get('/auth/me'),
  updateProfile: (data) => API.put('/auth/profile', data),
};

export const productsAPI = {
  getAll: (params) => API.get('/products/', { params }),
  getOne: (id) => API.get(`/products/${id}`),
  getFeatured: () => API.get('/products/featured'),
  getCategories: () => API.get('/products/categories'),
  getSuggestions: (q) => API.get('/products/search/suggestions', { params: { q } }),
};

export const cartAPI = {
  get: () => API.get('/cart/'),
  add: (product_id, quantity = 1) => API.post('/cart/add', { product_id, quantity }),
  update: (item_id, quantity) => API.put(`/cart/update/${item_id}`, { quantity }),
  remove: (item_id) => API.delete(`/cart/remove/${item_id}`),
  clear: () => API.delete('/cart/clear'),
};

export const wishlistAPI = {
  get: () => API.get('/wishlist/'),
  toggle: (product_id) => API.post('/wishlist/toggle', { product_id }),
};

export const ordersAPI = {
  get: () => API.get('/orders/'),
  place: (address) => API.post('/orders/place', { address }),
};

export const storesAPI = {
  getAll: () => API.get('/stores/'),
  getOne: (id, page) => API.get(`/stores/${id}`, { params: { page } }),
};

export const suggestionsAPI = {
  get: () => API.get('/suggestions/'),
};

export const couponsAPI = {
  apply: (code, total) => API.post('/coupons/apply', { code, total }),
};

export const addressesAPI = {
  get: () => API.get('/addresses/'),
  add: (data) => API.post('/addresses/', data),
  update: (id, data) => API.put(`/addresses/${id}`, data),
  delete: (id) => API.delete(`/addresses/${id}`),
  setDefault: (id) => API.post(`/addresses/set-default/${id}`),
};

export default API;
