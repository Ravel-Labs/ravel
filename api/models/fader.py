from ravel.api import db


class Fader(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer)
    average = db.Column(db.Float)
    min = db.Column(db.Float)
    max = db.Column(db.Float)
