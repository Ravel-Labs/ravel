from datetime import datetime
from ravel.api import db


class Userx(db.Model):
    # __tablename__ = "bana"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='post', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def to_dict(self):
        user = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "pass": self.password_hash
        }
        if not user.get("id"):
            del user['id']
        return user

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('userx.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

    def to_dict(self):
        user = {
            "id": self.id,
            "body": self.body,
            "time": self.timestamp,
            "user_id": self.user_id
        }
        if not user.get("id"):
            del user['id']
        return user