from ravel.api import db

class WavFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    binary = db.Column(db.LargeBinary)

    def create_obj(self):
        return {
            "id": self.id,
            "wav_binary": str(self.binary)
        }