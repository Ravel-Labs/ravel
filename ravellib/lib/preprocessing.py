import os
import math
import librosa
import numpy as np
import pyloudnorm as pyln
import scipy
from scipy.signal import butter, lfilter, freqz
from scipy.fftpack import fft
from scipy.stats import rankdata


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

def butter_filter(cutoff, sr, order, btype):
    nyq = 0.5 * sr
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype=btype, analog=False)
    return b, a

def butter_bandpass(lowcut, highcut, fs, order):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band', analog=False)
    return b, a

def calc_f_osc(x_d, b, a): return lfilter([1+b[0], b[1], b[2]], a, x_d)

def calc_f0(x_d, b, a): return lfilter(b, a, x_d) * 2

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

def compute_a0(f): return 6.5 * np.exp((-0.6*((f/1000)-3.3))**2) - 10**-3 * (f/1000)**4

def compute_chunk(norm_fft_db, window_size, sr, seconds):
    fft_length = norm_fft_db.shape[1]
    num_freqs = norm_fft_db.shape[0]
    chunk_size = int(np.ceil((1 / (window_size / sr)) * seconds))
    total_chunks = int(np.ceil(fft_length / chunk_size))
    avg_mat = np.zeros((num_freqs, total_chunks))
    avg_vec = np.zeros((1, chunk_size))
    for i in range(num_freqs):
        for j in range(total_chunks):
            if j > total_chunks - 1:
                avg_vec = norm_fft_db[i][chunk_size * j:]
                mu = np.mean(avg_vec)
                avg_mat[i][j] = mu
            avg_vec = norm_fft_db[i][chunk_size * j: chunk_size * (j+1)]
            mu = np.mean(avg_vec)
            avg_mat[i][j] = mu
    return avg_mat

def compute_effect_signal(y, effect_percent, hp_freq, lp_freq, order, sr):
    effect_signal = y * effect_percent
    y_hp = apply_bfilter(effect_signal, hp_freq, sr, order, 'highpass')
    y_out = apply_bfilter(y_hp, lp_freq, sr, order, 'lowpass')
    return y_out

def compute_gz(z): return np.where(z < 14, 1, 0.00012*z**4 - 0.0056*z**3 + 0.1*z**2 - 0.81*z + 3.51)

def compute_lfe(signal, order, cutoff, sr):
    lf_x = low_pass(signal, order, cutoff, sr)
    x_low = np.abs(librosa.core.stft(lf_x, n_fft=1024, hop_length=512))
    x = np.abs(librosa.core.stft(signal, n_fft=1024, hop_length=512))
    lfe = np.sum(np.divide(x_low, x, out=np.zeros_like(x_low), where=x!=0))
    return lfe

def compute_makeup_gain(x_in, x_out, rate):
    meter = pyln.Meter(rate)
    loudness_in = meter.integrated_loudness(x_in)
    loudness_out = meter.integrated_loudness(x_out)
    return loudness_in - loudness_out

def compute_norm_fft_db(x_norm, n_fft, window_size, hop_length):
    norm_fft = np.abs(librosa.core.stft(x_norm, n_fft=n_fft, 
                                    win_length=window_size, hop_length=hop_length))
    norm_fft_db = librosa.amplitude_to_db(norm_fft)
    return norm_fft_db

def compute_Nz(critical_band_fft):
    num = critical_band_fft.shape[0]
    N = np.zeros(critical_band_fft.shape)
    for z in range(num):
        a0_z = compute_a0(critical_band_fft[z][:])
        N[z] = a0_z * critical_band_fft[z][:]
    return N

def compute_rank(chunk_fft_db): 
    a = np.zeros(chunk_fft_db.shape)
    for row in range(chunk_fft_db.shape[1]):
        a[:, row] = np.abs(rankdata(chunk_fft_db[:, row], method='min') - (chunk_fft_db.shape[0])) + 1
    return a

def compute_sparsity(rank, num_bins):
    sparse_vec = np.zeros((1, rank.shape[1]))
    min_val = num_bins
    for i in range(rank.shape[1]):
        mu = np.mean(rank.T[i])
        if mu == min_val:
            sparse_vec[0, i] = 0
        else:
            sparse_vec[0, i] = 1
    return sparse_vec

def crest_attack_release(attack_max, release_max, crest_factor_sq):
    attack = (2 * attack_max) / crest_factor_sq
    release = (2 * release_max) / crest_factor_sq - attack
    return attack, release

def crest_factor(peaks, rms): 
    crest_factor = np.zeros(rms.shape)
    crest_factor[0] = 0
    crest_factor[1:] = peaks[1:] / rms[1:]
    return np.sqrt(crest_factor)

def critical_band_sum(bark_mat, bark_idx, N):
    M = bark_mat.shape[1]
    c_band_sum = np.zeros((N, M))
    for n in range(N):
        if bark_mat[n].size != 0:
            c_band_sum[n] = np.sum(bark_mat[bark_idx[n]], axis=0)[:M]
        else:
            c_band_sum[n] = 0
    return c_band_sum

def ema(x, y, decay): return ((1-decay)*x) + (decay*y)

