/* Tears of a Father: offline support. Generated at publish by wrap.py; do not edit sw.js by hand.
   - The whole site (text, pictures, Bible, voice clips, app files) is saved on the device only when the reader taps
     "Save the Book for Offline Reading". Until then, nothing but downloaded chapters is stored.
   - Pages are fetched fresh when online, and served from the device when offline.
   - Chapter audio the reader chose to download is served from the device, with seeking. */
const VERSION = '2310e1fc68';
const FILES = [["/app/apple-180.png","ed0158ae89"],["/app/favicon-32.png","da0e00e217"],["/app/icon-192.png","938b998e52"],["/app/icon-512.png","4d1b5febf5"],["/app/icon.svg","992b08a757"],["/app/maskable-512.png","5eec8980ca"],["/audio-manifest.json","3795e52a0a"],["/bible/01.json","bf4bd4a65b"],["/bible/02.json","69768775ef"],["/bible/03.json","8b79ae3ee6"],["/bible/04.json","3b81d468d8"],["/bible/05.json","199628576e"],["/bible/06.json","aace9b37d3"],["/bible/07.json","5f8e95e298"],["/bible/08.json","b3f08ae899"],["/bible/09.json","fb2c868f72"],["/bible/10.json","43261d99cb"],["/bible/11.json","c7114bed6e"],["/bible/12.json","b2093abef4"],["/bible/13.json","71b05b5380"],["/bible/14.json","20f7ec2fb6"],["/bible/15.json","ceb61eeef7"],["/bible/16.json","fec4329f3a"],["/bible/17.json","87bf6f06ae"],["/bible/18.json","796143c2d6"],["/bible/19.json","f47d2cc1b7"],["/bible/20.json","1de2e1301a"],["/bible/21.json","5b0f0bb27a"],["/bible/22.json","70e8425229"],["/bible/23.json","b3ca28d4b0"],["/bible/24.json","4f10adeb92"],["/bible/25.json","31b7c37259"],["/bible/26.json","75432cf339"],["/bible/27.json","a665e37903"],["/bible/28.json","8ee268a88e"],["/bible/29.json","4dce7198c6"],["/bible/30.json","1c3f840f01"],["/bible/31.json","bd0a2331f1"],["/bible/32.json","1f98a3911c"],["/bible/33.json","f4f510beae"],["/bible/34.json","be8b556d71"],["/bible/35.json","e4a08c01a4"],["/bible/36.json","7d0e1976cb"],["/bible/37.json","6412202ea0"],["/bible/38.json","987f329fa3"],["/bible/39.json","ef49966673"],["/bible/40.json","13bc8d5559"],["/bible/41.json","61bc01413b"],["/bible/42.json","182640101a"],["/bible/43.json","ce9e40c8c9"],["/bible/44.json","c431e1f757"],["/bible/45.json","2e89990db0"],["/bible/46.json","905f0b20e4"],["/bible/47.json","d8dba67939"],["/bible/48.json","5d447aef79"],["/bible/49.json","02075e48bc"],["/bible/50.json","d79b991fe5"],["/bible/51.json","e35f78fd69"],["/bible/52.json","6471da4265"],["/bible/53.json","a6c05c8b3b"],["/bible/54.json","52591f13d1"],["/bible/55.json","2b1635362e"],["/bible/56.json","06974baaf2"],["/bible/57.json","66b5f70a6e"],["/bible/58.json","ad1a7c1985"],["/bible/59.json","23a6ce8e28"],["/bible/60.json","0ee779c5c1"],["/bible/61.json","9c69a680b8"],["/bible/62.json","739b1729ef"],["/bible/63.json","3b645a742b"],["/bible/64.json","8c7f1e58f9"],["/bible/65.json","30017b73b5"],["/bible/66.json","9c2e4fc856"],["/bible/index.json","848e09203d"],["/bible/sidx_G.json","94bc9fa250"],["/bible/sidx_H.json","502f783ec9"],["/bible/strongs.json","8c4ec8ecb4"],["/manifest.webmanifest","fac35d763b"],["/media/11101a047c53d837a61bba24b07657a9.mp4","f6729555bd"],["/media/12bef84f7ade245a19ac2353d54c2065.mp4","b325368b2b"],["/media/185d6f91f952d7457a1214f5d2b2baf0.mp4","185d6f91f9"],["/media/196e2165a2f4a9c36ea0d61fb7ec0e48.mp4","a178386673"],["/media/21006684dcb6a0aa45bdea98a0b8b977.mp4","c223020773"],["/media/308fb97a6d6579513b3df4984b3a6861.mp4","3c3f7b6b13"],["/media/389e4a1c2102ce6e252059a6889c1b59.mp4","a02b7dc44d"],["/media/47f24e2e36ea4872b15735f649b6746d.mp4","abb42270fe"],["/media/4d6c332c0410eaa681be71860f9a25a0.jpg","56f62271fb"],["/media/562441e38ba4ed0bff8c0ee9c01aedca.jpg","562441e38b"],["/media/6364a98459e0305f05a0e94e154d5cae.mp4","6364a98459"],["/media/6a51f9275aeb38743470c23c795b1017.jpg","156401b38b"],["/media/6bcc45ecdf941c5b0bb49ff03cfc9dbc.jpg","d6fc6bfccb"],["/media/6d589eb42fd50f2e781193e6947235ff.jpg","748e4bbcfc"],["/media/91deab9ed6d64824503a4ec5c039502a.mp4","4baf8428fb"],["/media/9ed803c7e440e19c9018f1cfac0934c2.mp4","6365dd7bc1"],["/media/Tears-of-a-Father-Jalens-Composition.mp3","3bcae5b0df"],["/media/a12ba34764fc57a21d1ca6a8db73e73f.jpg","e962580ace"],["/media/a456c18d3e8b16560044d08f7df64780.mp4","ca60099802"],["/media/a9318edd68467dec35b5a0f9a60f3ab0.mp4","4579915219"],["/media/b59d21c3d889d58e6ef654a8a670b210.mp4","b59d21c3d8"],["/media/b7bcd16eb0afb51a34cbcb578439ad55.mp3","b7bcd16eb0"],["/media/b96001acb5c46dc74a73961a963a3dc1.jpg","076fb86fdb"],["/media/c83b67500b11a05a9adafb1ba27b2d06.mp4","ce952fd335"],["/media/c9b9ea1e6b7d46cd6ab99c93b6ba80eb.jpg","80869745ef"],["/media/d77c99e85640dd25464fa8e3462f1dab.mp4","d77c99e856"],["/media/ebcd7704366f0324286308ef2288ad32.mp4","d1e78b0d41"],["/media/ee17571d8f45a0081b6bf70e4863f5b5.mp4","5c21c0f486"],["/media/f0e248aca7b29c4838692d8148a34c9b.mp4","06a1021eed"],["/media/f9c1d57459648e69ca1729ac31c1b08d.mp4","328c28dd26"],["/privacy/index.html","40faee0870"]];            // [path, hash] for every site file except chapter audio
const SHELL = 'tof-shell', AUDIO = 'tof-audio', FONTS = 'tof-fonts', STATE = '/__offline_state';

