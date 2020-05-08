from ravel.api import db


class Compressor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer)
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
