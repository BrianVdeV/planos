import { api } from './api';

export const informesService = {
  /**
   * Obtiene los datos de informes de tareas/actividades (/api/informes/)
   */
  getInformes: async (params?: Record<string, unknown>): Promise<unknown> => {
    const { data } = await api.get('/informes/', { params });
    return data;
  },

  /**
   * Datos de gráficos analíticos (/api/chart/)
   */
  getChartData: async (params?: Record<string, unknown>): Promise<unknown> => {
    const { data } = await api.get('/chart/', { params });
    return data;
  },
};
