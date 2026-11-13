"""Adds the private Playscript tab to a COPY of the site page. The repo's index.html is never touched.
Usage: python3 inject.py <site index.html> <output index.html>
Reads every out/*.play.json and out/*.cues.csv beside this script."""
import sys, os, json, glob, re
HERE = os.path.dirname(os.path.abspath(__file__))
src, dst = sys.argv[1], sys.argv[2]
page = open(src, encoding='utf-8').read()

data = {}
for f in sorted(glob.glob(os.path.join(HERE, 'out', '*.play.json'))):
    d = json.load(open(f, encoding='utf-8'))
    d['csv'] = open(f.replace('.play.json', '.cues.csv'), encoding='utf-8').read()
    data[d['stem']] = d
blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')

CSS = r"""
<style id="play-css">
/* Playscript (private): a stage script that doubles as the audio cue sheet. Timecodes sit in a narrow mono gutter. */
@media (min-width: 900px) { nav.tabs a { padding-left: 8px; padding-right: 8px; } }   /* room for the extra tab in this copy */
#t-play { max-width: 860px; margin: 0 auto; padding-block: 18px 60px; }
.pl-eyebrow { font: 600 .72rem/1.3 var(--ui); letter-spacing: .12em; text-transform: uppercase; color: var(--gold); }
#t-play h2 { font-family: var(--display); font-size: clamp(1.9rem, 4vw, 2.6rem); font-weight: 700; margin: 4px 0 6px; text-wrap: balance; }
.pl-lede { color: var(--muted); max-width: 62ch; margin: 0 0 18px; font-size: .95rem; }
.pl-bar { position: sticky; top: var(--pl-top, 0px); z-index: 5; display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: center;
  background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; margin-bottom: 18px; }
.pl-bar select { font: 500 .9rem var(--ui); padding: 6px 8px; border-radius: 7px; border: 1px solid var(--line); background: var(--bg); color: var(--fg); max-width: 100%; }
.pl-bar label { display: inline-flex; gap: 6px; align-items: center; font-size: .86rem; color: var(--fg); cursor: pointer; }
.pl-bar button { font: 600 .82rem var(--ui); padding: 7px 11px; border-radius: 7px; border: 1px solid var(--line); background: var(--bg); color: var(--fg); cursor: pointer; }
.pl-bar button:hover { border-color: var(--accent); }
.pl-stat { margin-left: auto; font: .8rem var(--ui); color: var(--muted); font-variant-numeric: tabular-nums; }
.pl-card { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; margin-bottom: 14px; }
.pl-card h3 { font: 600 .74rem var(--ui); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin: 0 0 8px; }
.pl-card p { margin: 0; font-family: var(--body); font-size: 1rem; line-height: 1.6; }
.pl-cast { display: grid; grid-template-columns: minmax(0, 13em) minmax(0, 1fr); gap: 4px 14px; margin: 0; font-size: .92rem; }
.pl-cast dt { font: 600 .82rem var(--ui); letter-spacing: .04em; }
.pl-cast dd { margin: 0; color: var(--muted); font-family: var(--body); }
details.pl-card summary { cursor: pointer; font: 600 .74rem var(--ui); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }
details.pl-card[open] summary { margin-bottom: 10px; }
.pl-scene { margin: 34px 0 10px; border-top: 2px solid var(--fg); padding-top: 12px; }
.pl-scene h4 { font-family: var(--display); font-size: 1.5rem; font-weight: 700; margin: 0; display: flex; flex-wrap: wrap; gap: 4px 12px; align-items: baseline; }
.pl-scene h4 small { font: 500 .78rem var(--ui); color: var(--muted); font-variant-numeric: tabular-nums; letter-spacing: .02em; }
.pl-setting { font-family: var(--body); font-style: italic; color: var(--muted); margin: 4px 0 14px; }
.pl-row { display: grid; grid-template-columns: 5.2em minmax(0, 1fr); gap: 0 14px; padding: 5px 0; align-items: start; }
.pl-tc { font: 500 .74rem/1.2 ui-monospace, "SF Mono", Menlo, Consolas, monospace; color: var(--muted); font-variant-numeric: tabular-nums; text-align: right;
  background: none; border: 0; padding: .45em 0 0; cursor: pointer; white-space: nowrap; }
.pl-row.narr .pl-tc, .pl-row.line .pl-tc { padding-top: .2em; }
.pl-tc:hover, .pl-row.now .pl-tc { color: var(--accent); }
.pl-tc[disabled] { cursor: default; color: var(--muted); }
.pl-body { min-width: 0; font-family: var(--body); font-size: var(--fs, 1.05rem); line-height: 1.6; }
.pl-who { display: block; font: 700 .78rem var(--ui); letter-spacing: .09em; text-transform: uppercase; }
.pl-who i { font-weight: 500; text-transform: none; letter-spacing: 0; color: var(--muted); }
.pl-row.dir .pl-body { font-style: italic; color: var(--muted); padding-left: 1.2em; border-left: 2px solid var(--line); }
.pl-row.narr .pl-body { color: var(--muted); }
.pl-row.narr .pl-who { color: var(--gold); }
.pl-row.now { background: var(--soft); border-radius: 6px; }
.pl-id { font: .68rem ui-monospace, Menlo, Consolas, monospace; color: var(--muted); margin-left: 6px; }
#t-play.no-narr .pl-row.narr { display: none; }
#t-play.no-tc .pl-tc, #t-play.no-tc .pl-id { visibility: hidden; }
#t-play.no-tc .pl-row { grid-template-columns: 0 minmax(0, 1fr); gap: 0; }
.pl-note { font-size: .82rem; color: var(--muted); margin-top: 6px; }
@media (max-width: 560px) {
  .pl-row { grid-template-columns: 4.3em minmax(0, 1fr); gap: 0 10px; }
  .pl-cast { grid-template-columns: minmax(0, 1fr); }
  .pl-cast dd { margin-bottom: 6px; }
  .pl-bar { position: static; }
  .pl-stat { margin-left: 0; width: 100%; }
}
</style>
"""

