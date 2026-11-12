"""Voices through a microphone to a crowd (author picked the lightest levels, Nov 12).
hall: an indoor room (gala, assembly hall); plaza: outdoor loudspeakers with a late bounce off far buildings."""
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
SR = 24000
_rng = np.random.default_rng(11)
def _ir(rt60, pre):
    n = int(SR * rt60 * 1.1); t = np.arange(n) / SR
    ir = _rng.standard_normal(n) * np.exp(-6.9 * t / rt60)
    ir = sosfilt(butter(2, 3500, 'low', fs=SR, output='sos'), ir)
    ir = np.concatenate([np.zeros(int(SR * pre)), ir]); ir[0] = 0
    return (ir / np.sqrt(np.sum(ir ** 2))).astype(np.float32)
IR_HALL = _ir(1.8, 0.025); IR_OUT = _ir(1.2, 0.05)
LEVEL = {'hall': (0.10, 0.05, 0.11, 1.2, IR_HALL), 'plaza': (0.08, 0.06, 0.28, 1.0, IR_OUT)}
def mic(x, kind='hall'):
    wet, slap, dly, tail, ir = LEVEL[kind]
    pk = np.abs(x).max() + 1e-6
    y = sosfilt(butter(2, [180, 5500], 'band', fs=SR, output='sos'), x)
    y = np.tanh(y / (np.abs(y).max() + 1e-6) * 1.6) * pk
    s = np.zeros_like(y); d = int(SR * dly); s[d:] = y[:-d] * slap
    y = np.concatenate([(y + s).astype(np.float32), np.zeros(int(SR * tail), np.float32)])
    w = fftconvolve(y, ir)[:len(y)]
    w *= np.sqrt(np.mean(y ** 2) + 1e-12) / np.sqrt(np.mean(w ** 2) + 1e-12)
    return ((1 - wet) * y + wet * w).astype(np.float32)
