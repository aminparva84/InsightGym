import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      // Ensure token is properly formatted
      const cleanToken = token.trim();
      axios.defaults.headers.common['Authorization'] = `Bearer ${cleanToken}`;
      fetchUser();
    } else {
      // Clear any existing auth header
      delete axios.defaults.headers.common['Authorization'];
      setLoading(false);
    }
  }, [token]);

  // Add axios interceptor for error handling
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401 || error.response?.status === 422) {
          // Token is invalid or expired
          console.warn('Authentication error detected, clearing token');
          localStorage.removeItem('token');
          setToken(null);
          delete axios.defaults.headers.common['Authorization'];
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);

  const fetchUser = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }
      
      // Ensure token is set in axios defaults
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const response = await axios.get('http://localhost:5000/api/user');
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user:', error);
      // Only clear token on 401/422 errors
      if (error.response?.status === 401 || error.response?.status === 422) {
        localStorage.removeItem('token');
        setToken(null);
        delete axios.defaults.headers.common['Authorization'];
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await axios.post('http://localhost:5000/api/login', {
        username,
        password
      });
      const { access_token, user: userData } = response.data;
      
      // Ensure token is stored correctly
      if (access_token) {
        const cleanToken = access_token.trim();
        localStorage.setItem('token', cleanToken);
        setToken(cleanToken);
        axios.defaults.headers.common['Authorization'] = `Bearer ${cleanToken}`;
        setUser(userData);
        return { success: true };
      } else {
        return { success: false, error: 'No token received from server' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.response?.data?.error || 'Login failed' };
    }
  };

  const register = async (username, email, password, language = 'fa', profileData = null) => {
    try {
      const requestData = {
        username,
        email,
        password,
        language
      };
      
      if (profileData) {
        requestData.profile = profileData;
      }
      
      const response = await axios.post('http://localhost:5000/api/register', requestData);
      const { access_token, user: userData } = response.data;
      
      // Ensure token is stored correctly
      if (access_token) {
        const cleanToken = access_token.trim();
        localStorage.setItem('token', cleanToken);
        setToken(cleanToken);
        axios.defaults.headers.common['Authorization'] = `Bearer ${cleanToken}`;
        setUser(userData);
        return { success: true };
      } else {
        return { success: false, error: 'No token received from server' };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: error.response?.data?.error || 'Registration failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

