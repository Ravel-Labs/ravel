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
    eq = db.relationship("Equalizer", backref="eq", uselist=False)
    de = db.relationship("Compressor", backref="de", uselist=False)
    co = db.relationship("Deesser", backref="co", uselist=False)
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
            # "file_hash": self.file_hash.decode('utf-8')
        }
        if not user.get("id"):
            del user['id']
        return user


class Equalizer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer, db.ForeignKey("track_out.id"))
    freq = db.Column(db.String)
    filter_type = db.Column(db.String)
    gain = db.Column(db.Float)
    equalized_binary = db.Column(db.LargeBinary)

    def to_dict(self):
        return {
            "id": self.id,
            "trackout_id": self.trackout_id,
            "freq": self.freq,
            "filter_type": self.filter_type,
            "gain": self.gain
        }


class Deesser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer, db.ForeignKey("track_out.id"))
    sharpness_avg = db.Column(db.Float)


def to_dict(self):
    return {
        "id": self.id,
        "trackout_id": self.trackout_id,
        "sharpness_avg": self.sharpness_avg
    }


class Compressor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer, db.ForeignKey("track_out.id"))
    ratio = db.Column(db.Float)
    threshold = db.Column(db.Float)
    knee_width = db.Column(db.Float)
    attack = db.Column(db.Float)
    release = db.Column(db.Float)


def to_dict(self):
    return {
        "id": self.id,
        "trackout_id": self.trackout_id,
        "ratio": self.ratio,
        "threshold": self.threshold,
        "knee_width": self.knee_width,
        "attack": self.attack,
        "release": self.release
    }
