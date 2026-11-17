import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { FileText, Loader2, Search, X } from 'lucide-react';
import { proyectosService } from '@/services/proyectos.service';
import { useUIStore } from '@/store/useUIStore';
import type { OT } from '@/types';

export function GlobalSearchModal() {
  const navigate = useNavigate();
  const isOpen = useUIStore((state) => state.isSearchModalOpen);
  const setSearchModalOpen = useUIStore((state) => state.setSearchModalOpen);

  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  // Debounce de 300ms igual que initSearch() en base.html
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query.trim());
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  // Limpiar búsqueda al cerrar el modal
  useEffect(() => {
    if (!isOpen) {
      setQuery('');
      setDebouncedQuery('');
    }
  }, [isOpen]);

  // Atajo de teclado global Ctrl+K / Cmd+K y Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setSearchModalOpen(!isOpen);
      } else if (e.key === 'Escape' && isOpen) {
        setSearchModalOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, setSearchModalOpen]);

  const { data, isFetching, isError } = useQuery({
    queryKey: ['global-ot-search', debouncedQuery],
    queryFn: () =>
      proyectosService.getOTs({ search: debouncedQuery, page_size: 10 }),
    enabled: isOpen && debouncedQuery.length >= 2,
  });

  if (!isOpen) return null;

  const resultados: OT[] = Array.isArray(data)
    ? data
    : (data?.results ?? []);
  const totalCount: number = Array.isArray(data)
    ? data.length
    : (data?.count ?? resultados.length);
  const limit = 10;
  const itemsToShow = resultados.slice(0, limit);

  const handleSelectOT = (id: number) => {
    setSearchModalOpen(false);
    navigate(`/proyectos/${id}`);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-slate-900/60 p-4 pt-20 backdrop-blur-xs"
      onClick={() => setSearchModalOpen(false)}
    >
      <div
        className="w-full max-w-2xl overflow-hidden rounded-xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header con Input de Búsqueda */}
        <div className="flex items-center border-b border-slate-200 px-4 py-3 dark:border-slate-800">
          <Search className="mr-3 h-5 w-5 shrink-0 text-slate-400" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar OTs por código o nombre..."
            className="w-full bg-transparent text-sm text-slate-900 placeholder-slate-400 focus:outline-none dark:text-slate-100"
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery('')}
              className="mr-1 rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          <button
            type="button"
            onClick={() => setSearchModalOpen(false)}
            className="ml-2 rounded-md border border-slate-200 px-2 py-0.5 text-xs font-medium text-slate-500 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-400 dark:hover:bg-slate-800"
          >
            ESC
          </button>
        </div>

        {/* Resultados */}
        <div className="max-h-96 overflow-y-auto">
          {debouncedQuery.length < 2 ? (
            <div className="p-6 text-center">
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Escribe al menos 2 caracteres para comenzar a buscar...
              </p>
            </div>
          ) : isFetching ? (
            <div className="flex items-center justify-center gap-2 p-6 text-sm text-slate-600 dark:text-slate-300">
              <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
              <span>Buscando...</span>
            </div>
          ) : isError ? (
            <div className="p-6 text-center">
              <p className="text-sm font-medium text-red-500">
                Error al buscar OTs. Intenta nuevamente.
              </p>
            </div>
          ) : itemsToShow.length === 0 ? (
            <div className="p-6 text-center">
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                No se encontraron resultados para &quot;{debouncedQuery}&quot;
              </p>
            </div>
          ) : (
            <div>
              <div className="sticky top-0 border-b border-slate-200 bg-slate-50/95 px-4 py-2 backdrop-blur-xs dark:border-slate-800 dark:bg-slate-900/95">
                <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  Encontrados{' '}
                  <span className="text-red-500">{totalCount}</span> resultados
                  {totalCount > limit && (
                    <span className="ml-1 font-normal text-slate-400">
                      (Top 10)
                    </span>
                  )}
                </p>
              </div>

              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {itemsToShow.map((ot) => {
                  const titulo = ot.id_str || `${ot.id} - ${ot.nombre}` || 'Sin ID';
                  return (
                    <button
                      key={ot.id}
                      type="button"
                      onClick={() => handleSelectOT(ot.id)}
                      className="flex w-full items-center gap-3 px-4 py-3 text-left transition hover:bg-slate-50 dark:hover:bg-slate-800/70"
                    >
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600 dark:bg-blue-950/60 dark:text-blue-400">
                        <FileText className="h-4 w-4" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-slate-800 dark:text-slate-100">
                          {titulo}
                        </p>
                      </div>
                    </button>
                  );
                })}
              </div>

              {totalCount > limit && (
                <div className="bg-slate-50 px-4 py-2.5 text-center dark:bg-slate-800/50">
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    Sé más específico para ver el resultado exacto.
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
