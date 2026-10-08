import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUserData = async () => {
    try {
      const userRes = await apiClient.get('/auth/me');
      setUser(userRes.data);
      
      try {
        const profileRes = await apiClient.get('/users/profiles/me');
        setProfile(profileRes.data);
      } catch (err) {
        // Profile might not exist yet; handle silently
        setProfile(null);
      }
    } catch (err) {
      logout();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUserData();
    } else {
      setLoading(false);
    }
  }, []);

  const formatErrorDetail = (detail, defaultMsg) => {
    if (!detail) return defaultMsg;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail.map(item => item.msg || JSON.stringify(item)).join(' | ');
    }
    if (typeof detail === 'object') {
      return detail.msg || JSON.stringify(detail);
    }
    return defaultMsg;
  };

  const login = async (email, password) => {
    setLoading(true);
    try {
      const res = await apiClient.post('/auth/login', { email, password });
      const { access_token, refresh_token } = res.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      await fetchUserData();
      return { success: true };
    } catch (error) {
      setLoading(false);
      return {
        success: false,
        error: formatErrorDetail(error.response?.data?.detail, "Authentication failed.")
      };
    }
  };

  const register = async (email, password, roles = ["farmer"]) => {
    setLoading(true);
    try {
      await apiClient.post('/auth/register', { email, password, roles });
      return await login(email, password);
    } catch (error) {
      setLoading(false);
      return {
        success: false,
        error: formatErrorDetail(error.response?.data?.detail, "Registration failed.")
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setProfile(null);
    setLoading(false);
  };

  const createOrUpdateProfile = async (profileData, isNew = true) => {
    try {
      let res;
      if (isNew) {
        res = await apiClient.post('/users/profiles', profileData);
      } else {
        res = await apiClient.put('/users/profiles/me', profileData);
      }
      setProfile(res.data);
      return { success: true };
    } catch (err) {
      return {
        success: false,
        error: formatErrorDetail(err.response?.data?.detail, "Failed to save profile details.")
      };
    }
  };

  return (
    <AuthContext.Provider value={{ user, profile, loading, login, register, logout, createOrUpdateProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
