
// ==================== src/pages/PapersPage.jsx ====================
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { paperService } from '../services/paperService';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import '../css/App.css';

function PapersPage() {
    const [papers, setPapers] = useState([]);
    const [filteredPapers, setFilteredPapers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [filterStatus, setFilterStatus] = useState('all'); // all, read, unread
    const [sortBy, setSortBy] = useState('date'); // date, title, author

    useEffect(() => {
        fetchPapers();
    }, []);

    useEffect(() => {
        filterAndSortPapers();
    }, [papers, searchQuery, filterStatus, sortBy]);

    const fetchPapers = async () => {
        setLoading(true);
        setError('');
        
        try {
            const response = await paperService.getAllPapers();
            setPapers(response.papers || []);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to load papers');
        } finally {
            setLoading(false);
        }
    };

    const filterAndSortPapers = () => {
        let filtered = [...papers];

        // Search filter
        if (searchQuery) {
            const query = searchQuery.toLowerCase();
            filtered = filtered.filter(paper =>
                paper.title?.toLowerCase().includes(query) ||
                paper.authors?.toLowerCase().includes(query)
            );
        }

        // Status filter
        if (filterStatus === 'read') {
            filtered = filtered.filter(p => p.is_read);
        } else if (filterStatus === 'unread') {
            filtered = filtered.filter(p => !p.is_read);
        }

        // Sort
        filtered.sort((a, b) => {
            if (sortBy === 'title') {
                return (a.title || '').localeCompare(b.title || '');
            } else if (sortBy === 'author') {
                return (a.authors || '').localeCompare(b.authors || '');
            } else {
                // date
                return new Date(b.upload_date) - new Date(a.upload_date);
            }
        });

        setFilteredPapers(filtered);
    };

    const handleDelete = async (paperId, e) => {
        e.preventDefault(); // Prevent navigation
        if (!window.confirm('Are you sure you want to delete this paper?')) return;

        try {
            await paperService.deletePaper(paperId);
            setPapers(papers.filter(p => p.id !== paperId));
        } catch (err) {
            alert('Failed to delete paper');
        }
    };

    const handleToggleRead = async (paperId, e) => {
        e.preventDefault(); // Prevent navigation
        
        try {
            await paperService.toggleReadStatus(paperId);
            setPapers(papers.map(p => 
                p.id === paperId ? { ...p, is_read: !p.is_read } : p
            ));
        } catch (err) {
            alert('Failed to update status');
        }
    };

    if (loading) {
        return (
            <>
                {/* <Navbar /> */}
                <div className="min-h-screen flex items-center justify-center" style={{ paddingTop: '80px', padding: '80px 2rem 2rem' }}>
                    <LoadingSpinner size="lg" text="Loading papers..." />
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
                    <div style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'center',
                        marginBottom: '2rem',
                        flexWrap: 'wrap',
                        gap: '1rem'
                    }}>
                        <h1 style={{ fontSize: '2rem' }}>Research Library</h1>
                        <Link to="/papers/upload" className="btn btn-primary">
                            📤 Upload Paper
                        </Link>
                    </div>

                    {/* Filters */}
                    <div style={{ 
                        display: 'flex', 
                        gap: '1rem', 
                        marginBottom: '2rem',
                        flexWrap: 'wrap'
                    }}>
                        {/* Search */}
                        <input
                            type="text"
                            className="form-input"
                            placeholder="🔍 Search papers..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            style={{ flex: 1, minWidth: '250px' }}
                        />

                        {/* Filter Status */}
                        <select
                            className="form-input"
                            value={filterStatus}
                            onChange={(e) => setFilterStatus(e.target.value)}
                            style={{ minWidth: '150px' }}
                        >
                            <option value="all">All Papers</option>
                            <option value="read">Read</option>
                            <option value="unread">Unread</option>
                        </select>

                        {/* Sort */}
                        <select
                            className="form-input"
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value)}
                            style={{ minWidth: '150px' }}
                        >
                            <option value="date">Sort by Date</option>
                            <option value="title">Sort by Title</option>
                            <option value="author">Sort by Author</option>
                        </select>
                    </div>

                    {/* Papers Grid */}
                    {error ? (
                        <ErrorMessage message={error} onRetry={fetchPapers} />
                    ) : filteredPapers.length === 0 ? (
                        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                            <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>
                                {searchQuery || filterStatus !== 'all' 
                                    ? 'No papers match your filters'
                                    : '📄 No papers yet. Upload your first paper!'}
                            </p>
                        </div>
                    ) : (
                        <>
                            <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
                                Showing {filteredPapers.length} paper{filteredPapers.length !== 1 ? 's' : ''}
                            </p>
                            <div style={{ 
                                display: 'grid', 
                                gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', 
                                gap: '1.5rem' 
                            }}>
                                {filteredPapers.map(paper => (
                                    <PaperCardDetailed 
                                        key={paper.id} 
                                        paper={paper}
                                        onDelete={handleDelete}
                                        onToggleRead={handleToggleRead}
                                    />
                                ))}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </>
    );
}

function PaperCardDetailed({ paper, onDelete, onToggleRead }) {
    return (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Status Badge */}
            <div style={{ marginBottom: '1rem' }}>
                {paper.is_read ? (
                    <span style={{ 
                        fontSize: '0.75rem', 
                        padding: '0.25rem 0.75rem', 
                        backgroundColor: 'rgba(34, 197, 94, 0.2)',
                        color: '#22c55e',
                        borderRadius: '1rem'
                    }}>
                        ✓ Read
                    </span>
                ) : (
                    <span style={{ 
                        fontSize: '0.75rem', 
                        padding: '0.25rem 0.75rem', 
                        backgroundColor: 'rgba(251, 146, 60, 0.2)',
                        color: '#fb923c',
                        borderRadius: '1rem'
                    }}>
                        Unread
                    </span>
                )}
            </div>

            {/* Title */}
            <Link to={`/papers/${paper.id}`} style={{ textDecoration: 'none', flex: 1 }}>
                <h3 style={{ 
                    fontSize: '1.2rem', 
                    marginBottom: '0.75rem',
                    color: 'var(--text-primary)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical'
                }}>
                    {paper.title}
                </h3>
            </Link>

            {/* Authors */}
            {paper.authors && (
                <p style={{ 
                    color: 'var(--text-muted)', 
                    fontSize: '0.9rem',
                    marginBottom: '1rem'
                }}>
                    👤 {paper.authors}
                </p>
            )}

            {/* Actions */}
            <div style={{ 
                display: 'flex', 
                gap: '0.5rem', 
                paddingTop: '1rem',
                borderTop: '1px solid var(--border-color)'
            }}>
                <Link 
                    to={`/papers/${paper.id}`}
                    className="btn btn-primary"
                    style={{ flex: 1, fontSize: '0.85rem', padding: '0.5rem' }}
                >
                    View
                </Link>
                <button
                    onClick={(e) => onToggleRead(paper.id, e)}
                    className="btn btn-secondary"
                    style={{ flex: 1, fontSize: '0.85rem', padding: '0.5rem' }}
                >
                    {paper.is_read ? 'Mark Unread' : 'Mark Read'}
                </button>
                <button
                    onClick={(e) => onDelete(paper.id, e)}
                    className="btn btn-ghost"
                    style={{ fontSize: '0.85rem', padding: '0.5rem', color: '#ef4444' }}
                >
                    🗑️
                </button>
            </div>
        </div>
    );
}

export default PapersPage;