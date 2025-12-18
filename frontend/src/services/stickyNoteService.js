// Sticky note service - Sticky notes on PDFs
import api from './api';

export const stickyNoteService = {
    // Get all sticky notes for a paper
    getAllStickyNotes: async (paperId) => {
        const response = await api.get(`/papers/${paperId}/sticky-notes`);
        return response.data;
    },

    // Create new sticky note
    createStickyNote: async (paperId, noteData) => {
        const response = await api.post(`/papers/${paperId}/sticky-notes`, {
            position_x: noteData.positionX,
            position_y: noteData.positionY,
            width: noteData.width,
            height: noteData.height,
            content: noteData.content
        });
        return response.data;
    },

    // Update sticky note
    updateStickyNote: async (noteId, noteData) => {
        const response = await api.put(`/papers/sticky-notes/${noteId}`, {
            position_x: noteData.positionX,
            position_y: noteData.positionY,
            width: noteData.width,
            height: noteData.height,
            content: noteData.content
        });
        return response.data;
    },

    // Delete single sticky note
    deleteStickyNote: async (noteId) => {
        const response = await api.delete(`/papers/sticky-notes/${noteId}`);
        return response.data;
    },

    // Delete all sticky notes for a paper
    deleteAllStickyNotes: async (paperId) => {
        const response = await api.delete(`/papers/${paperId}/sticky-notes/all`);
        return response.data;
    }
};