import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app.extensions import db

class Category(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20), default="#3498db")
    icon = db.Column(db.String(50), default="fa-folder")
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    papers = db.relationship('Paper', secondary='paper_categories', backref='categories')
    
    # Helper methods
    def get_paper_count(self):
        return len(self.papers)
    
    def get_progress(self):
        # Calculate based on reading activity
        # For example: percentage of papers read in this category
        read_count = 0
        for paper in self.papers:
            if paper.is_read:
                read_count += 1
        
        if len(self.papers) == 0:
            return 0
        return int((read_count / len(self.papers)) * 100)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'icon': self.icon,
            'parent_id': self.parent_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'paper_count': self.get_paper_count(),
            'progress': self.get_progress()
            # "children": [child.id for child in self.children]  # or [child.to_dict() for full info]
        }