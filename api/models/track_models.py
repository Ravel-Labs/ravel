from datetime import datetime
from ravel.api import db


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trackouts = db.relationship('TrackOut', backref='trackouts', lazy='dynamic')
    name = db.Column(db.String(1000))
    user_id = db.Column(db.Integer)
    artist = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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


class TrackOut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    trackout_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(1000))
    type = db.Column(db.String(50))
    settings = db.Column(db.String(1000))
    wavefile = db.Column(db.Integer)
    # these relate to effect models such as Compressor, Deesser, and EQ
    compression = db.Column(db.Integer)
    eq = db.Column(db.Integer)
    deesser = db.Column(db.Integer)

    '''
    Wav File Representation
    '''
    file_binary = db.Column(db.LargeBinary)
    file_hash = db.Column(db.LargeBinary, unique=True)

    def to_dict(self):
        user = {
            "id": self.id,
            "created_at": self.created_at,
            "user_id": self.user_id,
            "name": self.name,
            "type": self.type,
            "settings": self.settings,
            "wavefile": self.wavefile,
            "track_id": self.track_id,
            "file_hash": str(self.file_hash)
        }
        if not user.get("id"):
            del user['id']
        return user
