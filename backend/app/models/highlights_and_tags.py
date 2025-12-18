import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app.extensions import db

# create a model for highlights with columns id, paper_id, start_offset, end_offset, color, text_content, created_at
class Highlights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'), nullable=False)

    start_offset = db.Column(db.Integer, nullable=False)
    end_offset = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(20), nullable=False)
    text_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship('User', backref='highlights')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
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

    papers = db.relationship(
    'Paper',
    secondary='paper_tags',
    back_populates='tags'
    )

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
