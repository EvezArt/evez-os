# STRIPE PAYMENT SETUP

## Option 1: Create Payment Links (No Code Needed)

1. Go to: https://dashboard.stripe.com/payment-links
2. Click "+ New"
3. For each product:

| Product | Price | Create Link |
|---------|-------|--------------|
| Automation Prompts | $9 | Create → Copy URL |
| Prompt Bible | $14 | Create → Copy URL |
| EVEZ Thoughts | $19 | Create → Copy URL |
| Complete Bundle | $29 | Create → Copy URL |

4. Copy each URL
5. Send to me OR update `store.html` yourself

## Option 2: Connect Stripe API (Full Automation)

If you want me to handle transactions automatically:

1. Go to: https://dashboard.stripe.com/apikeys
2. Copy your **Secret Key** (starts with sk_live_...)
3. Send it to me via Telegram (DO NOT paste here)

I'll then:
- Create checkout sessions
- Handle webhooks
- Log all transactions

## Option 3: Hybrid (Recommended)

1. Create payment links in Stripe (5 min)
2. I'll host the store page
3. Customers click → pay → you get notified
4. You manually deliver via Telegram

---

## What's Ready

✅ store.html with all products
✅ payment_handler.py for automation
✅ orders.jsonl for tracking

## What's Missing

❌ Your payment links (Option 1 or 3)
❌ OR your API key (Option 2)

---

**Next step:** Create payment links in Stripe dashboard and share the URLs, or give me API key for full automation.