"""Chapter 23: song under the recital video at one steady level (no ducking, levelled), fading out on the last crescendo. No horn (author, Nov 17). 'His knees went' follows soon after the fade."""
import sys, json, subprocess, numpy as np
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tts')); import fullcast as F
D=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + os.sep
V16=D+'music/v17_mono24k.flac'
EQ='equalizer=f=110:t=q:w=0.8:g=2,equalizer=f=450:t=q:w=1.2:g=-3'
SR=F.SR; name='24-chapter-23'
paras=F.file_paragraphs(name+'.md')
at=lambda s: next(i for i,p in enumerate(paras) if p.startswith(s))
raw=json.load(open(name+'.json')); F.NARRATOR=raw.pop('_narrator','Narrator'); who={int(k):v for k,v in raw.items()}
parts=[F.render_paragraph(p,who.get(i)) for i,p in enumerate(paras)]
p0=at('The cello began.'); pc=at('On the screen, the orchestra had begun'); ps=at('His knees went, and he was on the floor')
plen=[sum(len(s) for s in seg) for seg in parts]
def build(gaps):
    pieces=[]; starts=[]; n=0
    for i,seg in enumerate(parts):
        starts.append(n); pieces+=seg; n+=plen[i]
        g=gaps.get(i,0)
        if g: pieces.append(np.zeros(g,np.float32)); n+=g
    starts.append(n); return pieces,starts
T_END=262.0; FADE=3.5; AFTER=1.2   # Nov 17: song fades out over FADE s from the end of the last crescendo; 'His knees went' AFTER s later
pieces,starts=build({})
L=(starts[pc+1]-starts[p0])/SR+1.0
extra=T_END-L; gaps={}
cand=list(range(p0+2,pc))
print('narration span',round(L,1),'s; extra silence',round(extra,1),'s over',len(cand),'gaps')
if extra>0:
    for j in cand: gaps[j]=int(extra/len(cand)*SR)
pieces,starts=build(gaps)
TA=starts[p0]-int(1.0*SR)
gaps[ps]=int(3.0*SR)   # 3 s of silence after 'His knees went, and he was on the floor.' (was the sob line)
gaps[pc]=int((FADE+AFTER)*SR)
pieces,starts=build(gaps)
TA=starts[p0]-int(1.0*SR)
np.save('ch23_voice_raw.npy',np.concatenate(pieces).astype(np.float32)); a=np.concatenate(pieces); a=np.clip(a/max(1e-6,np.abs(a).max())*0.9,-1,1).astype(np.float32)
v=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-af',EQ,'-ar',str(SR),'-f','f32le','-'],input=a.tobytes(),capture_output=True).stdout,np.float32)[:len(a)].copy()
_act=np.abs(v)>1e-3; v=(v*(0.147/max(1e-6,float(np.sqrt(np.mean(v[_act]**2)))))); v=(v*min(1.0,0.97/max(1e-6,np.abs(v).max()))).astype(np.float32)   # plain gain: ffmpeg's one-pass loudnorm fell back to its dynamic mode and left a crackle (author heard it, Nov 11)
song=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',V16,'-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout,np.float32)
XF=int(2.0*SR)
def xfade(x,y):
    w=np.linspace(0,np.pi/2,XF).astype(np.float32)
    return np.concatenate([x[:-XF], x[-XF:]*np.cos(w)+y[:XF]*np.sin(w), y[XF:]])
END=int((T_END+FADE)*SR)
if extra<0:
    # narration runs long: loop the opening with smooth crossfades, then cross into the rest so the last crescendo ends with the narration
    A=song[:int(125.0*SR)].copy(); C=song[int(125.0*SR):END].copy()
    tc=(starts[pc+1]-gaps.get(pc,0))-int((T_END-125.0)*SR); P=tc-TA
    bed=A.copy()
    while len(bed)<P+XF: bed=xfade(bed,A)
    m=xfade(bed[:P+XF],C)
else:
    m=song[:END].copy()
# level the song so it sits at one steady volume (slow gain, no pumping)
hop=int(0.5*SR); n=len(m)//hop
rms=np.array([np.sqrt(np.mean(m[i*hop:(i+1)*hop]**2))+1e-6 for i in range(n)])
k=np.ones(9)/9; env=np.convolve(rms,k,mode='same')
tgt=np.median(env[4:-4]) if n>8 else np.median(env)
g=np.clip(20*np.log10(tgt/env),-8,9); g=np.convolve(g,np.ones(7)/7,mode='same')
gs=np.interp(np.arange(len(m)),np.arange(n)*hop+hop//2,10**(g/20)).astype(np.float32)
m=(m*gs).astype(np.float32)
fi=int(2*SR); m[:fi]*=np.linspace(0,1,fi)**2
fo=int(FADE*SR); m[-fo:]*=np.cos(np.linspace(0,np.pi/2,fo))**2
t0=TA
if t0+len(m)>len(v): v=np.concatenate([v,np.zeros(t0+len(m)-len(v),np.float32)])
speech=np.abs(v)>0.02; vr=np.sqrt(np.mean(v[speech]**2)) if speech.any() else 0.1; mr=np.sqrt(np.mean(m[fi:-fo]**2))+1e-9
m*=vr/mr*10**(-7/20)   # one steady level under the narration, no ducking
v[t0:t0+len(m)]+=m
print('song at',round(t0/SR,1),'s for',round(len(m)/SR,1),'s; crescendo narration ends song-time',round(((starts[pc+1]-gaps.get(pc,0))-TA)/SR,1),'; knees line at song-time',round((starts[ps]-TA)/SR,1),'; peak before norm',round(float(np.abs(v).max()),2))
v=v/max(1.0,np.abs(v).max()/0.89)
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-b:a','192k','24-chapter-23-v17.mp3'],input=v.astype(np.float32).tobytes(),check=True)
print('done',round(len(v)/SR/60,1),'min')
json.dump({'starts':[round(s/SR,2) for s in starts],'total':round(len(v)/SR,2)},open('24-chapter-23.times.json','w'))
print('times written')
