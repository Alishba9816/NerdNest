#base
from app.extensions import db

# Association table for many-to-many relationship between papers and categories
paper_categories = db.Table('paper_categories',
    db.Column('paper_id', db.Integer, db.ForeignKey('paper.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

# category 
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
#highlights_and_tags 
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app.extensions import db

# create a model for highlights with columns id, paper_id, start_offset, end_offset, color, text_content, created_at
class Highlights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'), nullable=False)
    start_offset = db.Column(db.Integer, nullable=False)
    end_offset = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(20), nullable=False)
    text_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"Highlights('{self.text_content[:50]}...', '{self.created_at}')"

    def to_dict(self):
        return {
            'id': self.id,
            'paper_id': self.paper_id,
            'start_offset': self.start_offset,
            'end_offset': self.end_offset,
            'color': self.color,
            'text_content': self.text_content,
            'created_at': self.created_at.isoformat()
        }


# make table tags with columns id, name, color, created_at

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"Tags('{self.name}', '{self.color}')"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at.isoformat()
        }
    
# association table paper_tags (paper_id, tag_id)
paper_tags = db.Table('paper_tags',
    db.Column('paper_id', db.Integer, db.ForeignKey('paper.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

#note
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
#paper
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app.extensions import db

class Paper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    authors = db.Column(db.String(300), nullable=False)
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
#stickynotes
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app.extensions import db

# StickyNote model to represent sticky notes on papers with columns id, paper_id, position_x, position_y, width, height, content, created_at
class StickyNote(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'), nullable=False)
    position_x = db.Column(db.Integer, nullable=False)
    position_y = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"StickyNote('{self.content[:50]}...', '{self.created_at}')"

    def to_dict(self):
        return {
            'id': self.id,
            'paper_id': self.paper_id,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'width': self.width,
            'height': self.height,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }
#user
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app.extensions import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    papers = db.relationship('Paper', backref='user', lazy=True)
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }