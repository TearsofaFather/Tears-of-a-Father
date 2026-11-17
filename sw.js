/* Tears of a Father: offline support. Generated at publish by wrap.py; do not edit sw.js by hand.
   - The whole site (text, pictures, Bible, voice clips, app files) is saved on the device only when the reader taps
     "Save the Book for Offline Reading". Until then, nothing but downloaded chapters is stored.
   - Pages are fetched fresh when online, and served from the device when offline.
   - Chapter audio the reader chose to download is served from the device, with seeking. */
const VERSION = 'd1ff128351';
const FILES = [["/app/apple-180.png","ed0158ae89"],["/app/favicon-32.png","da0e00e217"],["/app/icon-192.png","938b998e52"],["/app/icon-512.png","4d1b5febf5"],["/app/icon.svg","992b08a757"],["/app/maskable-512.png","5eec8980ca"],["/audio-manifest.json","6abe16af65"],["/bible/01.json","bf4bd4a65b"],["/bible/02.json","69768775ef"],["/bible/03.json","8b79ae3ee6"],["/bible/04.json","3b81d468d8"],["/bible/05.json","199628576e"],["/bible/06.json","aace9b37d3"],["/bible/07.json","5f8e95e298"],["/bible/08.json","b3f08ae899"],["/bible/09.json","fb2c868f72"],["/bible/10.json","43261d99cb"],["/bible/11.json","c7114bed6e"],["/bible/12.json","b2093abef4"],["/bible/13.json","71b05b5380"],["/bible/14.json","20f7ec2fb6"],["/bible/15.json","ceb61eeef7"],["/bible/16.json","fec4329f3a"],["/bible/17.json","87bf6f06ae"],["/bible/18.json","796143c2d6"],["/bible/19.json","f47d2cc1b7"],["/bible/20.json","1de2e1301a"],["/bible/21.json","5b0f0bb27a"],["/bible/22.json","70e8425229"],["/bible/23.json","b3ca28d4b0"],["/bible/24.json","4f10adeb92"],["/bible/25.json","31b7c37259"],["/bible/26.json","75432cf339"],["/bible/27.json","a665e37903"],["/bible/28.json","8ee268a88e"],["/bible/29.json","4dce7198c6"],["/bible/30.json","1c3f840f01"],["/bible/31.json","bd0a2331f1"],["/bible/32.json","1f98a3911c"],["/bible/33.json","f4f510beae"],["/bible/34.json","be8b556d71"],["/bible/35.json","e4a08c01a4"],["/bible/36.json","7d0e1976cb"],["/bible/37.json","6412202ea0"],["/bible/38.json","987f329fa3"],["/bible/39.json","ef49966673"],["/bible/40.json","13bc8d5559"],["/bible/41.json","61bc01413b"],["/bible/42.json","182640101a"],["/bible/43.json","ce9e40c8c9"],["/bible/44.json","c431e1f757"],["/bible/45.json","2e89990db0"],["/bible/46.json","905f0b20e4"],["/bible/47.json","d8dba67939"],["/bible/48.json","5d447aef79"],["/bible/49.json","02075e48bc"],["/bible/50.json","d79b991fe5"],["/bible/51.json","e35f78fd69"],["/bible/52.json","6471da4265"],["/bible/53.json","a6c05c8b3b"],["/bible/54.json","52591f13d1"],["/bible/55.json","2b1635362e"],["/bible/56.json","06974baaf2"],["/bible/57.json","66b5f70a6e"],["/bible/58.json","ad1a7c1985"],["/bible/59.json","23a6ce8e28"],["/bible/60.json","0ee779c5c1"],["/bible/61.json","9c69a680b8"],["/bible/62.json","739b1729ef"],["/bible/63.json","3b645a742b"],["/bible/64.json","8c7f1e58f9"],["/bible/65.json","30017b73b5"],["/bible/66.json","9c2e4fc856"],["/bible/index.json","848e09203d"],["/bible/sidx_G.json","94bc9fa250"],["/bible/sidx_H.json","502f783ec9"],["/bible/strongs.json","8c4ec8ecb4"],["/manifest.webmanifest","fac35d763b"],["/media/143b022fc6f4439d778f65657a1dd31b.mp3","143b022fc6"],["/media/14659f5405861a829a05812e4a2565b3.mp3","14659f5405"],["/media/16df4a64779304fa8bd20a564210213f.mp3","16df4a6477"],["/media/37483cc05d3e2c7203701337f2b838fc.mp3","37483cc05d"],["/media/399a89dd07a5f24b0c2eb827e39a2af3.mp3","399a89dd07"],["/media/4d6c332c0410eaa681be71860f9a25a0.jpg","56f62271fb"],["/media/544580d56c76a2a38b0bcc4d557b807c.mp3","544580d56c"],["/media/562441e38ba4ed0bff8c0ee9c01aedca.jpg","562441e38b"],["/media/69b4b2fc607c7c0e2f1831d654f574af.mp3","69b4b2fc60"],["/media/6a51f9275aeb38743470c23c795b1017.jpg","156401b38b"],["/media/6bcc45ecdf941c5b0bb49ff03cfc9dbc.jpg","d6fc6bfccb"],["/media/6c0066eb48a394304a4526676e9ab31f.mp3","6c0066eb48"],["/media/6d589eb42fd50f2e781193e6947235ff.jpg","748e4bbcfc"],["/media/9ae2f3d951e94ae0a49e253461492d12.mp3","9ae2f3d951"],["/media/Tears-of-a-Father-Jalens-Composition.mp3","3bcae5b0df"],["/media/a12ba34764fc57a21d1ca6a8db73e73f.jpg","e962580ace"],["/media/ae7d96493becfb25284f61b03073a7bc.mp3","ae7d96493b"],["/media/b2118a49b46ad8a9fbc7ca86a0bfce05.mp3","b2118a49b4"],["/media/b7bcd16eb0afb51a34cbcb578439ad55.mp3","b7bcd16eb0"],["/media/b96001acb5c46dc74a73961a963a3dc1.jpg","076fb86fdb"],["/media/bd4f99ac057151b9d5a80b380f102c1a.mp3","bd4f99ac05"],["/media/c07a11de90d65eb54cc9a6123a9ad09d.mp3","c07a11de90"],["/media/c7616f4b9b0140a26248fded90e72a00.mp3","c7616f4b9b"],["/media/c84f1e0b0d51b389a25c76bc63d27325.mp3","c84f1e0b0d"],["/media/c9b9ea1e6b7d46cd6ab99c93b6ba80eb.jpg","80869745ef"],["/media/cb1342312b38512e112ef65ef67ef9df.mp3","cb1342312b"],["/media/d77c99e85640dd25464fa8e3462f1dab.mp4","d77c99e856"],["/media/e84075ff50634dd87c717e889adcc65f.mp3","e84075ff50"],["/media/ebcd7704366f0324286308ef2288ad32.mp4","d1e78b0d41"],["/media/f268d1d624d0ed75f7ec5f57a42bb59f.mp3","f268d1d624"],["/media/kingdom-of-little-things-preview.jpg","d58e3d4d6c"],["/media/posters/poster-1-sm.jpg","bb30529b98"],["/media/posters/poster-1.jpg","20a9400343"],["/media/posters/poster-2-sm.jpg","9c4ed4f511"],["/media/posters/poster-2.jpg","7a4f553319"],["/media/posters/poster-3-sm.jpg","e46484fbec"],["/media/posters/poster-3.jpg","a422a68865"],["/privacy/index.html","40faee0870"]];            // [path, hash] for every site file except chapter audio
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

const stemOf = p => p.replace(/^\/audio\//, '').replace(/\.[0-9a-f]{8}\.mp3$/, '').replace(/\.mp3$/, '');
let SAVED = null;   // which chapter parts are saved on this device (by name, any render)
function loadSaved() {
  return caches.open(AUDIO).then(c => c.keys()).then(ks => { SAVED = new Set(ks.map(k => stemOf(new URL(k.url).pathname))); }).catch(() => {});
}
loadSaved();

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
  if (p.startsWith('/audio/') && p.endsWith('.mp3')) {
    // only chapters saved on this device go through here; everything else streams straight from the site,
    // since a phone can cut off a long stream that a service worker is passing along (Nov 16)
    const known = SAVED; loadSaved();
    if (known && !known.has(stemOf(p)) && self.navigator.onLine !== false) return;
    e.respondWith(audioFetch(req, p)); return;
  }
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
