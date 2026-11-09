"""Full-cast renderer: narrator for narration, a tailored voice for each character's lines.
Usage:
  python3 fullcast.py chapter manuscript.md "Chapter 1:" maps/ch01.json out.wav
  python3 fullcast.py sampler out.wav
Speaker map: {"para index": "Name"} -> quoted words in that paragraph spoken by Name, the rest by the narrator.
             {"para index": "*Name"} -> the whole paragraph by Name (a text message, a letter, a recording)."""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import readfix
import json, re, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import narrate as N
import cast as C

# name: (voice blend, speed, pitch). Pitch stays within 0.88-1.05 so nobody sounds shrill or cartoonish.
CAST = {
    'Narrator':     ('am_michael:0.75,am_puck:0.25', 0.93, 1.00, {'breathe': True, 'inner': True}),   # Ezra tells the story (option D)
    # the grown men
    'Ezra':         ('am_michael:0.75,am_puck:0.25', 0.93, 1.00, {'breathe': True}),
    'Calvin':       ('am_santa:0.5,am_fenrir:0.5', 0.84, 1.00, {'breathe': True, 'accent': 'southern'}),   # an old Southern country preacher
    'Walt':           ('am_michael:0.6,am_onyx:0.4', 0.90, 1.00, {'breathe': True, 'tremor': 0.004, 'rate': 4.5}),
    'Pastor Grant':   ('am_fenrir:0.5,am_michael:0.5', 0.95, 1.00, {'breathe': True}),
    'Mr. Hart':       ('bm_fable:0.7,bm_george:0.3', 0.88, 1.00, {'breathe': True}),
    'Crowe':          ('bm_george:0.5,am_michael:0.5', 0.93, 1.00, {'breathe': True}),
    'Trent':          ('am_puck:0.6,am_michael:0.4', 1.02, 1.00, {'breathe': True}),
    'Elijah':       ('am_michael:0.6,hm_omega:0.4', 0.92, 1.00, {'breathe': True, 'accent': 'mideast'}),   # an old man from the Middle East
    # the young
    'Jalen':          ('am_puck:0.7,am_fenrir:0.3', 0.98, 1.00, {'breathe': True}),
    'Mia':            ('af_heart:0.7,af_sky:0.3', 0.92, 1.05, {'breathe': True}),   # clear set: one small lift so she still sounds five
    # the women
    'Kambria':      ('af_bella', 0.93, 1.00, {'breathe': True}),
    'Kambria Narrator': ('af_bella', 0.93, 1.00, {'breathe': True, 'inner': True}),   # she tells her own chapters
    'Angela':         ('af_heart:0.5,af_nicole:0.5', 0.92, 0.95, {'breathe': True}),   # new voice, approved Nov 6
    'Loretta':        ('af_heart:0.5,af_nicole:0.5', 0.84, 1.00, {'breathe': True, 'tremor': 0.007, 'rate': 5.0}),
    'Celeste':        ('af_nicole:0.5,af_heart:0.5', 0.92, 1.00, {'breathe': True}),
    'Dr. Shaw':       ('bf_emma:0.8,bf_isabella:0.2', 0.96, 1.00, {'breathe': True}),
    'Mother Hattie':  ('af_heart:0.6,af_bella:0.4', 0.87, 0.94, {'breathe': True, 'tremor': 0.005, 'rate': 4.6, 'boom': 4}),   # Grandma, approved Nov 9 (voice C); phone-line effect is added per call via 'Mother Hattie Phone'
    'Mother Hattie Phone': ('af_heart:0.6,af_bella:0.4', 0.87, 0.94, {'breathe': True, 'tremor': 0.005, 'rate': 4.6, 'boom': 4, 'phone': 3.0}),
    'Bishop Sterling': ('am_fenrir:0.6,bm_george:0.4', 0.92, 1.00, {'breathe': True}),
    'Lucas Thorne': ('am_michael:0.6,bm_george:0.4', 0.96, 1.00, {'breathe': True}),
    # minor parts
    'Man':            ('am_michael:0.5,am_fenrir:0.5', 1.00, 1.00, {'breathe': True}),
    'Old man':        ('bm_fable:0.6,am_fenrir:0.4', 0.88, 1.00, {'breathe': True, 'tremor': 0.006, 'rate': 5.0}),
    'Woman':          ('af_heart:0.5,af_sarah:0.5', 0.97, 1.00, {'breathe': True}),
    'Anchor':         ('af_kore:0.5,af_heart:0.5', 1.00, 1.00, {'breathe': True}),
    'Professor':      ('bm_george:0.6,am_michael:0.4', 0.95, 1.00, {'breathe': True}),
    'Ruth':           ('af_sarah:0.6,af_kore:0.4', 0.93, 1.00, {'breathe': True}),
    # the Tribulation cast
    'Nina':           ('af_nova:0.5,af_alloy:0.3,bf_emma:0.2', 0.95, 0.96, {'breathe': True, 'tremor': 0.002, 'rate': 3.0}),
    'Juno':           ('af_nicole:0.5,bf_isabella:0.3,af_aoede:0.2', 0.94, 0.97, {'breathe': True, 'accent': 'mideast_soft', 'tremor': 0.002, 'rate': 3.5}),   # Nina's AI assistant: warm, softly accented, not mechanical
    'Kroll':          ('am_eric:0.6,am_liam:0.4', 0.99, 1.00, {'breathe': True}),
    'Volkov':         ('am_onyx:0.7,am_adam:0.3', 0.88, 1.00, {'breathe': True}),
    'Vale':           ('bm_lewis:0.6,am_echo:0.4', 0.93, 1.00, {'breathe': True}),
    'Arcangeli':      ('im_nicola:0.5,bm_george:0.5', 0.92, 1.00, {'breathe': True}),
    'Michael':        ('am_onyx:0.5,am_fenrir:0.5', 0.94, 1.00, {'breathe': True}),
    'David':          ('am_adam:0.6,am_liam:0.4', 0.99, 1.00, {'breathe': True}),
    'Kyle':           ('am_liam:0.7,am_puck:0.3', 1.00, 1.00, {'breathe': True}),
    'Girl':           ('af_sky:0.7,af_heart:0.3', 0.95, 1.06, {'breathe': True}),
    'Leon':           ('am_onyx:0.6,am_santa:0.4', 0.86, 1.00, {'breathe': True}),
    'Patrice':        ('af_heart:0.6,bf_emma:0.4', 0.93, 1.00, {'breathe': True}),
    'Witness':        ('am_onyx:0.5,bm_fable:0.5', 0.86, 1.00, {'breathe': True}),
    'Witness 2':      ('bm_george:0.5,am_santa:0.5', 0.86, 1.00, {'breathe': True}),
    'Sal':            ('am_onyx:0.6,am_fenrir:0.4', 0.90, 1.00, {'breathe': True}),
    'Denise':         ('af_sarah:0.6,af_heart:0.4', 0.95, 1.00, {'breathe': True}),
    'Sarah':          ('af_jessica:0.6,af_sarah:0.4', 0.98, 1.00, {'breathe': True}),
}
_voices = {}
NARRATOR = 'Narrator'   # whose voice tells this chapter; a map can set "_narrator"
SR = N.SR


