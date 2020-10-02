from ravellib.lib.effects import ReverbSignal
class Reverb():
    def __init__(self, main_trackout, sr):
        self.main_trackout = main_trackout
        self.sr = sr

    def reverb(self):
        # audio type is the instrument on the track
        audio_type = "vocal"
        # tweakable
        amount = 95
        room_scale = 10
        rev = ReverbSignal(
            self.main_trackout, 1024, 1024, 1024, -12, audio_type, self.sr,
            amount, 0.0, room_scale, 0.0, 0.4, 600, 6000, 2, 70, 12
        )
        processed = rev.reverb()
        return processed
