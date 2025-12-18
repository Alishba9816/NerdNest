// Category service - All category-related API calls
import api from './api';

export const categoryService = {
    // ===== Category CRUD =====
    
    // Get all top-level categories (categories without parents)
    getAllCategories: async () => {
        const response = await api.get('/categories/view_all');
        return response.data;
    },

    // Get specific category with its papers
    getCategory: async (categoryId) => {
        const response = await api.get(`/categories/view/${categoryId}`);
        return response.data;
    },

    // Create new category
    createCategory: async (categoryData) => {
        const response = await api.post('/categories/create', {
            name: categoryData.name,
            color: categoryData.color || '#3498db',
            icon: categoryData.icon || 'fa-folder',
            parent_id: categoryData.parentId || null
        });
        return response.data;
    },

    // Update category
    updateCategory: async (categoryId, categoryData) => {
        const response = await api.put(`/categories/${categoryId}/update`, {
            name: categoryData.name,
            color: categoryData.color,
            icon: categoryData.icon,
            parent_id: categoryData.parentId
        });
        return response.data;
    },

    // Delete category
    deleteCategory: async (categoryId) => {
        const response = await api.delete(`/categories/${categoryId}/delete`);
        return response.data;
    },

    // ===== Category Hierarchy =====

    // Get child categories for a parent
    getChildCategories: async (categoryId) => {
        const response = await api.get(`/categories/${categoryId}/children`);
        return response.data;
    },

    // Get available parent categories (for editing, avoids circular reference)
    getAvailableParents: async (categoryId) => {
        const response = await api.get(`/categories/${categoryId}/available_parents`);
        return response.data;
    },

    // ===== Helper Methods =====

    // Build category tree structure (hierarchical)
    buildCategoryTree: (categories) => {
        const categoryMap = new Map();
        const rootCategories = [];

        // First pass: create map of all categories
        categories.forEach(cat => {
            categoryMap.set(cat.id, { ...cat, children: [] });
        });

        // Second pass: build tree structure
        categories.forEach(cat => {
            if (cat.parent_id) {
                const parent = categoryMap.get(cat.parent_id);
                if (parent) {
                    parent.children.push(categoryMap.get(cat.id));
                } else {
                    // Parent not found, treat as root
                    rootCategories.push(categoryMap.get(cat.id));
                }
            } else {
                rootCategories.push(categoryMap.get(cat.id));
            }
        });

        return rootCategories;
    },

    // Flatten category tree to list with indentation levels
    flattenCategories: (categories, level = 0) => {
        let flattened = [];
        
        categories.forEach(cat => {
            flattened.push({ ...cat, level });
            if (cat.children && cat.children.length > 0) {
                flattened = flattened.concat(
                    categoryService.flattenCategories(cat.children, level + 1)
                );
            }
        });

        return flattened;
    },

    // Get full category path (breadcrumb)
    getCategoryPath: async (categoryId) => {
        const path = [];
        let currentId = categoryId;

        while (currentId) {
            const response = await api.get(`/categories/view/${currentId}`);
            const category = response.data.category;
            path.unshift(category); // Add to beginning
            currentId = category.parent_id;
        }

        return path;
    }
};

export default categoryService;