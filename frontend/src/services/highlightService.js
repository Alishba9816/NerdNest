// Highlight service - Text highlighting API calls
import api from './api';

export const highlightService = {
    // Get all highlights for a paper
    getAllHighlights: async (paperId) => {
        const response = await api.get(`/papers/${paperId}/highlights`);
        return response.data;
    },

    // Create new highlight
    createHighlight: async (paperId, highlightData) => {
        const response = await api.post(`/papers/${paperId}/highlights`, {
            start_offset: highlightData.startOffset,
            end_offset: highlightData.endOffset,
            color: highlightData.color,
            text_content: highlightData.textContent
        });
        return response.data;
    },

    // Delete highlight
    deleteHighlight: async (paperId, highlightId) => {
        const response = await api.delete(
            `/papers/${paperId}/highlights/${highlightId}`
        );
        return response.data;
    }
};


