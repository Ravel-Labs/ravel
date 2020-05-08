from ravel.api import db


class Pan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer),
    location = db.Column(db.Float)


def to_dict(self):
    return {
        "id": self.id,
        "trackout_id": self.trackout_id,
        "location": self.location
    }
