import { createContext, useContext, useState } from 'react';

const backendUrl: string = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8080';

interface AuthContextType {
  accessToken: string | null;
  refreshToken: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  register: (username: string, email: string, password: string) => Promise<boolean>;
  logout: () => void;
  authFetch: (input: RequestInfo, init?: RequestInit) => Promise<Response>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [accessToken, setAccessToken] = useState<string | null>(localStorage.getItem('accessToken'));
  const [refreshToken, setRefreshToken] = useState<string | null>(localStorage.getItem('refreshToken'));

  const login = async (username: string, password: string) => {
    const response = await fetch(`${backendUrl}/api/auth/signin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!response.ok) return false;
    const data = await response.json();
    setAccessToken(data.accessToken);
    setRefreshToken(data.refreshToken);
    localStorage.setItem('accessToken', data.accessToken);
    localStorage.setItem('refreshToken', data.refreshToken);
    return true;
  };

  const register = async (username: string, email: string, password: string) => {
    const response = await fetch(`${backendUrl}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password, role: ['user'] }),
    });
    return response.ok;
  };

  const logout = () => {
    setAccessToken(null);
    setRefreshToken(null);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  };

  const refreshAccessToken = async (): Promise<boolean> => {
    if (!refreshToken) return false;

    const response = await fetch(`${backendUrl}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refreshToken }),
    });

    if (!response.ok) {
      logout(); // clear invalid tokens
      return false;
    }

    const data = await response.json();
    setAccessToken(data.accessToken);
    localStorage.setItem('accessToken', data.accessToken);
    return true;
  };

  const authFetch = async (input: RequestInfo, init: RequestInit = {}, retry = true): Promise<Response> => {
    if (!accessToken) throw new Error("No access token");

    const modifiedInit: RequestInit = {
      ...init,
      headers: {
        ...(init.headers || {}),
        Authorization: `Bearer ${accessToken}`,
      },
    };

    const response = await fetch(input, modifiedInit);

    if (response.status === 401 && retry) {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        return authFetch(input, init, false); // retry once
      }
    }

    return response;
  };

  return (
    <AuthContext.Provider value={{ accessToken, refreshToken, login, register, logout, authFetch }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
