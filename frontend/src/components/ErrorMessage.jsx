function ErrorMessage({ message, onRetry }) {
    return (
        <div style={{
            padding: '2rem',
            textAlign: 'center',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '0.5rem',
            color: '#ef4444'
        }}>
            <p style={{ marginBottom: onRetry ? '1rem' : 0 }}>{message}</p>
            {onRetry && (
                <button onClick={onRetry} className="btn btn-secondary">
                    Try Again
                </button>
            )}
        </div>
    );
}

export default ErrorMessage;