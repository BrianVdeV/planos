import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import {
  ChevronDown,
  LogOut,
  Menu,
  Moon,
  Search,
  Sun,
} from 'lucide-react';
import { useAuthStore } from '@/store/useAuthStore';
import { useUIStore } from '@/store/useUIStore';

export function Topbar() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const theme = useUIStore((state) => state.theme);
  const toggleTheme = useUIStore((state) => state.toggleTheme);
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);
  const setMobileSidebarOpen = useUIStore((state) => state.setMobileSidebarOpen);
  const setSearchModalOpen = useUIStore((state) => state.setSearchModalOpen);

  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Cerrar dropdown al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Nombre del colaborador o username
  const displayName =
    user?.first_name || user?.last_name
      ? `${user.first_name ?? ''} ${user.last_name ?? ''}`.trim()
      : (user?.username ?? 'Colaborador');

  const areaName =
    user?.colaborador?.area_nombre || 'Área no asignada';

  const avatarUrl = user?.colaborador?.foto || '/images/avatar-1.svg';

  const handleLogout = () => {
    setIsDropdownOpen(false);
    logout();
    queryClient.clear();
    navigate('/login', { replace: true });
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white px-4 shadow-2xs transition-colors dark:border-slate-800 dark:bg-slate-900 lg:px-6">
      {/* Lado Izquierdo: Botón contraer sidebar + Botón modal de búsqueda global de OTs */}
      <div className="flex items-center gap-3">
        {/* Botón para móvil */}
        <button
          type="button"
          onClick={() => setMobileSidebarOpen(true)}
          aria-label="Abrir menú"
          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800 lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Botón para contraer/expandir sidebar en desktop */}
        <button
          type="button"
          onClick={toggleSidebar}
          aria-label="Contraer o expandir menú lateral"
          title="Contraer / Expandir menú"
          className="hidden rounded-lg p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800 lg:inline-flex"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Botón que abre el modal de búsqueda global de OTs */}
        <button
          type="button"
          onClick={() => setSearchModalOpen(true)}
          className="flex items-center gap-2.5 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-slate-500 transition hover:border-slate-300 hover:bg-slate-100 dark:border-slate-800 dark:bg-slate-800/60 dark:text-slate-400 dark:hover:border-slate-700 dark:hover:bg-slate-800"
        >
          <Search className="h-4 w-4 text-slate-400" />
          <span className="hidden sm:inline">Buscar OTs...</span>
          <kbd className="hidden rounded border border-slate-200 bg-white px-1.5 py-0.5 text-[10px] font-medium text-slate-400 sm:inline-block dark:border-slate-700 dark:bg-slate-900">
            Ctrl K
          </kbd>
        </button>
      </div>

      {/* Lado Derecho: Botón cambio de tema Claro/Oscuro + Colaborador con Dropdown */}
      <div className="flex items-center gap-3">
        {/* Botón para cambiar entre tema Claro y Oscuro */}
        <button
          type="button"
          onClick={toggleTheme}
          title={theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
          aria-label="Cambiar tema"
          className="rounded-lg p-2 text-slate-600 transition hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          {theme === 'dark' ? (
            <Sun className="h-5 w-5 text-amber-400" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </button>

        {/* Perfil del Colaborador + Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            type="button"
            onClick={() => setIsDropdownOpen((prev) => !prev)}
            className="flex items-center gap-2.5 rounded-lg border border-transparent px-2 py-1.5 transition hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <img
              src={avatarUrl}
              alt={displayName}
              onError={(e) => {
                e.currentTarget.src = '/images/avatar-1.svg';
              }}
              className="h-8 w-8 rounded-full object-cover ring-1 ring-slate-200 dark:ring-slate-700"
            />
            <div className="hidden text-left md:block">
              <p className="text-sm font-semibold leading-tight text-slate-800 dark:text-slate-100">
                {displayName}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {areaName}
              </p>
            </div>
            <ChevronDown className="h-4 w-4 text-slate-400" />
          </button>

          {isDropdownOpen && (
            <div className="absolute right-0 mt-2 w-52 origin-top-right rounded-xl border border-slate-200 bg-white py-1.5 shadow-lg dark:border-slate-800 dark:bg-slate-900">
              <div className="border-b border-slate-100 px-4 py-2 dark:border-slate-800">
                <p className="text-xs font-semibold text-slate-400 uppercase">
                  ¡Bienvenido!
                </p>
                <p className="truncate text-sm font-medium text-slate-800 dark:text-slate-200 md:hidden">
                  {displayName}
                </p>
              </div>

              <button
                type="button"
                onClick={handleLogout}
                className="flex w-full items-center gap-2.5 px-4 py-2 text-left text-sm font-medium text-red-600 transition hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/40"
              >
                <LogOut className="h-4 w-4" />
                <span>Cerrar Sesión</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
