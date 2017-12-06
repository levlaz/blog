
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


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True)
    website = db.Column(db.String, nullable=True)
    comment_body = db.Column(db.Text, nullable=False)
    is_visible = db.Column(db.Boolean, default=False)
    is_spam = db.Column(db.Boolean, default=False)
    is_from_admin = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))

    def status(self):
        if self.is_spam:
            return 'spam'
        if self.is_visible:
            return 'approved'
        else:
            return 'unprocessed'