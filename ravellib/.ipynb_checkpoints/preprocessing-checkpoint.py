import os
import librosa
import numpy as np
import pyloudnorm as pyln
import scipy
from scipy.fftpack import fft
from scipy.stats import rankdata

class Signal:
    def __init__(self, path, n_fft, window_size, hop_length, R, bins, roll_percent):
        self.path = path
        self.sr = librosa.get_samplerate(self.path)
        self.n_fft = n_fft
        self.window_size = window_size
        self.hop_length = hop_length
        self.signal, _ = librosa.load(self.path, sr=self.sr)
        self.fft = np.abs(librosa.core.stft(self.signal, n_fft=self.n_fft, 
                                            win_length=self.window_size, hop_length=self.hop_length))
        self.freq_bins = self.fft.shape[0]
        self.fft_db = librosa.amplitude_to_db(self.fft)
        self.R = librosa.db_to_amplitude(R)
        self.bins = bins
        self.freqs = np.array([i * self.sr / self.fft.shape[0] for i in range(self.fft.shape[0])])
        self.roll_percent = roll_percent

    def compute_energy_percent(self):
        total_energy = np.sum(self.chunk_fft)
        energy_percents = []
        for i in range(len(self.bins)-1):
            arr = np.argwhere((self.freqs >= self.bins[i]) & (self.freqs < self.bins[i+1])).flatten()
            bin_sum = np.sum([self.chunk_fft[i] for i in arr])
            energy_percent = bin_sum / total_energy
            energy_percents.append(energy_percent)
        if energy_percents[0] < 0.2:
            return self.bins[1]

    def compute_rolloff(self):
        rolloffs = librosa.feature.spectral_rolloff(self.signal, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length, 
                             win_length=self.window_size, roll_percent=self.roll_percent)
        r_active = rolloffs[0, np.argwhere(rolloffs > 0).flatten()]
        r_avg = np.mean(r_active)
        return r_avg
        
    def set_norm_db(self):
        """Calculate scalar for signal on a linear scale"""
        x = self.signal
        n = x.shape[0]
        a = np.sqrt((n * self.R**2) / np.sum(x**2))
        x_norm_db = librosa.amplitude_to_db(a * x)
        self.norm_fft_db = np.abs(librosa.core.stft(x_norm_db, n_fft=self.n_fft, 
                                            win_length=self.window_size, hop_length=self.hop_length))
    
    def set_chunk(self, seconds):
        fft_length = self.norm_fft_db.shape[1]
        num_freqs = self.norm_fft_db.shape[0]
        chunk_size = int(np.ceil((1 / (self.window_size / self.sr)) * seconds))
        total_chunks = int(np.ceil(fft_length / chunk_size))
        avg_mat = np.zeros((num_freqs, total_chunks))
        avg_vec = np.zeros((1, chunk_size))
        for i in range(num_freqs):
            for j in range(total_chunks):
                if j > total_chunks - 1:
                    avg_vec = self.norm_fft_db[i][chunk_size * j:]
                    mu = np.mean(avg_vec)
                    avg_mat[i][j] = mu
                avg_vec = self.norm_fft_db[i][chunk_size * j: chunk_size * (j+1)]
                mu = np.mean(avg_vec)
                avg_mat[i][j] = mu
        self.chunk_fft = avg_mat

    def set_rank_2d(self): 
        a = np.zeros(self.chunk_fft.shape)
        for row in range(self.chunk_fft.shape[1]):
            a[:, row] = np.abs(rankdata(self.chunk_fft[:, row], method='min') - (self.chunk_fft.shape[0])) + 1
        self.rank = a

    def set_sparsity(self):
        sparse_vec = np.zeros((1, self.rank.shape[1]))
        min_val = self.freq_bins
        for i in range(self.rank.shape[1]):
            mu = np.mean(self.rank.T[i])
            if mu == min_val:
                sparse_vec[0, i] = 0
            else:
                sparse_vec[0, i] = 1
        self.sparse_vec = sparse_vec

    def overlap(self, sv1):
        overlap_vec = self.sparse_vec * sv1
        num_overlaps = np.sum(overlap_vec)
        overlap_ratio = num_overlaps / overlap_vec.shape[1]
        return overlap_vec, num_overlaps, overlap_ratio

    def sparse_overlap_avg(self, overlap_vec, num_overlaps):
        soa_vec = np.zeros((self.freq_bins, 1))
        for i in range(self.freq_bins):
            soa_vec[i] = np.sum((self.chunk_fft[i] * self.sparse_vec) * overlap_vec) / num_overlaps
        return soa_vec

    def rank_soa_vec(self, soa_vec): return np.abs(rankdata(soa_vec, method='min') - (soa_vec.shape[0])) + 1

    def masker_rank_vec(self, r_soa_vec): return np.expand_dims(np.where(r_soa_vec > 10, 1, 0), axis=1)

    def maskee_rank_vec(self, r_soa_vec): return np.expand_dims(np.where(r_soa_vec <= 10, 1, 0), axis=1)


