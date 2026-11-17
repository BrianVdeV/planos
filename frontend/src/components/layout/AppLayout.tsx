import { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { authService } from '@/services/auth.service';
import { useAuthStore } from '@/store/useAuthStore';
import { useUIStore } from '@/store/useUIStore';
import { cn } from '@/lib/utils';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { GlobalSearchModal } from './GlobalSearchModal';

export function AppLayout() {
  const theme = useUIStore((state) => state.theme);
  const isSidebarCollapsed = useUIStore((state) => state.isSidebarCollapsed);
  const setUser = useAuthStore((state) => state.setUser);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  // Sincronizar la clase 'dark' en <html> cuando carga o cambia el tema
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  // Obtener los datos del colaborador/usuario actual (/api/users/me/)
  const { data: currentUser } = useQuery({
    queryKey: ['auth-me'],
    queryFn: authService.getMe,
    enabled: isAuthenticated,
  });

  useEffect(() => {
    if (currentUser) {
      setUser(currentUser);
    }
  }, [currentUser, setUser]);

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 transition-colors dark:bg-slate-950 dark:text-slate-100">
      {/* Menú Lateral */}
      <Sidebar />

      {/* Contenedor Principal desplazado según el ancho del Sidebar */}
      <div
        className={cn(
          'flex min-h-screen flex-col transition-all duration-200',
          isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'
        )}
      >
        <Topbar />

        <main className="flex-1 p-4 lg:p-6">
          <Outlet />
        </main>

        {/* Footer idéntico a base.html */}
        <footer className="border-t border-slate-200 bg-white px-6 py-4 text-xs text-slate-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
          <div className="flex flex-col items-center justify-between gap-2 sm:flex-row">
            <div>{new Date().getFullYear()} © Planos Perú</div>
            <div className="hidden gap-4 sm:flex">
              <span className="cursor-pointer hover:text-slate-700 dark:hover:text-slate-200">
                Acerca
              </span>
              <span className="cursor-pointer hover:text-slate-700 dark:hover:text-slate-200">
                Soporte
              </span>
              <span className="cursor-pointer hover:text-slate-700 dark:hover:text-slate-200">
                Contacto
              </span>
            </div>
          </div>
        </footer>
      </div>

      {/* Modal de Búsqueda Global de OTs */}
      <GlobalSearchModal />
    </div>
  );
}
