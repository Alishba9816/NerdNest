// ==================== src/pages/UploadPaperPage.jsx ====================
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { paperService } from '../services/paperService';    
import '../css/App.css';

function UploadPaperPage() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        title: '',
        authors: '',
        abstract: '',
        category_id: ''
    });
    const [file, setFile] = useState(null);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [uploadProgress, setUploadProgress] = useState(0);

    useEffect(() => {
        fetchCategories();
    }, []);

    const fetchCategories = async () => {
        try {
            const response = await paperService.getCategories();
            setCategories(response.categories || []);
        } catch (err) {
            console.error('Failed to load categories:', err);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setError('');
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        
        if (selectedFile) {
            // Validate file type
            if (selectedFile.type !== 'application/pdf') {
                setError('Please select a PDF file');
                setFile(null);
                return;
            }
            
            // Validate file size (max 10MB)
            if (selectedFile.size > 10 * 1024 * 1024) {
                setError('File size must be less than 10MB');
                setFile(null);
                return;
            }
            
            setFile(selectedFile);
            setError('');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setUploadProgress(0);

        // Validation
        if (!file) {
            setError('Please select a PDF file');
            setLoading(false);
            return;
        }

        if (!formData.title.trim()) {
            setError('Title is required');
            setLoading(false);
            return;
        }

        try {
            // Create FormData for file upload
            const uploadData = new FormData();
            uploadData.append('file', file);
            uploadData.append('title', formData.title);
            uploadData.append('authors', formData.authors);
            uploadData.append('abstract', formData.abstract);
            
            if (formData.category_id) {
                uploadData.append('category_id', formData.category_id);
            }

            // Simulate upload progress (replace with real progress if available)
            const progressInterval = setInterval(() => {
                setUploadProgress(prev => {
                    if (prev >= 90) {
                        clearInterval(progressInterval);
                        return 90;
                    }
                    return prev + 10;
                });
            }, 200);

            const response = await paperService.uploadPaper(uploadData);
            
            clearInterval(progressInterval);
            setUploadProgress(100);

            // Success - redirect to the new paper
            setTimeout(() => {
                navigate(`/papers/${response.paper_id}`);
            }, 500);

        } catch (err) {
            setError(err.response?.data?.error || 'Failed to upload paper');
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            {/* <Navbar /> */}
            <div className="min-h-screen" style={{ paddingTop: '80px', padding: '80px 2rem 2rem' }}>
                <div className="container" style={{ maxWidth: '800px', margin: '0 auto' }}>
                    <div style={{ marginBottom: '2rem' }}>
                        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
                            Upload Research Paper
                        </h1>
                        <p style={{ color: 'var(--text-muted)' }}>
                            Add a new paper to your library
                        </p>
                    </div>

                    <div className="card">
                        {error && (
                            <div style={{
                                padding: '1rem',
                                marginBottom: '1.5rem',
                                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                border: '1px solid rgba(239, 68, 68, 0.3)',
                                borderRadius: '0.5rem',
                                color: '#ef4444'
                            }}>
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit}>
                            {/* File Upload */}
                            <div className="form-group">
                                <label className="form-label">
                                    PDF File <span style={{ color: '#ef4444' }}>*</span>
                                </label>
                                <div style={{
                                    border: '2px dashed var(--border-color)',
                                    borderRadius: '0.5rem',
                                    padding: '2rem',
                                    textAlign: 'center',
                                    backgroundColor: 'var(--bg-secondary)',
                                    cursor: 'pointer',
                                    transition: 'var(--transition-fast)'
                                }}
                                onDragOver={(e) => {
                                    e.preventDefault();
                                    e.currentTarget.style.borderColor = 'var(--purple-primary)';
                                }}
                                onDragLeave={(e) => {
                                    e.currentTarget.style.borderColor = 'var(--border-color)';
                                }}
                                onDrop={(e) => {
                                    e.preventDefault();
                                    e.currentTarget.style.borderColor = 'var(--border-color)';
                                    const droppedFile = e.dataTransfer.files[0];
                                    if (droppedFile) {
                                        handleFileChange({ target: { files: [droppedFile] } });
                                    }
                                }}>
                                    <input
                                        type="file"
                                        accept=".pdf"
                                        onChange={handleFileChange}
                                        disabled={loading}
                                        style={{ display: 'none' }}
                                        id="file-input"
                                    />
                                    <label htmlFor="file-input" style={{ cursor: 'pointer' }}>
                                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>
                                            📄
                                        </div>
                                        {file ? (
                                            <div>
                                                <p style={{ color: 'var(--purple-primary)', fontWeight: '500' }}>
                                                    {file.name}
                                                </p>
                                                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                                                    {(file.size / 1024 / 1024).toFixed(2)} MB
                                                </p>
                                            </div>
                                        ) : (
                                            <div>
                                                <p style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                                                    Click to upload or drag and drop
                                                </p>
                                                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                                                    PDF files only (Max 10MB)
                                                </p>
                                            </div>
                                        )}
                                    </label>
                                </div>
                            </div>

                            {/* Upload Progress */}
                            {loading && uploadProgress > 0 && (
                                <div style={{ marginBottom: '1.5rem' }}>
                                    <div style={{ 
                                        height: '8px', 
                                        backgroundColor: 'var(--bg-secondary)',
                                        borderRadius: '4px',
                                        overflow: 'hidden'
                                    }}>
                                        <div style={{
                                            width: `${uploadProgress}%`,
                                            height: '100%',
                                            background: 'var(--gradient-primary)',
                                            transition: 'width 0.3s ease'
                                        }} />
                                    </div>
                                    <p style={{ 
                                        textAlign: 'center', 
                                        color: 'var(--text-muted)', 
                                        fontSize: '0.9rem',
                                        marginTop: '0.5rem'
                                    }}>
                                        Uploading... {uploadProgress}%
                                    </p>
                                </div>
                            )}

                            {/* Title */}
                            <div className="form-group">
                                <label className="form-label">
                                    Paper Title <span style={{ color: '#ef4444' }}>*</span>
                                </label>
                                <input
                                    type="text"
                                    name="title"
                                    className="form-input"
                                    placeholder="Enter paper title"
                                    value={formData.title}
                                    onChange={handleChange}
                                    required
                                    disabled={loading}
                                />
                            </div>

                            {/* Authors */}
                            <div className="form-group">
                                <label className="form-label">Authors</label>
                                <input
                                    type="text"
                                    name="authors"
                                    className="form-input"
                                    placeholder="e.g., John Doe, Jane Smith"
                                    value={formData.authors}
                                    onChange={handleChange}
                                    disabled={loading}
                                />
                            </div>

                            {/* Abstract */}
                            <div className="form-group">
                                <label className="form-label">Abstract</label>
                                <textarea
                                    name="abstract"
                                    className="form-input"
                                    placeholder="Brief summary of the paper..."
                                    value={formData.abstract}
                                    onChange={handleChange}
                                    rows="4"
                                    disabled={loading}
                                    style={{ resize: 'vertical' }}
                                />
                            </div>

                            {/* Category */}
                            {categories.length > 0 && (
                                <div className="form-group">
                                    <label className="form-label">Category (Optional)</label>
                                    <select
                                        name="category_id"
                                        className="form-input"
                                        value={formData.category_id}
                                        onChange={handleChange}
                                        disabled={loading}
                                    >
                                        <option value="">Select a category</option>
                                        {categories.map(cat => (
                                            <option key={cat.id} value={cat.id}>
                                                {cat.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            {/* Buttons */}
                            <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                    disabled={loading}
                                    style={{ flex: 1 }}
                                >
                                    {loading ? (
                                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}>
                                            <span className="loading"></span>
                                            Uploading...
                                        </span>
                                    ) : (
                                        '📤 Upload Paper'
                                    )}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => navigate('/papers')}
                                    className="btn btn-secondary"
                                    disabled={loading}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </>
    );
}

export default UploadPaperPage;