def eq_filter(x, fc, sr, G, f_b, f_type="boost"):
    d = -np.cos(2*np.pi * (fc/sr))
    V0 = 10**(G/20)
    H0 = V0 - 1
    c_boost = (np.tan(np.pi * (f_b / sr)) - 1) / np.tan(np.pi*(f_b/sr) + 1)
    c_cut = (np.tan(np.pi*(f_b/sr)) - V0) / (np.tan(np.pi*(f_b/sr)) + V0)
    x_h = np.zeros(x.shape[0])
    y1 = np.zeros(x.shape[0])
    y = np.zeros(x.shape[0])
    if f_type == "boost":
        c = c_boost
    elif f_type == "cut":
        c = c_cut
    for n in range(x_h.shape[0]):
        if n < 2:
            x_h[n] = x[n]
            y1[n] = -c * x_h[n]
        else:
            x_h[n] = x[n] - d * (1 - c) * x_h[n-1] + c * x_h[n-2]
            y1[n] = -c * x_h[n] + d * (1 - c) * x_h[n-1] + x_h[n-2]
        y[n] = (H0 / 2) * (x[n] - y1[n]) + x[n]
    return y

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

def freq_to_bark(arr): return 13 * np.arctan((0.76/1000) * arr) + 3.5 * np.arctan(arr/1000)**2

def freq_bark_map(freqs, critical_bands):
    #computes row indices that belong in critical band
    # loops through critical bands and puts freq index in list if its less than or equal to critical band
    bark_idx = []
    bark_idx.append(np.argwhere(freqs < critical_bands[0]))
    for i in range(len(critical_bands)-1):
        idx = np.argwhere((freqs > critical_bands[i]) & (freqs <= critical_bands[i+1])).flatten()
        bark_idx.append(idx)
    return bark_idx


def half_wave_rectifier(x): return (x + np.absolute(x)) / 2

def h_lp(fc, sr, Q):
    k = np.tan(np.pi*(fc/sr))
    k_1 = 1 / (1+(k/Q)+k**2)
    a_0 = 1
    a_1 = 2 * (k**2 - 1) * k_1
    a_2 = (1 - (k / Q) + k**2) * k_1
    b_0 = k**2 * k_1
    b_1 = 2 * k * k_1
    b_2 = k**2 * k_1
    return np.array([b_0, b_1, b_2]), np.array([a_0, a_1, a_2])

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

# def loudness(x, decay):
#     N = x.shape[0]
#     e_y = np.zeros(2)
#     L_m = np.zeros(x.shape)
#     sum_x = abs(x[0]**2)
#     elems = 1
#     mean_x = sum_x / elems
#     e_x = math.sqrt(mean_x)
#     e_y[0] = (1-decay) * e_x
#     e_y[1] = ema(e_x, e_y[0], decay)
#     L_m[0] = 0.691 * (10 * math.log10(e_y[1]+1e-14))
#     e_y[0] = e_y[1]
#     for n in range(1, N):
#         sum_x+=abs(x[n]**2)
#         elems=n+1
#         mean_x = sum_x / elems
#         e_x = math.sqrt(mean_x)
#         e_y[1] = ema(e_x, e_y[0], decay)
#         L_m[n] = 0.691 * (10 * math.log10(e_y[1]+1e-14))
#         e_y[0] = e_y[1]
#     return L_m

def loudness(x, decay):
    cum_sum = np.cumsum(np.abs(x)**2)
    count = np.arange(1, x.shape[0]+1)
    energy = cum_sum / count
    ema_y = lfilter([1-decay], [1, decay], energy)
    L_m = 0.691 * (10 * np.log10(ema_y+1e-14))
    return L_m

def low_pass(signal, order, cutoff, sr):
    nyq = sr * 0.5
    normal_cutoff = cutoff / nyq
    b,a = scipy.signal.butter(order, normal_cutoff)
    y = scipy.signal.lfilter(b, a, signal)
    return y

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

def maskee_rank_vec(r_soa_vec): return np.expand_dims(np.where(r_soa_vec <= 10, 1, 0), axis=1)

def masker_rank_vec(r_soa_vec): return np.expand_dims(np.where(r_soa_vec > 10, 1, 0), axis=1)

def noise_gate(x, holdtime, ltrhold, utrhold, release, attack, fs):
    rel = round(release * fs)
    att = round(attack * fs)
    g = np.zeros(x.shape)
    lthcnt = 0
    uthcnt = 0
    ht = round(holdtime * fs)
    for n in range(len(x)):
        if (x[n] <= ltrhold) or ((x[n] < utrhold) and (lthcnt>0)):
            lthcnt+=1
            uthcnt = 0
            if lthcnt > ht:
                if lthcnt > (rel + ht):
                    g[n] = 0
                else:
                    g[n] = 1 - ((lthcnt - ht) / rel)
            elif ((n < ht) and (lthcnt==n)):
                g[n] = 0;
            else:
                g[n] = 1;
        elif (x[n] >= utrhold) or ((x[n] > ltrhold) and (uthcnt > 0)):
            uthcnt+=1
            if (g[n-1] < 1):
                g[n] = np.maximum(uthcnt / att, g[n-1])
            else:
                g[n] = 1
            lthcnt = 0
        else:
            g[n] = g[n-1]
            lthcnt = 0
            uthcnt = 0
    return g

