"""Tears of a Father render kit runner.
  python run.py test    render the comparison passage (opening of Ch1) and upload it
  python run.py queue   render the chapters in queue.txt, earliest first, uploading each one as it finishes
"""
import os, sys, subprocess, time, shutil, json
ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, 'work'); OUT = os.path.join(ROOT, 'out')
PY = sys.executable
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
        r = subprocess.run([PY, 'render10.py', n], cwd=WORK, env=ENV, stdout=log, stderr=subprocess.STDOUT)
        log.close()
        if r.returncode or not os.path.exists(os.path.join(WORK, n + '.mp3')):
            print('  !! render failed; uploading the log for Claude'); upload([os.path.join(OUT, n + '.log')], 'PC render FAILED: ' + n); sys.exit(1)
        for ext in ('.mp3', '.times.json'):
            shutil.move(os.path.join(WORK, n + ext), os.path.join(OUT, n + ext))
        open(os.path.join(OUT, n + '.src'), 'w').write(src_hash(n))
        print('  done in %.1f min' % ((time.time() - t) / 60))
        upload([os.path.join(OUT, n + e) for e in ('.mp3', '.times.json', '.log', '.src')], 'PC render: ' + n)

if __name__ == '__main__':
    {'test': test, 'upload-test': lambda: test(True), 'queue': queue}[sys.argv[1] if len(sys.argv) > 1 else 'queue']()
