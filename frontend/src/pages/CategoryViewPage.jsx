// Page to view a single category and its papers
import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import categoryService from '../services/categoryService';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import '../css/App.css';

function CategoryViewPage() {
    const { categoryId } = useParams();
    const [category, setCategory] = useState(null);
    const [papers, setPapers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchCategory();
    }, [categoryId]);

    const fetchCategory = async () => {
        setLoading(true);
        setError('');
        
        try {
            const response = await categoryService.getCategory(categoryId);
            setCategory(response.category);
            setPapers(response.papers || []);
        } catch (err) {
            setError('Failed to load category');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <>
                {/* <Navbar /> */}
                <div className="min-h-screen flex items-center justify-center" style={{ paddingTop: '80px', padding: '80px 2rem 2rem' }}>
                    <LoadingSpinner size="lg" text="Loading category..." />
                </div>
            </>
        );
    }

    if (error) {
        return (
            <>
                {/* <Navbar /> */}
                <div className="min-h-screen flex items-center justify-center" style={{ paddingTop: '80px', padding: '80px 2rem 2rem' }}>
                    <ErrorMessage message={error} onRetry={fetchCategory} />
                </div>
            </>
        );
    }

    return (
        <>
            {/* <Navbar /> */}
            <div className="min-h-screen" style={{ paddingTop: '80px', padding: '80px 2rem 2rem' }}>
                <div className="container">
                    {/* Header */}
                    <div style={{ marginBottom: '2rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                            <i
                                className={category.icon}
                                style={{
                                    fontSize: '2rem',
                                    color: category.color
                                }}
                            />
                            <h1 style={{ fontSize: '2rem' }}>{category.name}</h1>
                        </div>
                        <p style={{ color: 'var(--text-muted)' }}>
                            {papers.length} paper{papers.length !== 1 ? 's' : ''} in this category
                        </p>
                    </div>

                    {/* Papers Grid */}
                    {papers.length === 0 ? (
                        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                            <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>
                                No papers in this category yet
                            </p>
                            <Link to="/papers/upload" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                                Upload Paper
                            </Link>
                        </div>
                    ) : (
                        <div style={{ 
                            display: 'grid', 
                            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', 
                            gap: '1.5rem' 
                        }}>
                            {papers.map(paper => (
                                <Link 
                                    key={paper.id}
                                    to={`/papers/${paper.id}`}
                                    style={{ textDecoration: 'none' }}
                                >
                                    <div className="card" style={{ height: '100%' }}>
                                        <h3 style={{ 
                                            fontSize: '1.1rem', 
                                            marginBottom: '0.75rem',
                                            color: 'var(--text-primary)'
                                        }}>
                                            {paper.title}
                                        </h3>
                                        {paper.authors && (
                                            <p style={{ 
                                                color: 'var(--text-muted)', 
                                                fontSize: '0.9rem' 
                                            }}>
                                                👤 {paper.authors}
                                            </p>
                                        )}
                                    </div>
                                </Link>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}

export default CategoryViewPage;