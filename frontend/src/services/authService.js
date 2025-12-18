// Authentication service - Login, Register, Logout
import api from './api';

export const authService = {
    // Register new user
    register: async (username, email, password) => {
        const response = await api.post('/auth/register', {
            username,
            email,
            password
        });
        return response.data;
    },

    // Login user
    login: async (username, password) => {
        const response = await api.post('/auth/login', {
            username,
            password
        });
        
        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        
        return response.data;
    },

    // Logout user
    logout: () => {
        localStorage.removeItem('token');
    },

    // Check if user is authenticated
    isAuthenticated: () => {
        return !!localStorage.getItem('token');
    },

    // Get current token
    getToken: () => {
        return localStorage.getItem('token');
    }
};
