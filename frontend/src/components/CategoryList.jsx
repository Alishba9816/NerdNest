// Display list of categories with papers count
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import categoryService from '../services/categoryService';
import LoadingSpinner from './LoadingSpinner';

function CategoryList() {
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchCategories();
    }, []);

    const fetchCategories = async () => {
        try {
            const response = await categoryService.getAllCategories();
            setCategories(response.categories || []);
        } catch (err) {
            setError('Failed to load categories');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <LoadingSpinner />;
    if (error) return <div style={{ color: '#ef4444' }}>{error}</div>;

    return (
        <div>
            <h3 style={{ marginBottom: '1rem' }}>Categories</h3>
            {categories.length === 0 ? (
                <p style={{ color: 'var(--text-muted)' }}>No categories yet</p>
            ) : (
                <div style={{ display: 'grid', gap: '0.75rem' }}>
                    {categories.map(category => (
                        <Link
                            key={category.id}
                            to={`/categories/${category.id}`}
                            style={{ textDecoration: 'none' }}
                        >
                            <div className="card" style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '1rem',
                                padding: '1rem',
                                borderLeft: `4px solid ${category.color}`
                            }}>
                                <i
                                    className={category.icon}
                                    style={{
                                        fontSize: '1.5rem',
                                        color: category.color
                                    }}
                                />
                                <div style={{ flex: 1 }}>
                                    <h4 style={{ margin: 0, color: 'var(--text-primary)' }}>
                                        {category.name}
                                    </h4>
                                    <p style={{
                                        margin: 0,
                                        fontSize: '0.85rem',
                                        color: 'var(--text-muted)'
                                    }}>
                                        {category.paper_count || 0} papers
                                    </p>
                                </div>
                                <span style={{ color: 'var(--text-muted)' }}>→</span>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}

export default CategoryList;