import { api } from './api';
import type { Actividad, PaginatedResponse, Tarea } from '@/types';

export const kanbanService = {
  /**
   * Obtiene las tareas del tablero Kanban (Superusuario: /api/kanban/, Usuario normal: /api/kanban/mi-kanban/)
   */
  getKanbanTasks: async (
    isSuperuser: boolean,
    params?: Record<string, unknown>
  ): Promise<PaginatedResponse<Tarea> | Tarea[]> => {
    const endpoint = isSuperuser ? '/kanban/' : '/kanban/mi-kanban/';
    const { data } = await api.get<PaginatedResponse<Tarea> | Tarea[]>(endpoint, {
      params,
    });
    return data;
  },

  /**
   * Lista general de tareas (/api/tarea/)
   */
  getTareas: async (
    params?: Record<string, unknown>
  ): Promise<PaginatedResponse<Tarea> | Tarea[]> => {
    const { data } = await api.get<PaginatedResponse<Tarea> | Tarea[]>('/tarea/', {
      params,
    });
    return data;
  },

  /**
   * Detalle de una tarea (/api/tarea/:id/)
   */
  getTareaById: async (id: number): Promise<Tarea> => {
    const { data } = await api.get<Tarea>(`/tarea/${id}/`);
    return data;
  },

  /**
   * Crea una nueva tarea (/api/tarea/)
   */
  createTarea: async (payload: Partial<Tarea>): Promise<Tarea> => {
    const { data } = await api.post<Tarea>('/tarea/', payload);
    return data;
  },

  /**
   * Actualiza estado, orden o campos de una tarea (/api/tarea/:id/)
   */
  updateTarea: async (id: number, payload: Partial<Tarea>): Promise<Tarea> => {
    const { data } = await api.patch<Tarea>(`/tarea/${id}/`, payload);
    return data;
  },

  /**
   * Inicia una tarea desde el Kanban (/api/tarea/:id/iniciar/)
   */
  iniciarTarea: async (id: number): Promise<void> => {
    await api.post(`/tarea/${id}/iniciar/`);
  },

  /**
   * Lista de actividades registradas (/api/actividades/)
   */
  getActividades: async (
    params?: Record<string, unknown>
  ): Promise<PaginatedResponse<Actividad> | Actividad[]> => {
    const { data } = await api.get<PaginatedResponse<Actividad> | Actividad[]>(
      '/actividades/',
      { params }
    );
    return data;
  },

  /**
   * Crea o inicia una actividad (/api/actividades/)
   */
  createActividad: async (payload: Partial<Actividad>): Promise<Actividad> => {
    const { data } = await api.post<Actividad>('/actividades/', payload);
    return data;
  },

  /**
   * Actualiza una actividad (/api/actividades/:id/)
   */
  updateActividad: async (
    id: number,
    payload: Partial<Actividad>
  ): Promise<Actividad> => {
    const { data } = await api.patch<Actividad>(`/actividades/${id}/`, payload);
    return data;
  },

  /**
   * Elimina una actividad (/api/actividades/:id/)
   */
  deleteActividad: async (id: number): Promise<void> => {
    await api.delete(`/actividades/${id}/`);
  },
};
