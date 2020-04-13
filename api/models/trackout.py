import datetime
from ravel.api import db


class TrackOut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(1000))
    type = db.Column(db.String(50))
    instrument = db.Column(db.String(50))
    settings = db.Column(db.String(1000))
    wavefile = db.Column(db.Integer)

    def to_dict(self):
        user = {
            "id": self.id,
            "user": self.user,
            "name": self.name,
            "settings": self.settings,
        }
        if not user.get("id"):
            del user['id']
        return user
