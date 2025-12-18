import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app.extensions import db

# StickyNote model to represent sticky notes on papers with columns id, paper_id, position_x, position_y, width, height, content, created_at
class StickyNote(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # todo recheck if user_id is needed
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