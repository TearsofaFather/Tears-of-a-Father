"""Chapter 8, third cut: the song carries the performance.
The song plays once, start to finish, at one steady level, with a shorter narration laid over it.
Near the end it rises smoothly so the crescendos hit harder. The shofar blast is lifted off the end of
the song and sounded at the moment Mr. Hart blows it in the story."""
import sys, json, subprocess, wave, numpy as np
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts'))
import fullcast as F

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
SONG = D + 'music/v17_mono24k.flac'   # author, Nov 11: no last uprise; the piece ends on its own
SHOFAR_AT = 296.4
EQ = 'equalizer=f=110:t=q:w=0.8:g=2,equalizer=f=450:t=q:w=1.2:g=-3'
SR = F.SR
paras = F.file_paragraphs(D + 'work/09-chapter-8.md')
# Jalen's two single-word answers are spoken as "Yes," (a lone "Yeah" comes out electronic in the voice)
paras = [p.replace('"Yeah," he said. "But just call it', '"Yes," he said. "But just call it').replace('"Yeah," Jalen said. "For when', '"Yes," Jalen said. "For when') for p in paras]
raw = json.load(open(D + 'work/09-chapter-8.json')); F.NARRATOR = raw.pop('_narrator', 'Narrator')
who = {int(k): v for k, v in raw.items()}
at = lambda s: next(i for i, p in enumerate(paras) if p.startswith(s))
P_BOW, P_AFTER, P_BLEW = at('He drew the bow'), at('In the silence after it'), at('The old man filled his lungs')

def eq(x):
    x = x / max(1e-6, np.abs(x).max()) * 0.9
    r = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', EQ,
                        '-ar', str(SR), '-f', 'f32le', '-'], input=x.astype(np.float32).tobytes(), capture_output=True)
    y = np.frombuffer(r.stdout, np.float32)
    act = np.abs(y) > 1e-3; y = y * (0.147 / max(1e-6, float(np.sqrt(np.mean(y[act] ** 2)))))
    return (y * min(1.0, 0.97 / max(1e-6, np.abs(y).max()))).astype(np.float32)   # plain gain instead of one-pass loudnorm (crackle, Nov 11)

def rend(lo, hi):
    out = []
    for i in range(lo, hi): out += F.render_paragraph(paras[i], who.get(i))
    return eq(np.concatenate(out))

# the shorter narration over the song, each passage placed at the part of the song it describes (seconds)
OVER = [
    (6, "The first note was so low that people felt it before they heard it. It was the note he had started with a year and a half ago, the night he heard the fear in his mother's voice through the studio window. Under it, so softly that at first only Jalen could hear it, the viola came in, holding him up."),
    (45, "He played the chemo room, and his father's hands shaking on the clippers. He played the hospital bed in the living room, and his father asleep on the couch with the television on, every night, every night, every night."),
    (85, "Then, from somewhere behind the closed curtain, a harp began: his mother's Sunday-afternoon music. In the front rows, people looked at one another. There was no harp on the stage."),
    (128, "Then the viola fell away and left him alone, and the cello climbed to the long note at the very top, the note he could never get past. His bow arm began to shake. He didn't stop. He leaned into the bow and gave the note his whole weight, and it grew, and grew, until the cello was shaking against his chest."),
    (182, "And then he stopped. Four hundred people sat in the dark and did not breathe."),
    (201, "Then, very softly, he began again from the bottom. It sounded like someone getting up off the floor."),
    (229, "Then, behind him, the curtain began to open. Fifty-eight students in white, on risers that climbed to the back wall. Every one of them had been playing from the very first note."),
    (241, "He remembered his mother's voice."),
    (244, "ANGELA:One day the curtain will certainly open, Jalen. And you'll see everybody who was playing with you the whole time."),
]
song_all = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', SONG, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                                        capture_output=True).stdout, np.float32)
# FIX A: gradual swell across the cello's last note (281.4 -> 288.4s), unity after; end point unchanged
def _ride(x):
    x = x.copy(); a, b = int(281.4*SR), int(288.4*SR); w = int(0.05*SR)
    seg = x[a:b]; fr = max(1, int(0.1*SR)); n = len(seg)//fr
    rms = np.array([np.sqrt(np.mean(seg[i*fr:(i+1)*fr]**2)) + 1e-6 for i in range(n)])
    tgt = np.interp(np.arange(n)/n, [0, 1], [0.135, 0.19])
    g = np.clip(tgt/rms, 0.4, 1.3)
    from scipy.ndimage import uniform_filter1d
    g = uniform_filter1d(g, 7); g[-6:] = np.linspace(g[-7], 1, 6)
    gs = np.interp(np.arange(len(seg))/fr, np.arange(n)+0.5, g)
    x[a:a+len(seg)] = seg*gs
    return x
