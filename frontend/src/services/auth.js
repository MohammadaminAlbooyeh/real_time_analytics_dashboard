import api from './api';

export async function login(email, password) {
  const { data } = await api.post('/auth/login', { email, password });
  localStorage.setItem('token', data.access_token);
  return data;
}

export async function register(email, username, password, fullName) {
  const { data } = await api.post('/auth/register', {
    email, username, password, full_name: fullName,
  });
  return data;
}

export async function getCurrentUser() {
  const { data } = await api.get('/api/v1/users/me');
  return data;
}

export function logout() {
  localStorage.removeItem('token');
  window.location.href = '/login';
}

export function isAuthenticated() {
  return !!localStorage.getItem('token');
}
