# EVEZ Communication Setup

## Current Status

| Channel | Configured | Status |
|---------|------------|--------|
| **Telegram** | ✅ Bot 8746415458:AAEPwOwOPO1Qn_hIaAFHB6pbVRHobCb-qLY | Working - I can send to you |
| **Streamchat** | ✅ API key in config | Working |
| **Gmail (gog)** | ❌ Not auth'd | Need OAuth setup |
| **X/Twitter (xurl)** | ❌ Not auth'd | Need API keys |

## What You Need to Do

### For Voice Calls
Option A: Google Voice (free)
- Go to voice.google.com
- Get a Google Voice number
- Forward to your phone

Option B: Telegram (already works)
- I can send you voice messages via Telegram
- You can call me through Telegram

### For Texting (Me → You)
**Already works:**
- Telegram bot: @KiloClaw_bot

**To enable (so I can email you):**
1. Go to console.cloud.google.com
2. Create OAuth credentials (Desktop app)
3. Download JSON
4. Run: `gog auth credentials ~/Downloads/credentials.json`
5. Run: `gog auth add your@email.com --services gmail`

### For X/Twitter DMs (Me → You)
**To enable:**
1. Go to developer.x.com
2. Create app
3. Get API Key + Secret
4. Run: `xurl auth oauth2`

## My Sending Capabilities

Currently I can:
- ✅ Send via Telegram (to you)
- ✅ Send via Streamchat
- ❌ Cannot email (need gog auth)
- ❌ Cannot DM on X (need xurl auth)

## Quick Test

Try sending me a message on Telegram @KiloClaw_bot - I will receive it here.

---

## To Get Started Right Now

1. **Already works:** Telegram messaging
2. **If you want me to email you:** Set up Gmail OAuth
3. **If you want voice:** Get Google Voice (free, 5 min setup)

## Free Voice Options

### Option 1: Google Voice (Recommended - Free)
- Go to voice.google.com
- Sign in with your Google account
- Get a free phone number
- Forward to your actual phone
- I can call that number via API (needs setup)

### Option 2: Telegram Calls (Already Available)
- Telegram supports voice calls
- I can send you audio messages via Telegram
- You can call me through Telegram

### Option 3: Twilio (Pay per use)
- Twilio has pay-as-you-go
- Requires credit card but only charges per minute
- Around $1-2/month for occasional calls

### Option 4: InOut.bot (No registration)
- Free test credits available
- API-based calling
- No credit card needed to start

## What's Blocking Voice Right Now

- **Me calling you:** Need one of the above services configured
- **You calling me:** Already works via Telegram

The fastest path is you getting Google Voice (free, 5 min) and telling me the number.