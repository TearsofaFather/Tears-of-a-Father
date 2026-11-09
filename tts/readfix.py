"""Pronounce the past tense of 'read' as 'red' (the voices say 'reed' for every 'read')."""
import re
PRE_RED = {'had','has','have',"haven't","hadn't","hasn't","i've","you've","we've","they've","he'd","she'd","i'd","we'd","they'd","you'd"}
PRE_REED = {"i'll","you'll","we'll","they'll","he'll","she'll",'than','help','helped','come','go','try','want','wanted','start','began','begin','keep','stop','needed','need','to','could','would','will','can',"can't","couldn't","wouldn't","won't",'should','might','must','let','make','makes','him','her','them','me','us','be','being','shall','cannot'}
SUBJ = {'he','she','they','we','you','i','it'}
DO = {'do','does',"don't","doesn't",'did',"didn't"}
IRREG = {'sat','stood','took','came','went','knelt','leaned','spoke','said','held','kept','began','opened','pulled','found','laid','wrote','turned','looked','sighed','nodded','smiled','paused','stopped','picked','sat','ran','got','was','were','saw','heard','knew','felt','thought','made','told','gave','understood','meant','wanted','sat','lay','fell','rose','broke','drove','began','thought','knew','saw','shook','slept','woke','wept','bent','caught','brought','sent','spent','stole','swept','taught','tore','threw','wore','won','came','kept','left','lost','met','paid','put','read'} - {'read'}
TOKEN = re.compile(r"[A-Za-z']+")

def _words_before(text, i, n=4):
    w = TOKEN.findall(text[max(0, i-80):i])
    return [x.lower() for x in w[-n:]]

def _clause(text, i, j):
    a = max(text.rfind('.', 0, i), text.rfind('!', 0, i), text.rfind('?', 0, i), text.rfind('\n', 0, i)) + 1
    b = [k for k in (text.find('.', j), text.find('!', j), text.find('?', j), text.find('\n', j)) if k >= 0]
    return text[a:(min(b) if b else len(text))]

def _past(clause):
    for w in TOKEN.findall(clause.lower()):
        if w == 'read': continue
        if (w.endswith('ed') and len(w) > 4 and w not in ('need','needed')) or w in IRREG or w in ('was','were','had'): return True
    return False

def decide(text, m):
    d = _decide(text, m)
    if d != '?': return d
    return 'red' if _past(_clause(text, m.start(), m.end())) else 'reed'

def _decide(text, m):
    """'red', 'reed' or '?' for the match m of a bare 'read' in text"""
    i = m.start()
    before = _words_before(text, i)
    prev = before[-1] if before else ''
    pre = text[max(0, i-3):i]
    # start of a sentence or quotation: an order ("Read it again.") -> reed
    if not before or re.search(r'[.!?:"“]\s*[*_]*$', text[max(0, i-6):i]) or text[max(0, i-1):i] in ('\n', ''):
        return 'reed'
    if prev == 'not' or prev == 'never' or prev in ('ever','always','still','just','already','also','then','often','aloud'):
        # look through the adverb to the word before it
        q = before[-2] if len(before) > 1 else ''
        if q in DO or q in PRE_REED: return 'reed'
        if q in PRE_RED: return 'red'
        if prev in ('ever','always','still','just','already','also','often') and q in SUBJ | {'who','nobody'}: return '?'
        if q in SUBJ or q.istitle(): return 'red' if prev in ('never','not') else '?'
        return '?'
    if prev in DO or prev in PRE_REED: return 'reed'
    if prev in PRE_RED: return 'red'
    if prev in ('and','or','then',','):
        return '?'
    # a subject or a name in front: narration is past tense
    if prev in SUBJ or re.search(r"\b[A-Z][a-z]+\s*$", text[max(0, i-20):i]) or prev in ('typesetter','pastor','report','photograph','woman','bottom','nobody','anyone'):
        return '?' if prev in ('i','you','we','they') else 'red'
    return '?'

OVERRIDES = [   # (words around the 'read', pronunciation), settled by reading every case in the manuscript
 ('They read Psalms mostly','red'), ('never once read that part','red'), ('Delivered.* Not read','red'),
 ('he always read them','red'), ('But I read it in three papers','red'), ('Fifty years I read that book','red'),
 ('You read the notebook. You know','red'), ('They read at Ezra','red'), ('You read me James','red'),
 ('You read it better than I could','red'), ('I read it too. I was in those rooms','red'),
 ('every read from all three samples','reed'), ('"I read it," he said','reed'),
 ('make you read Angela','reed'), ('make you read the notebook','reed')]

def fix_read(text):
    text = re.sub(r'\b[Mm]oedim\b', 'Moah-deem', text)
    text = re.sub(r'\bXavier\b', 'Ex-ay-vee-er', text)
    def sub(m):
        d = decide(text, m)
        for ctx, val in OVERRIDES:
            s = max(0, m.start()-40); e = min(len(text), m.end()+40)
            if ctx in text[s:e]: d = val; break
        if d == 'red': return 'Red' if m.group(0)[0] == 'R' else 'red'
        return m.group(0)
    return re.sub(r'\b[Rr]ead\b', sub, text)
