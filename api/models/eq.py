from ravel.api import db


class Equalizer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer)
    freq = db.Column(db.String)
    filter_type = db.Column(db.String)
    gain = db.Column(db.Float)


def to_dict(self):
    return {
        "id": self.id,
        "trackout_id": self.trackout_id,
        "freq": self.freq,
        "filter_type": self.filter_type,
        "gain": self.gain
    }