def apply_bfilter(signal, cutoff, sr, order, btype):
    b, a = butter_filter(cutoff, sr, order, btype)
    y = lfilter(b, a, signal)
    return y
    
def attack(attack_max, crest_factor_n2):
    return (2*attack_max) / crest_factor_n2

def audio_sparsity(r_y, min_y):
    sparse_vec = np.zeros((1, r_y.shape[1]))
    for i in range(r_y.shape[1]):
        mu = np.mean(r_y.T[i])
        if mu == min_y:
            sparse_vec[0, i] = 0
        else:
            sparse_vec[0, i] = 1
    return sparse_vec

def butter_bandpass(lowcut, highcut, fs, order):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band', analog=False)
    return b, a

def cf_avg(signals):
    sum = 0
    for sig in signals:
        cfs = cf(sig)
        sum += cfs
    return sum / len(signals)

def compression_parameters(path, files, time_constant, order, cutoff, sr, std, attack_max, release_max):
    compress_info = []
    signal_paths = [os.path.join(path, files[i]) for i in range(len(files))]
    signals = []
    for sig in signal_paths:
        y, _ = librosa.load(sig, sr=sr)
        signals.append(y)
    cfa = cf_avg(signals)
    lfa = lf_avg(signals, order, cutoff, sr)
    for i, signal in enumerate(signals):
        w_p, cf = wp(signal, cfa, std)
        w_f = lf_weighting(signal, lfa, order, cutoff, sr)
        rms = librosa.feature.rms(signal, frame_length=1024, hop_length=512)
        rms_db = np.mean(librosa.amplitude_to_db(rms))
        r = float(ratio(w_f, w_p))
        t = float(threshold(rms_db, w_p))
        kw = float(knee_width(t))
        a = float(attack(attack_max, cf**2))
        rel = float(release(release_max, cf**2))
        compress_info.append({signal_paths[i]:[t, r, a, rel, kw]})
    return compress_info

def crest_attack_release(attack_max, release_max, crest_factor_sq):
    attack = (2 * attack_max) / crest_factor_sq
    release = (2 * release_max) / crest_factor_sq - attack
    return attack, release

def crest_factor(peaks, rms): 
    crest_factor = np.zeros(rms.shape)
    crest_factor[0] = 0
    crest_factor[1:] = peaks[1:] / rms[1:]
    return np.sqrt(crest_factor)

def export_params(path, files, rank_threshold, window_size, hop_length, sr, max_n):
    '''
    This function takes a directory path, list of files, rank threshold,
    sample rate, and the number of top mask values and returns a list of
    parameters in dictionary form. Each list element contains a file path
    and the top mask values according to the mask function.
    '''

    params_list = []
    for idx in range(len(files)):
        masker_path = os.path.join(path, files[idx])
        maskee_path = [os.path.join(path, files[i]) for i in range(len(files)) if i != idx]
        mask_array = mask(masker_path, maskee_path, rank_threshold, window_size, hop_length,  sr, max_n)
        masker_dic = {masker_path: mask_array}
        params_list.append(masker_dic)
    return params_list

def fft_2d(audio_signal, window_size, hop_length, sr):
	'''
	This function takes the path to an audio signal and the accompanying
	sample rate and returns the magnitude (decibels) and time of the 
	signal in a 2d numpy array.

	After loading the audio signal, the function uses a short-time
	fourier transform on non-overlapping windows of size 1024. We
	then transform the frequency from amplitude to decibel scale.
	'''	
	y, sr = librosa.load(audio_signal, sr=sr)
	D = np.abs(librosa.core.stft(y, n_fft=window_size, hop_length=hop_length))
	D_db = librosa.amplitude_to_db(D)
	return D_db

