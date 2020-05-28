import os
import librosa
import scipy
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from pydub import AudioSegment
from pyo import *
from preprocessing import *


def compress_signals(params_list, files, path, prefix, size, sr):
    if not os.path.exists(path):
        os.mkdir(path)
    for i in range(len(params_list)):
        file_params = params_list[i]
        new_file_name = prefix + files[i]
        full_file_path = list(file_params.keys())[0]
        dur = sndinfo(full_file_path)[1]
        filename = os.path.join(path, new_file_name)
        s = Server(audio='offline').boot()
        s.recordOptions(dur=dur, filename=filename)
        for file, params in params_list[i].items():
            out = SfPlayer(full_file_path)
            out = Compress(out, thresh=params[0], ratio=params[1], risetime=params[2], falltime=params[3], knee=0.4).out()
            s.start()
            outp, rate = sf.read(filename)
            inp, _ = sf.read(file)
            meter = pyln.Meter(rate)
            out_l = meter.integrated_loudness(outp)
            inp_l = meter.integrated_loudness(inp)
            makeup_gain = inp_l - out_l
            compressed_signal = AudioSegment.from_wav(file)
            compressed_signal = compressed_signal + makeup_gain
            compressed_signal.export(filename, format="wav")
        s.shutdown()