// Dashboard service - Dashboard and search
import api from './api';

export const dashboardService = {
    // Get dashboard data
    getDashboardData: async () => {
        const response = await api.get('/dashboard');
        return response.data;
    },

    // Search papers and categories
    searchAll: async (query) => {
        const response = await api.get('/search-all', {
            params: { q: query }
        });
        return response.data;
    }
};