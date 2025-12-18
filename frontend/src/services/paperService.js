// Paper service - All paper-related API calls
import api from './api';

export const paperService = {
    // Get all papers for current user
    getAllPapers: async () => {
        const response = await api.get('/papers');
        return response.data;
    },

    // Get single paper details
    getPaper: async (paperId) => {
        const response = await api.get(`/papers/${paperId}`);
        return response.data;
    },

    // Upload new paper with PDF file
    uploadPaper: async (formData) => {
        const response = await api.post('/papers/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    },

    // Delete paper
    deletePaper: async (paperId) => {
        const response = await api.delete(`/papers/${paperId}`);
        return response.data;
    },

    // Toggle read/unread status
    toggleReadStatus: async (paperId) => {
        const response = await api.put(`/papers/${paperId}/toggle-read`);
        return response.data;
    },

    // Download paper PDF
    downloadPaper: async (paperId) => {
        const response = await api.get(`/papers/${paperId}/download`, {
            responseType: 'blob'
        });
        return response.data;
    },

    // Get categories
    getCategories: async () => {
        const response = await api.get('/papers/categories');
        return response.data;
    }
};



export const paperCategoryMethods = {
    // Assign paper to category
    assignPaperToCategory: async (paperId, categoryId) => {
        // You'll need to add this route to your backend
        const response = await api.post(`/papers/${paperId}/categories`, {
            category_id: categoryId
        });
        return response.data;
    },

    // Remove paper from category
    removePaperFromCategory: async (paperId, categoryId) => {
        // You'll need to add this route to your backend
        const response = await api.delete(`/papers/${paperId}/categories/${categoryId}`);
        return response.data;
    },

    // Get all categories for a paper
    getPaperCategories: async (paperId) => {
        // You'll need to add this route to your backend
        const response = await api.get(`/papers/${paperId}/categories`);
        return response.data;
    },

    // Get all papers in a category
    getCategoryPapers: async (categoryId) => {
        // This already exists in your backend!
        const response = await api.get(`/categories/view/${categoryId}`);
        return response.data.papers;
    }
};

// Export everything
export default {
    ...paperService,
    ...paperCategoryMethods
};