def fft_avg(audio_signal, window_size, hop_length, sr):
	'''
	This function takes the path to an audio signal and the accompanying
	sample rate and returns the spectrum of the signal.

	After loading the audio signal, the function uses a short-time
	fourier transform on non-overlapping windows of size 1024. We
	then transform the frequency from amplitude to decibel scale.

	Lastly, we create the average magnitude over the entire length of 
	the audio signal.
	'''
	y, sr = librosa.load(audio_signal, sr=sr)
	D = np.abs(librosa.core.stft(y, n_fft=window_size, hop_length=hop_length))
	D_db = librosa.amplitude_to_db(D)
	return np.mean(D_db, axis=1)

# def fft_chunk_avg(path, window_size, hop_length):
#     sr = librosa.get_samplerate(path)
#     y, sr = librosa.load(path, sr=sr)
#     onset_env = librosa.onset.onset_strength(y, sr=sr)
#     tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
#     D = np.abs(librosa.core.stft(y, n_fft=window_size, hop_length=hop_length))
#     D_db = librosa.amplitude_to_db(D)
#     D_s = librosa.core.frames_to_samples(D_db, hop_length=hop_length, n_fft=window_size)


def file_scraper(path): return [f for f in os.listdir(path) if not f.startswith('.') and os.path.isfile(os.path.join(path, f))]

def full_file_scraper(path): 
    files = [os.path.join(path, f) for f in os.listdir(path) if not f.startswith('.') and os.path.isfile(os.path.join(path, f))]
    return files

def forget_factor(time_constant, sr): 
    '''
    Alpha signifies the forget factor for parameter autonomation equations
    '''
    return np.exp(-1 / (time_constant * sr))

def freq_bin(signal, n, sr): return n * (sr / signal.shape[0])

def half_wave_rectifier(x): return (x + np.absolute(x)) / 2

def knee_width(thresh): return abs(thresh) / 2

def lf_avg(signals, order, cutoff, sr):
    sum = 0  
    for sig in signals:
        x_low = low_pass(sig, order, cutoff, sr)
        fft_xlow = np.abs(librosa.core.stft(x_low, n_fft=1024, hop_length=512))
#         print(fft_xlow)
        fft_x = np.abs(librosa.core.stft(sig, n_fft=1024, hop_length=512))
#         print(fft_x)
        total = np.sum(np.divide(fft_xlow, fft_x, out=np.zeros_like(fft_xlow), where=fft_x!=0))
#         total = np.sum(fft_xlow / fft_x)
        sum += total
    return sum / 4

def lf_weighting(signal, lf_avg, order, cutoff, sr):
    lf_x = low_pass(signal, order, cutoff, sr)
    x_low = np.abs(librosa.core.stft(lf_x, n_fft=1024, hop_length=512))
    x = np.abs(librosa.core.stft(signal, n_fft=1024, hop_length=512))
    lfe = np.sum(np.divide(x_low, x, out=np.zeros_like(x_low), where=x!=0))
#     lfe = np.sum(x_low / x)
    return lfe / lf_avg

def low_pass(signal, order, cutoff, sr):
    nyq = sr * 0.5
    normal_cutoff = cutoff / nyq
    b,a = scipy.signal.butter(order, normal_cutoff)
    y = scipy.signal.lfilter(b, a, signal)
    return y

def makeup_gain(x_in, x_out, rate):
    meter = pyln.Meter(rate)
    loudness_in = meter.integrated_loudness(x_in)
    loudness_out = meter.integrated_loudness(x_out)
    return loudness_in - loudness_out  

def mask(signal_a, signals, rank_threshold, window_size, hop_length, sr, max_n):
    '''
    This function returns a list of parameters that can be used during
    the equalization process. 

    The input for this function is a list of
    loaded audio signals, the rank threshold for the masking formula,
    the sample rate, and the number of top mask values to return. 

    For the max_n occurences of masking within a frequency, the function 
    returns their signal index, frequency bin,
    and the value of the masking function.
    ''' 
    mask = np.array([])
    mask_info = []
    masker_fft = fft_avg(signal_a, window_size, hop_length, sr)
    maskee_ffts = [fft_avg(signal, window_size, hop_length, sr) for signal in signals]
    masker_rank = rank_signal_1d(masker_fft)
    maskee_ranks = [rank_signal_1d(maskee_fft) for maskee_fft in maskee_ffts]
    # creates boolean matrices that return 1 or 0 based on the rank threshold
    masker_rank_mat = np.where(masker_rank > rank_threshold, 1, 0)
    num_bins = masker_fft.shape[0]
    for i in range(len(signals)):
        maskee_fft = maskee_ffts[i]
        maskee_rank = maskee_ranks[i]
        maskee_rank_mat = np.where(maskee_rank <= 10, 1, 0)
        # uses elementwise multiplication between the boolean matrices and frequency
        # signals to calculate the spectral masking for all values that meet the rank
        # threshold conditions
        mask_ab = (masker_rank_mat * maskee_rank_mat) * (masker_fft - maskee_fft)
        mask = np.append(mask, mask_ab)
    # saves max_n mask values from the mask matrix and uses the indices to add the
    # frequency and mask value to a mask info array    
    top_m = np.argsort(mask)[-max_n:]
    idx = np.unravel_index(top_m, mask.shape)[0]
    for i in idx:
        freq_bin = (i % num_bins) * (sr / num_bins)
        mask_val = mask[i]
        if (mask_val) > 0 and (freq_bin <= 20000) and (freq_bin >= 20):
            mask_info.append([freq_bin, mask_val])
    return np.array(mask_info)

