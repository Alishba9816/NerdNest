import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app.extensions import db

class Paper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    authors = db.Column(db.String(300), nullable=False, default="Unknown Author")
    abstract = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False) 
    file_path = db.Column(db.String(300), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #Relationship
    tags = db.relationship('Tags', secondary='paper_tags', back_populates='papers')
    highlights = db.relationship('Highlights', backref='paper', lazy=True, cascade='all, delete-orphan')

    # Relationships for notes and sticky notes to_check
    notes = db.relationship('Note', backref='paper', lazy=True)
    sticky_notes = db.relationship('StickyNote', backref='paper', lazy=True, cascade='all, delete-orphan')




    def __repr__(self):
        return f"Paper('{self.title}', '{self.authors}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'is_read': self.is_read,
            'file_path': self.file_path,
            'upload_date': self.upload_date.isoformat(),
            'user_id': self.user_id
        }