def voice(name):
    if name not in _voices:
        spec, sp, pt, *fx = CAST[name]
        _voices[name] = (N.blend(spec), sp, pt, fx[0] if fx else {})
    return _voices[name]


def _southern(s):
    s = s.replace('aɪ', 'aː')                       # "right" -> "raht"
    s = re.sub(r'ɛ([nm])', r'ɪ\1', s)               # "parents" -> "parints"
    s = re.sub(r'ɪŋ\b', 'ɪn', s)                    # "goin'"
    s = s.replace('eɪ', 'ɛɪ')
    s = s.replace('ˈæ', 'ˈæɪ')                      # "last" -> "laist"
    return s.replace('ˈɪ', 'ˈɪə')                   # the drawl on stressed short i


def _mideast(s):
    s = s.replace('ɜː', 'ɛr').replace('ɚ', 'er').replace('ɹ', 'r')   # every r rolled and spoken
    for a, b in (('oʊ', 'o'), ('eɪ', 'e'), ('ɑː', 'a'), ('ɔː', 'o'), ('æ', 'a'), ('ʌ', 'a'), ('ɪ', 'i'), ('ʊ', 'u')):
        s = s.replace(a, b)                          # pure, even vowels
    return s.replace('p', 'b')


def _mideast_soft(s):
    s = s.replace('ɜː', 'ɛr').replace('ɚ', 'er').replace('ɹ', 'ɾ')   # a light tapped r, no hard American r
    for a, b in (('oʊ', 'o'), ('eɪ', 'e'), ('ɑː', 'a'), ('æ', 'a'), ('ʌ', 'a')):
        s = s.replace(a, b)                          # steadier vowels, nothing else flattened
    return s


