"""The Chapter 8 ram's horn, saved once so Chapters 23 and 36 use the same one (author, Nov 12: Ch8's horn is the right one).
Same cut as ch8_v9.py: only the clean front of the v17 blast, sustained, a crafted release, then the big hall."""
import os, subprocess, numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
SR = 24000
song_all = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', D + 'music/v17_mono24k.flac', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True).stdout, np.float32).copy()
att = song_all[int(290.09 * SR):int(292.59 * SR)].copy()
loop = song_all[int(291.29 * SR):int(292.59 * SR)].copy()
xf = int(0.25 * SR); up = np.sqrt(np.linspace(0, 1, xf)).astype(np.float32); dn = np.sqrt(np.linspace(1, 0, xf)).astype(np.float32)
out = att
for _ in range(2):
    out = np.concatenate([out[:-xf], out[-xf:] * dn + loop[:xf] * up, loop[xf:]])
out[:int(.015 * SR)] *= np.linspace(0, 1, int(.015 * SR)).astype(np.float32)
rel = int(1.8 * SR); out[-rel:] *= ((1 + np.cos(np.linspace(0, np.pi, rel))) / 2).astype(np.float32)
rng = np.random.default_rng(11)
def hall_ir(rt60=1.8, pre=0.025):
    n = int(SR * rt60 * 1.1); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-6.9 * t / rt60)
    ir = sosfilt(butter(2, 3500, 'low', fs=SR, output='sos'), ir)
    ir = np.concatenate([np.zeros(int(SR * pre)), ir]); ir[0] = 0
    return (ir / np.sqrt(np.sum(ir ** 2))).astype(np.float32)
hall_ir()                                   # same random sequence as ch8_v9.py (its first, smaller hall)
IR = hall_ir(rt60=2.6, pre=0.035)
x = np.concatenate([out, np.zeros(int(SR * 3.5), np.float32)])
w = fftconvolve(x, IR)[:len(x)]
w *= np.sqrt(np.mean(x ** 2) + 1e-12) / np.sqrt(np.mean(w ** 2) + 1e-12)
horn = ((1 - 0.45) * x + 0.45 * w).astype(np.float32)
np.save(D + 'music/horn_ch8.npy', horn)
print('horn', round(len(horn) / SR, 2), 's, peak', round(float(np.abs(horn).max()), 3))