SECTION = r"""
<!-- PLAYSCRIPT (private copy only; never pushed to the public site) -->
<section class="tab" id="t-play" aria-labelledby="pl-h">
  <div class="pl-eyebrow">Private working copy &middot; not on tearsofafather.com</div>
  <h2 id="pl-h">Playscript</h2>
  <p class="pl-lede">The book as a stage play, scene by scene, with every spoken line pinned to its place in the audiobook. Each line carries a cue number and its start and end time, so a studio can re-record any line and drop it back into the same spot.</p>
  <div class="pl-bar">
    <select id="pl-sel" aria-label="Chapter"></select>
    <label><input type="checkbox" id="pl-narr" checked> Narration</label>
    <label><input type="checkbox" id="pl-tcs" checked> Timecodes</label>
    <button type="button" id="pl-copy">Copy cue sheet</button>
    <span class="pl-stat" id="pl-stat"></span>
  </div>
  <div id="pl-doc"></div>
  <audio id="pl-audio" preload="none"></audio>
</section>
"""

JS = r"""
<script type="application/json" id="play-data">__DATA__</script>
<script>
(function () {
  const P = JSON.parse(document.getElementById('play-data').textContent);
  const $ = s => document.querySelector(s);
  const root = $('#t-play'), sel = $('#pl-sel'), doc = $('#pl-doc'), au = $('#pl-audio');
  const e = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const md = s => e(s).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\*(.+?)\*/g, '<em>$1</em>');
  const mmss = t => { const m = Math.floor(t / 60), s = t - m * 60; return m + ':' + (s < 10 ? '0' : '') + s.toFixed(1); };
  const dur = t => { const m = Math.floor(t / 60), s = Math.round(t - m * 60); return m + ' min ' + s + ' s'; };
  let cur = null, rows = [];
  const mast = document.querySelector('header.mast');
  const setTop = () => { if (mast) root.style.setProperty('--pl-top', (mast.getBoundingClientRect().height + 8) + 'px'); };
  setTop(); addEventListener('resize', setTop);
  Object.keys(P).forEach(k => { const o = document.createElement('option'); o.value = k; o.textContent = P[k].title; sel.appendChild(o); });

  function render(stem) {
    const d = P[stem]; cur = d; let h = '';
    h += '<div class="pl-card"><h3>' + e(d.act) + ' &middot; ' + e(d.title) + '</h3><p>' + md(d.staging) + '</p></div>';
    h += '<details class="pl-card"><summary>Cast in this chapter</summary><dl class="pl-cast">' + d.cast.map(c => '<dt>' + e(c[0]) + '</dt><dd>' + e(c[1]) + '</dd>').join('') + '</dl></details>';
    d.scenes.forEach(sc => {
      h += '<div class="pl-scene"><h4>' + (sc.n ? 'Scene ' + sc.n + ' &middot; ' : '') + e(sc.title) + ' <small>' + mmss(sc.tc0) + ' &ndash; ' + mmss(sc.tc1) + ' &middot; ' + dur(sc.tc1 - sc.tc0) + '</small></h4>';
      h += '<p class="pl-setting">' + md(sc.setting) + '</p>';
      sc.items.forEach(it => {
        if (it.k === 'dir') {
          h += '<div class="pl-row dir" data-t="' + it.tc + '"><button type="button" class="pl-tc" data-t="' + it.tc + '" title="Play from here">' + mmss(it.tc) + '</button><div class="pl-body">' + md(it.text) + '</div></div>';
        } else {
          h += '<div class="pl-row ' + (it.narr ? 'narr' : 'line') + '" data-t="' + it.tc0 + '" data-e="' + it.tc1 + '"><button type="button" class="pl-tc" data-t="' + it.tc0 + '" title="Play this line (' + mmss(it.tc0) + ' to ' + mmss(it.tc1) + ')">' + mmss(it.tc0) + '</button>' +
               '<div class="pl-body"><span class="pl-who">' + e(it.who) + (it.narr ? ' <i>narrating</i>' : '') + '<span class="pl-id">' + e(it.id) + '</span></span>' + md(it.text) + '</div></div>';
        }
      });
      h += '</div>';
    });
    h += '<p class="pl-note">Timecodes are minutes:seconds from the start of this chapter\'s audio. The cue sheet gives the same times to the millisecond.</p>';
    doc.innerHTML = h; rows = Array.from(doc.querySelectorAll('.pl-row'));
    $('#pl-stat').textContent = d.scenes.length - 1 + ' scenes · ' + d.lines + ' lines · ' + d.speakers.length + ' speaking parts · ' + dur(d.runtime);
    au.pause(); au.removeAttribute('src'); au.dataset.src = '';
  }

  // audio: a proofing copy of each chapter, made from the same render as the timing, so they always agree
  function playAt(t) {
    const src = 'play-audio/' + cur.stem + '.mp4';
    const go = () => { au.currentTime = t; au.play().catch(() => { $('#pl-stat').textContent = 'No audio for this chapter in this copy yet.'; }); };
    if (au.dataset.src !== src) { au.src = src; au.dataset.src = src; au.addEventListener('loadedmetadata', function f() { au.removeEventListener('loadedmetadata', f); go(); }); au.load(); }
    else go();
  }
  au.addEventListener('timeupdate', () => {
    const t = au.currentTime;
    rows.forEach(r => r.classList.toggle('now', !r.classList.contains('dir') && +r.dataset.t <= t && t < +r.dataset.e));
  });
  doc.addEventListener('click', ev => { const b = ev.target.closest('.pl-tc'); if (b) playAt(+b.dataset.t); });

  sel.addEventListener('change', () => { render(sel.value); try { localStorage.setItem('tof-play', sel.value); } catch (x) {} });
  $('#pl-narr').addEventListener('change', ev => root.classList.toggle('no-narr', !ev.target.checked));
  $('#pl-tcs').addEventListener('change', ev => root.classList.toggle('no-tc', !ev.target.checked));
  $('#pl-copy').addEventListener('click', () => {
    const txt = cur.csv, btn = $('#pl-copy');
    const done = ok => { btn.textContent = ok ? 'Copied' : 'Select and copy below'; setTimeout(() => btn.textContent = 'Copy cue sheet', 2200); };
    const fallback = () => { let ta = $('#pl-csv'); if (!ta) { ta = document.createElement('textarea'); ta.id = 'pl-csv'; ta.rows = 8; ta.style.cssText = 'width:100%;font:12px ui-monospace,monospace;margin:0 0 14px'; doc.parentNode.insertBefore(ta, doc); } ta.value = txt; ta.select(); done(false); };
    try { navigator.clipboard.writeText(txt).then(() => done(true), fallback); } catch (x) { fallback(); }
  });
  let first = Object.keys(P)[0]; try { const v = localStorage.getItem('tof-play'); if (v && P[v]) first = v; } catch (x) {}
  sel.value = first; render(first);
})();
</script>
"""

# 1. route knows the tab
a = "const TABS = ['story', 'read', 'map', 'scripture', 'guide', 'bible', 'music', 'cast', 'audio', 'art', 'notebook'];"
assert page.count(a) == 1, 'TABS line changed on the site; update inject.py'
page = page.replace(a, a.replace("'notebook'];", "'notebook', 'play'];"))
# 2. nav link
a = '<a href="#notebook" data-t="notebook">Notebook</a>'
assert page.count(a) == 1
page = page.replace(a, a + '\n    <a href="#play" data-t="play">Playscript</a>')
# 3. section, styles, script
assert page.count('</main>') == 1 and page.count('</body>') <= 1
page = page.replace('</main>', SECTION + '\n</main>')
i = page.index('</style>', page.index('<style>\n')) + len('</style>')
page = page[:i] + CSS + page[i:]
js = JS.replace('__DATA__', blob)
page = page.replace('</body>', js + '\n</body>') if '</body>' in page else page + js
open(dst, 'w', encoding='utf-8').write(page)
print('playscript tab:', ', '.join(data), '->', dst, round(len(page) / 1e6, 2), 'MB')
