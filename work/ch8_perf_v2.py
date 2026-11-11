"""The performance, told in the gaps: the song is split at four natural breaths. Before each part the
narrator briefly sets it up in the clear, then the music plays on its own with no talking over it."""
import sys, subprocess, numpy as np
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
import fullcast as F
from scipy.signal import fftconvolve, butter, sosfilt

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
SONG = D + 'music/v16_mono24k.flac'
EQ = 'equalizer=f=110:t=q:w=0.8:g=2,equalizer=f=450:t=q:w=1.2:g=-3,loudnorm=I=-18:TP=-1.5:linear=true'
SR = F.SR
rng = np.random.default_rng(11)

def eq(x):
    x = x / max(1e-6, np.abs(x).max()) * 0.9
    r = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', EQ,
                        '-ar', str(SR), '-f', 'f32le', '-'], input=x.astype(np.float32).tobytes(), capture_output=True)
    return np.frombuffer(r.stdout, np.float32)

def hall_ir(rt60=1.8, pre=0.025):
    n = int(SR * rt60 * 1.1); t = np.arange(n) / SR
    ir = sosfilt(butter(2, 3500, 'low', fs=SR, output='sos'), rng.standard_normal(n) * np.exp(-6.9 * t / rt60))
    ir = np.concatenate([np.zeros(int(SR * pre)), ir])
    return (ir / np.sqrt(np.sum(ir ** 2))).astype(np.float32)
IR = hall_ir()

def hall(x, wet=0.18):
    w = fftconvolve(x, IR)[:len(x)]
    w *= np.sqrt(np.mean(x ** 2) + 1e-12) / np.sqrt(np.mean(w ** 2) + 1e-12)
    return ((1 - wet) * x + wet * w).astype(np.float32)

def say(text, who=None):
    who = who or F.NARRATOR
    return eq(np.concatenate(F.say(text, who)))

def soft(text):          # Angela's remembered words: her own voice, soft and plain
    x = sosfilt(butter(2, 120, 'high', fs=SR, output='sos'), say(text, 'Angela')).astype(np.float32)
    return x * 10 ** (-3 / 20)

song_all = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', SONG, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                                        capture_output=True).stdout, np.float32) * 10 ** (-2.5 / 20)
song = hall(song_all[:int(282.6 * SR)].copy())
CUTS = [0, 184.7, 282.6]                        # one breath in the song, where Jalen stops
def part(i):
    x = song[int(CUTS[i] * SR):int(CUTS[i + 1] * SR)].copy()
    fi, fo = int(SR * 2.0), int(SR * (3.0 if i == 0 else 0.3))
    if i > 0: x[:fi] *= np.linspace(0, 1, fi) ** 2
    x[-fo:] *= np.linspace(1, 0, fo) ** 0.5
    return x

def duck_under(p, at, line, voice_db, music_db=-10):
    """lower the music smoothly, let the narrator say his line, then bring the music back up"""
    v = sosfilt(butter(2, 120, 'high', fs=SR, output='sos'), say(line)).astype(np.float32) * 10 ** (voice_db / 20)
    s0 = int(SR * at); e0 = s0 + len(v)
    g = np.ones(len(p), np.float32)
    r = int(SR * 1.5)
    g[max(0, s0 - r):s0] = np.linspace(1, 10 ** (music_db / 20), min(r, s0))
    g[s0:e0] = 10 ** (music_db / 20)
    g[e0:e0 + r] = np.linspace(10 ** (music_db / 20), 1, len(g[e0:e0 + r]))
    p = p * g
    p[s0:e0] += v[:max(0, len(p) - s0)]
    return p

FIRST = "The first note was so low that people felt it before they heard it. Under it, so softly that at first only Jalen could hear it, the viola came in, holding him up."
CLIMB = (121.5, "The viola fell away, and the cello climbed alone to the note he could never get past. He didn't stop.")
STOP = "And then he stopped. Four hundred people sat in the dark and did not breathe. Then, very softly, he began again from the bottom."
OVER = (230.0 - 184.7, "And the curtain began to open behind them.")
z = lambda s: np.zeros(int(SR * s), np.float32)

def performance():
    a = duck_under(part(0), CLIMB[0], CLIMB[1], voice_db=-4)
    b = duck_under(part(1), OVER[0], OVER[1], voice_db=-12, music_db=-6)
    return np.concatenate([say(FIRST), z(0.6), a, z(0.8), say(STOP), z(0.6), b, z(0.8)])

if __name__ == '__main__':
    F.NARRATOR = 'Narrator'
    x = np.concatenate([say("He drew the bow across the C string."), z(0.8), performance()])
    x = x / np.abs(x).max() * 0.95
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-b:a', '160k',
                    D + 'out/Chapter 8 sample - told in the gaps v2 (music under the curtain line).mp3'], input=x.tobytes(), check=True)
    print('sample', len(x) / SR / 60, 'min')
