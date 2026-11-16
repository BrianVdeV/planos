import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ThemeMode = 'light' | 'dark';

interface UIState {
  theme: ThemeMode;
  isSidebarCollapsed: boolean;
  isMobileSidebarOpen: boolean;
  isSearchModalOpen: boolean;
  toggleTheme: () => void;
  setTheme: (theme: ThemeMode) => void;
  toggleSidebar: () => void;
  setMobileSidebarOpen: (open: boolean) => void;
  setSearchModalOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      theme: 'light',
      isSidebarCollapsed: false,
      isMobileSidebarOpen: false,
      isSearchModalOpen: false,

      toggleTheme: () =>
        set((state) => {
          const nextTheme: ThemeMode = state.theme === 'light' ? 'dark' : 'light';
          if (typeof document !== 'undefined') {
            document.documentElement.classList.toggle('dark', nextTheme === 'dark');
          }
          return { theme: nextTheme };
        }),

      setTheme: (theme) => {
        if (typeof document !== 'undefined') {
          document.documentElement.classList.toggle('dark', theme === 'dark');
        }
        set({ theme });
      },

      toggleSidebar: () =>
        set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),

      setMobileSidebarOpen: (open) => set({ isMobileSidebarOpen: open }),

      setSearchModalOpen: (open) => set({ isSearchModalOpen: open }),
    }),
    {
      name: 'planos-ui-storage',
      partialize: (state) => ({
        theme: state.theme,
        isSidebarCollapsed: state.isSidebarCollapsed,
      }),
    }
  )
);
