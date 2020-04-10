from ravel.api import db
from hashlib import md5
class WavFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    binary = db.Column(db.LargeBinary)
    wav_hash = db.Column(db.LargeBinary, unique=True)
    def create_obj(self):
        return {
            "id": self.id,
            "wav_binary": str(self.binary),
            "wav_hash": str(self.wav_hash)
        }