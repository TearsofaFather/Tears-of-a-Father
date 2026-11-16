// Stripe Checkout for gifts on tearsofafather.com (Cloudflare Pages Function).
// The Give button posts here; this creates a Stripe-hosted Checkout page and sends the reader to it.
// Pages Functions can't load Stripe's Node package without a build step, so this calls the Stripe API directly.
// Setup (Cloudflare dashboard > the Pages project > Settings > Variables and Secrets):
//   STRIPE_SECRET_KEY  (secret)  sk_test_... while testing, sk_live_... when live
//   STRIPE_PRICE_ID    (plain)   the gift Price, e.g. price_... (see STRIPE_INTEGRATION_TODO.md)
//   DOMAIN             (plain, optional)  defaults to the site the request came from

function form(params, prefix = '', out = new URLSearchParams()) {
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null) continue;
    const key = prefix ? `${prefix}[${k}]` : k;
    if (typeof v === 'object') form(v, key, out);
    else out.append(key, String(v));
  }
  return out;
}

export async function onRequestPost({ request, env }) {
  if (!env.STRIPE_SECRET_KEY) return new Response('Giving is not set up yet.', { status: 503 });
  const domain = (env.DOMAIN || new URL(request.url).origin).replace(/\/$/, '');

  // TODO: Set mode to "subscription" if offering recurring gifts.
  const mode = 'payment';

  const sessionParams = {
    // configured in Checkout Studio
    ui_mode: 'hosted_page',
    billing_address_collection: 'auto',
    phone_number_collection: { enabled: false },
    automatic_tax: { enabled: false },
    allow_promotion_codes: false,
    submit_type: 'auto',
    integration_identifier: 'hosted_web_0002',
    origin_context: 'web',
    // placeholders: see STRIPE_INTEGRATION_TODO.md
    mode,
    success_url: `${domain}/?gift=thanks&session_id={CHECKOUT_SESSION_ID}#support`,
    cancel_url: `${domain}/#support`,
    line_items: { 0: { price: env.STRIPE_PRICE_ID || 'price_...', quantity: 1 } },
  };
  if (mode === 'subscription') sessionParams.payment_method_collection = 'always';

  const r = await fetch('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: {
      authorization: `Bearer ${env.STRIPE_SECRET_KEY}`,
      'content-type': 'application/x-www-form-urlencoded',
    },
    body: form(sessionParams),
  });
  const session = await r.json();
  if (!r.ok || !session.url) {
    console.log('Stripe Checkout error:', JSON.stringify(session.error || session));
    return new Response('Sorry, giving is not available right now. Please try again later.', { status: 502 });
  }
  return Response.redirect(session.url, 303);
}
