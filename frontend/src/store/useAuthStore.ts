import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  setTokens: (access: string, refresh?: string) => void;
  setUser: (user: User | null) => void;
  loginSuccess: (access: string, refresh: string, user?: User | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      setTokens: (access, refresh) =>
        set((state) => ({
          accessToken: access,
          refreshToken: refresh ?? state.refreshToken,
          isAuthenticated: Boolean(access),
        })),

      setUser: (user) => set({ user }),

      loginSuccess: (access, refresh, user = null) =>
        set({
          accessToken: access,
          refreshToken: refresh,
          user,
          isAuthenticated: true,
        }),

      logout: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        }),
    }),
    {
      name: 'planos-auth-storage',
    }
  )
);
