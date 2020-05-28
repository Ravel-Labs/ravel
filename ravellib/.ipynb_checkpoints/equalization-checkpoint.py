import scipy
from preprocessing import *
from pyo import *


def EQ_signal(params, Q):
    for file, eq_params in params.items():
        out = SfPlayer(file)
        if len(eq_params) < 0:
            return out
        for param in eq_params:
            freq = float(param[0])
            gain = float(param[1])
            eq_type = int(param[2])
            eq = EQ(out, freq=freq, q=Q, boost=-gain, type=eq_type)
    return eq

def mix_signals(params_list, Q, filename):
    s = Server(audio='offline').boot()
    # Should add in logic to ensure that all audio is the same duration
    first_file_params = params_list[0]
    first_file = list(first_file_params.keys())[0]
    dur = sndinfo(first_file)[1]
    mixer = Mixer()
    s.recordOptions(dur=dur, filename=filename)
    for i in range(len(params_list)):
        out = EQ_signal(params_list[i], Q)
        mixer.addInput(i, out)
    final_mix = mixer.out()
    s.start()
    s.shutdown()

def save_signals(params_list, files, Q, path, prefix):
    s = Server(audio='offline').boot()
    if not os.path.exists(path):
        os.mkdir(path)
    for i in range(len(params_list)):
        file_params = params_list[i]
        new_file_name = prefix + files[i]
        full_file_path = list(file_params.keys())[0]
        dur = sndinfo(full_file_path)[1]
        filename = os.path.join(path, new_file_name)
        s.recordOptions(dur=dur, filename=filename)
        out = EQ_signal(params_list[i], Q).out()
        s.start()
    s.shutdown()

# def save_sigs(params_list, files, Q, path, prefix):
#     s = Server(audio='offline').boot()
#     if not os.path.exists(path):
#         os.mkdir(path)
#     for i in range(len(params_list)):
#         EQ_params = params_list[i][1:]