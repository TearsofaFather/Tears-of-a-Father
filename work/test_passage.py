"""Render the opening of Chapter 1 (an already-finished chapter) so the PC copy can be compared with the cloud copy."""
import sys, os, json, wave, numpy as np
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, '..', 'tts')); import fullcast as F
name = '02-chapter-1'
paras = F.file_paragraphs(os.path.join(here, name + '.md'))[:14]
raw = json.load(open(os.path.join(here, name + '.json'), encoding='utf-8')); F.NARRATOR = raw.pop('_narrator', 'Narrator'); who = {int(k): v for k, v in raw.items()}
pieces = []
for i, p in enumerate(paras):
    pieces += F.render_paragraph(p, who.get(i))
a = np.concatenate(pieces); a = np.clip(a / max(1e-6, np.abs(a).max()) * 0.9, -1, 1)
out = sys.argv[1] if len(sys.argv) > 1 else 'test.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(F.SR); w.writeframes((a * 32767).astype(np.int16).tobytes())
print('wrote', out, round(len(a) / F.SR, 1), 's')
