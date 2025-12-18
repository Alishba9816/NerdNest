import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { dashboardService } from '../services/dashboardService';
import { paperService } from '../services/paperService';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import '../css/App.css';

function DashboardPage() {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [dashboardData, setDashboardData] = useState(null);
    const [papers, setPapers] = useState([]);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        setLoading(true);
        setError('');
        
        try {
            const [dashData, papersData] = await Promise.all([
                dashboardService.getDashboardData(),
                paperService.getAllPapers()
            ]);
            
            setDashboardData(dashData);
            setPapers(papersData.papers || []);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to load dashboard');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            // ← REMOVED <Navbar />
            <div className="min-h-screen flex items-center justify-center">
                <LoadingSpinner size="lg" text="Loading dashboard..." />
            </div>
        );
    }

    if (error) {
        return (
            // ← REMOVED <Navbar />
            <div className="min-h-screen flex items-center justify-center">
                <ErrorMessage message={error} onRetry={fetchDashboardData} />
            </div>
        );
    }

    const totalPapers = papers.length;
    const readPapers = papers.filter(p => p.is_read).length;
    const unreadPapers = totalPapers - readPapers;

    return (
        // ← REMOVED <Navbar />
        <div className="min-h-screen" style={{ paddingTop: '80px', padding: '80px 2rem 2rem' }}>
            <div className="container">
                {/* Welcome Section */}
                <div style={{ marginBottom: '3rem' }}>
                    <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>
                        Welcome to Your Research Hub
                    </h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>
                        Manage your papers, take notes, and organize your research
                    </p>
                </div>

                {/* Stats Cards */}
                <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
                    gap: '1.5rem',
                    marginBottom: '3rem'
                }}>
                    <StatsCard
                        title="Total Papers"
                        value={totalPapers}
                        icon="📚"
                        color="var(--purple-primary)"
                    />
                    <StatsCard
                        title="Papers Read"
                        value={readPapers}
                        icon="✅"
                        color="var(--accent-cyan)"
                    />
                    <StatsCard
                        title="To Read"
                        value={unreadPapers}
                        icon="📖"
                        color="var(--accent-orange)"
                    />
                </div>

                {/* Quick Actions */}
                <div style={{ marginBottom: '3rem' }}>
                    <h2 style={{ marginBottom: '1.5rem' }}>Quick Actions</h2>
                    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                        <Link to="/papers/upload" className="btn btn-primary">
                            📤 Upload Paper
                        </Link>
                        <Link to="/papers" className="btn btn-secondary">
                            📚 View Library
                        </Link>
                    </div>
                </div>

                {/* Recent Papers */}
                <div style={{ marginBottom: '3rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                        <h2>Recent Papers</h2>
                        <Link to="/papers" style={{ color: 'var(--purple-primary)' }}>
                            View All →
                        </Link>
                    </div>
                    
                    {dashboardData?.recent_papers?.length > 0 ? (
                        <div style={{ 
                            display: 'grid', 
                            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', 
                            gap: '1rem' 
                        }}>
                            {dashboardData.recent_papers.map(paper => (
                                <PaperCard key={paper.id} paper={paper} />
                            ))}
                        </div>
                    ) : (
                        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                            <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
                                📄 No papers yet
                            </p>
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                                Upload your first research paper to get started
                            </p>
                        </div>
                    )}
                </div>

                {/* Categories */}
                {dashboardData?.user_categories?.length > 0 && (
                    <div>
                        <h2 style={{ marginBottom: '1.5rem' }}>Categories</h2>
                        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                            {dashboardData.user_categories.map(category => (
                                <div 
                                    key={category.id}
                                    className="card"
                                    style={{ padding: '0.75rem 1.25rem', display: 'inline-block' }}
                                >
                                    {category.name}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function StatsCard({ title, value, icon, color }) {
    return (
        <div className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>
                {icon}
            </div>
            <h3 style={{ fontSize: '2rem', color, marginBottom: '0.25rem' }}>
                {value}
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
                {title}
            </p>
        </div>
    );
}

function PaperCard({ paper }) {
    return (
        <Link to={`/papers/${paper.id}`} style={{ textDecoration: 'none' }}>
            <div className="card" style={{ height: '100%' }}>
                <div style={{ marginBottom: '0.5rem' }}>
                    {paper.is_read ? (
                        <span style={{ 
                            fontSize: '0.75rem', 
                            padding: '0.25rem 0.5rem', 
                            backgroundColor: 'rgba(34, 197, 94, 0.2)',
                            color: '#22c55e',
                            borderRadius: '0.25rem'
                        }}>
                            ✓ Read
                        </span>
                    ) : (
                        <span style={{ 
                            fontSize: '0.75rem', 
                            padding: '0.25rem 0.5rem', 
                            backgroundColor: 'rgba(251, 146, 60, 0.2)',
                            color: '#fb923c',
                            borderRadius: '0.25rem'
                        }}>
                            Unread
                        </span>
                    )}
                </div>
                <h3 style={{ 
                    fontSize: '1.1rem', 
                    marginBottom: '0.5rem',
                    color: 'var(--text-primary)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical'
                }}>
                    {paper.title}
                </h3>
                {paper.authors && (
                    <p style={{ 
                        color: 'var(--text-muted)', 
                        fontSize: '0.9rem',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                    }}>
                        {paper.authors}
                    </p>
                )}
            </div>
        </Link>
    );
}

export default DashboardPage;