const norm = u => { const x = new URL(u, self.location.origin); return x.origin === self.location.origin ? x.pathname : x.href; };

async function readState(c) { const r = await c.match(STATE); return r ? r.json() : { hashes: {} }; }
async function writeState(c, s) { await c.put(STATE, new Response(JSON.stringify(s), { headers: { 'content-type': 'application/json' } })); }

async function optedIn() { try { return !!(await readState(await caches.open(SHELL))).optin; } catch (e) { return false; } }
let syncing = null;
function syncShell() {
  if (syncing) return syncing;
  syncing = (async () => {
    const c = await caches.open(SHELL), st = await readState(c), want = {};
    if (!st.optin) return;
    FILES.forEach(([p, h]) => { want[p] = h; });
    // drop files the new version no longer has
    for (const p of Object.keys(st.hashes)) if (!(p in want)) { await c.delete(p); delete st.hashes[p]; }
    let done = 0;
    st.version = VERSION; st.total = FILES.length;
    for (const [p, h] of FILES) {
      if (st.hashes[p] === h && await c.match(p)) { done++; continue; }
      try {
        const r = await fetch(p, { cache: 'no-cache' });
        if (r.ok && r.status === 200) { await c.put(p, r); st.hashes[p] = h; done++; }
      } catch (e) { /* offline or flaky: try again next time */ }
      st.done = done; if (done % 10 === 0) { await writeState(c, st); tell({ type: 'offline-state', state: { optin: true, total: st.total, done, complete: false } }); }
    }
    st.done = done; st.complete = done === FILES.length; st.at = Date.now();
    await writeState(c, st);
    await tell({ type: 'offline-state', state: { optin: true, version: VERSION, total: st.total, done, complete: st.complete } });
  })().finally(() => { syncing = null; });
  return syncing;
}

