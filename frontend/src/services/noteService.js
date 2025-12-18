// Note service - Paper notes API calls
import api from './api';

export const noteService = {
    // Get all notes for a paper
    getAllNotes: async (paperId) => {
        const response = await api.get(`/papers/${paperId}/notes`);
        return response.data;
    },

    // Create new note
    createNote: async (paperId, content) => {
        const response = await api.post(`/papers/${paperId}/notes`, {
            content
        });
        return response.data;
    },

    // Delete note
    deleteNote: async (noteId) => {
        const response = await api.delete(`/papers/notes/${noteId}`);
        return response.data;
    }
};

