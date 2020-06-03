# Processing takes in a request and applies to correct audio processing to it.
# This is a wrapper around the Ravel API Library to expose it to a web server
# in a more usable and meaningful way.
# import librosa
import numpy as np
from io import BytesIO
import pickle
import sys
import scipy.io as sio
# PWD = "/Users/storj/dev/ravellabs/ravel/"
# sys.path.append(PWD)
from ravel.ravellib.lib.effects import EQSignal, CompressSignal, ReverbSignal,\
                                    DeEsserSignal, SignalAggregator


class Processor():
    def __init__(self, wavfile):
        print(f'Creating Processor with wavfile: {wavfile}')
        self.wavfile = wavfile
        self.trackouts = []
        self.signal_aggregator = []
        self.compression_params = []
        self.processed_tracks = []
        self.num_signals = 1

        # NB: This may not always be 44100 but we can deal with that later
        self.sample_rate = 44100
        self.signal_aggregator = SignalAggregator(
            self.sample_rate, self.num_signals)

    def equalize(self):
        print("PROCESSING EQUALIZER")
        if self.wavfile is None:
            print(f"finished processing None wavfile.{self.wavefile}")
            pass

        eq = Equalize(self.wavfile)
        processed = eq.equalize()
        return processed

    def compress(self):
        print("Processor compressor")
        pass

    def limit(self):
        print("Processor limiter")
        pass


class Equalize():
    """
    Creates a new Equalizer
    """

    def __init__(self, wavfile):
        self.wavfile = wavfile
        print(f"type of wavefile:.{type(self.wavfile)}")
        pass

    def equalize(self):
        print(f'Equalizer.equalize() hit')
        # REF: https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.io.wavfile.read.html
        load_bytes = BytesIO(self.wavfile)
        load_bytes.seek(0)
        print(f"Type {type(self.wavfile)} ")
        picked_obj = pickle.dumps(load_bytes)
        loaded_np = np.frombuffer(picked_obj)
        print(loaded_np)
        # TODO: signals is a list of all trackouts for this track.
        '''
            @parameters
                1: numpy array
                3: more to be desired...
        '''

        eq = EQSignal(loaded_np, 1024, 1024,
                      1024, -12, "vocal", 10, 3, -2)

        print(f'eq signal: {eq}')
        # get all other trackouts for a track
        # signals is all of the other trackouts signals (aka numpy arrays)
        # get eq params for all trackout signals for this track
        params = eq.eq_params([eq])

        print(f'params: {params}')
        # equalize the track
        equalized = eq.equalization(params, 2)
        print(f'equalized: {equalized}')

        # write it back to a wavefile
        # REF: https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html
        eqwave = []

        # return the equalized trackprint()
        print(f'returning eqwave: {eqwave}')
        return eqwave


class Compress():
    """
    Creates a new Compressor channel
    """

    def __init__(self, wavfile, signal_aggregator):
        self.wavfile = wavfile
        self.signal_aggregator = signal_aggregator
        print("Creating a new Compressor: ", self)
        pass

    def compress(self):
        """
        compression deals with Compressor and SignalAggregator classes.
        the signal aggregator class calculates stats that are relative
        to each other and themselves.
        Compressor needs to know about all the attributes from each of
        the trackouts in the track to make an accurate guess.
        """

        trackouts = []
        comp_signals = []
        comp_lfe = []
        comp_crest = []
        processed_signals = []

        # turn waveile into numpy array
        numpy_array = []

        # get params for compression
        # audio_type is the track type, e.g. vocals, drums, guitar, etc...
        audio_type = "vocal"

        # do this for each track out in a track
        for track in trackouts:
            comp_signal = CompressSignal(
                "", numpy_array, 1024, 1024, 1024,
                -12, audio_type, 0.2, 1, 1000,
                2, 0.08, 1.0)

            comp_signals.append(comp_signal)
            comp_params = comp_signal.comp_params()
            # push lfe and crest factor for each track into comp_lfe and
            # comp_crest in order

        num_signals = len(trackouts)

        # we want to use 44100 sample rate as much as possible.
        # we can get this from librosa
        sample_rate = 44100
        agg = SignalAggregator(sample_rate, num_signals)
        lfa = agg.lfa(comp_lfe)
        cfa = agg.cfa(comp_crest)

        for i in range(len(comp_signals)):
            cp = comp_signals[i].comp_params(cfa, lfa)
            compressed = comp_signals[i].compression(cp)
            processed_signals.append(compressed)

        return processed_signals


class Reverb():
    def __init__(self):
        print("Creating a new Reverber: ", self)
        pass

    def reverb(self):
        numpy_array = []

        # audio type is the instrument on the track
        audio_type = "vocal"

        # tweakable
        amount = 95
        room_scale = 10
        rev = ReverbSignal(
            "", numpy_array, 1024, 1024, 1024, -12, audio_type,
            amount, 0.0, room_scale, 0.0, 0.4, 600, 6000, 2, 70, 12
        )
        processed = rev.reverb()
        return processed


class DeEsser():
    def __init__(self):
        print("creating new DeEsser: ", self)
        pass

    def deess(self):
        # critical bands are the frequencies at which the deesser looks at to
        # calculate sharpness
        critical_bands = [
            100, 200, 300, 400, 510, 630, 770, 920, 1080, 1270,
            1480, 1720, 2000, 2320, 2700, 3150, 3700, 4400,
            5300, 6400, 7700, 9500, 12000, 15500
        ]
        c = 0.08

        # get numpy array from wavefile
        numpy_array = []

        # audio type is the track type
        audio_type = "vocal"
        sig = DeEsserSignal("", numpy_array, 256, 256, 256, -12, audio_type,
                            critical_bands, c, 1.2, 0.65)

        sharpness = sig.compute_sharpness()
        gr = sig.gain_reduction(sharpness)
        processed = sig.deesser(gr)

        return processed


class Handler():
    """
    The Handler is responsible for queueing and building the effects for each
    track.
    """

    def __init__(self):
        """
        creates a new builder
        """
        self._builder = None
        self._builder = Processor(None)
        print("assigned builder: ", self._builder)
        pass

    def Builder(self):
        """
        The Handler works with the builder instance to create the processing
        stack for each request.
        """
        return self._builder

    def SignalAggregator(self):
        """
        This gets the SignalAggregator for a given track
        """
        pass

    def GetTrackouts(self, track_id):
        """
        GetTrackouts returns all the trackouts for a given `track_id`
        """
        pass


if __name__ == "__main__":
    """
    Allows the script to be run from the command line for proof of concept
    """

    handler = Handler()
    print("handler created: ", handler)

    builder = handler.Builder()
    print("builder from handler: ", builder)

    processor = Processor()

    print("processor created: ", processor)
    processor.equalize()
    processor.compress()
    processor.limit()

    # e.g. apply some processing
    # handler.default_processing()
    # e.g. apply all processing
    # handler.all()
