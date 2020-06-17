from datetime import datetime
from ravel.api import db

'''
    This file contains the database relational schema
    Hierarchy can be followed top down
    Tree:
        Track (1->n) TrackOuts
        TrackOuts (1->1) Equalizer
                         Compression
                         Deesser
'''


class Track(db.Model):
    '''
        Database Generated Fields
    '''
    id = db.Column(db.Integer, primary_key=True)
    trackouts = db.relationship('TrackOut', backref='trackouts', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    '''
        Configurable Fields
    '''
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(1000))
    artist = db.Column(db.String(200))
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
    '''
        Database Generated Fields
    '''
    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    '''
        Configurable Fields
    '''
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(1000))
    type = db.Column(db.String(50))
    settings = db.Column(db.String(1000))
    eq = db.relationship("Equalizer", backref="eq", lazy='subquery', uselist=False)
    de = db.relationship("Compressor", backref="de", uselist=False)
    co = db.relationship("Deesser", backref="co", uselist=False)

    '''
    Wav File Representation
    '''
    path = db.Column(db.String(1000))
    file_hash = db.Column(db.LargeBinary, unique=True)

    def to_dict(self):
        trackout = {
            "id": self.id,
            "user_id": self.user_id,
            "track_id": self.track_id,
            "created_at": self.created_at,
            "name": self.name,
            "type": self.type,
            "path": self.path,
            "settings": self.settings
        }

        return trackout


class Equalizer(db.Model):
    '''
        Database Generated Fields
    '''
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer, db.ForeignKey("track_out.id"))

    '''
        Configurable Fields
    '''
    freq = db.Column(db.String)
    filter_type = db.Column(db.String)
    gain = db.Column(db.Float)
    path = db.Column(db.String(1000))

    def to_dict(self):
        return {
            "id": self.id,
            "trackout_id": self.trackout_id,
            "freq": self.freq,
            "filter_type": self.filter_type,
            "gain": self.gain
        }


class Deesser(db.Model):
    '''
        Database Generated Fields
    '''
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer, db.ForeignKey("track_out.id"))

    '''
        Configurable Fields
    '''
    sharpness_avg = db.Column(db.Float)

    def to_dict(self):
        return {
            "id": self.id,
            "trackout_id": self.trackout_id,
            "sharpness_avg": self.sharpness_avg
        }


class Compressor(db.Model):
    '''
        Database Generated Fields
    '''
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer, db.ForeignKey("track_out.id"))

    '''
        Configurable Fields
    '''
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
