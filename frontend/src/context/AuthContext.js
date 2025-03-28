import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { setAuthToken } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load user from session on initial render
  useEffect(() => {
    const loadUser = async () => {
      try {
        const res = await axios.get('/api/users/profile');
        setUser(res.data);
        setIsAuthenticated(true);
      } catch (err) {
        console.error('Error loading user:', err);
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  // Register user
  const register = async (userData) => {
    setLoading(true);
    setError(null);
    
    try {
      const res = await axios.post('/api/users/register', userData);
      setUser(res.data);
      setIsAuthenticated(true);
      return res.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Login user
  const login = async (userData) => {
    setLoading(true);
    setError(null);
    
    try {
      const res = await axios.post('/api/users/login', userData);
      setUser(res.data);
      setIsAuthenticated(true);
      return res.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Logout user
  const logout = async () => {
    setLoading(true);
    
    try {
      await axios.post('/api/users/logout');
      setUser(null);
      setIsAuthenticated(false);
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Update user profile
  const updateProfile = async (userData) => {
    setLoading(true);
    setError(null);
    
    try {
      const res = await axios.put('/api/users/profile', userData);
      setUser({ ...user, ...userData });
      return res.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Profile update failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Update user preferences
  const updatePreferences = async (preferences) => {
    setLoading(true);
    setError(null);
    
    try {
      const res = await axios.put('/api/users/preferences', preferences);
      setUser({ ...user, preferences });
      return res.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Preferences update failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        error,
        register,
        login,
        logout,
        updateProfile,
        updatePreferences
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