# (the v16 crescendo ride is not needed: v17 has no final crescendo)
def _tame(x):   # author, Nov 11: the last crescendo arrives too suddenly and too big; let it rise slowly and top out lower
    x = x.copy(); fr = int(0.1 * SR); a, b = int(274 * SR), int(292 * SR)
    seg = x[a:b]; n = len(seg) // fr
    lev = np.array([20 * np.log10(np.sqrt(np.mean(seg[i*fr:(i+1)*fr] ** 2)) + 1e-9) for i in range(n)])
    from scipy.ndimage import uniform_filter1d
    lev = uniform_filter1d(lev, 10)                        # the level over a second, not every bow stroke
    t = 274 + (np.arange(n) + 0.5) * 0.1
    cap = np.interp(t, [274, 280, 287, 292], [-17.5, -17.0, -15.0, -15.0])   # a slow climb of about two decibels
    gdb = np.minimum(0, cap - lev); gdb = uniform_filter1d(gdb, 15)           # only ever turn it down, smoothly
    g = 10 ** (np.interp(np.arange(len(seg)) / fr, np.arange(n) + 0.5, gdb) / 20)
    x[a:a + len(seg)] = seg * g.astype(np.float32)
    return x
song = song_all[:int(282.6 * SR)].copy()                     # the piece, without the horn
def _lift(x, ratio):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af',
                        'asetrate=%d,atempo=%.6f,aresample=%d' % (int(SR * ratio), 1 / ratio, SR), '-f', 'f32le', '-'],
                       input=x.astype(np.float32).tobytes(), capture_output=True)
    return np.frombuffer(r.stdout, np.float32).copy()
# the master's second blast has the orchestra's last notes under it, and the gap between the blasts is hiss; use only the clean first blast
def _craft_horn():   # author, Nov 11: only the clean front of the blast (the later part carries a stormy hiss); sustain it, then a crafted release
    att = song_all[int(290.09 * SR):int(292.59 * SR)].copy()            # attack and the first, clean seconds
    loop = song_all[int(291.29 * SR):int(292.59 * SR)].copy()           # steady tone to hold the note a little longer
    xf = int(0.25 * SR); up = np.sqrt(np.linspace(0, 1, xf)).astype(np.float32); dn = np.sqrt(np.linspace(1, 0, xf)).astype(np.float32)
    out = att
    for _ in range(2):                                                # equal-power crossfades, so the joins don't show
        out = np.concatenate([out[:-xf], out[-xf:] * dn + loop[:xf] * up, loop[xf:]])
    out[:int(.015 * SR)] *= np.linspace(0, 1, int(.015 * SR)).astype(np.float32)
    rel = int(1.8 * SR); out[-rel:] *= ((1 + np.cos(np.linspace(0, np.pi, rel))) / 2).astype(np.float32)   # a breath running out, then the hall carries it
    return out
_b1 = _craft_horn()
_b2 = _lift(song_all[int(299.3 * SR):int(305.55 * SR)], 4 / 3); _b2[:int(.05*SR)] *= np.linspace(0, 1, int(.05*SR)); _b2[-int(.5*SR):] *= np.linspace(1, 0, int(.5*SR))
shofar = _b1      # the horn, saved for its moment: the clean first blast only, and the chapter's sound ends there
f = int(SR * 0.3); song[-f:] *= np.linspace(1, 0, f)
# one steady level under the narrator, then a single smooth rise into the final crescendos
t = np.arange(len(song)) / SR
SONG_GAIN = (10 ** (np.interp(t, [0, 252, 262, 300], [0, 0, 0, 0]) / 20)).astype(np.float32)

from scipy.signal import fftconvolve, butter, sosfilt
import cast as C
rng = np.random.default_rng(11)

def hall_ir(rt60=1.8, pre=0.025):
    """an auditorium: a short pre-delay, then a dark, smoothly decaying tail"""
    n = int(SR * rt60 * 1.1); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-6.9 * t / rt60)
    ir = sosfilt(butter(2, 3500, 'low', fs=SR, output='sos'), ir)
    ir = np.concatenate([np.zeros(int(SR * pre)), ir]); ir[0] = 0
    return (ir / np.sqrt(np.sum(ir ** 2))).astype(np.float32)
IR = hall_ir()

def hall(x, wet=0.3, tail=2.2):
    """the sound in the room: the dry sound plus the hall's reverberation, with room for the tail"""
    x = np.concatenate([x, np.zeros(int(SR * tail), np.float32)])
    w = fftconvolve(x, IR)[:len(x)]
    w *= np.sqrt(np.mean(x ** 2) + 1e-12) / np.sqrt(np.mean(w ** 2) + 1e-12)
    return ((1 - wet) * x + wet * w).astype(np.float32)