def normalize(x, peak):
    current_peak = np.max(np.abs(x))
    gain = np.power(10.0, peak/20.0) / current_peak
    output = gain * x
    return output

def overlap(sv0, sv1):
    overlap_vec = sv0 * sv1
    num_overlaps = np.sum(overlap_vec)
    overlap_ratio = num_overlaps / overlap_vec.shape[1]
    return overlap_vec, num_overlaps, overlap_ratio

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

def peak_filter(signal, cutoff, sr, order, btype, window_step, num_steps):
    y = apply_bfilter(signal, cutoff, sr, order, btype)
    num_steps = int(signal.shape[0] / window_step)
    peaks = np.zeros(num_steps)
    for i in range(num_steps):
        y_window = y[i*window_step:(i+1)*window_step]
        peak = y_window.max()
        peaks[i] = peak
    return peaks

def peak_filter_bank(signal, cutoffs, sr, order, btype, window_step, num_steps):
    num_cutoffs = len(cutoffs)
    peaks = np.zeros((num_cutoffs, num_steps))
    for i in range(num_cutoffs):
        peaks[i] = peak_filter(signal, cutoffs[i], sr, order, btype, window_step, num_steps)
    maxs = np.argmax(peaks, axis=0)
    freq_counts = np.unique(maxs, return_counts=True)
    max_idx = np.argmax(freq_counts[:][1])
    return cutoffs[max_idx]

def preprocess_pll(x, high_cutoff, low_cutoff, sr, high_order, low_order, x_env):
    x_low = apply_bfilter(x, cutoff=low_cutoff, sr=sr, order=low_order, btype='low')
    x = apply_bfilter(x_low, cutoff=high_cutoff, sr=sr, order=high_order, btype='high')
    x_in = x * (1/x_env)
    return x_in

def rank_signal_1d(audio_signal):
	return np.abs(rankdata(audio_signal, method='min') - (audio_signal.shape[0])) + 1

def rank_signal_2d(audio_signal): 
    a = np.zeros(audio_signal.shape)
    for row in range(audio_signal.shape[1]):
        a[:, row] = np.abs(rankdata(audio_signal[:, row], method='min') - (audio_signal.shape[0])) + 1
    return a

def rank_soa_vec(soa_vec): return np.abs(rankdata(soa_vec, method='min') - (soa_vec.shape[0])) + 1

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

def sparse_overlap_avg(num_bins, chunk_fft_db, sparse_vec, overlap_vec, num_overlaps):
    soa_vec = np.zeros((num_bins, 1))
    for i in range(num_bins):
        soa_vec[i] = np.sum((chunk_fft_db[i] * sparse_vec) * overlap_vec) / num_overlaps
    return soa_vec

def spectrum(fft_signal): return np.mean(fft_signal, axis=0)

def spectral_flux(fft_signal):
    difference = np.zeros(fft_signal.shape)
    difference[:, 1:] = np.diff(np.absolute(fft_signal), axis=1)
    hwr = half_wave_rectifier(difference)
    spectral_flux = hwr / np.absolute(fft_signal)
    return np.sum(spectral_flux, axis=0)

def tonal_balance(path, high_cutoff, low_cutoff, high_order, low_order, x_env, Q, K_d, fc, G, f_b, f_type):
    sig = Signal(path=path, window_size=1024, hop_length=512)
    x = sig.signal
    sr = sig.sr
    x_in = preprocess_pll(x, high_cutoff=high_cutoff, low_cutoff=low_cutoff, 
                          sr=sr, high_order=high_order, low_order=low_order, x_env=x_env)
    b, a = h_lp(fc=fc, sr=sr, Q=Q)
    x_d = x_in * K_d
    f_osc = calc_f_osc(x_d, b, a)
    y_cos_osc = np.zeros(f_osc.shape)
    y_sin_osc = np.zeros(f_osc.shape)
    for n in range(x_in.shape[0]):
        y_cos_osc[n] = np.cos(2*np.pi * (f_osc[n] / 44100) * n)
        y_sin_osc[n] = np.sin(2*np.pi * (f_osc[n] / 44100) * n)
    x_d = x_d * y_cos_osc
    f0 = calc_f0(x_d, b, a)
    f0_fft = np.abs(np.fft.fft(f0))
    bins_arr = [20, 40, 60, 80, 100, 150, 200, 250, 500, 750, 1000, 1250, 1500]
    val, bins = np.histogram(f0_fft, bins=bins_arr, range=(20, 1500), density=False)
    top_vals = np.argsort(mask)[-5:]
    top_freqs = bins[top_vals]
    y = x
    for freq in top_freqs:
        y = eq_filter(y, fc=fc, sr=sr, G=G, f_b=f_b, f_type=f_type)
    return y

def wp(cf, cf_avg, std):
    gaussian = ((cf - cf_avg)**2) / (2*(std**2))
    if cf <= cf_avg:
        wp = np.exp(gaussian)
    else:
        wp = 2 - np.exp(gaussian)
    return wp