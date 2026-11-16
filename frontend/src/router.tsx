import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import { LoginPage } from '@/features/auth/LoginPage';
import { useAuthStore } from '@/store/useAuthStore';

function ProtectedRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}

function DashboardPlaceholder() {
  const logout = useAuthStore((state) => state.logout);

  return (
    <div className="min-h-screen bg-slate-50 p-8 dark:bg-slate-950">
      <div className="mx-auto max-w-4xl rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">
              Planos Perú — Frontend React + Vite (Fases 1 y 2 Completadas)
            </h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Infraestructura TypeScript, Tailwind CSS v4, Zustand, React Query, Recharts y capa de servicios JWT lista.
            </p>
          </div>
          <button
            type="button"
            onClick={logout}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            Cerrar sesión
          </button>
        </div>
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
        path: '/',
        element: <DashboardPlaceholder />,
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);
