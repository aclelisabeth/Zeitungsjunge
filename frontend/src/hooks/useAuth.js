// Authentication hook
import { useCallback } from 'react';
import { useAuthStore } from '../store';
import { authAPI } from '../api/client';

export const useAuth = () => {
  const { user, token, isLoading, error, setUser, setToken, setLoading, setError, logout } = 
    useAuthStore();

  const login = useCallback(async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authAPI.login({ username, password });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      setToken(access_token);
      setUser(userData);
      
      return response.data;
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError, setToken, setUser]);

  const register = useCallback(async (userData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authAPI.register(userData);
      const { access_token, user: userInfo } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(userInfo));
      
      setToken(access_token);
      setUser(userInfo);
      
      return response.data;
    } catch (err) {
      const message = err.response?.data?.detail || 'Registration failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError, setToken, setUser]);

  const getCurrentUser = useCallback(async () => {
    if (!token) return null;
    
    try {
      const response = await authAPI.getMe();
      setUser(response.data);
      return response.data;
    } catch (err) {
      logout();
      return null;
    }
  }, [token, setUser, logout]);

  const refreshAccessToken = useCallback(async () => {
    if (!token) return null;
    
    try {
      const response = await authAPI.refreshToken();
      const { access_token } = response.data;
      
      localStorage.setItem('access_token', access_token);
      setToken(access_token);
      
      return access_token;
    } catch (err) {
      logout();
      return null;
    }
  }, [token, setToken, logout]);

  const logoutUser = useCallback(() => {
    logout();
  }, [logout]);

  const isAuthenticated = !!token && !!user;

  return {
    user,
    token,
    isLoading,
    error,
    isAuthenticated,
    login,
    register,
    getCurrentUser,
    refreshAccessToken,
    logout: logoutUser
  };
};

export default useAuth;
