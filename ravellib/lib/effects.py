import ravel.ravellib.lib.preprocessing as preprocessing
import librosa
import numpy as np
import pyloudnorm as pyln
from pysndfx import AudioEffectsChain
from scipy.io.wavfile import write


class Signal:
    def __init__(self, signal, n_fft, window_size, hop_length, peak, audio_type):
        # self.path = path
        # self.sr = librosa.get_samplerate(self.path)
        self.sr = 44100
        self.n_fft = n_fft
        self.window_size = window_size
        self.hop_length = hop_length
        self.signal = signal
        self.signal_db = librosa.amplitude_to_db(self.signal)
        self.peak = peak
        self.audio_type = audio_type
        self.x_norm = preprocessing.normalize(self.signal, self.peak)
        
        self.fft = np.abs(librosa.core.stft(self.signal, n_fft=self.n_fft, 
                                            win_length=self.window_size, hop_length=self.hop_length))
        self.num_bins = self.fft.shape[0]
        self.fft_db = librosa.amplitude_to_db(self.fft)
        self.norm_fft_db = preprocessing.compute_norm_fft_db(self.x_norm, self.n_fft, self.window_size, self.hop_length)
        self.freqs = np.array([i * self.sr / self.fft.shape[0] for i in range(self.num_bins)])


class EQSignal(Signal):
    def __init__(self, signal, n_fft, window_size, hop_length, peak, audio_type, 
                rank_threshold, max_n, max_eq):
        super().__init__(signal, n_fft, window_size, hop_length, peak, audio_type)
        self.fft_db_avg = np.mean(self.fft_db, axis=1)
        self.rank = preprocessing.rank_signal_1d(self.fft_db_avg)
        self.rank_threshold = rank_threshold
        self.masker_rank_vec = np.where(self.rank > self.rank_threshold, 1, 0)
        self.maskee_rank_vec = np.where(self.rank <= self.rank_threshold, 1, 0)
        self.max_n = max_n
        self.max_eq = max_eq

    def compute_mask(self, signal):
        mask_ab = (self.masker_rank_vec * signal.maskee_rank_vec) * (self.fft_db_avg - signal.fft_db_avg)
        return mask_ab

    def eq_params(self, signals):
        num_signals = len(signals)
        num_bins = self.num_bins
        max_n = self.max_n
        sr = self.sr
        max_eq = self.max_eq
        mask = np.array([])
        eq_info = []
        for m in range(num_signals):
            mask_ab = self.compute_mask(signals[m])
            mask = np.append(mask, mask_ab, axis=0)
        mask_m = np.zeros(num_bins)
        for b in range(num_bins):
            arr = mask[b::num_bins]
            max_b = np.max(arr)
            mask_m[b] = max_b
        top_m = np.argsort(mask_m)[-max_n:]
        top_m_max = mask_m[top_m].max()
        idx = np.unravel_index(top_m, mask_m.shape)[0]
        for x in idx:
            freq_bin = x  * (sr / num_bins)
            mask_val = mask_m[x]
            if (mask_val > 0) and (freq_bin <= 20000) and (freq_bin >= 20):
                mask_val_scaled = (mask_val / top_m_max) * max_eq
                eq_type = 0
                eq_info.append([freq_bin, mask_val_scaled, eq_type])
        if self.audio_type == "vocal":
            # logic for subtractive EQ with highpass and shelf EQ
            eq_info.append([270, 5, 3]) # low shelf filter
            eq_info.append([100, 0 , 1]) # highpass filter best practice
        return eq_info

    def equalization(self, eq_info, Q):
        num_filters = len(eq_info)
        y = self.signal
        for i in range(num_filters):
            freq = float(eq_info[i][0])
            gain = float(eq_info[i][1])
            eq_type = int(eq_info[i][2])
            if eq_type == 0:
                eq = AudioEffectsChain().equalizer(freq, Q, -gain)
                y = eq(y)
            elif eq_type == 1:
                eq = AudioEffectsChain().highpass(freq)
                y = eq(y)
            elif eq_type == 2:
                eq = AudioEffectsChain().lowpass(freq)
                y = eq(y)
            elif eq_type == 3:
                eq = AudioEffectsChain().lowshelf(-gain, freq)

            elif eq_type == 4:
                eq = AudioEffectsChain().highshelf(gain, freq)
        return y


    # def compute_energy_percent(self):
    #     total_energy = np.sum(self.chunk_fft_db)
    #     energy_percents = []
    #     for i in range(len(self.bins)-1):
    #         arr = np.argwhere((self.freqs >= self.bins[i]) & (self.freqs < self.bins[i+1])).flatten()
    #         bin_sum = np.sum([self.chunk_fft_db[i] for i in arr])
    #         energy_percent = bin_sum / total_energy
    #         energy_percents.append(energy_percent)
    #     if energy_percents[0] < 0.2:
    #         return self.bins[1]

    # def compute_rolloff(self):
    #     rolloffs = librosa.feature.spectral_rolloff(self.signal, sr=self.sr, n_fft=self.n_fft, hop_length=self.hop_length, 
    #                          win_length=self.window_size, roll_percent=self.roll_percent)
    #     r_active = rolloffs[0, np.argwhere(rolloffs > 0).flatten()]
    #     r_avg = np.mean(r_active)
    #     return r_avg

    # def compute_mask(self, signal, overlap_vec, num_overlaps):
    #     soa_vec_i = preprocessing.sparse_overlap_avg(self.num_bins, self.chunk_fft_db, 
    #                                                 self.sparse_vec, overlap_vec, num_overlaps)
    #     soa_vec_j = preprocessing.sparse_overlap_avg(signal.num_bins, signal.chunk_fft_db, 
    #                                                 signal.sparse_vec, overlap_vec, num_overlaps)
    #     r_soa_vec_i = preprocessing.rank_soa_vec(soa_vec_i)
    #     r_soa_vec_j = preprocessing.rank_soa_vec(soa_vec_j)
    #     masker_vec_i = preprocessing.masker_rank_vec(r_soa_vec_i)
    #     maskee_vec_j = preprocessing.maskee_rank_vec(r_soa_vec_j)
    #     mask_ij = ((masker_vec_i * maskee_vec_j) * (soa_vec_i - soa_vec_j)).flatten()
    #     m_f = np.concatenate((mask_ij[:, np.newaxis], self.freqs[:, np.newaxis]), axis=1)
    #     return mask_ij 


