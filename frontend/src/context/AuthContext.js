import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
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
  const justLoggedInRef = useRef(false);

  // Initialize auth state on mount only
  useEffect(() => {
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
            
            // Check if we have a valid token before clearing
            const currentToken = localStorage.getItem('token');
            if (currentToken && currentToken.trim() !== '') {
              console.warn('Axios interceptor: Authentication error detected, clearing token');
              console.warn('Error URL:', url);
              console.warn('Error status:', status);
              localStorage.removeItem('token');
              setToken(null);
              setUser(null);
              delete axios.defaults.headers.common['Authorization'];
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
      axios.defaults.headers.common['Authorization'] = `Bearer ${cleanToken}`;
      
      console.log('Fetching user with token:', cleanToken.substring(0, 20) + '...');
      const response = await axios.get('http://localhost:5000/api/user');
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
      
      // Only clear token and user on actual authentication errors (401/422)
      // Don't clear on network errors, CORS errors, or other errors
      if (error.response) {
        const status = error.response.status;
        if (status === 401 || status === 422) {
          if (preserveExistingUser) {
            // Don't clear token or user if we're preserving existing user (e.g., after login)
            console.warn('Authentication error (401/422) but preserveExistingUser=true, keeping token and user');
          } else {
            console.warn('Authentication error (401/422), clearing token and user');
            localStorage.removeItem('token');
            setToken(null);
            setUser(null);
            delete axios.defaults.headers.common['Authorization'];
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
      
      const response = await axios.post('http://localhost:5000/api/login', {
        username,
        password
      }, config);
      
      const { access_token, user: userData } = response.data;
      
      // Ensure token is stored correctly
      if (access_token) {
        const cleanToken = access_token.trim();
        console.log('Login successful, storing token:', cleanToken.substring(0, 20) + '...');
        localStorage.setItem('token', cleanToken);
        setToken(cleanToken);
        axios.defaults.headers.common['Authorization'] = `Bearer ${cleanToken}`;
        
        // Set user from login response - don't call fetchUser immediately
        // The user data from login is sufficient, and we'll verify it later if needed
        setUser(userData);
        setLoading(false);
        justLoggedInRef.current = true; // Flag that we just logged in
        console.log('User set after login:', userData);
        
        // Clear the flag after a short delay to allow any immediate requests to complete
        setTimeout(() => {
          justLoggedInRef.current = false;
        }, 3000);
        
        // DON'T call fetchUser immediately after login - the user data from login is sufficient
        // fetchUser will be called on page reload if needed
        // This prevents any race conditions or immediate failures from clearing the user
        
        return { success: true };
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
      
      const response = await axios.post('http://localhost:5000/api/register', requestData, config);
      const { access_token, user: userData } = response.data;
      
      // Ensure token is stored correctly
      if (access_token) {
        const cleanToken = access_token.trim();
        console.log('Registration successful, storing token:', cleanToken.substring(0, 20) + '...');
        localStorage.setItem('token', cleanToken);
        setToken(cleanToken);
        axios.defaults.headers.common['Authorization'] = `Bearer ${cleanToken}`;
        setUser(userData);
        setLoading(false);
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

