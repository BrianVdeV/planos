import { createBrowserRouter, Navigate, Outlet, useParams } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { LoginPage } from '@/features/auth/LoginPage';
import { useAuthStore } from '@/store/useAuthStore';

function ProtectedRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}

function ModulePlaceholder({ title, subtitle }: { title: string; subtitle?: string }) {
  const params = useParams();
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">
          {title} {params.id ? `#${params.id}` : ''}
        </h2>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-2xs dark:border-slate-800 dark:bg-slate-900">
        <p className="text-sm text-slate-600 dark:text-slate-400">
          {subtitle ?? `Vista del módulo "${title}" lista para conectarse en la Fase 4.`}
        </p>
      </div>
    </div>
  );
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          {
            path: '/',
            element: <Navigate to="/actividades" replace />,
          },
          {
            path: '/dashboard/proyectos',
            element: <ModulePlaceholder title="Tablero de Control — Proyectos" />,
          },
          {
            path: '/dashboard/gastos',
            element: <ModulePlaceholder title="Tablero de Control — Gastos" />,
          },
          {
            path: '/actividades',
            element: <ModulePlaceholder title="Ingresar Actividades (Inicio)" />,
          },
          {
            path: '/calendario',
            element: <ModulePlaceholder title="Calendario" />,
          },
          {
            path: '/gastos',
            element: <ModulePlaceholder title="Gastos" />,
          },
          {
            path: '/kanban_tarea',
            element: <ModulePlaceholder title="Agenda — Tareas" />,
          },
          {
            path: '/kanban',
            element: <ModulePlaceholder title="Agenda — Tablero Kanban" />,
          },
          {
            path: '/informes/detallado',
            element: <ModulePlaceholder title="Informes — Detallado de tareas" />,
          },
          {
            path: '/informes/actividades',
            element: <ModulePlaceholder title="Informes — Detallado de actividades" />,
          },
          {
            path: '/informes/resumen',
            element: <ModulePlaceholder title="Informes — Reporte de personal" />,
          },
          {
            path: '/informes/promedio',
            element: <ModulePlaceholder title="Informes — Promedio de tareas" />,
          },
          {
            path: '/informes/gastos',
            element: <ModulePlaceholder title="Informes — Gastos" />,
          },
          {
            path: '/mapa',
            element: <ModulePlaceholder title="Ubicaciones — Mapa" />,
          },
          {
            path: '/proyectos',
            element: <ModulePlaceholder title="Proyectos (OTs)" />,
          },
          {
            path: '/proyectos/:id',
            element: <ModulePlaceholder title="Proyecto Detallado" />,
          },
          {
            path: '/expedientes',
            element: <ModulePlaceholder title="Expedientes — Sunarp" />,
          },
          {
            path: '/municipalidad-otros',
            element: <ModulePlaceholder title="Expedientes — Municipalidad y Otros" />,
          },
          {
            path: '/aprobaciones',
            element: <ModulePlaceholder title="Finanzas — Aprobaciones" />,
          },
          {
            path: '/cotizaciones',
            element: <ModulePlaceholder title="Finanzas — Cotizaciones" />,
          },
          {
            path: '/equipo',
            element: <ModulePlaceholder title="Equipo (Administración)" />,
          },
          {
            path: '/equipo/user',
            element: <ModulePlaceholder title="Equipo" />,
          },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/actividades" replace />,
  },
]);