class CompressSignal(Signal):
    def __init__(self, signal, n_fft, window_size, hop_length, peak, audio_type, 
                time_constant, order, cutoff, std, attack_max, release_max):
        super().__init__(signal, n_fft, window_size, hop_length, peak, audio_type)
        self.time_constant = time_constant
        self.order = order
        self.cutoff = cutoff
        self.std = std
        self.attack_max = attack_max
        self.release_max = release_max
        self.rms = librosa.feature.rms(signal, frame_length=self.window_size, hop_length=self.hop_length)
        self.rms_db = np.mean(librosa.amplitude_to_db(self.rms))
        self.peak_db = librosa.amplitude_to_db(np.sum(self.fft, axis=0)).max()
        self.crest_factor = self.peak_db / self.rms_db
        self.lfe = preprocessing.compute_lfe(self.signal, self.order, self.cutoff, self.sr)
    
    def compute_wp(self, cf_avg): return preprocessing.wp(self.crest_factor, cf_avg, self.std)

    def compute_lf_weighting(self, lfa): return self.lfe / lfa

    def ratio(self, wf, wp): return float(0.54*wp + 0.764*wf + 1)

    def threshold(self, wp):return float(-11.03 + 0.44*self.rms_db - 4.897*wp)

    def knee_width(self, threshold): return abs(threshold) / 2

    def attack(self): return float((2*self.attack_max) / self.crest_factor ** 2)

    def release(self): return float((2*self.release_max) / self.crest_factor ** 2)

    def comp_params(self, cfa, lfa):
        w_p = self.compute_wp(cfa)
        w_f = self.compute_lf_weighting(lfa)
        r = self.ratio(w_f, w_p)
        t = self.threshold(w_p)
        kw = self.knee_width(t)
        a = self.attack()
        rel = self.release()
        return [t, r, a, rel, kw]

    def compression(self, params):
        compress = AudioEffectsChain().compand(attack=params[2], decay=params[3], soft_knee=params[1], 
                    threshold=params[0], db_from=params[0], db_to=params[0])
        y = compress(self.signal)
        makeup_gain = preprocessing.compute_makeup_gain(self.signal, y, self.sr)
        gain = (AudioEffectsChain().gain(makeup_gain))
        return gain(y)

