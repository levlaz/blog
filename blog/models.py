
from datetime import datetime

from blog.blog import db


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, nullable=False)
    text_raw = db.Column(db.String, nullable=False)
    text_compiled = db.Column(db.String, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