def eq_chunks(paths, n_fft, window_size, hop_length, seconds, R, bins, roll_percent, rank_threshold, max_n, min_overlap_ratio, max_eq):
    signals = [Signal(path=path, n_fft=n_fft, window_size=window_size, hop_length=hop_length, R=R, bins=bins, roll_percent=roll_percent) for path in paths]
    num_signals = len(signals)
    sr = signals[0].sr
    num_bins = signals[0].freq_bins
    for sig in signals:
        sig.set_norm_db()
        sig.set_chunk(seconds=seconds)
        sig.set_rank_2d()
        sig.set_sparsity()
    overlap_mat = np.zeros((num_signals, num_signals))
    params_list = []
    for i in range(num_signals):
        mask = np.empty(shape=[0, 2])
        eq_info = []
        for j in range(num_signals):
            overlap_vec, num_overlaps, overlap_ratio = signals[i].overlap(signals[j].sparse_vec)
            overlap_mat[i][j] = overlap_ratio
            if (overlap_ratio > min_overlap_ratio) and (i != j):
                soa_vec_i = signals[i].sparse_overlap_avg(overlap_vec, num_overlaps)
                soa_vec_j = signals[j].sparse_overlap_avg(overlap_vec, num_overlaps)
                r_soa_vec_i = signals[i].rank_soa_vec(soa_vec_i)
                r_soa_vec_j = signals[j].rank_soa_vec(soa_vec_j)
                masker_vec_i = signals[i].masker_rank_vec(r_soa_vec_i)
                maskee_vec_j = signals[j].maskee_rank_vec(r_soa_vec_j)
                mask_ij = ((masker_vec_i * maskee_vec_j) * (soa_vec_i - soa_vec_j)).flatten()
                m_f = np.concatenate((mask_ij[:, np.newaxis], signals[i].freqs[:, np.newaxis]), axis=1)
                mask = np.append(mask, m_f, axis=0)
            else:
                mask_ij = 0
        mask_m = np.zeros(num_bins)
        for b in range(num_bins):
            arr = mask[b::num_bins, :]
            max_b, _ = np.max(arr, axis=0)
            mask_m[b] = max_b
        top_m = np.argsort(mask_m)[-max_n:]
        top_m_max = mask_m[top_m].max()
        idx = np.unravel_index(top_m, mask_m.shape)[0]
        for x in idx:
            freq_bin = x  * (sr / num_bins)
            mask_val = mask_m[x]
            if (mask_val) > 0 and (freq_bin <= 20000) and (freq_bin >= 20):
                mask_val_scaled = (mask_val / top_m_max) * max_eq
                eq_type = 0
                eq_info.append([freq_bin, mask_val_scaled, eq_type])
        rolloff = signals[i].compute_rolloff()
        energy_percent = signals[i].compute_energy_percent()
        eq_info.append([rolloff, 0.71, 2])
        if energy_percent is not None:
            eq_info.append([energy_percent, 0.71, 1])
        params_list.append({signals[i].path: eq_info})
    return params_list