ACCENTS = {'southern': _southern, 'mideast': _mideast, 'mideast_soft': _mideast_soft}   # accents live in the pronunciation, not in effects


def say(text, name, mood=(1.0, 0.0)):
    """speak text in a character's voice; the pitch is set by resampling, the speed is compensated so the pace stays right"""
    v, sp, pt, fx = voice(name)
    text = N.ref_aloud(readfix.fix_read(text)).replace('*', '').strip()
    # titles are read as words, so "Mr. Hart" flows as one name instead of breaking after the period
    text = re.sub(r'\b(?:MENE|Mene)\b', 'Men-eh', text)
    for a, b in (('Mrs.', 'Missus'), ('Mr.', 'Mister'), ('Ms.', 'Miz'), ('Dr.', 'Doctor'), ('Rev.', 'Reverend')):
        text = text.replace(a + ' ', b + ' ')
    out = []
    rng = np.random.default_rng(len(text))
    units = []
    acc = ACCENTS.get(fx.get('accent'), lambda s: s)
    for ph in map(acc, N.chunks(text)):          # whole phrases of several sentences, so the voice flows across them
        f = 1.0
        if fx.get('breathe'):          # a gentle, natural drift in pace from phrase to phrase
            f = 1 + rng.uniform(-0.02, 0.02)
            if ph.rstrip().endswith(('…', '...')): f -= 0.04
        units.append((ph, sp * f * mood[0]))
    for ph, spd in units:
        a = N.speak(ph, v, spd / pt)
        if abs(pt - 1) > 1e-3:
            from fractions import Fraction
            from scipy.signal import resample_poly
            fr = Fraction(pt).limit_denominator(100)
            a = resample_poly(a, fr.denominator, fr.numerator).astype(np.float32)
        if fx.get('tremor'):    # the slight unsteady pitch of an old voice
            t = np.arange(len(a)) / SR
            pos = np.cumsum(1 + fx['tremor'] * np.sin(2 * np.pi * fx['rate'] * t))
            pos = pos[pos < len(a) - 1]
            a = np.interp(pos, np.arange(len(a)), a).astype(np.float32)
        if fx.get('boom'):      # a fuller chest: lift the low end of the voice
            from scipy.signal import butter, sosfilt
            low = sosfilt(butter(2, 220, 'low', fs=SR, output='sos'), a)
            a = (a + low * (10 ** (fx['boom'] / 20) - 1)).astype(np.float32)
        if fx.get('jitter'):    # the uneven pitch of a weathered old voice
            rng = np.random.default_rng(len(a))
            n = len(a) // 240 + 2
            wob = np.interp(np.arange(len(a)), np.arange(n) * 240, rng.standard_normal(n))
            pos = np.cumsum(1 + fx['jitter'] * wob)
            pos = pos[pos < len(a) - 1]
            a = np.interp(pos, np.arange(len(a)), a).astype(np.float32)
        if fx.get('rasp'):      # grit: drive the voice, then add breath noise that follows the words
            from scipy.signal import butter, sosfilt
            a = a / max(1e-6, np.abs(a).max())
            a = np.tanh(a * fx['rasp']) / np.tanh(fx['rasp'])
            env = sosfilt(butter(1, 30, 'low', fs=SR, output='sos'), np.abs(a))
            rng = np.random.default_rng(7)
            hiss = sosfilt(butter(2, [1200, 5000], 'band', fs=SR, output='sos'), rng.standard_normal(len(a)))
            a = (a + fx.get('breath', 0.0) * env * hiss / max(1e-6, np.abs(hiss).max()) * 3).astype(np.float32)
        if fx.get('phone'):     # a voice coming down a phone line: narrow band, a little warmth kept, soft edge
            from scipy.signal import butter, sosfilt
            a = sosfilt(butter(2, [260, 3600], 'band', fs=SR, output='sos'), a).astype(np.float32)
            a = np.tanh(a * fx['phone'] / max(1e-6, np.abs(a).max())) .astype(np.float32)
        if fx.get('soften'):    # take the harsh edge off a young voice
            from scipy.signal import butter, sosfilt
            a = sosfilt(butter(2, 6000, 'low', fs=SR, output='sos'), a).astype(np.float32)
        # trim the dead air the engine leaves at each end, so phrases join the way speech does
        lvl = np.abs(a); thr = max(1e-4, lvl.max() * 0.02)
        idx = np.where(lvl > thr)[0]
        if len(idx):
            pad = int(SR * 0.04)
            a = a[max(0, idx[0] - pad): idx[-1] + pad]
        # even loudness by average level, not peaks, so no phrase jumps out
        rms = np.sqrt(np.mean(a ** 2)) + 1e-6
        target = 0.12 * (10 ** (-1.5 / 20) if fx.get('inner') else 1.0) * 10 ** ((mood[1] + (-4.0 if name == 'Angela' else 0.0)) / 20)   # narration sits a little closer and quieter, a voice in the head
        a = a * (target / rms)
        pk = np.abs(a).max()
        if pk > 0.95: a = a * (0.95 / pk)
        end = ph.rstrip()[-1:] if ph.strip() else '.'
        pause = 0.26 if end in '.!?…' else 0.16 if end in ',;:—' else 0.2
        out += [a.astype(np.float32), np.zeros(int(SR * pause), np.float32)]
    return out