class FaderSignal(Signal):
    def __init__(self, path, signal, n_fft, window_size, hop_length, peak, audio_type,
                decay, step, lead, max_fader, min_fader, B):
        super().__init__(path, signal, n_fft, window_size, hop_length, peak, audio_type)
        self.decay = decay
        self.step = step
        self.lead = lead
        self.max_fader = max_fader
        self.min_fader = min_fader
        self.B = B
    
    def full_loudness(self):
        x_norm = self.x_norm
        sr = self.sr
        step = self.step
        decay = self.decay
        N = x_norm.shape[0]
        num_segments = int(N / (step * sr))
        L_m = np.zeros(x_norm.shape)
        for n in range(num_segments):
            L_m[step*sr*n: step*sr*(n+1)] = preprocessing.loudness(x_norm[step*sr*n: step*sr*(n+1)], decay)
        L_m[step*sr*(n+1):] = preprocessing.loudness(x_norm[step*sr*(n+1):], decay)
        # ind = np.where(~np.isnan(L_m))[0] # temp fix until figuring out why function returns NaN values
        # first, last = ind[0], ind[-1]
        # L_m[:first] = L_m[first]
        # L_m[last + 1:] = L_m[last]
        mask = np.isnan(L_m)
        L_m[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), L_m[~mask])
        return L_m

    def compute_fader(self, L_av, L2):
        F_m = np.zeros(L2.shape)
        for n in range(len(F_m)):
            F_m[n] = 10 ** ((L_av[n] - L2[n]) / 20)
        if self.lead == True:
            F_m[n] = F_m[n] * 10 ** (self.B/20)

        F_m = np.where(F_m > self.max_fader, self.max_fader, F_m)
        F_m = np.where(F_m < self.min_fader, self.min_fader, F_m)
        return F_m

    def fader(self, fader_output): return self.signal * fader_output

class PanSignal(Signal):
    def __init__(self, path, signal, n_fft, window_size, hop_length, peak, audio_type, 
                cutoffs, window, order, btype):
        super().__init__(path, signal, n_fft, window_size, hop_length, peak, audio_type)
        self.window = window
        self.order = order
        self.btype = btype
        self.cutoffs = cutoffs
        self.window_step = int(self.sr * self.window)
        self.num_steps = int(self.signal.shape[0] / self.window_step)
        self.K = len(cutoffs)


    def lead_filter(self): 
        return preprocessing.peak_filter_bank(self.signal, self.cutoffs, 
                                self.sr, self.order, self.btype, 
                                self.window_step, self.num_steps)


    def pan(self, P):
        # quick fix - should be done from the signal aggregator function
        if self.audio_type == "vocal":
            P = 0.5
        left = np.cos(P * np.pi) * self.signal
        right = np.sin(P * np.pi) * self.signal
        return np.dstack((left,right))[0]

class DeEsserSignal(Signal):
    def __init__(self, signal, n_fft, window_size, hop_length, peak, audio_type,
                critical_bands, c, sharp_thresh, max_reduction):
        super().__init__(signal, n_fft, window_size, hop_length, peak, audio_type)
        self.critical_bands = critical_bands
        self.bark_idx = preprocessing.freq_bark_map(self.freqs, self.critical_bands)
        self.c = c
        self.sharp_thresh = sharp_thresh
        self.max_reduction = max_reduction
        self.cb_fft = preprocessing.critical_band_sum(self.fft, self.bark_idx, len(critical_bands))
        self.N_z = preprocessing.compute_Nz(self.cb_fft)
        self.g_z = np.apply_along_axis(np.exp, 0, (0.171*self.cb_fft))

    def compute_sharpness(self):
        numr = np.sum(self.N_z*self.g_z, axis=0)
        denom = np.sum(self.N_z, axis=0)
        S = self.c * (numr / (denom+1e-9))
        return S

    def compute_zcr(self):
        y0 = preprocessing.apply_bfilter(self.signal, 60, self.sr, 1, 'highpass')
        y1 = preprocessing.apply_bfilter(y1, 600, self.sr, 1, 'lowpass')
        zcr = librosa.feature.zero_crossing_rate(y1, frame_length=self.window_size, 
                                                hop_length=self.hop_length)
        return zcr

    def compute_ste(self, rab):
        N = self.window_size
        frames = librosa.util.frame(self.signal, frame_length=self.window_size,
                                    hop_length=self.hop_length)
        if rab:
            idx = np.array(range(256))
            hn = 0.54 - 0.46 * np.cos(2*np.pi * idx / (N-1))
            ste = np.sum(frames*hn, axis=0, keepdims=True)
            return ste
        ste = np.mean(np.abs(frames)**2, axis=0, keepdims=True)
        return ste

    def gain_reduction(self, sharpness):
        N = sharpness.shape[0]
        sharpness
        gain = np.ones(N)
        for n in range(N):
            if sharpness[n] > self.sharp_thresh:
                gain[n] = 1 + (np.log(sharpness[n]) / np.log(0.1))
                if gain[n] < self.max_reduction:
                    gain[n] = self.max_reduction

        return gain

    def deesser(self, gain):
        y_out = np.zeros(self.signal.shape)
        frame_sig = librosa.util.frame(self.signal, frame_length=self.n_fft, hop_length=self.hop_length)
        '''
            M is the number of time frames. It needs to remain flexible based on the length of song.
            M will be an integer that depends on how many time frames an audio signal has.
        '''
        M, N = frame_sig.shape[0], frame_sig.shape[1]
        # fix padding that makes these dimensions not always aligned via stft
        # quick fix is a truncation of array 
        y = np.zeros((M, N))
        # TODO uncomment this..
        for m in range(9):
            print(m)
            print(len(gain))
            print(len(y))
            print(len(frame_sig))
            y[m] = gain[m] * frame_sig[m]
        y = y.flatten('F')
        n = y.shape[0]
        y_out[:n] = y
        return y_out


