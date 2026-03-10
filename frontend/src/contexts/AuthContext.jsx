import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { userAuthApi } from '@/lib/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [onlineUsers, setOnlineUsers] = useState([]);

  // Check for existing session on mount
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('auth_user');
    
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
        // Verify token is still valid
        userAuthApi.getCurrentUser()
          .then(res => {
            setUser(res.data);
            localStorage.setItem('auth_user', JSON.stringify(res.data));
          })
          .catch(() => {
            // Token invalid, clear storage
            localStorage.removeItem('auth_token');
            localStorage.removeItem('auth_user');
            setUser(null);
          })
          .finally(() => setLoading(false));
      } catch {
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, []);

  // Poll for online users every 30 seconds
  useEffect(() => {
    if (!user) return;

    const fetchOnlineUsers = async () => {
      try {
        const res = await userAuthApi.getAllUsers();
        setOnlineUsers(res.data);
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    };

    fetchOnlineUsers();
    const interval = setInterval(fetchOnlineUsers, 30000);
    return () => clearInterval(interval);
  }, [user]);

  const login = useCallback(async (username, password) => {
    const res = await userAuthApi.login(username, password);
    const { token, user: userData } = res.data;
    
    localStorage.setItem('auth_token', token);
    localStorage.setItem('auth_user', JSON.stringify(userData));
    setUser(userData);
    
    return userData;
  }, []);

  const logout = useCallback(async () => {
    try {
      await userAuthApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      setUser(null);
    }
  }, []);

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
    onlineUsers,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
