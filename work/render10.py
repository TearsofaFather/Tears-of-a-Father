"""Final rebuild (Nov 4). One chapter, paragraph by paragraph. Cues: Ch4 (gradual fade-in from the prayer, one steady lower level) and Ch23 (Jalen's piece under the recital video)."""
import sys, json, subprocess, numpy as np
import os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tts')); import fullcast as F
D='/tmp/claude-0/-home-claude/648222c4-914f-5409-b146-d2968a0774e6/scratchpad/'
V16=D+'music/v16 orchestral cry ending/Tears of a Father - Reference Master v16.flac'
EQ='equalizer=f=110:t=q:w=0.8:g=2,equalizer=f=450:t=q:w=1.2:g=-3,equalizer=f=9000:t=h:w=1:g=2,loudnorm=I=-18:TP=-1.5:linear=true'
SR=F.SR
name=sys.argv[1]
paras=F.file_paragraphs(name+'.md')
at=lambda s: next(i for i,p in enumerate(paras) if p.startswith(s))
raw=json.load(open(name+'.json')); F.NARRATOR=raw.pop('_narrator','Narrator'); who={int(k):v for k,v in raw.items()}

ACT = {'02-chapter-1': (None, 'Act One: Two Lives.'), '06-chapter-5': ('End of Act One.', 'Act Two: The Fall.'), '10-chapter-9': ('End of Act Two.', 'Act Three: The Signs.'), '14-chapter-13': ('End of Act Three.', 'Act Four: The Watchman.'), '18-chapter-17': ('End of Act Four.', 'Act Five: The World Darkens.'), '21-chapter-20': ('End of Act Five.', 'Act Six: The Rapture.'), '23-chapter-22': ('End of Act Six.', 'Act Seven: The Way of Escape.'), '27-chapter-26': ('End of Act Seven.', 'Act Eight: The Tribulation Watchman.'), '33-chapter-32': ('End of Act Eight.', 'Act Nine: The Patience of the Saints.')}
INTRO = {'01-prologue': 'Ezra Patterson: a carpenter in Washington, D.C., a husband, and the father of two. This is where his story begins, and for now it is told in his voice.', '02-chapter-1': 'Kambria Elizabeth: a forensic scientist at the C.D.C., and the closest friend Angela Patterson ever had. She tells this part: how Ezra and Angela began, and the night everything else did.', '10-chapter-9': 'From here, the story passes to Kambria, and she tells it.'}
pieces=[]; starts=[]; n=0
def _say(t, g):
    global n
    seg = F.say(t, F.NARRATOR) + F.gap(g); pieces.extend(seg); n += sum(len(x) for x in seg)
if name in ACT:
    end, begin = ACT[name]
    if end: _say(end, 3.0)
    _say(begin, 1.6)
if name in INTRO: _say(INTRO[name], 1.4)
for i,p in enumerate(paras):
    starts.append(n); seg=F.render_paragraph(p,who.get(i)); pieces+=seg; n+=sum(len(s) for s in seg)
starts.append(n)
json.dump({'sr':SR,'starts':[round(x/SR,2) for x in starts]},open(name+'.times.tmp','w')); import os; os.replace(name+'.times.tmp',name+'.times.json')
a=np.concatenate(pieces); a=np.clip(a/max(1e-6,np.abs(a).max())*0.9,-1,1).astype(np.float32)
v=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-af',EQ,'-ar',str(SR),'-f','f32le','-'],input=a.tobytes(),capture_output=True).stdout,np.float32)[:len(a)].copy()
song=None
if name in ('05-chapter-4','24-chapter-23'):
    song=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',V16,'-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout,np.float32)
if name=='05-chapter-4':
    # the prayer begins at "He didn't know how to pray"; the long note breaks off as her breath stops (end of "Her breathing slowed...")
    PRAY=at("He didn't know how to pray"); BRK=at('Her breathing slowed'); LEAD=PRAY-4; TAIL=BRK+1
    t0=starts[PRAY]; end=starts[BRK+1]; brk=181.0; src0=brk-(end-t0)/SR
    assert src0>=0, src0
    m=song[int(src0*SR):int(199.0*SR)].copy()
    w=int(1.0*SR); nwin=len(m)//w
    rms=np.array([np.sqrt(np.mean(m[i*w:(i+1)*w]**2))+1e-6 for i in range(nwin)])
    tgt=np.median(rms[:int((end-t0)/SR)]) if nwin else 1
    g=np.clip(tgt/rms,10**(-6/20),10**(6/20)); g=np.convolve(np.pad(g,(2,2),mode='edge'),np.ones(5)/5,mode='valid')
    gi=np.interp(np.arange(len(m))/SR,(np.arange(nwin)+.5),g); m*=gi.astype(np.float32)
    fi=int(28*SR); m[:fi]*=np.linspace(0,1,fi)**1.5; fo=int(4*SR); m[-fo:]*=np.linspace(1,0,fo)
    if t0+len(m)>len(v): v=np.concatenate([v,np.zeros(t0+len(m)-len(v),np.float32)])
    reg=v[starts[LEAD]:starts[TAIL+1]]; vr=np.sqrt(np.mean(reg[np.abs(reg)>0.02]**2)); mr=np.sqrt(np.mean(m**2))+1e-9
    m*=vr/mr*10**((-6-14-3)/20)
    v[t0:t0+len(m)]+=m
    print(name,'cue at',round(t0/SR,1),'s for',round(len(m)/SR,1),'s')
elif name=='24-chapter-23':
    p0=at('The cello began.'); p1=at('They ended together, every one of them'); s0,s1=0.0,317.5
    def seg(a,b): return song[int(a*SR):int(b*SR)].copy()
    A=seg(s0,125.0); C=seg(125.0,s1)
    ta=max(0,starts[p0]-int(1.0*SR)); tc=max(ta+len(A),starts[p1+1]+int(1.0*SR)-len(C))
    parts=[(ta,A)]; t=ta+len(A)
    while tc-t>int(20*SR):
        B=seg(s0,125.0)[:tc-t]; parts.append((t,B)); t+=len(B)
    parts.append((tc,C))
    m=np.zeros(tc+len(C)-ta,np.float32)
    for (pt,pc) in parts:
        pc=pc.copy(); fi=int(2*SR); fo=int(3*SR)
        pc[:fi]*=np.linspace(0,1,fi)**2; pc[-fo:]*=np.linspace(1,0,fo)
        m[pt-ta:pt-ta+len(pc)]+=pc[:len(m)-(pt-ta)]
    t0=ta
    if t0+len(m)>len(v): v=np.concatenate([v,np.zeros(t0+len(m)-len(v),np.float32)])
    speech=np.abs(v)>0.02; vr=np.sqrt(np.mean(v[speech]**2)); mr=np.sqrt(np.mean(m**2))+1e-9
    m*=vr/mr*10**(-6/20)
    env=np.convolve((np.abs(v[t0:t0+len(m)])>0.01).astype(np.float32),np.ones(int(0.25*SR))/int(0.25*SR),mode='same')
    duck=np.clip(np.convolve(env>0.02,np.ones(int(0.7*SR))/int(0.7*SR),mode='same'),0,1)
    v[t0:t0+len(m)]+=m*10**(-10*duck/20)
    print(name,'cue at',round(t0/SR,1),'s for',round(len(m)/SR,1),'s')
v=v/max(1.0,np.abs(v).max()/0.89)
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-b:a','96k',name+'.mp3'],input=v.astype(np.float32).tobytes(),check=True)
print('done',name,round(len(v)/SR/60,1),'min')