def mask_2d(signals, rank_threshold, window_size, hop_length, sr, top_n):
    '''
    This function returns a list of parameters that can be used during
    the equalization process using time and frequency opposed to an
    averaged frequency over time. 

    The input for this function is a list of
    loaded audio signals, the rank threshold for the masking formula,
    the sample rate, and the number of top mask values to return. 

    For the top x occurences of masking within a frequency, the function 
    returns their signal index, frequency bin,
    and the value of the masking function.
    '''
    n = len(signals)
    fft_signals = [fft_2d(signal, window_size, hop_length, sr) for signal in signals]
    rank_signals = [rank_signal_2d(fft_signal) for fft_signal in fft_signals]
    mask_info = []
    for i in range(n):
        for j in range(n-1):
            sig_a = fft_signals[i]
            sig_b = fft_signals[(i + j + 1) % n]
            rank_a = rank_signals[i]
            rank_b = rank_signals[(i+j+1) % n]
            # creates boolean matrices that return 1 or 0 based on the rank threshold
            r_a = np.where(rank_a > rank_threshold, 1, 0)
            r_b = np.where(rank_b <= rank_threshold, 1, 0)
            # uses elementwise multiplication between the boolean matrices and frequency
            # signals to calculate the spectral masking for all values that meet the rank
            # threshold conditions
            v = (r_a*r_b)*(sig_a - sig_b)
            # flattens matrix to find the top_n values and appends the signal
            # index, freq_bin, and mask value to the mask_info list
            v_1d = v.flatten()
            idx_1d = v_1d.argsort()[-top_n:]
            x_idx, y_idx = np.unravel_index(idx_1d, v.shape)
            for x, y, in zip(x_idx, y_idx):
                freq_bin = x * (sr / v.shape[0])
                mask_ab = v[x][y]
                mask_info.append([i, freq_bin, mask_ab])
    return mask_info

def peak(audio_signal, time_constant, sr):
    onset_env = librosa.onset.onset_strength(y=audio_signal, sr=sr, n_fft=1024, hop_length=512, aggregate=np.median)
    peaks = librosa.util.peak_pick(onset_env, 3, 3, 3, 5, 0.5, 10)
    peak_bool = np.array([1 if i in peaks else 0 for i in range(onset_env.shape[0])])
    peak_mat = onset_env * peak_bool
    x = np.mean(np.abs(librosa.core.stft(audio_signal, n_fft=1024, hop_length=512)), axis=0)
    alpha = forget_factor(time_constant, sr)
    peaks_squared = np.zeros(peak_mat.shape)
    for i in range(1, len(peaks_squared)):
        peak_factor = alpha * peak_mat[i-1]**2 + (1 - alpha) * np.absolute(x[i])**2
        peaks_squared[i] = max(x[i]**2, peak_factor)
    return peaks_squared 

def rank_signal_1d(audio_signal):
	return np.abs(rankdata(audio_signal, method='min') - (audio_signal.shape[0])) + 1

def rank_signal_2d(audio_signal): 
    a = np.zeros(audio_signal.shape)
    for row in range(audio_signal.shape[1]):
        a[:, row] = np.abs(rankdata(audio_signal[:, row], method='min') - (audio_signal.shape[0])) + 1
    return a

def ratio(wp, wf):return 0.54*wp + 0.764*wf + 1

def release(release_max, crest_factor_n2):
    return (2*release_max) / crest_factor_n2

def rms_normalization(x, R):
    """Calculate scalar for signal on a linear scale"""
    n = x.shape[0]
    a = np.sqrt((n * R**2) / np.sum(x**2))
    return a

def rms_squared(audio_signal, time_constant, sr):
    alpha = forget_factor(time_constant, sr)
    rms = librosa.feature.rms(audio_signal, frame_length=1024, hop_length=512)
    rms_squared = np.zeros(rms.shape)
    for i in range(1, rms.shape[1]):
        rms_squared[0,i] = alpha * rms[0,i-1]**2 + (1-alpha)*np.absolute(audio_signal[i]**2)
    return np.squeeze(rms_squared, axis=0) 

def spectrum(fft_signal): return np.mean(fft_signal, axis=0)

def spectral_flux(fft_signal):
    difference = np.zeros(fft_signal.shape)
    difference[:, 1:] = np.diff(np.absolute(fft_signal), axis=1)
    hwr = half_wave_rectifier(difference)
    spectral_flux = hwr / np.absolute(fft_signal)
    return np.sum(spectral_flux, axis=0)

def threshold(rms, wp):return -11.03 + 0.44*rms - 4.897*wp

def wp(signal, cf_avg, std):
    cfs = cf(signal)
    gaussian = ((cfs - cf_avg)**2) / (2*(std**2))
    if cfs <= cf_avg:
        wp = np.exp(gaussian)
    else:
        wp = 2 - np.exp(gaussian)
    return wp, cfs

def cf(signal):
    rms = librosa.feature.rms(signal, frame_length=1024, hop_length=512)
    rms_db = np.mean(librosa.amplitude_to_db(rms))
    D = np.abs(librosa.core.stft(signal, n_fft=1024, hop_length=512))
    peak_db = librosa.amplitude_to_db(np.sum(D, axis=0)).max()
    cf = peak_db / rms_db
    return cf