def gap(s):
    return [np.zeros(int(SR * s), np.float32)]


def paragraphs(md, start):
    lines = C.chapters(md, start)
    paras, buf = [], []
    for ln in lines:
        if ln.strip() == '':
            if buf: paras.append(' '.join(buf)); buf = []
        else:
            buf.append(ln.strip())
    if buf: paras.append(' '.join(buf))
    return paras


def file_paragraphs(path):
    paras, buf = [], []
    for ln in open(path).read().split('\n'):
        if ln.strip() == '':
            if buf: paras.append(' '.join(buf)); buf = []
        else:
            buf.append(ln.strip())
    if buf: paras.append(' '.join(buf))
    return paras


MOODS = [   # tone words in the narration around a line -> (pace, loudness in dB)
    (r'\b(mouth twisted|dryly|wryly|sardonic\w*)\b', (0.93, 0.5)),
    (r'\b(whisper\w*|murmur\w*|breathed|under (?:her|his) breath)\b', (0.92, -5.0)),
    (r'\b(quietly|softly|gently|tenderly|barely|very quietly|hoarse\w*|rough)\b', (0.95, -3.0)),
    (r'\b(sighed|tired\w*|slowly|wearily|finally)\b', (0.95, -1.5)),
    (r'\b(shout\w*|yell\w*|snapped|cried out|roared|bellowed)\b', (1.05, 3.0)),
    (r'\b(laugh\w*|grinn\w*|teas\w*|sarcastic\w*|chuckl\w*)\b', (1.03, 1.0)),
    (r'\b(sharply|hard|firmly|flatly|grumbled)\b', (1.02, 1.5)),
    (r'\b(excited\w*|jumping|bright\w*|eager\w*|confidently)\b', (1.04, 1.5)),
]


def mood_of(narr):
    for pat, m in MOODS:
        if re.search(pat, narr, re.I):
            return m
    return (1.0, 0.0)


BOOKS = r"(?:[1-3] ?)?(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song of Solomon|Song of Songs|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation)"


def speak_refs(p):
    """Scripture ranges are said, not dashed: 'Proverbs 7:6-9, 22-23' -> 'Proverbs 7:6 through 9, 22 through 23'. Single verses are left alone."""
    def rep(m):
        return re.sub(r'\s*[-\u2013]\s*', ' through ', m.group(0))
    p = re.sub(r'\b' + BOOKS + r' \d+:\d+(?:[-\u2013]\d+(?::\d+)?)?(?:,\s*\d+(?::\d+)?(?:[-\u2013]\d+(?::\d+)?)?)*', rep, p)
    p = re.sub(r'\b(?:verses|chapters|vv\.|ch\.) \d+\s*[-\u2013]\s*\d+', rep, p)
    p = re.sub(r'\b' + BOOKS + r' \d+[-\u2013]\d+\b(?!:)', rep, p)
    # any other number range (ages, times, counts) is said 'to'
    p = re.sub(r'(?<![\w:-])(\d{1,4}(?::\d{2})?)\s*[-\u2013]\s*(\d{1,4}(?::\d{2})?)(?![\w:]|\s*[-\u2013]\s*\d)', r'\1 to \2', p)
    return p


