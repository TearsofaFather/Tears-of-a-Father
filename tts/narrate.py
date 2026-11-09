import json, re, subprocess, sys, os
import numpy as np
import onnxruntime as rt
import wave

# Render kit for Tears of a Father (Windows/GPU copy of the cloud pipeline).
# Same model, same voices, same text processing; pronunciations come from a cache built on the
# cloud machine (espeak-ng 1.53.0), so every word is phonemized exactly as it was there.
BASE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(os.path.dirname(BASE), "models")
cfg = json.load(open(os.path.join(BASE, "config.json"), encoding="utf-8"))
VOCAB = cfg["vocab"]
SR = 24000

opts = rt.SessionOptions()
opts.intra_op_num_threads = int(os.environ.get("TOF_THREADS", "8"))
_want = os.environ.get("TOF_PROVIDER", "auto")
_avail = rt.get_available_providers()
if _want == "cpu":
    _prov = ["CPUExecutionProvider"]
else:
    _prov = [p for p in ("CUDAExecutionProvider", "DmlExecutionProvider") if p in _avail] + ["CPUExecutionProvider"]
sess = rt.InferenceSession(os.path.join(MODELS, "kokoro-v1.0.onnx"), opts, providers=_prov)
PROVIDER = sess.get_providers()[0]
inputs = {i.name: i for i in sess.get_inputs()}
TOK = "input_ids" if "input_ids" in inputs else "tokens"
voices = np.load(os.path.join(MODELS, "voices-v1.0.bin"))

_CACHE_PATH = os.path.join(BASE, "phonemes.json")
_CACHE = json.load(open(_CACHE_PATH, encoding="utf-8")) if os.path.exists(_CACHE_PATH) else {}
MISSES = []


def _espeak(p):
    if p in _CACHE:
        return _CACHE[p]
    MISSES.append(p)
    raise RuntimeError("No cached pronunciation for: %r  (the kit is out of date; ask Claude to rebuild it)" % p)


def phonemize(text):
    # espeak drops punctuation, so phonemize the words between punctuation marks
    parts = re.split(r'([,.;:!?—…"“”()])', text)
    out = []
    for p in parts:
        if not p:
            continue
        if re.fullmatch(r'[,.;:!?—…"“”()]', p):
            out.append(p if p in VOCAB else "")
            continue
        if not p.strip():
            out.append(" ")
            continue
        ph = _espeak(p)
        lead = " " if p[0].isspace() else ""
        trail = " " if p[-1].isspace() else ""
        out.append(lead + ph + trail)
    s = "".join(out)
    s = "".join(c for c in s if c in VOCAB)
    s = s.replace("bjˈuːɾifəl", "bjˈuːɾɪfəl")   # "beautiful": a short i, not "beauty-full" (Nov 4)
    s = s.replace("bˈɔɪ", "bˈoɪ")     # "boy": the closer o, so it is not drawn out into "baoy" (chosen Nov 4, option 4)
    return re.sub(r"\s+", " ", s).strip()


def speak(phonemes, voice, speed):
    toks = [VOCAB[c] for c in phonemes if c in VOCAB][:510]
    style = voice[len(toks) - 1]
    feed = {TOK: np.array([[0, *toks, 0]], dtype=np.int64),
            "style": np.asarray(style, dtype=np.float32).reshape(1, -1),
            "speed": np.array([speed], dtype=np.float32)}
    return sess.run(None, feed)[0].squeeze()


def sentences(par):
    return [s for s in re.split(r'(?<=[.!?…])["”]?\s+(?=[A-Z"“*])', par) if s.strip()]


def chunks(par, limit=380):
    buf, out = "", []
    for s in sentences(par):
        ps = phonemize(s)
        if len(ps) > limit:
            # long sentence: split on commas/semicolons
            for sub in re.split(r'(?<=[,;:—])\s+', s):
                sp = phonemize(sub)
                if buf and len(buf) + len(sp) + 1 > limit:
                    out.append(buf); buf = ""
                buf = (buf + " " + sp).strip()
            continue
        if buf and len(buf) + len(ps) + 1 > limit:
            out.append(buf); buf = ""
        buf = (buf + " " + ps).strip()
    if buf:
        out.append(buf)
    return out


def ref_aloud(line):
    # "— Genesis 5:24" -> "Genesis chapter 5, verse 24."
    def rep(m):
        book, ch, vs = m.group(1), m.group(2), m.group(3)
        vs = vs.replace("–", " through ").replace(",", " and")
        word = "verses" if (" through " in vs or " and" in vs) else "verse"
        return f"{book}, chapter {ch}, {word} {vs}."
    line = re.sub(r"—\s*((?:[1-3] )?[A-Z][a-z]+(?: [a-z]+ [A-Z][a-z]+)?) (\d+):([\d,–\s]+)", rep, line)
    return line


def blend(spec):
    total, acc = 0.0, None
    for part in spec.split(","):
        name, w = (part.split(":") + ["1"])[:2]
        w = float(w); v = voices[name].astype(np.float32) * w
        acc = v if acc is None else acc + v; total += w
    return acc / total


def narrate(text, out_path, voice_spec="am_onyx:0.6,am_santa:0.4", speed=0.9):
    voice = blend(voice_spec)
    pieces = []
    sil_short = np.zeros(int(SR * 0.35), dtype=np.float32)
    sil_par = np.zeros(int(SR * 0.7), dtype=np.float32)
    sil_break = np.zeros(int(SR * 1.6), dtype=np.float32)
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        if line in ("* * *", "\\* \\* \\*"):
            pieces.append(sil_break); continue
        line = line.lstrip("> ").strip()
        line = ref_aloud(line)
        line = line.replace("*", "")
        for ph in chunks(line):
            pieces.append(speak(ph, voice, speed)); pieces.append(sil_short)
        pieces.append(sil_par)
    audio = np.concatenate(pieces)
    audio = np.clip(audio / max(1e-6, np.abs(audio).max()) * 0.9, -1, 1)
    pcm = (audio * 32767).astype(np.int16)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    spec = sys.argv[3] if len(sys.argv) > 3 else "am_onyx:0.6,am_santa:0.4"
    speed = float(sys.argv[4]) if len(sys.argv) > 4 else 0.9
    narrate(open(src).read(), out, spec, speed)