self.addEventListener('install', e => {
  e.waitUntil(self.skipWaiting());
});
self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (![SHELL, AUDIO, FONTS].includes(k)) await caches.delete(k);
    // not saved for offline: keep nothing but downloaded chapters
    if (!(await optedIn())) await caches.delete(SHELL);
    await self.clients.claim();
  })().then(() => syncShell()));
});
async function tell(msg) { (await self.clients.matchAll()).forEach(x => x.postMessage(msg)); }
self.addEventListener('message', e => {
  const job = (async () => {
    if (e.data === 'save') {
      const c = await caches.open(SHELL), st = await readState(c); st.optin = true; await writeState(c, st);
      try { const r = await fetch('/', { cache: 'no-cache' }); if (r.ok) await c.put('/', r); } catch (err) {}
      await syncShell();
    } else if (e.data === 'unsave') {
      await caches.delete(SHELL); await caches.delete(FONTS);
      await tell({ type: 'offline-state', state: { optin: false } });
    } else if (e.data === 'sync') {
      await syncShell();
    }
  })();
  if (e.waitUntil) e.waitUntil(job);
});

// a cached chapter file, answered whole or by byte range (players seek with ranges)
async function serveAudio(req, res) {
  const blob = await res.blob(), size = blob.size, range = req.headers.get('range');
  const base = { 'content-type': 'audio/mpeg', 'accept-ranges': 'bytes' };
  if (!range) return new Response(blob, { status: 200, headers: { ...base, 'content-length': String(size) } });
  const m = /bytes=(\d*)-(\d*)/.exec(range) || [];
  let s, e;
  if (m[1] === '' || m[1] === undefined) { const n = +m[2] || 0; s = Math.max(0, size - n); e = size - 1; }
  else { s = +m[1]; e = m[2] ? Math.min(+m[2], size - 1) : size - 1; }
  if (s >= size) return new Response(null, { status: 416, headers: { 'content-range': 'bytes */' + size } });
  return new Response(blob.slice(s, e + 1), { status: 206, headers: { ...base, 'content-range': 'bytes ' + s + '-' + e + '/' + size, 'content-length': String(e - s + 1) } });
}

async function audioFetch(req, path) {
  const c = await caches.open(AUDIO);
  let hit = await c.match(path);
  if (hit) return serveAudio(req, hit);
  try { return await fetch(req); }
  catch (err) {
    // offline and this exact render isn't saved: play an earlier saved render of the same chapter part
    const stem = path.replace(/^\/audio\//, '').replace(/\.[0-9a-f]{8}\.mp3$/, '').replace(/\.mp3$/, '');
    for (const k of await c.keys()) {
      const p = new URL(k.url).pathname;
      if (p.replace(/^\/audio\//, '').replace(/\.[0-9a-f]{8}\.mp3$/, '') === stem) return serveAudio(req, await c.match(k));
    }
    throw err;
  }
}

async function pageFetch(req) {
  const c = await caches.open(SHELL);
  try {
    const ctl = new AbortController(), t = setTimeout(() => ctl.abort(), 8000);
    const r = await fetch(req, { signal: ctl.signal }); clearTimeout(t);
    if (r.ok && r.status === 200 && !r.redirected) c.put('/', r.clone());
    return r;
  } catch (e) {
    return (await c.match('/')) || Response.error();
  }
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) {
    if (/^fonts\.(googleapis|gstatic)\.com$/.test(url.hostname)) {
      e.respondWith(optedIn().then(on => !on ? fetch(req) : caches.open(FONTS).then(async c => {
        const hit = await c.match(req);
        const net = fetch(req).then(r => { if (r.ok) c.put(req, r.clone()); return r; }).catch(() => hit);
        return hit || net;
      })));
    }
    return;
  }
  const p = url.pathname;
  if (p.startsWith('/api/')) return;
  if (p.startsWith('/audio/') && p.endsWith('.mp3')) { e.respondWith(audioFetch(req, p)); return; }
  e.respondWith(optedIn().then(on => on ? siteFetch(e, req, p) : fetch(req)));
});
function siteFetch(e, req, p) {
  if (req.mode === 'navigate' || p === '/' || p === '/index.html') return pageFetch(req);
  if (p === '/audio-manifest.json') {
    return caches.open(SHELL).then(async c => {
      try { const r = await fetch(req); if (r.ok) c.put(p, r.clone()); return r; }
      catch (err) { return (await c.match(p)) || Response.error(); }
    });
  }
  return caches.open(SHELL).then(async c => {
    const hit = await c.match(p);
    if (hit) return hit;
    try { return await fetch(req); } catch (err) { return Response.error(); }
  });
}
