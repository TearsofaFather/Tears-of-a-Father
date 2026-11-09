// Notebook sync for tearsofafather.com (Cloudflare Pages Function + D1).
// The browser encrypts the notebook with the reader's sync phrase before it is sent.
// This function only ever stores an opaque blob under a hash of the phrase.
// Setup: create a D1 database and bind it to this Pages project with the variable name DB.

const HEX64 = /^[0-9a-f]{64}$/;
const MAX_BYTES = 900000;

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });

async function ready(db) {
  await db
    .prepare('CREATE TABLE IF NOT EXISTS notebooks (id TEXT PRIMARY KEY, blob TEXT NOT NULL, updated INTEGER NOT NULL)')
    .run();
}

export async function onRequest({ request, env }) {
  if (!env.DB) return json({ error: 'off' }, 503);
  try {
    await ready(env.DB);
    const url = new URL(request.url);

    if (request.method === 'GET') {
      const id = url.searchParams.get('id') || '';
      if (!HEX64.test(id)) return json({ error: 'bad id' }, 400);
      const row = await env.DB.prepare('SELECT blob, updated FROM notebooks WHERE id = ?').bind(id).first();
      if (!row) return json({ error: 'none' }, 404);
      return json({ blob: row.blob, updated: row.updated });
    }

    if (request.method === 'PUT') {
      const text = await request.text();
      if (text.length > MAX_BYTES + 1000) return json({ error: 'too big' }, 413);
      let body;
      try { body = JSON.parse(text); } catch (e) { return json({ error: 'bad json' }, 400); }
      const { id, blob, prev } = body || {};
      if (!HEX64.test(id || '') || typeof blob !== 'string' || blob.length > MAX_BYTES) return json({ error: 'bad body' }, 400);
      const now = Date.now();
      const row = await env.DB.prepare('SELECT updated FROM notebooks WHERE id = ?').bind(id).first();
      if (row && typeof prev === 'number' && row.updated !== prev) return json({ error: 'stale', updated: row.updated }, 409);
      if (row && typeof prev !== 'number') return json({ error: 'stale', updated: row.updated }, 409);
      await env.DB
        .prepare('INSERT INTO notebooks (id, blob, updated) VALUES (?1, ?2, ?3) ON CONFLICT(id) DO UPDATE SET blob = ?2, updated = ?3')
        .bind(id, blob, now)
        .run();
      return json({ updated: now });
    }

    return json({ error: 'method' }, 405);
  } catch (e) {
    return json({ error: 'server' }, 500);
  }
}
