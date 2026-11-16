import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Lock, LogIn, User as UserIcon } from 'lucide-react';
import { toast } from 'sonner';
import { authService } from '@/services/auth.service';
import { useAuthStore } from '@/store/useAuthStore';

export function LoginPage() {
  const navigate = useNavigate();
  const loginSuccess = useAuthStore((state) => state.loginSuccess);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const loginMutation = useMutation({
    mutationFn: authService.login,
    onSuccess: (tokens) => {
      loginSuccess(tokens.access, tokens.refresh);
      toast.success('¡Bienvenido a Planos Perú!');
      navigate('/', { replace: true });
    },
    onError: () => {
      toast.error('Credenciales incorrectas. Verifica tu usuario y contraseña.');
    },
  });

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!username.trim() || !password) return;
    loginMutation.mutate({ username: username.trim(), password });
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4 dark:bg-slate-950">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-lg dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Planos Perú Intranet
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Ingresa tus credenciales para continuar
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="username"
              className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
            >
              Usuario
            </label>
            <div className="relative">
              <UserIcon className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                id="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Tu nombre de usuario"
                className="w-full rounded-lg border border-slate-300 bg-white py-2.5 pr-3 pl-9 text-sm text-slate-900 focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="password"
              className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
            >
              Contraseña
            </label>
            <div className="relative">
              <Lock className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-lg border border-slate-300 bg-white py-2.5 pr-3 pl-9 text-sm text-slate-900 focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loginMutation.isPending}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60"
          >
            <LogIn className="h-4 w-4" />
            {loginMutation.isPending ? 'Ingresando...' : 'Iniciar Sesión'}
          </button>
        </form>
      </div>
    </div>
  );
}
