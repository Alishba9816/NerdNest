def register_blueprints(app):
    """
    Import and register all blueprints.
    MUST be called inside app context to avoid circular imports.
    """
    
    # Import blueprints HERE, not at top of file
    from app.routes.auth import auth_bp
    from app.routes.papers import papers_bp
    from app.routes.categories import categories_bp
    from app.routes.notes import notes_bp
    from app.routes.highlights import highlights_bp
    from app.routes.tags import tags_bp
    from app.routes.stickynotes import stickynotes_bp
    from app.routes.mainpage import main_bp
    # Register all blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(papers_bp)  # Already has prefix in file
    app.register_blueprint(categories_bp)
    app.register_blueprint(notes_bp)  # Already has prefix in file
    app.register_blueprint(highlights_bp)  # Already has prefix in file
    app.register_blueprint(tags_bp)  # ← NO PREFIX! Routes define full paths
    app.register_blueprint(stickynotes_bp)  # Already has prefix in file
    app.register_blueprint(main_bp)
    
    print("✓ All blueprints registered successfully")