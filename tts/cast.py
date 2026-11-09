"""Split chapters into narration and dialogue and guess who is speaking.
Usage: python3 cast.py manuscript.md "Chapter 1:" > listing"""
import re, sys, json

MALE = ['Ezra', 'Jalen', 'Walt', 'Xavier', 'Trent', 'Pastor Grant', 'Grant', 'Calvin', 'Mr. Hart', 'Hart', 'Kyle',
        'Mr. Harold', 'Harold', 'the professor', 'Lionel']
FEMALE = ['Kambria', 'Angela', 'Mia', 'Loretta', 'Grandma', 'Celeste', 'Dr. Shaw', 'Shaw', 'Evelyn', 'Rosa', 'Sarah',
          'Lorraine', 'the anchor', 'Mother Hattie', 'Mrs. Okafor', 'the vice principal']
CANON = {'Grant': 'Pastor Grant', 'Hart': 'Mr. Hart', 'Lionel': 'Mr. Hart', 'Harold': 'Mr. Harold',
         'Grandma': 'Loretta', 'Shaw': 'Dr. Shaw', 'Evelyn': 'Dr. Shaw'}
NAMES = sorted(MALE + FEMALE, key=len, reverse=True)
GENDER = {n: 'm' for n in MALE} | {n: 'f' for n in FEMALE}
VERBS = r'(?:said|asked|whispered|murmured|called|answered|told|repeated|wheezed|grumbled|shouted|cried|replied|began|went on|added|says|breathed|sighed|laughed)'


def chapters(md, start):
    lines = md.split('\n')
    out, on = [], False
    for ln in lines:
        if ln.startswith('## '):
            if on and (ln.startswith('## Chapter') or ln.startswith('## Act') or ln.startswith('## Scripture')):
                break
            if ln.startswith('## ' + start):
                on = True
        if on:
            out.append(ln)
    return out


def segments(par):
    """split a paragraph into ('n'|'q', text) pieces on double quotes"""
    par = par.replace('“', '"').replace('”', '"')
    parts = re.split(r'("[^"]*")', par)
    segs = []
    for p in parts:
        if not p.strip():
            continue
        segs.append(('q' if p.startswith('"') and p.endswith('"') and len(p) > 2 else 'n', p))
    return segs


def guess(par_narr, last, recent):
    m = re.search(r'(' + '|'.join(map(re.escape, NAMES)) + r')\s*,?\s*' + VERBS, par_narr) or \
        re.search(VERBS + r'\s+(' + '|'.join(map(re.escape, NAMES)) + r')', par_narr)
    if m:
        return CANON.get(m.group(1), m.group(1))
    m = re.search(r'\b(he|she)\s+' + VERBS, par_narr, re.I)
    if m:
        g = 'm' if m.group(1).lower() == 'he' else 'f'
        for nm in reversed(recent):
            if GENDER.get(nm) == g:
                return nm
    for nm in NAMES:   # first name mentioned in the narration
        if re.search(r'\b' + re.escape(nm) + r'\b', par_narr):
            return CANON.get(nm, nm)
    return None


def build(md, start):
    lines = chapters(md, start)
    paras, buf = [], []
    for ln in lines:
        if ln.strip() == '':
            if buf:
                paras.append(' '.join(buf)); buf = []
        else:
            buf.append(ln.strip())
    if buf:
        paras.append(' '.join(buf))
    recent, speakers, last_q = [], [], []
    rows = []
    for i, p in enumerate(paras):
        segs = segments(p)
        narr = ' '.join(t for k, t in segs if k == 'n')
        for nm in NAMES:
            if re.search(r'\b' + re.escape(nm) + r'\b', narr):
                c = CANON.get(nm, nm)
                if c in recent:
                    recent.remove(c)
                recent.append(c)
        sp = None
        if any(k == 'q' for k, _ in segs) and not p.startswith('>') and not p.startswith('#'):
            sp = guess(narr, last_q, recent)
            if sp is None and len(last_q) >= 2:
                sp = last_q[-2]       # untagged line: conversation alternates
            if sp:
                last_q.append(sp)
        rows.append({'i': i, 'speaker': sp, 'text': p})
    return rows


if __name__ == '__main__':
    md = open(sys.argv[1]).read()
    rows = build(md, sys.argv[2])
    for r in rows:
        if r['speaker'] or '"' in r['text']:
            q = re.findall(r'"([^"]*)"', r['text'].replace('“', '"').replace('”', '"'))
            print(r['i'], '|', r['speaker'], '|', ' / '.join(x[:50] for x in q)[:110])
