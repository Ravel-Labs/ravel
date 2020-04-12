from ravel.api import db

class TrackOut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(64))
    name = db.Column(db.String(1000))

    # TODO Fix this hack, used to return user as json valid back to client
    def create_obj(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password_hash": self.password_hash
        }