def mic(x):
    """a voice through the stage microphone and the house speakers"""
    y = sosfilt(butter(2, [180, 5500], 'band', fs=SR, output='sos'), x)
    y = np.tanh(y / (np.abs(y).max() + 1e-6) * 1.6) * np.abs(x).max()          # a little speaker push
    slap = np.zeros_like(y); dly = int(SR * 0.11); slap[dly:] = y[:-dly] * 0.05   # the back wall answering, lightly (author picked the lightest, Nov 12)
    return hall((y + slap).astype(np.float32), wet=0.10, tail=1.2)

def whisper(x):
    """just the voice, soft and plain: no echo, no effects"""
    return sosfilt(butter(2, 120, 'high', fs=SR, output='sos'), x).astype(np.float32)

IR_BIG = None
def big_hall(x, wet=0.45, tail=3.5):
    """the horn in a large hall: a longer, fuller tail"""
    global IR
    keep = IR; IR = hall_ir(rt60=2.6, pre=0.035)
    try: return hall(x, wet=wet, tail=tail)
    finally: IR = keep

def applause(dur=24.0, people=400):
    """four hundred people on their feet: a dense roar of hands, rising fast, holding, then thinning out"""
    n = int(SR * dur); t = np.arange(n) / SR
    env = np.interp(t, [0, 0.4, 2.5, 13, 19, dur], [0, 0.35, 1.0, 1.0, 0.35, 0.0])
    out = np.zeros(n, np.float32)
    for lo, hi in [(700, 1800), (1000, 2600), (1400, 3400), (1900, 4500), (900, 2200), (1200, 3000)]:
        k = int(SR * 0.03); kt = np.arange(k) / SR
        kern = sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), rng.standard_normal(k)) * np.exp(-kt / 0.006)
        rate = people * 4.2 / 6                                   # claps per second from this group
        events = np.zeros(n, np.float32)
        idx = rng.integers(0, n, int(rate * dur)); events[idx] += rng.uniform(0.3, 1.0, len(idx)).astype(np.float32)
        events *= (rng.uniform(0, 1, n) < env).astype(np.float32) + 0.0   # fewer hands at the start and end
        out += fftconvolve(events, kern)[:n].astype(np.float32)
    out *= env.astype(np.float32)
    out = hall(out / (np.abs(out).max() + 1e-6), wet=0.4, tail=1.5)
    return out

LEN = {}
def rend_one(i):
    x = _rend_one(i); LEN[i] = len(x); return x
def _rend_one(i):
    p = paras[i]
    if i in REMEMBER:
        txt = paras[i].strip('*').strip()
        return np.concatenate([whisper(eq(np.concatenate(F.say(txt, 'Angela', (0.9, 0.0))))) * 10 ** (-3 / 20), np.zeros(int(SR * 0.6), np.float32)])
    if i in MIC:      # the spoken words go through the microphone, the narration stays dry
        out = []
        segs = C.segments(p)
        mood = F.mood_of(' '.join(t for k, t in segs if k == 'n'))
        for kind, txt in segs:
            txt = txt.strip()
            if kind == 'q': out.append(('mic', np.concatenate(F.say(txt.strip('"'), who[i], mood))))
            elif any(ch.isalpha() for ch in txt): out.append(('dry', np.concatenate(F.say(txt, F.NARRATOR))))
        x = np.concatenate([eq(a) if k == 'dry' else mic(eq(a) * 0.9) for k, a in out] + [np.zeros(int(SR * 0.45), np.float32)])
        return x
    return eq(np.concatenate(F.render_paragraph(p, who.get(i))))

