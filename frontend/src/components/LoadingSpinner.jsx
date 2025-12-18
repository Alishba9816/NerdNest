function LoadingSpinner({ size = 'md', text = '' }) {
    const sizes = {
        sm: '20px',
        md: '40px',
        lg: '60px'
    };

    return (
        <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            gap: '1rem',
            padding: '2rem'
        }}>
            <div 
                className="loading" 
                style={{ 
                    width: sizes[size], 
                    height: sizes[size] 
                }}
            />
            {text && (
                <p style={{ color: 'var(--text-muted)' }}>{text}</p>
            )}
        </div>
    );
}

export default LoadingSpinner;
