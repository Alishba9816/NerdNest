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