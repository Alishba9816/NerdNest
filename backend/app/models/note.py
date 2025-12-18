import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app.extensions import db

class Note(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Note('{self.content[:50]}...', '{self.created_at}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'paper_id': self.paper_id,
            'user_id': self.user_id
        }