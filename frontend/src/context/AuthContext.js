import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { getApiBase } from '../services/apiBase';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const API_BASE = getApiBase();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(() => {
    // Initialize from localStorage on mount
    const storedToken = localStorage.getItem('token');
    return storedToken && storedToken.trim() !== '' ? storedToken.trim() : null;
  });
  const justLoggedInRef = useRef(false);
  const initializedRef = useRef(false);

  // Initialize auth state on mount only
  useEffect(() => {
    // Prevent multiple initializations
    if (initializedRef.current) {
      return;
    }
    initializedRef.current = true;

    // Check localStorage on mount (source of truth)
    const storedToken = localStorage.getItem('token');
    
    if (storedToken && storedToken.trim() !== '') {
      const cleanToken = storedToken.trim();
      // Update state
      setToken(cleanToken);
      // Always set axios defaults
      axios.defaults.headers.common['Authorization'] = `Bearer ${cleanToken}`;
      // Fetch user data
      fetchUser();
    } else {
      // No token in localStorage
      setToken(null);
      // Clear any existing auth header
      delete axios.defaults.headers.common['Authorization'];
      setUser(null);
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount

  // Add axios interceptor for error handling
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        // Don't interfere with login/register endpoints
        const url = error.config?.url || '';
        if (url.includes('/api/login') || url.includes('/api/register')) {
          // Let login/register handle their own errors
          return Promise.reject(error);
        }
        
        // Don't clear token for /api/user endpoint - let fetchUser handle it
        // This prevents premature logout when fetchUser is called on page reload
        if (url.includes('/api/user')) {
          return Promise.reject(error);
        }
        
        // Only handle authentication errors, and only if we have a response
        if (error.response) {
          const status = error.response.status;
          if (status === 401 || status === 422) {
            // Don't clear token immediately after login - give it a moment to settle
            // This prevents race conditions where fetchUser might fail right after login
            if (justLoggedInRef.current) {
              console.warn('Axios interceptor: Auth error right after login, ignoring (might be race condition)');
              console.warn('Error URL:', url);
              return Promise.reject(error);
            }
            
            // For 422 errors, always treat as token error (Flask-JWT-Extended returns 422 for invalid tokens)
            // For 401 errors, check the error message
            const errorData = error.response.data || {};
            const errorMessage = (errorData.error || errorData.message || '').toLowerCase();
            const isTokenError = status === 422 || // 422 from Flask-JWT-Extended always means invalid token
                                 (status === 401 && errorMessage.includes('token') && 
                                  (errorMessage.includes('expired') || 
                                   errorMessage.includes('invalid') || 
                                   errorMessage.includes('missing')));
            
            // Check if we have a valid token before clearing
            const currentToken = localStorage.getItem('token');
            if (currentToken && currentToken.trim() !== '' && isTokenError) {
              console.warn('Axios interceptor: Token error detected, clearing token');
              console.warn('Error URL:', url);
              console.warn('Error status:', status);
              console.warn('Error message:', errorMessage);
              localStorage.removeItem('token');
              setToken(null);
              setUser(null);
              delete axios.defaults.headers.common['Authorization'];
            } else if (currentToken && currentToken.trim() !== '' && !isTokenError) {
              // Auth error but not specifically a token error - don't clear token
              // This might be a temporary backend issue or permission issue
              console.warn('Axios interceptor: Auth error but not a token error, keeping token');
              console.warn('Error URL:', url);
              console.warn('Error status:', status);
            }
          }
        }
        // Don't clear token on network errors - let the component handle it
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);

  const fetchUser = async (preserveExistingUser = false) => {
    try {
      const token = localStorage.getItem('token');
      if (!token || token.trim() === '') {
        console.log('No token found in localStorage, skipping user fetch');
        if (!preserveExistingUser) {
          setUser(null);
        }
        setLoading(false);
        return;
      }
      
      // Ensure token is properly formatted and set in axios defaults
      const cleanToken = token.trim();
      
      // Remove any existing "Bearer " prefix if accidentally added
      const tokenWithoutBearer = cleanToken.startsWith('Bearer ') 
        ? cleanToken.replace(/^Bearer\s+/i, '').trim() 
        : cleanToken;
      
      // Set axios defaults with proper format
      const authHeader = `Bearer ${tokenWithoutBearer}`;
      axios.defaults.headers.common['Authorization'] = authHeader;
      
      console.log('Fetching user with token:', tokenWithoutBearer.substring(0, 20) + '...');
      console.log('Authorization header format:', authHeader.substring(0, 30) + '...');
      console.log('Token length:', tokenWithoutBearer.length);
      console.log('Full token (for debugging):', tokenWithoutBearer);
      
      const response = await axios.get(`${API_BASE}/api/user`, {
        headers: {
          'Authorization': authHeader
        }
      });
      console.log('User fetched successfully:', response.data);
      setUser(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching user:', error);
      console.error('Error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      });
      
      // Only clear token and user if error explicitly indicates token is invalid/expired
      // Don't clear on network errors, CORS errors, or ambiguous auth errors
      if (error.response) {
        const status = error.response.status;
        const errorData = error.response.data || {};
        const errorMessage = (errorData.error || errorData.message || '').toLowerCase();
        
        // Check if error specifically mentions token expiration or invalidity
        const isTokenExpired = errorMessage.includes('token') && errorMessage.includes('expired');
        const isTokenInvalid = errorMessage.includes('token') && 
                              (errorMessage.includes('invalid') || 
                               errorMessage.includes('missing') ||
                               errorMessage.includes('format'));
        
        if (status === 401 || status === 422) {
          if (isTokenExpired || isTokenInvalid) {
            // Token is explicitly expired or invalid - clear it
            if (preserveExistingUser) {
              console.warn('Token expired/invalid but preserveExistingUser=true, keeping token and user');
            } else {
              console.warn('Token expired/invalid, clearing token and user');
              localStorage.removeItem('token');
              setToken(null);
              setUser(null);
              delete axios.defaults.headers.common['Authorization'];
            }
          } else {
            // Auth error but not specifically a token error - keep token
            // This might be a temporary backend issue, permission issue, or other auth problem
            console.warn('Authentication error (401/422) but not a token error, keeping token');
            console.warn('Error message:', errorMessage);
            if (!preserveExistingUser) {
              // Don't set user, but keep token for retry
              setUser(null);
            }
          }
        } else {
          // Non-auth error - keep token and user if preserveExistingUser is true
          if (!preserveExistingUser) {
            console.warn(`Non-auth error (${status}), keeping token but not setting user`);
            setUser(null);
          } else {
            console.warn(`Non-auth error (${status}), keeping existing user and token`);
          }
        }
      } else {
        // Network error or no response - keep token and user if preserveExistingUser is true
        // Never clear token on network errors - user might just be offline
        if (!preserveExistingUser) {
          console.warn('Network error or no response, keeping token. Error:', error.message);
          console.warn('User will need to refresh or retry when backend is available');
          setUser(null);
        } else {
          console.warn('Network error or no response, keeping existing user and token. Error:', error.message);
        }
      }
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      console.log('Login attempt for username:', username);
      // Make sure we don't send any auth headers for login
      const config = {
        headers: {
          'Content-Type': 'application/json'
        }
      };
      // Temporarily remove auth header if it exists
      const oldAuthHeader = axios.defaults.headers.common['Authorization'];
      if (oldAuthHeader) {
        delete axios.defaults.headers.common['Authorization'];
      }
      
      const response = await axios.post(`${API_BASE}/api/login`, {
        username,
        password
      }, config);
      
      const { access_token, user: userData } = response.data;
      
      // Ensure token is stored correctly
      if (access_token) {
        // Remove any accidental "Bearer " prefix from backend response
        let cleanToken = access_token.trim();
        if (cleanToken.startsWith('Bearer ')) {
          cleanToken = cleanToken.replace(/^Bearer\s+/i, '').trim();
        }
        
        console.log('Login successful, storing token:', cleanToken.substring(0, 20) + '...');
        console.log('Token length:', cleanToken.length);
        console.log('Token format check - starts with eyJ:', cleanToken.startsWith('eyJ'));
        
        localStorage.setItem('token', cleanToken);
        setToken(cleanToken);
        axios.defaults.headers.common['Authorization'] = `Bearer ${cleanToken}`;
        setUser(userData);
        justLoggedInRef.current = true;
        console.log('User set after login:', userData);

        // Load full user (with profile/gender) so theme applies immediately without reload
        try {
          await fetchUser(true);
        } catch (e) {
          // Keep minimal user on failure; theme may stay unisex until next load
        }
        setLoading(false);
        setTimeout(() => {
          justLoggedInRef.current = false;
        }, 3000);

        return { success: true, user: userData };
      } else {
        console.error('No access_token in response:', response.data);
        return { success: false, error: 'No token received from server' };
      }
    } catch (error) {
      console.error('Login error:', error);
      console.error('Login error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      });
      return { success: false, error: error.response?.data?.error || error.message || 'Login failed' };
    }
  };

  const register = async (username, email, password, language = 'fa', profileData = null) => {
    try {
      console.log('Registration attempt for username:', username);
      const requestData = {
        username,
        email,
        password,
        language
      };
      
      if (profileData) {
        requestData.profile = profileData;
      }
      
      // Make sure we don't send any auth headers for registration
      const config = {
        headers: {
          'Content-Type': 'application/json'
        }
      };
      // Temporarily remove auth header if it exists
      const oldAuthHeader = axios.defaults.headers.common['Authorization'];
      if (oldAuthHeader) {
        delete axios.defaults.headers.common['Authorization'];
      }
      
      const response = await axios.post(`${API_BASE}/api/register`, requestData, config);
      const { access_token, user: userData } = response.data;
      
      // Ensure token is stored correctly
      if (access_token) {
        // Remove any accidental "Bearer " prefix from backend response
        let cleanToken = access_token.trim();
        if (cleanToken.startsWith('Bearer ')) {
          cleanToken = cleanToken.replace(/^Bearer\s+/i, '').trim();
        }
        
        console.log('Registration successful, storing token:', cleanToken.substring(0, 20) + '...');
        console.log('Token length:', cleanToken.length);
        console.log('Token format check - starts with eyJ:', cleanToken.startsWith('eyJ'));
        
        localStorage.setItem('token', cleanToken);
        setToken(cleanToken);
        axios.defaults.headers.common['Authorization'] = `Bearer ${cleanToken}`;
        setUser(userData);
        justLoggedInRef.current = true;

        // Load full user (with profile/gender) so theme applies immediately without reload
        try {
          await fetchUser(true);
        } catch (e) {
          // Keep minimal user on failure
        }
        setLoading(false);
        setTimeout(() => {
          justLoggedInRef.current = false;
        }, 3000);
        console.log('User set after registration:', userData);
        return { success: true };
      } else {
        console.error('No access_token in response:', response.data);
        return { success: false, error: 'No token received from server' };
      }
    } catch (error) {
      console.error('Registration error:', error);
      console.error('Registration error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      });
      return { success: false, error: error.response?.data?.error || error.message || 'Registration failed' };
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

