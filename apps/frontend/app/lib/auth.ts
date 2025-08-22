const TOKEN_KEY = 'briefcase_token';
const REFRESH_KEY = 'briefcase_refresh_token';
const EXPIRES_AT_KEY = 'briefcase_token_expires_at';
const USER_KEY = 'briefcase_user';

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
  refresh_token?: string;
  expires_in?: number; // seconds
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export const authStorage = {
  getToken: (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken: (token: string): void => {
    if (typeof window === 'undefined') return;
    localStorage.setItem(TOKEN_KEY, token);
  },

  removeToken: (): void => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(TOKEN_KEY);
  },

  getRefreshToken: (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_KEY);
  },

  setRefreshToken: (token: string | null): void => {
    if (typeof window === 'undefined') return;
    if (token) {
      localStorage.setItem(REFRESH_KEY, token);
    } else {
      localStorage.removeItem(REFRESH_KEY);
    }
  },

  getExpiresAt: (): number | null => {
    if (typeof window === 'undefined') return null;
    const raw = localStorage.getItem(EXPIRES_AT_KEY);
    return raw ? Number(raw) : null;
  },

  setExpiresAt: (timestampMs: number | null): void => {
    if (typeof window === 'undefined') return;
    if (timestampMs) {
      localStorage.setItem(EXPIRES_AT_KEY, String(timestampMs));
    } else {
      localStorage.removeItem(EXPIRES_AT_KEY);
    }
  },

  getUser: (): User | null => {
    if (typeof window === 'undefined') return null;
    const user = localStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
  },

  setUser: (user: User): void => {
    if (typeof window === 'undefined') return;
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  removeUser: (): void => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(USER_KEY);
  },

  clear: (): void => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(EXPIRES_AT_KEY);
    localStorage.removeItem(USER_KEY);
  }
};

export const apiClient = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const doFetch = async (): Promise<Response> => {
      const token = authStorage.getToken();
      const url = `${this.baseURL}${endpoint}`;
      const config: RequestInit = {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
          ...options.headers,
        },
        ...options,
      };
      return fetch(url, config);
    };

    // First attempt
    let response = await doFetch();

    // If unauthorized, attempt one refresh and retry once
    if (response.status === 401) {
      const refreshed = await this.tryRefreshToken();
      if (refreshed) {
        response = await doFetch();
      }
    }

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  },

  async tryRefreshToken(): Promise<boolean> {
    try {
      const refreshToken = authStorage.getRefreshToken();
      if (!refreshToken) return false;
      const url = `${this.baseURL}/api/v1/auth/refresh`;
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      });
      if (!res.ok) return false;
      const data: { access_token: string; token_type: string; expires_in?: number } = await res.json();
      if (!data.access_token) return false;
      authStorage.setToken(data.access_token);
      if (data.expires_in) {
        authStorage.setExpiresAt(Date.now() + data.expires_in * 1000);
      }
      return true;
    } catch {
      return false;
    }
  },

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const result = await this.request<AuthResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: credentials.email, password: credentials.password }),
    });
    // Persist refresh and expiry if provided
    if (result.refresh_token) {
      authStorage.setRefreshToken(result.refresh_token);
    }
    if (typeof result.expires_in === 'number') {
      authStorage.setExpiresAt(Date.now() + result.expires_in * 1000);
    }
    return result;
  },

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/v1/users/me');
  }
};