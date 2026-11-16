# Stripe Integration TODO

Giving on tearsofafather.com uses **Hosted Stripe Checkout**: the reader taps **Give a Gift** on the Support tab, lands on a Stripe-hosted page, types the amount they want to give, and pays. No tax is added (automatic tax is off).

The Support tab is on the **preview site only** (preview.tears-of-a-father.pages.dev) and the private site until it's approved for the live site.

## Values to Replace

The following values are placeholders and must be updated before going live.

**Files containing placeholders:**
- [functions/api/create-checkout-session.js](functions/api/create-checkout-session.js)

| Field | Current Value | What to Set |
|-------|--------------|-------------|
| mode | payment | Keep "payment" for one-time gifts. Use "subscription" only if you add monthly giving. |
| success_url | `{DOMAIN}/?gift=thanks&session_id={CHECKOUT_SESSION_ID}#support` | Already points back to the Support tab, which shows a thank-you note. Change it only if you add a separate thank-you page. Keep the {CHECKOUT_SESSION_ID} template. |
| cancel_url | `{DOMAIN}/#support` | Already returns the reader to the Support tab. |
| line_items[].price | `price_1UcR8Q3pdiZIb8On7mePDUOM` (set Nov 16; the `STRIPE_PRICE_ID` variable overrides it) | Done. When you go live, set `STRIPE_PRICE_ID` in Cloudflare Production to the live-mode Price ID, unless this one is already live. |

## Configured Parameters

These parameters were configured in Checkout Studio and are already set correctly.

**Files containing these parameters:**
- [functions/api/create-checkout-session.js](functions/api/create-checkout-session.js)

| Parameter | Value |
|-----------|-------|
| ui_mode | hosted_page |
| billing_address_collection | auto |
| phone_number_collection | enabled: false |
| automatic_tax | enabled: false |
| allow_promotion_codes | false |
| submit_type | auto |
| integration_identifier | hosted_web_0002 |
| origin_context | web |

`payment_method_collection` (always) is applied only if `mode` is changed to "subscription".

## Setup

1. **API keys.** In the Stripe Dashboard, open Developers > API keys (https://dashboard.stripe.com/test/apikeys). Copy the **secret key** (`sk_test_...` while testing).
2. **The gift Price (reader chooses the amount).** In the Dashboard, go to Product catalog > Add product:
   - Name: *Gift to support Tears of a Father*
   - Pricing: **One-off**, and choose **Customer chooses price** (sometimes shown as "Let customers decide").
   - Currency: USD. Optionally set a suggested amount and a minimum (for example $5 suggested, $1 minimum).
   - Save, then copy the Price ID (`price_...`).
3. **Cloudflare variables.** In the Cloudflare dashboard, open Workers & Pages > the tearsofafather project > Settings > Variables and Secrets. Add these for **both Preview and Production**:
   - `STRIPE_SECRET_KEY`: type **Secret**, value `sk_test_...` (switch to `sk_live_...` when you go live)
   - `STRIPE_PRICE_ID` (optional): the code already uses `price_1UcR8Q3pdiZIb8On7mePDUOM`. Add this only to use a different Price, for example the live-mode one.
   - `DOMAIN` (optional): leave it out to use whichever site the reader is on
4. Redeploy (any new push redeploys), or use **Retry deployment** on the latest deployment so the variables take effect.

Never put keys in the site's code or in this repository. See https://docs.stripe.com/keys-best-practices.

## Project structure

- `functions/api/create-checkout-session.js`: new. Creates the Checkout Session and redirects the reader to Stripe.
- The Support tab's **Give a Gift** button posts to `/api/create-checkout-session`. After a gift, Stripe sends the reader back to the Support tab with a thank-you note.

No Stripe package is installed. The function calls the Stripe API directly, and no API version is set, so your account's default API version applies.

## How it works

1. The reader taps **Give a Gift**.
2. The function creates a Checkout Session with the settings above and answers with a redirect to Stripe's page.
3. The reader enters an amount and pays on Stripe.
4. Stripe sends them back to `/?gift=thanks...#support`.
5. You see the gift in the Stripe Dashboard under Payments, and Stripe emails a receipt if receipts are turned on (Settings > Customer emails).

No webhook is set up, because nothing needs to happen on the site after a gift. Add one later (Developers > Webhooks, event `checkout.session.completed`) if you want automatic thank-you emails or a gift log.

## Testing

Use the preview site with **test** keys and a test-mode Price.

- Card that succeeds: `4242 4242 4242 4242`, any future expiry date, any CVC, any ZIP
- Card that is declined: `4000 0000 0000 0002`
- Card that needs extra authentication: `4000 0025 0000 3155`

Check the test payment under Payments in test mode. Then switch both variables to live values.

**If Checkout fails to open:** check Workers & Pages > the project > Functions > logs for "Stripe Checkout error":
- If Stripe rejects `ui_mode: hosted_page`, your account's API version predates it. Change it to `hosted` in the function, which is the value for older versions.
- If Stripe rejects `integration_identifier` or `origin_context`, remove those two lines. They are Checkout Studio settings that some accounts don't accept through the API.

## Next steps

- When the Support tab is approved, it moves from the preview site to the live site.
- Consider changing **Submit type** to "donate" in Checkout Studio, so Stripe's button reads "Donate". If you do, change `submit_type` in the function to match.
- Monthly giving: create a recurring Price and switch `mode` to "subscription".

## Resources

- https://support.stripe.com
- https://docs.stripe.com/mcp
