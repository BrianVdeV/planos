import { useState } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart3,
  BookOpen,
  Calendar,
  ChevronDown,
  ChevronRight,
  ClipboardList,
  Clock,
  Coins,
  DollarSign,
  FileText,
  Gauge,
  KanbanSquare,
  LayoutDashboard,
  MapPin,
  ReceiptText,
  Users,
  X,
} from 'lucide-react';
import { notificacionesService } from '@/services/notificaciones.service';
import { useAuthStore } from '@/store/useAuthStore';
import { useUIStore } from '@/store/useUIStore';
import { cn } from '@/lib/utils';

export function Sidebar() {
  const location = useLocation();
  const user = useAuthStore((state) => state.user);
  const isSuperuser = Boolean(user?.is_superuser);

  const isCollapsed = useUIStore((state) => state.isSidebarCollapsed);
  const isMobileOpen = useUIStore((state) => state.isMobileSidebarOpen);
  const setMobileSidebarOpen = useUIStore((state) => state.setMobileSidebarOpen);

  // Estado de menús colapsables (idénticos a sidebar.html)
  const [openMenus, setOpenMenus] = useState<Record<string, boolean>>({
    dashboard: location.pathname.startsWith('/dashboard'),
    agenda:
      location.pathname.startsWith('/kanban') ||
      location.pathname.startsWith('/kanban_tarea'),
    informes: location.pathname.startsWith('/informes'),
    expedientes:
      location.pathname.startsWith('/expedientes') ||
      location.pathname.startsWith('/municipalidad-otros'),
    finanzas:
      location.pathname.startsWith('/aprobaciones') ||
      location.pathname.startsWith('/cotizaciones'),
  });

  const toggleMenu = (key: string) => {
    setOpenMenus((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  // Consulta al endpoint /sidebar que retorna { agenda, pending, rejected }
  const { data: badges } = useQuery({
    queryKey: ['sidebar-badges'],
    queryFn: notificacionesService.getSidebarBadges,
    refetchInterval: 60 * 1000, // Refrescar cada minuto
  });

  const agendaBadge = badges?.agenda ?? 0;
  const pendingBadge = badges?.pending ?? 0;
  const rejectedBadge = badges?.rejected ?? 0;

  // Detectar si estamos viendo un proyecto detallado (/proyectos/:id) igual que {% if ot %} en sidebar.html
  const isProyectoDetallado = /^\/proyectos\/\d+/.test(location.pathname);

  const navItemClass = ({ isActive }: { isActive: boolean }) =>
    cn(
      'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
      isActive
        ? 'bg-blue-600/15 text-blue-500 dark:bg-blue-500/20 dark:text-blue-400'
        : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-100',
      isCollapsed && 'justify-center px-2'
    );

  const subNavItemClass = ({ isActive }: { isActive: boolean }) =>
    cn(
      'block rounded-md py-2 pr-3 pl-9 text-sm transition-colors',
      isActive
        ? 'font-semibold text-white'
        : 'text-slate-400 hover:text-slate-200'
    );

  const closeMobileIfOpen = () => {
    if (isMobileOpen) setMobileSidebarOpen(false);
  };

  return (
    <>
      {/* Overlay móvil */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-xs lg:hidden"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex flex-col bg-[#313a46] text-slate-300 transition-all duration-200 dark: border-r dark:border-slate-800 dark:bg-slate-900',
          isCollapsed ? 'w-20' : 'w-64',
          isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Brand Logo */}
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-slate-700/50 px-4">
          <Link
            to="/actividades"
            onClick={closeMobileIfOpen}
            className="flex items-center justify-center w-full"
          >
            {isCollapsed ? (
              <img
                src="/images/logo-sm.png"
                alt="Planos Perú"
                className="h-8 w-auto object-contain"
              />
            ) : (
              <img
                src="/images/logo.png"
                alt="Planos Perú"
                className="h-8 w-auto object-contain"
              />
            )}
          </Link>

          <button
            type="button"
            onClick={() => setMobileSidebarOpen(false)}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Menú de Navegación */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {/* 1. Dashboard (Superusuario ve submenú Proyectos / Gastos; Usuario normal ve enlace directo) */}
          {isSuperuser ? (
            <div>
              <button
                type="button"
                onClick={() => toggleMenu('dashboard')}
                title="Dashboard"
                className={cn(
                  'flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400 transition-colors hover:bg-slate-800/60 hover:text-slate-100',
                  isCollapsed && 'justify-center px-2'
                )}
              >
                <span className="flex items-center gap-3">
                  <LayoutDashboard className="h-5 w-5 shrink-0" />
                  {!isCollapsed && <span>Dashboard</span>}
                </span>
                {!isCollapsed &&
                  (openMenus.dashboard ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  ))}
              </button>
              {!isCollapsed && openMenus.dashboard && (
                <div className="mt-1 space-y-0.5">
                  <NavLink
                    to="/dashboard/proyectos"
                    onClick={closeMobileIfOpen}
                    className={subNavItemClass}
                  >
                    Proyectos
                  </NavLink>
                  <NavLink
                    to="/dashboard/gastos"
                    onClick={closeMobileIfOpen}
                    className={subNavItemClass}
                  >
                    Gastos
                  </NavLink>
                </div>
              )}
            </div>
          ) : (
            <NavLink
              to="/dashboard/proyectos"
              onClick={closeMobileIfOpen}
              title="Dashboard"
              className={navItemClass}
            >
              <Gauge className="h-5 w-5 shrink-0" />
              {!isCollapsed && <span>Dashboard</span>}
            </NavLink>
          )}

          {/* 2. Inicio */}
          <NavLink
            to="/actividades"
            onClick={closeMobileIfOpen}
            title="Inicio"
            className={navItemClass}
          >
            <Clock className="h-5 w-5 shrink-0" />
            {!isCollapsed && <span>Inicio</span>}
          </NavLink>

          {/* 3. Calendario */}
          <NavLink
            to="/calendario"
            onClick={closeMobileIfOpen}
            title="Calendario"
            className={navItemClass}
          >
            <Calendar className="h-5 w-5 shrink-0" />
            {!isCollapsed && <span>Calendario</span>}
          </NavLink>

          {/* 4. Gastos (con badge rejected_expenses) */}
          <NavLink
            to="/gastos"
            onClick={closeMobileIfOpen}
            title="Gastos"
            className={navItemClass}
          >
            <Coins className="h-5 w-5 shrink-0" />
            {!isCollapsed && (
              <span className="flex flex-1 items-center justify-between">
                <span>Gastos</span>
                {rejectedBadge > 0 && (
                  <span className="inline-flex items-center justify-center rounded-full bg-red-500 px-2 py-0.5 text-xs font-semibold text-white">
                    {rejectedBadge}
                  </span>
                )}
              </span>
            )}
          </NavLink>

          {/* 5. Agenda (con badge-agenda) */}
          <div>
            <button
              type="button"
              onClick={() => toggleMenu('agenda')}
              title="Agenda"
              className={cn(
                'flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400 transition-colors hover:bg-slate-800/60 hover:text-slate-100',
                isCollapsed && 'justify-center px-2'
              )}
            >
              <span className="flex items-center gap-3">
                <KanbanSquare className="h-5 w-5 shrink-0" />
                {!isCollapsed && <span>Agenda</span>}
              </span>
              {!isCollapsed && (
                <span className="flex items-center gap-1.5">
                  {agendaBadge > 0 && (
                    <span className="inline-flex items-center justify-center rounded-full bg-slate-600 px-2 py-0.5 text-xs font-semibold text-white">
                      {agendaBadge}
                    </span>
                  )}
                  {openMenus.agenda ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </span>
              )}
            </button>
            {!isCollapsed && openMenus.agenda && (
              <div className="mt-1 space-y-0.5">
                {isSuperuser && (
                  <NavLink
                    to="/kanban_tarea"
                    onClick={closeMobileIfOpen}
                    className={subNavItemClass}
                  >
                    Tareas
                  </NavLink>
                )}
                <NavLink
                  to="/kanban"
                  onClick={closeMobileIfOpen}
                  className={subNavItemClass}
                >
                  Kanban
                </NavLink>
              </div>
            )}
          </div>

          {/* SECCIÓN: ANALIZAR */}
          {!isCollapsed && (
            <div className="pt-4 pb-1 pl-3 text-[11px] font-bold tracking-wider text-slate-500 uppercase">
              Analizar
            </div>
          )}

          {/* 6. Informes */}
          <div>
            <button
              type="button"
              onClick={() => toggleMenu('informes')}
              title="Informes"
              className={cn(
                'flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400 transition-colors hover:bg-slate-800/60 hover:text-slate-100',
                isCollapsed && 'justify-center px-2'
              )}
            >
              <span className="flex items-center gap-3">
                <BarChart3 className="h-5 w-5 shrink-0" />
                {!isCollapsed && <span>Informes</span>}
              </span>
              {!isCollapsed &&
                (openMenus.informes ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                ))}
            </button>
            {!isCollapsed && openMenus.informes && (
              <div className="mt-1 space-y-0.5">
                <NavLink
                  to="/informes/detallado"
                  onClick={closeMobileIfOpen}
                  className={subNavItemClass}
                >
                  Detallado de tareas
                </NavLink>
                <NavLink
                  to="/informes/actividades"
                  onClick={closeMobileIfOpen}
                  className={subNavItemClass}
                >
                  Detallado de actividades
                </NavLink>
                {isSuperuser && (
                  <>
                    <NavLink
                      to="/informes/resumen"
                      onClick={closeMobileIfOpen}
                      className={subNavItemClass}
                    >
                      Reporte de personal
                    </NavLink>
                    <NavLink
                      to="/informes/promedio"
                      onClick={closeMobileIfOpen}
                      className={subNavItemClass}
                    >
                      Promedio de tareas
                    </NavLink>
                    <NavLink
                      to="/informes/gastos"
                      onClick={closeMobileIfOpen}
                      className={subNavItemClass}
                    >
                      Gastos
                    </NavLink>
                  </>
                )}
              </div>
            )}
          </div>

          {/* 7. Ubicaciones */}
          <NavLink
            to="/mapa"
            onClick={closeMobileIfOpen}
            title="Ubicaciones"
            className={navItemClass}
          >
            <MapPin className="h-5 w-5 shrink-0" />
            {!isCollapsed && <span>Ubicaciones</span>}
          </NavLink>

          {/* 8. Base de conocimientos */}
          <a
            href="https://conoce.planosperu.com.pe/"
            target="_blank"
            rel="noreferrer"
            title="Base de conocimientos"
            className={cn(
              'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400 transition-colors hover:bg-slate-800/60 hover:text-slate-100',
              isCollapsed && 'justify-center px-2'
            )}
          >
            <BookOpen className="h-5 w-5 shrink-0" />
            {!isCollapsed && <span>Base de conocimientos</span>}
          </a>

          {/* SECCIÓN: GESTIONAR */}
          {!isCollapsed && (
            <div className="pt-4 pb-1 pl-3 text-[11px] font-bold tracking-wider text-slate-500 uppercase">
              Gestionar
            </div>
          )}

          {/* 9. Proyectos */}
          <NavLink
            to="/proyectos"
            end
            onClick={closeMobileIfOpen}
            title="Proyectos"
            className={navItemClass}
          >
            <FileText className="h-5 w-5 shrink-0" />
            {!isCollapsed && <span>Proyectos</span>}
          </NavLink>

          {/* 9b. Proyecto detallado (solo visible cuando se está en /proyectos/:id) */}
          {isProyectoDetallado && (
            <div
              className={cn(
                'flex items-center gap-3 rounded-lg bg-blue-600/15 px-3 py-2.5 text-sm font-medium text-blue-400',
                isCollapsed && 'justify-center px-2'
              )}
              title="Proyecto detallado"
            >
              <ClipboardList className="h-5 w-5 shrink-0" />
              {!isCollapsed && <span>Proyecto detallado</span>}
            </div>
          )}

          {/* 10. Expedientes */}
          <div>
            <button
              type="button"
              onClick={() => toggleMenu('expedientes')}
              title="Expedientes"
              className={cn(
                'flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400 transition-colors hover:bg-slate-800/60 hover:text-slate-100',
                isCollapsed && 'justify-center px-2'
              )}
            >
              <span className="flex items-center gap-3">
                <ReceiptText className="h-5 w-5 shrink-0" />
                {!isCollapsed && <span>Expedientes</span>}
              </span>
              {!isCollapsed &&
                (openMenus.expedientes ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                ))}
            </button>
            {!isCollapsed && openMenus.expedientes && (
              <div className="mt-1 space-y-0.5">
                <NavLink
                  to="/expedientes"
                  onClick={closeMobileIfOpen}
                  className={subNavItemClass}
                >
                  Sunarp
                </NavLink>
                <NavLink
                  to="/municipalidad-otros"
                  onClick={closeMobileIfOpen}
                  className={subNavItemClass}
                >
                  Municipalidad y Otros
                </NavLink>
              </div>
            )}
          </div>

          {/* 11. Finanzas (solo superuser, con badge pending-expenses) */}
          {isSuperuser && (
            <div>
              <button
                type="button"
                onClick={() => toggleMenu('finanzas')}
                title="Finanzas"
                className={cn(
                  'flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400 transition-colors hover:bg-slate-800/60 hover:text-slate-100',
                  isCollapsed && 'justify-center px-2'
                )}
              >
                <span className="flex items-center gap-3">
                  <DollarSign className="h-5 w-5 shrink-0" />
                  {!isCollapsed && <span>Finanzas</span>}
                </span>
                {!isCollapsed && (
                  <span className="flex items-center gap-1.5">
                    {pendingBadge > 0 && (
                      <span className="inline-flex items-center justify-center rounded-full bg-amber-500 px-2 py-0.5 text-xs font-semibold text-slate-950">
                        {pendingBadge}
                      </span>
                    )}
                    {openMenus.finanzas ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </span>
                )}
              </button>
              {!isCollapsed && openMenus.finanzas && (
                <div className="mt-1 space-y-0.5">
                  <NavLink
                    to="/aprobaciones"
                    onClick={closeMobileIfOpen}
                    className={subNavItemClass}
                  >
                    Aprobaciones
                  </NavLink>
                  <NavLink
                    to="/cotizaciones"
                    onClick={closeMobileIfOpen}
                    className={subNavItemClass}
                  >
                    Cotizaciones
                  </NavLink>
                </div>
              )}
            </div>
          )}

          {/* SECCIÓN: COMPLEMENTOS */}
          {!isCollapsed && (
            <div className="pt-4 pb-1 pl-3 text-[11px] font-bold tracking-wider text-slate-500 uppercase">
              Complementos
            </div>
          )}

          {/* 12. Equipo */}
          <NavLink
            to={isSuperuser ? '/equipo' : '/equipo/user'}
            onClick={closeMobileIfOpen}
            title="Equipo"
            className={navItemClass}
          >
            <Users className="h-5 w-5 shrink-0" />
            {!isCollapsed && <span>Equipo</span>}
          </NavLink>
        </div>
      </aside>
    </>
  );
}
