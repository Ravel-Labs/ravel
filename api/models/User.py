from flask_login import UserMixin
from ravel.api import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(64))
    name = db.Column(db.String(1000))

    def to_dict(self):
        user = {
            "id": self.id or "",
            "name": self.name,
            "email": self.email,
            "password_hash": self.password_hash
        }

        if not user.get("id"):
            del user['id']
        return user