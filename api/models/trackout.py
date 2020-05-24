import datetime
from ravel.api import db


class TrackOut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(1000))
    type = db.Column(db.String(50))
    settings = db.Column(db.String(1000))
    wavefile = db.Column(db.Integer)
    track_id = db.Column(db.Integer)
    # these relate to effect models such as Compressor, Deesser, and EQ
    compression = db.Column(db.Integer)
    eq = db.Column(db.Integer)
    deesser = db.Column(db.Integer)

    def to_dict(self):
        user = {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "owner_id": self.owner_id,
            "name": self.name,
            "type": self.type,
            "settings": self.settings,
            "wavefile": self.wavefile,
            "track_id": self.track_id
        }
        if not user.get("id"):
            del user['id']
        return user
