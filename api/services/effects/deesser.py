from ravellib.lib.effects import DeEsserSignal
class Deesser():
    def __init__(self, main_trackout, sr):
        self.main_trackout = main_trackout
        self.sr = sr

    def deess(self):
        # critical bands are the frequencies at which the deesser looks at to
        # calculate sharpness
        critical_bands = [
            100, 200, 300, 400, 510, 630, 770, 920, 1080, 1270,
            1480, 1720, 2000, 2320, 2700, 3150, 3700, 4400,
            5300, 6400, 7700, 9500, 12000, 15500
        ]
        c = 0.08


        # audio type is the track type
        audio_type = "vocal"
        sig = DeEsserSignal(self.main_trackout, 256, 256, 256, -12, audio_type, self.sr,
                            critical_bands, c, 1.2, 0.65)

        sharpness = sig.compute_sharpness()
        gr = sig.gain_reduction(sharpness)
        processed = sig.deesser(gr)

        return processed