def render_paragraph(p, who):
    if who == 'SKIP' or p.startswith('&#91;image') or p.startswith('[image'):
        return []   # illustrations and their captions are not read aloud
    if p in ('* * *', '\\* \\* \\*'):
        return gap(1.6)
    if p.startswith('#'):
        return say(p.lstrip('#').strip(), NARRATOR) + gap(1.0)
    p = p.lstrip('> ').strip()
    # Hebrew, Aramaic and Greek letters are for the eye; the narrator reads the English transliteration
    p = re.sub(r'[\u0590-\u05FF\u0370-\u03FF\u1F00-\u1FFF]+[.,]?', '', p)
    p = speak_refs(p)
    p = re.sub(r"Strong's ([HG])(\d+)", lambda m: "Strong's " + m.group(1) + ' ' + m.group(2), p)
    p = re.sub(r'\s+([.,])', r'\1', re.sub(r'  +', ' ', p))
    if who and who.startswith('*'):
        return say(p, who[1:]) + gap(0.45)
    if not who:
        return say(p, NARRATOR) + gap(0.45)
    out = []
    segs = C.segments(p)
    mood = mood_of(' '.join(t for k, t in segs if k == 'n'))   # how the line is said, from the words around it
    for kind, t in segs:
        t = t.strip()
        if kind == 'q':
            out += say(t.strip('"'), who, mood)
        elif re.search(r'[A-Za-z]', t):
            out += say(t, NARRATOR)
    return out + gap(0.45)


def write(pieces, path):
    a = np.concatenate(pieces)
    a = np.clip(a / max(1e-6, np.abs(a).max()) * 0.9, -1, 1)
    import wave
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


SAMPLES = [
    ('Narrator', 'Tears of a Father. The cast.'),
    ('Ezra', "Well, I can see the doomsday club is in session."),
    ('Angela', "When you were sixteen, you didn't have a father who came to anything."),
    ('Kambria', "I will. Every day. As long as it takes."),
    ('Mia', "That's Daddy on the couch. He doesn't see it because he's sleeping."),
    ('Jalen', "It's called The Tears of a Son. I wrote it for my dad."),
    ('Loretta', "He knew every single word in that book, and not a single one reached all the way into his heart."),
    ('Calvin', "Children, obey your parents in the Lord: for this is right. You hear me, kid? This is the Word of God."),
    ('Walt', "They never check their dates. Forty years I set type. Nobody ever checked their dates but me."),
    ('Mr. Hart', "You play it. I'm just the floor under it."),
    ('Pastor Grant', "Well, the Lord's in charge of that, isn't He? We just pray."),
    ('Celeste', "You carry so much, Ezra. Let somebody carry a little of it for you."),
    ('Elijah', "Come on, man, you've been in that house a whole year. One night out."),
    ('Trent', "Job's on schedule. You did good work this week, Ezra."),
    ('Dr. Shaw', "Mister Patterson, the stage is yours."),
]

if __name__ == '__main__':
    if sys.argv[1] == 'sampler':
        pieces = []
        for name, line in SAMPLES:
            if name != 'Narrator':
                pieces += say(name.replace('Mr.', 'Mister').replace('Dr.', 'Doctor') + '.', 'Narrator') + gap(0.3)
            pieces += say(line, name) + gap(1.0)
        write(pieces, sys.argv[2])
    elif sys.argv[1] == 'file':
        _, _, src, mapp, out = sys.argv
        raw = json.load(open(mapp)) if os.path.exists(mapp) else {}
        NARRATOR = raw.pop('_narrator', 'Narrator')
        who = {int(k): v for k, v in raw.items()}
        pieces = []
        for i, p in enumerate(file_paragraphs(src)):
            pieces += render_paragraph(p, who.get(i))
        write(pieces, out)
    else:
        _, _, mdp, start, mapp, out = sys.argv
        md = open(mdp).read()
        who = {int(k): v for k, v in json.load(open(mapp)).items()}
        pieces = []
        for i, p in enumerate(paragraphs(md, start)):
            pieces += render_paragraph(p, who.get(i))
        write(pieces, out)
