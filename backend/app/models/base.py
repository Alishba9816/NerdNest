from app.extensions import db

# Association table for many-to-many relationship between papers and categories
paper_categories = db.Table('paper_categories',
    db.Column('paper_id', db.Integer, db.ForeignKey('paper.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

