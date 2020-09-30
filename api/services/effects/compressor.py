from ravellib.lib.effects import CompressSignal
class Compress():
    """
    Creates a new Compressor channel
    """

    def __init__(self, all_trackouts, signal_aggregator, sr):
        # TODO all of all - main_trackout
        self.all_trackouts = all_trackouts
        self.agg = signal_aggregator
        self.sr = sr


    def compress(self):
        """
            compression deals with Compressor and SignalAggregator classes.
            the signal aggregator class calculates stats that are relative
            to each other and themselves.
            Compressor needs to know about all the attributes from each of
            the trackouts in the track to make an accurate guess.
        """

        audio_type = "vocal"
        num_signals = len(self.all_trackouts)
        comp_signals = []  # All the other trackouts in a track np array of signals
        comp_lfe = []  # Convenience methods
        comp_crest = []
        compressed_signals = []

        # TODO custom: get params for compression
        for loaded_np in self.all_trackouts:
            cp = CompressSignal(
                loaded_np, 1024, 1024, 123,
                200, audio_type, self.sr, 0.2, 1, 1000,
                2, 0.08, 1.0)
            comp_signals.append(cp)
            cp_crest_factor = cp.crest_factor
            cp_lfe = cp.lfe
            comp_crest.append(cp_crest_factor)
            comp_lfe.append(cp_lfe)
            cfa = self.agg.cfa(comp_crest)
            lfa = self.agg.lfa(comp_lfe)
            comp_params = cp.comp_params(cfa=cfa, lfa=lfa)

        lfa = self.agg.lfa(comp_lfe)
        cfa = self.agg.cfa(comp_crest)

        for mono_signal in comp_signals:
            cp = mono_signal.comp_params(cfa, lfa)
            print(cp)
            compressed = mono_signal.compression(cp)
            compressed_signals.append(compressed)
        print(f"WOOT {compressed_signals}")
        return compressed_signals
