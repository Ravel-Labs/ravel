from ravel.api import db


class Deesser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer)
    sharpness_avg = db.Column(db.Float)


def to_dict(self):
    return {
        "id": self.id,
        "trackout_id": self.trackout_id,
        "sharpness_avg": self.sharpness_avg
    }
