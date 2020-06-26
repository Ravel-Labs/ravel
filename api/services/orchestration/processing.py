from ravel.api.services.effects import reverb, equalizer, compressor, deesser
from ravel.ravellib.lib.effects import SignalAggregator


class Processor():
    def __init__(self, num_signals):
        self.num_signals = num_signals
        self.sample_rate = 44100
        self.signal_aggregator = SignalAggregator(
            self.sample_rate, self.num_signals)

    def equalize(self, main_trackout, other_trackouts):
        eq = equalizer.Equalize(main_trackout, other_trackouts)
        processed = eq.equalize()
        print(f"Successful equalization: \n\t {type(processed)}")
        return processed

    def compress(self, all_trackouts):
        co = compressor.Compress(all_trackouts, self.signal_aggregator)
        processed = co.compress()
        print(f"Successful compression of type {type(processed)}: \n\t{processed}")
        return processed

    def deesser(self, main_trackout):
        de = deesser.Deesser(main_trackout)
        processed = de.deess()
        print(f"Successful deesser of type {type(processed)}: \n\t{processed}")
        return processed

    def reverb(self, main_trackout):
        re = reverb.Reverb(main_trackout)
        processed = re.reverb()
        print(f"Successful reverb of type {type(processed)}: \n\t{processed}")
        return processed