class ReverbSignal(Signal):
    def __init__(self, signal, n_fft, window_size, hop_length, peak, audio_type,
                reverbance, hf_damping, room_scale, wet_gain, effect_percent, hp_freq, lp_freq, order,
                stereo_depth, pre_delay):
        super().__init__(signal, n_fft, window_size, hop_length, peak, audio_type)
        self.reverbance = reverbance
        self.hf_damping = hf_damping
        self.room_scale = room_scale
        self.wet_gain = wet_gain
        self.effect_percent = effect_percent
        self.hp_freq = hp_freq
        self.lp_freq = lp_freq
        self.order = order
        self.stereo_depth = stereo_depth
        self.pre_delay = pre_delay
        self.effect_signal = preprocessing.compute_effect_signal(self.signal, self.effect_percent,
                                                                self.hp_freq, self.lp_freq, self.order, self.sr)
        self.dry_signal = self.signal * (1 - self.effect_percent)

    def reverb(self):
        fx = AudioEffectsChain().reverb(self.reverbance, self.hf_damping, self.room_scale, self.stereo_depth,
                                        self.pre_delay, self.wet_gain)
        y_fx = fx(self.effect_signal)
        y_out = self.dry_signal + y_fx
        return y_out


class SignalAggregator:
    '''Computes all of the aggregated stats for each effect'''
    def __init__(self, sr, M):
        self.sr = sr
        self.M = M

    def lfa(self, lfes): return sum([lfe for lfe in lfes]) / self.M

    def cfa(self, cfs): return sum([cf for cf in cfs]) / self.M

    def panning_locations(self, filter_freqs, signal_peaks):
        N_ks = np.unique(signal_peaks, return_inverse=True, return_counts=True)
        num_k = N_ks[0].shape[0]
        Ps = []
        for k in np.arange(num_k):
            freq = N_ks[0][k]
            N_k = N_ks[2][k]
            P = np.zeros((N_k))
            for i in np.arange(N_k):
                if N_k == 1:
                    P[i] = 1/2
                elif N_k + i % 2 != 0:
                    P[i] = (N_k - i - 1) / (2 * (N_k - i))
                elif (N_k + i % 2 == 0) and (N_k != 1):
                    P[i] = 1 - ((N_k - i) / (2 * (N_k -1)))
                idx = np.argwhere(signal_peaks == freq)[i][0]
                Ps.append([idx, P[i]])
        return Ps

    def loudness_avg(self, channels, holdtime, ltrhold, utrhold, release, attack):
        gains = [preprocessing.noise_gate(channels[i], holdtime, ltrhold, utrhold, release, attack, self.sr) 
                 for i in range(len(channels))]
        gains = [np.where(gain < 1, 0, 1) for gain in gains]
        gain_val = np.array(gains).sum(axis=0)
        L_g = [channel * gain for channel, gain in zip(channels, gains)] 
        L_c = np.array(L_g).sum(axis=0)
        # L_av = np.where(gain_val > 0, L_c / gain_val, -50)
        L_av = np.ones(gain_val.shape[0]) * -30
        np.divide(L_c, gain_val, out=L_av, where=gain_val != 0)
        return L_av
        # apply ema filter
        return L_av


class Mixer:
    def __init__(self, signals, output_path, sr):
        self.signals = signals
        self.output_path = output_path
        self.sr = sr

    def mix(self): 
        output = np.sum(self.signals, axis=0)
        return output.astype(np.float32)

    def output_wav(self, mixed_file): 
        write(self.output_path, self.sr, mixed_file)


class Track:
    def __init__(self, track, sr):
        self.track = track
        self.sr = sr

    def calculate_peak(self):
        peak = self.track.max()
        peak_db = librosa.amplitude_to_db([peak])
        return peak_db[0]

    def calculate_loudness(self):
        meter = pyln.Meter(self.sr)
        loudness = meter.integrated_loudness(self.track)
        return loudness

    def calculate_rms(self):
        rms_frame = librosa.feature.rms(self.track)
        rms = np.mean(rms_frame, axis=1)
        rms_db = librosa.amplitude_to_db(rms)
        return rms_db[0]
