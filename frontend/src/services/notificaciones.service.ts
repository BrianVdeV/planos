import { api } from './api';
import type { NotificacionToast, SidebarBadges } from '@/types';

export const notificacionesService = {
  /**
   * Obtiene los contadores de badges del Sidebar (/sidebar)
   */
  getSidebarBadges: async (): Promise<SidebarBadges> => {
    const { data } = await api.get<SidebarBadges>('/sidebar', {
      baseURL: '', // El endpoint en intranet/urls.py está en la raíz '/sidebar'
    });
    return data;
  },

  /**
   * Obtiene las notificaciones pendientes tipo toast (/api/jquery-toast/)
   */
  getToastNotifications: async (): Promise<NotificacionToast[]> => {
    const { data } = await api.get<NotificacionToast[]>('/jquery-toast/');
    return data;
  },

  /**
   * Obtiene el listado general de notificaciones (/api/notificaciones/)
   */
  getNotificaciones: async (): Promise<unknown[]> => {
    const { data } = await api.get<unknown[]>('/notificaciones/');
    return data;
  },

  /**
   * Envía una consulta al asistente IA de Planos Perú (/chatbot/api/query/)
   */
  queryChatbot: async (message: string): Promise<{ response: string }> => {
    const { data } = await api.post<{ response: string }>(
      '/chatbot/api/query/',
      { message },
      { baseURL: '' }
    );
    return data;
  },
};