MIC = {at('At 8:20, the vice principal'), next(i for i, p in enumerate(paras) if p.startswith('"I\'m dedicating this'))}
P_STAND = at('For a second no one stirred')
REMEMBER = {i for i, p in enumerate(paras) if p.startswith('*Your dad hears more')}
lead = np.concatenate([rend_one(i) for i in range(0, P_BOW + 1)])
up = np.concatenate([rend_one(i) for i in range(P_AFTER, P_BLEW + 1)])
mid = np.concatenate([rend_one(i) for i in range(P_BLEW + 1, P_STAND + 1)])
rest_parts = [rend_one(i) for i in range(P_STAND + 1, len(paras))]
rest = np.concatenate(rest_parts)
P_MIA = next(i for i, p in enumerate(paras) if 'went to be with Jesus' in p)
if False and P_MIA > P_STAND:   # no music under Mia comforting her father and brother
    off = sum(len(x) for x in rest_parts[:P_MIA - P_STAND - 1])
    TURN = 268.5; t0 = max(0, off - int((TURN - 262.0) * SR))
    cue = song_all[int((TURN - (off - t0) / SR) * SR):int(279.5 * SR)].copy()
    fi, fo = int(2.5 * SR), int(4 * SR); cue[:fi] *= np.linspace(0, 1, fi) ** 2; cue[-fo:] *= np.linspace(1, 0, fo)
    if t0 + len(cue) > len(rest): rest = np.concatenate([rest, np.zeros(t0 + len(cue) - len(rest), np.float32)])
    sp = np.abs(rest) > 0.02; vr = np.sqrt(np.mean(rest[sp] ** 2)); cue *= vr / (np.sqrt(np.mean(cue ** 2)) + 1e-9) * 10 ** (-6 / 20)
    env = np.convolve((np.abs(rest[t0:t0 + len(cue)]) > 0.01).astype(np.float32), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode='same')
    duck = np.clip(np.convolve(env > 0.02, np.ones(int(0.7 * SR)) / int(0.7 * SR), mode='same'), 0, 1)
    rest[t0:t0 + len(cue)] += cue * 10 ** (-10 * duck / 20)
    print('Mia cue at', round(t0 / SR, 1), 's into the last part')
z = lambda s: np.zeros(int(SR * s), np.float32)
horn = np.concatenate([np.zeros(int(1.7*SR), np.float32), big_hall(shofar)])          # the ram's horn filling the hall
clap = applause() * 0.55
song = hall(song, wet=0.18, tail=0.0)[:len(song)] * SONG_GAIN   # a touch of the auditorium on the whole piece
sys.argv = ['x']
import importlib.util
spec = importlib.util.spec_from_file_location('perf', D + 'work/ch8_perf_v2.py'); perf = importlib.util.module_from_spec(spec); spec.loader.exec_module(perf)
_end = song_all[:int(288.0 * SR)].copy(); _end[-int(1.0 * SR):] *= np.linspace(1, 0, int(1.0 * SR))   # the whole crescendo, then its natural fade to silence
perf.song = _end                              # the orchestra exactly as mastered: no added echo of ours
perf.duck_under = lambda p, at, line, voice_db, music_db=-10: p   # nothing spoken over the orchestra while it plays
perf.CUTS = [0, 184.7, len(perf.song) / SR]
def _part(i):   # author, Nov 11: smooth, rounded fades so no piece stops short
    x = perf.song[int(perf.CUTS[i] * SR):int(perf.CUTS[i + 1] * SR)].copy()
    fi, fo = int(SR * 2.0), int(SR * (4.0 if i == 0 else 1.5))
    if i > 0: x[:fi] *= ((1 - np.cos(np.linspace(0, np.pi, fi))) / 2).astype(np.float32)
    x[-fo:] *= ((1 + np.cos(np.linspace(0, np.pi, fo))) / 2).astype(np.float32)
    return x
perf.part = _part
bed = perf.performance()
full = np.concatenate([lead[:-1] if False else lead, z(0.8), bed, z(2.6), up, z(0.6), horn, z(0.6), mid, rest])
# exact paragraph start times (seconds into the chapter audio), for the follow-along text
_st = {}; _c = 0.0
for _i in range(0, P_BOW + 1): _st[_i] = _c; _c += LEN[_i] / SR
_c += 0.8; _bed = [_i for _i in range(P_BOW + 1, P_AFTER)]; _w = np.array([len(paras[_i]) + 10 for _i in _bed], float)
_b0 = _c; _c += len(bed) / SR; _cum = np.concatenate([[0], np.cumsum(_w)]) / _w.sum()
for _k, _i in enumerate(_bed): _st[_i] = _b0 + _cum[_k] * (len(bed) / SR)
_c += 2.6
for _i in range(P_AFTER, P_BLEW + 1): _st[_i] = _c; _c += LEN[_i] / SR
_c += 0.6 + len(horn) / SR + 0.6
for _i in range(P_BLEW + 1, len(paras)): _st[_i] = _c; _c += LEN[_i] / SR
json.dump({'starts': [round(_st[_i], 2) for _i in range(len(paras))], 'total': round(len(full) / SR, 2)}, open(D + 'work/09-chapter-8-new.times.json', 'w'))
print('times written; end', round(_c, 1), 'vs audio', round(len(full) / SR, 1))
full = np.nan_to_num(full)
mix = np.clip(full / max(1.0, np.abs(full).max() / 0.97), -1, 1)
c0 = 0
with wave.open(D + 'work/09-chapter-8-new.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('built', len(mix) / SR / 60, 'min; applause at', c0 / SR / 60)
