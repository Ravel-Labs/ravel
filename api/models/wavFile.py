from ravel.api import db


class WavFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer)  # relates to Trackout
    file_binary = db.Column(db.LargeBinary)
    file_hash = db.Column(db.LargeBinary, unique=True)

    def to_dict(self):
        wavfile = {
            "id": self.id,
            "track_id": self.track_id,
            "wav_binary": str(self.file_binary),
            "wav_hash": str(self.file_hash)
        }
        # Del id happens upon POST, id hasn't been defined yet
        if not wavfile.get('id'):
            del wavfile['id']
        return wavfile
