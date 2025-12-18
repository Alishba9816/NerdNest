// Display a single category badge
function CategoryBadge({ category, onRemove = null }) {
    return (
        <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.25rem 0.75rem',
            backgroundColor: category.color + '20', // 20% opacity
            color: category.color,
            borderRadius: '1rem',
            fontSize: '0.85rem',
            border: `1px solid ${category.color}40`
        }}>
            <i className={category.icon} style={{ fontSize: '0.75rem' }} />
            <span>{category.name}</span>
            {onRemove && (
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        onRemove(category.id);
                    }}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: 'inherit',
                        cursor: 'pointer',
                        padding: '0',
                        fontSize: '0.75rem',
                        marginLeft: '0.25rem'
                    }}
                >
                    ×
                </button>
            )}
        </span>
    );
}

export default CategoryBadge;