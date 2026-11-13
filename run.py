"""Tears of a Father render kit runner.
  python run.py test    render the comparison passage (opening of Ch1) and upload it
  python run.py queue   render the chapters in queue.txt, earliest first, uploading each one as it finishes
"""
import os, sys, subprocess, time, shutil, json
ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, 'work'); OUT = os.path.join(ROOT, 'out')
PY = sys.executable
# run with the kit's own Python (the venv setup.ps1 made), whichever python started this script
_VPY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'Scripts', 'python.exe')
if os.path.exists(_VPY) and os.path.normcase(os.path.abspath(PY)) != os.path.normcase(_VPY):
    sys.exit(subprocess.run([_VPY, os.path.abspath(__file__)] + sys.argv[1:]).returncode)
ENV = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
os.makedirs(OUT, exist_ok=True)

def _find_git():
    g = shutil.which('git')
    if g: return g
    for c in (r'C:\Program Files\Git\cmd\git.exe', r'C:\Program Files\Git\bin\git.exe',
              os.path.join(os.environ.get('LOCALAPPDATA', ''), r'Programs\Git\cmd\git.exe')):
        if os.path.exists(c): return c
    sys.exit('Git was not found. Close this window, open a new PowerShell window, and run the command again.')
GIT = None

def git(*a, check=True):
    global GIT
    GIT = GIT or _find_git()
    return subprocess.run([GIT, '-C', ROOT, *a], check=check, capture_output=True, text=True)

def sync_remote():
    """Match the branch on GitHub exactly (finished renders are already uploaded)."""
    git('rebase', '--abort', check=False)
    git('fetch', 'origin', 'render-kit', check=False)
    git('reset', '--hard', 'FETCH_HEAD', check=False)

def upload(paths, msg):
    for attempt in range(5):
        for p in paths: git('add', '-f', p)
        git('commit', '-m', msg, check=False)
        r = git('push', 'origin', 'HEAD:render-kit', check=False)
        if r.returncode == 0:
            print('  uploaded'); return
        # someone else pushed first: keep our files, take everything else from GitHub, try again
        keep = {}
        for p in paths:
            if os.path.exists(p): keep[p] = open(p, 'rb').read()
        sync_remote()
        for p, b in keep.items(): open(p, 'wb').write(b)
        time.sleep(3)
    print('  !! upload failed:', r.stderr.strip()); sys.exit(1)

def src_hash(n):
    import hashlib
    h = hashlib.sha1()
    for ext in ('.md', '.json'):
        h.update(open(os.path.join(WORK, n + ext), 'rb').read())
    return h.hexdigest()

def is_done(n):
    mp3 = os.path.join(OUT, n + '.mp3'); src = os.path.join(OUT, n + '.src')
    return os.path.exists(mp3) and os.path.exists(src) and open(src).read().strip() == src_hash(n)

def provider():
    r = subprocess.run([PY, '-c', 'import sys; sys.path.insert(0,"tts"); import narrate; print(narrate.PROVIDER)'], cwd=ROOT, env=ENV, capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip()[-300:])

def test(upload_only=False):
    out = os.path.join(OUT, 'test-pc.wav')
    if upload_only and os.path.exists(out):
        upload([out, os.path.join(OUT, 'test-pc.txt')], 'PC render: comparison passage'); print('Done. Tell Claude the test is uploaded.'); return
    print('Voice engine running on:', provider())
    t = time.time()
    r = subprocess.run([PY, 'test_passage.py', out], cwd=WORK, env=ENV)
    if r.returncode: sys.exit('The test render failed. Copy the red error text to Claude.')
    secs = round(time.time() - t)
    open(os.path.join(OUT, 'test-pc.txt'), 'w').write('provider %s\nseconds %d\n' % (provider(), secs))
    print('Rendered the test passage in', secs, 'seconds.')
    upload([out, os.path.join(OUT, 'test-pc.txt')], 'PC render: comparison passage')
    print('Done. Tell Claude the test is uploaded.')

# the four chapters with music use their own scripts (author, Nov 11)
SPECIAL = {
    '09-chapter-8': ('ch8_v9.py', [('09-chapter-8-new.wav', '09-chapter-8.mp3'), ('09-chapter-8-new.times.json', '09-chapter-8.times.json')]),
    '24-chapter-23': ('render23_v17.py', [('24-chapter-23-v17.mp3', '24-chapter-23.mp3'), ('24-chapter-23.times.json', '24-chapter-23.times.json')]),
    '37-chapter-36': ('render_ch36_C.py', [('37-chapter-36-C.mp3', '37-chapter-36.mp3')]),
}

def fit_github(mp3, limit=95 * 1024 * 1024):
    """GitHub refuses files over 100 MB: re-encode a long chapter at a lower bitrate so it fits."""
    if not os.path.exists(mp3) or os.path.getsize(mp3) <= limit: return
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp3], capture_output=True, text=True)
    try:
        secs = float(r.stdout.strip())
        kbps = max(48, min(128, int(limit * 8 / secs / 1000) - 4))
    except ValueError:
        kbps = 80
    tmp = mp3 + '.fit.mp3'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-b:a', '%dk' % kbps, tmp], check=True)
    os.replace(tmp, mp3)
    print('  re-encoded at %dk to fit GitHub (%.1f MB)' % (kbps, os.path.getsize(mp3) / 1048576))

def queue():
    print('Voice engine running on:', provider())
    while True:
        sync_remote()
        names = open(os.path.join(ROOT, 'queue.txt')).read().split()
        todo = [n for n in names if not is_done(n)]
        if not todo:
            print('All chapters in the queue are rendered and uploaded.'); return
        n = todo[0]; t = time.time()
        print('Rendering', n, '...', flush=True)
        log = open(os.path.join(OUT, n + '.log'), 'w', encoding='utf-8')
        script, made = SPECIAL.get(n, ('render10.py', [(n + '.mp3', n + '.mp3'), (n + '.times.json', n + '.times.json')]))
        args = [PY, script] + ([n] if script == 'render10.py' else [])
        r = subprocess.run(args, cwd=WORK, env=ENV, stdout=log, stderr=subprocess.STDOUT)
        log.close()
        ok = r.returncode == 0 and all(os.path.exists(os.path.join(WORK, a)) for a, b in made)
        if not ok:
            print('  !! render failed; uploading the log for Claude'); upload([os.path.join(OUT, n + '.log')], 'PC render FAILED: ' + n); sys.exit(1)
        for a, b in made:
            if a.endswith('.wav'):   # the chapter 8 script writes a wav; send an mp3 like the others
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(WORK, a), '-b:a', '96k', os.path.join(OUT, b)], check=True)
                os.remove(os.path.join(WORK, a))
            else:
                shutil.move(os.path.join(WORK, a), os.path.join(OUT, b))
        fit_github(os.path.join(OUT, n + '.mp3'))
        open(os.path.join(OUT, n + '.src'), 'w').write(src_hash(n))
        print('  done in %.1f min' % ((time.time() - t) / 60))
        upload([os.path.join(OUT, n + e) for e in ('.mp3', '.times.json', '.log', '.src') if os.path.exists(os.path.join(OUT, n + e))], 'PC render: ' + n)

if __name__ == '__main__':
    {'test': test, 'upload-test': lambda: test(True), 'queue': queue}[sys.argv[1] if len(sys.argv) > 1 else 'queue']()
