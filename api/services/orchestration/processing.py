from api.services.effects import reverb, equalizer, compressor, deesser
from ravellib.lib.effects import SignalAggregator
from flask import current_app as app


class Processor():
    def __init__(self, num_signals, sample_rate=44100):
        self.num_signals = num_signals
        self.sample_rate = sample_rate
        self.signal_aggregator = SignalAggregator(
            self.sample_rate, self.num_signals)

    def equalize(self, main_trackout, other_trackouts):
        try:
            eq = equalizer.Equalize(main_trackout, other_trackouts, self.sample_rate)
            processed = eq.equalize()
            print(f"Successful equalization: \n\t {type(processed)}")
            return processed
        except Exception as err:
            app.logger.error(f"error in equalize for trackID:", err)
            raise Exception(f"Error occurred in equalize:\n {err}")

    def compress(self, all_trackouts):
        try:
            co = compressor.Compress(all_trackouts, self.signal_aggregator, self.sample_rate)
            processed = co.compress()
            print(f"Successful compression of type {type(processed)}: \n\t{processed}")
            return processed
        except Exception as err:
            app.logger.error(f"error in compress for trackID:", err)
            raise Exception(f"Error occurred in compress:\n {err}")

    def deesser(self, main_trackout):
        try:
            de = deesser.Deesser(main_trackout, self.sample_rate)
            processed = de.deess()
            print(f"Successful deesser of type {type(processed)}: \n\t{processed}")
            return processed
        except Exception as err:
            app.logger.error(f"error in deesser for trackID:", err)
            raise Exception(f"Error occurred in deesser:\n {err}")

    def reverb(self, main_trackout):
        try:
            re = reverb.Reverb(main_trackout, self.sample_rate)
            processed = re.reverb()
            print(f"Successful reverb of type {type(processed)}: \n\t{processed}")
            return processed
        except Exception as err:
            app.logger.error(f"error in reverb for trackID:", err)
            raise Exception(f"Error occurred in reverb:\n {err}")
