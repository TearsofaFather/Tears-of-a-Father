"""Chapter 23 re-render (Nov 4, new text): song under the recital video, narration spaced so the last crescendo ends at song 290s, horn silent, then the one-liner."""
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
T_END=262.0; T_SOB=312.4   # v17: the last crescendo now ends where the held note begins; the sob line follows the horn
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
gaps[pc]=int((T_SOB-T_END)*SR) if extra<0 else int(max(1.0,T_SOB-(starts[pc+1]-TA)/SR)*SR)
pieces,starts=build(gaps)
TA=starts[p0]-int(1.0*SR)
np.save('ch23_voice_raw.npy',np.concatenate(pieces).astype(np.float32)); a=np.concatenate(pieces); a=np.clip(a/max(1e-6,np.abs(a).max())*0.9,-1,1).astype(np.float32)
v=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-af',EQ,'-ar',str(SR),'-f','f32le','-'],input=a.tobytes(),capture_output=True).stdout,np.float32)[:len(a)].copy()
_act=np.abs(v)>1e-3; v=(v*(0.147/max(1e-6,float(np.sqrt(np.mean(v[_act]**2)))))); v=(v*min(1.0,0.97/max(1e-6,np.abs(v).max()))).astype(np.float32)   # plain gain: ffmpeg's one-pass loudnorm fell back to its dynamic mode and left a crackle (author heard it, Nov 11)
song=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',V16,'-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout,np.float32)
m=song[:int(309.3*SR)].copy()
if extra<0:
    # narration runs long: stretch the middle by looping the opening, keep the ending aligned to the last crescendo
    A=song[:int(125.0*SR)].copy(); C=song[int(125.0*SR):int(309.3*SR)].copy()
    tc=(starts[pc+1]-gaps.get(pc,0))-int((T_END-125.0)*SR); parts2=[(TA,A)]; t=TA+len(A)
    while tc-t>int(20*SR):
        B=A[:tc-t].copy(); parts2.append((t,B)); t+=len(B)
    parts2.append((tc,C)); m=np.zeros(tc+len(C)-TA,np.float32)
    for pt,pc_ in parts2:
        pc_=pc_.copy(); fi=int(2*SR); fo=int(3*SR); pc_[:fi]*=np.linspace(0,1,fi)**2; pc_[-fo:]*=np.linspace(1,0,fo)
        m[pt-TA:pt-TA+len(pc_)]+=pc_[:len(m)-(pt-TA)]
else:
    fi=int(2*SR); m[:fi]*=np.linspace(0,1,fi)**2
t0=TA
if t0+len(m)>len(v): v=np.concatenate([v,np.zeros(t0+len(m)-len(v),np.float32)])
speech=np.abs(v)>0.02; vr=np.sqrt(np.mean(v[speech]**2)); mr=np.sqrt(np.mean(m**2))+1e-9
m*=vr/mr*10**(-4/20)
env=np.convolve((np.abs(v[t0:t0+len(m)])>0.01).astype(np.float32),np.ones(int(0.25*SR))/int(0.25*SR),mode='same')
duck=np.clip(np.convolve(env>0.02,np.ones(int(0.7*SR))/int(0.7*SR),mode='same'),0,1)
v[t0:t0+len(m)]+=m*10**(-5*duck/20)
print('song at',round(t0/SR,1),'s for',round(len(m)/SR,1),'s; crescendo narration ends song-time',round(((starts[pc+1]-gaps.get(pc,0))-TA)/SR,1),'; sob line at song-time',round((starts[ps]-TA)/SR,1),'; peak before norm',round(float(np.abs(v).max()),2))
v=v/max(1.0,np.abs(v).max()/0.89)
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-b:a','192k','24-chapter-23-v17.mp3'],input=v.astype(np.float32).tobytes(),check=True)
print('done',round(len(v)/SR/60,1),'min')
json.dump({'starts':[round(s/SR,2) for s in starts],'total':round(len(v)/SR,2)},open('24-chapter-23.times.json','w'))
print('times written')
