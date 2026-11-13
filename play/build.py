"""Playscript builder.
Merges a chapter's manuscript paragraphs (kit work/<stem>.md), speaker map (work/<stem>.json),
line timing from the renderer (out/<stem>.lines.json, paragraph starts in out/<stem>.times.json)
and the hand-written stage layer (spec/<stem>.json) into:
  out/<stem>.play.json   the script, for the private Playscript tab
  out/<stem>.cues.csv    a cue sheet for a recording session: every spoken line with timecode in/out
Usage: python3 build.py <stem> [kitdir]
"""
import sys, os, json, re, csv
HERE = os.path.dirname(os.path.abspath(__file__))
stem = sys.argv[1]; KIT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/kitwt'
sys.path.insert(0, os.path.join(KIT, 'tts'))
import fullcast as F, cast as C

paras = F.file_paragraphs(os.path.join(KIT, 'work', stem + '.md'))
raw = json.load(open(os.path.join(KIT, 'work', stem + '.json'))); raw.pop('_narrator', None)
who = {int(k): v for k, v in raw.items()}
spec = json.load(open(os.path.join(HERE, 'spec', stem + '.json')))
L = json.load(open(os.path.join(KIT, 'out', stem + '.lines.json')))['lines']
starts = json.load(open(os.path.join(KIT, 'out', stem + '.times.json')))['starts']
assert len(starts) == len(paras) + 1, ('times.json does not match this text', len(starts), len(paras))
END = starts[-1]
VOX = spec.get('voices', {}); NARR = spec.get('narrator', 'Narrator')

def clean(t):
    t = t.strip().lstrip('> ').strip()
    t = re.sub(r'^#+\s*', '', t)
    return t.replace('\\*', '*')

def show_name(voice):
    return VOX.get(voice, voice).upper()

# group timed lines by paragraph, in order
byp = {}
for x in L: byp.setdefault(x['p'], []).append(x)

def para_lines(i):
    """the spoken lines of paragraph i, with the manuscript's own wording where the split lines up"""
    got = byp.get(i, [])
    if not got: return []
    p = paras[i]; w = who.get(i)
    if len(got) == 1:
        texts = [clean(p)]
    else:
        segs = [(k, t.strip()) for k, t in C.segments(clean(p)) if k == 'q' or re.search(r'[A-Za-z]', t)]
        texts = [t for k, t in segs] if len(segs) == len(got) else [g['text'] for g in got]
    out = []
    for g, t in zip(got, texts):
        narr = g['who'] == NARR
        if not narr and t.startswith('"') and t.endswith('"'): t = t[1:-1]
        out.append({'k': 'line', 'who': show_name(g['who']), 'voice': g['who'], 'narr': narr,
                    'text': t, 'tc0': g['t0'], 'tc1': g['t1'], 'p': i})
    return out

scenes = spec['scenes']; dirs = {int(k): v for k, v in spec['dirs'].items()}
out_scenes = []
for si, sc in enumerate(scenes):
    p0 = sc['p0']; p1 = scenes[si + 1]['p0'] if si + 1 < len(scenes) else len(paras)
    items = []
    for i in ([-1] if p0 == -1 else range(p0, p1)):
        if i in dirs:
            items.append({'k': 'dir', 'text': dirs[i], 'tc': 0.0 if i < 0 else starts[i], 'p': i})
        items += para_lines(i)
    tc0 = 0.0 if p0 < 0 else starts[p0]
    tc1 = starts[p1] if p1 < len(paras) else END
    if p0 == -1: tc1 = starts[0]
    out_scenes.append({'n': si, 'title': sc['title'], 'setting': sc['setting'], 'tc0': tc0, 'tc1': tc1, 'items': items})

# cue numbers: <chapter>-<scene>-<line>
chap = re.sub(r'\D', '', stem.split('-', 1)[1]) or '0'
for sc in out_scenes:
    k = 0
    for it in sc['items']:
        if it['k'] == 'line':
            k += 1; it['id'] = '%s.%d.%03d' % (chap, sc['n'], k)

# every timed line must land in the script exactly once, in time order
seen = [it for sc in out_scenes for it in sc['items'] if it['k'] == 'line']
assert len(seen) == len(L), ('lines lost', len(seen), len(L))
assert all(a['tc0'] <= b['tc0'] for a, b in zip(seen, seen[1:])), 'out of order'
missing = sorted(set(dirs) - {it['p'] for sc in out_scenes for it in sc['items'] if it['k'] == 'dir'})
assert not missing, ('directions not placed', missing)

play = {k: spec[k] for k in ('stem', 'title', 'act', 'staging', 'cast')}
play.update({'runtime': END, 'scenes': out_scenes, 'lines': len(seen),
             'speakers': sorted({it['who'] for it in seen if not it['narr']})})
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
json.dump(play, open(os.path.join(HERE, 'out', stem + '.play.json'), 'w'), ensure_ascii=False, indent=1)

def tc(s):
    h = int(s // 3600); m = int(s % 3600 // 60); return '%02d:%02d:%06.3f' % (h, m, s % 60)
with open(os.path.join(HERE, 'out', stem + '.cues.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['cue', 'chapter', 'scene', 'kind', 'character', 'voice_slot', 'tc_in', 'tc_out', 'seconds_in', 'seconds_out', 'duration', 'text'])
    for sc in out_scenes:
        for it in sc['items']:
            if it['k'] == 'line':
                w.writerow([it['id'], spec['title'], '%d. %s' % (sc['n'], sc['title']), 'narration' if it['narr'] else 'dialogue',
                            it['who'], it['voice'], tc(it['tc0']), tc(it['tc1']), it['tc0'], it['tc1'], round(it['tc1'] - it['tc0'], 2), it['text']])
            else:
                w.writerow(['', spec['title'], '%d. %s' % (sc['n'], sc['title']), 'direction', '', '', tc(it['tc']), '', it['tc'], '', '', it['text']])
print(stem, len(out_scenes), 'scenes,', len(seen), 'lines,', round(END / 60, 1), 'min')
