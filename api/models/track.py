import datetime
from ravel.api import db
from ravel.api.models import trackout

class Track(db.Model):
    # __tablename__ = "Person"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    # pets = db.relationship('track_out', backref='owner')
    user_id = db.Column(db.Integer)
    artist = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    info = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "artist": self.artist,
            "info": self.info,
            "created_at": self.created_at
        }
