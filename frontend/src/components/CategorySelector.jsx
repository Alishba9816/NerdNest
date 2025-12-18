// Component to select categories for a paper (multi-select)
import { useState, useEffect } from 'react';
import categoryService from '../services/categoryService';
import '../css/App.css';

function CategorySelector({ paperId, selectedCategories = [], onCategoriesChange }) {
    const [allCategories, setAllCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchCategories();
    }, []);

    const fetchCategories = async () => {
        try {
            const response = await categoryService.getAllCategories();
            setAllCategories(response.categories || []);
        } catch (err) {
            setError('Failed to load categories');
        } finally {
            setLoading(false);
        }
    };

    const handleToggleCategory = async (categoryId) => {
        const isSelected = selectedCategories.some(cat => cat.id === categoryId);

        try {
            if (isSelected) {
                // Remove category
                await categoryService.removePaperFromCategory(paperId, categoryId);
                onCategoriesChange(selectedCategories.filter(cat => cat.id !== categoryId));
            } else {
                // Add category
                await categoryService.assignPaperToCategory(paperId, categoryId);
                const category = allCategories.find(cat => cat.id === categoryId);
                onCategoriesChange([...selectedCategories, category]);
            }
        } catch (err) {
            alert('Failed to update categories');
        }
    };

    if (loading) return <div className="loading"></div>;
    if (error) return <div style={{ color: '#ef4444' }}>{error}</div>;

    return (
        <div>
            <h4 style={{ marginBottom: '1rem' }}>Categories</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {allCategories.map(category => {
                    const isSelected = selectedCategories.some(cat => cat.id === category.id);
                    return (
                        <label
                            key={category.id}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                padding: '0.5rem',
                                cursor: 'pointer',
                                borderRadius: '0.25rem',
                                backgroundColor: isSelected ? 'rgba(139, 92, 246, 0.1)' : 'transparent',
                                transition: 'var(--transition-fast)'
                            }}
                        >
                            <input
                                type="checkbox"
                                checked={isSelected}
                                onChange={() => handleToggleCategory(category.id)}
                                style={{ cursor: 'pointer' }}
                            />
                            <span
                                style={{
                                    width: '12px',
                                    height: '12px',
                                    borderRadius: '50%',
                                    backgroundColor: category.color
                                }}
                            />
                            <span>{category.name}</span>
                        </label>
                    );
                })}
            </div>
        </div>
    );
}

export default CategorySelector;
