// Tag service - Tag management and paper-tag associations
import api from './api';

export const tagService = {
    // ===== Tag CRUD =====
    
    // Get all tags
    getAllTags: async () => {
        const response = await api.get('/tags');
        return response.data;
    },

    // Create new tag
    createTag: async (name, color) => {
        const response = await api.post('/tags', {
            name,
            color
        });
        return response.data;
    },

    // Update tag
    updateTag: async (tagId, name, color) => {
        const response = await api.put(`/tags/${tagId}`, {
            name,
            color
        });
        return response.data;
    },

    // Delete tag
    deleteTag: async (tagId) => {
        const response = await api.delete(`/tags/${tagId}`);
        return response.data;
    },

    // ===== Paper-Tag Associations =====
    
    // Get tags for a specific paper
    getPaperTags: async (paperId) => {
        const response = await api.get(`/papers/${paperId}/tags`);
        return response.data;
    },

    // Add single tag to paper
    addTagToPaper: async (paperId, tagId) => {
        const response = await api.post(`/papers/${paperId}/tags`, {
            tag_id: tagId
        });
        return response.data;
    },

    // Add multiple tags to paper
    assignMultipleTags: async (paperId, tagIds) => {
        const response = await api.post(`/papers/${paperId}/tags/assign`, {
            tag_ids: tagIds
        });
        return response.data;
    },

    // Remove tag from paper
    removeTagFromPaper: async (paperId, tagId) => {
        const response = await api.delete(`/papers/${paperId}/tags/${tagId}`);
        return response.data;
    }
};

