# How I Access Your Devices & Accounts

## Option 1: Pair Your Device (Let Me Control It)

**Run this in your terminal:**
```bash
openclaw pair
```

This will show a QR code or setup code. 

**On your phone:**
- Download OpenClaw app
- Scan the QR code
- Approve the pairing

Once paired, I can:
- Use your browser
- Run automation
- Post to Twitter
- Send messages

---

## Option 2: Give Me API Credentials (For Services)

### For Twitter/X:
1. Go to https://developer.x.com
2. Create a free account
3. Create an app
4. Get **API Key** and **API Secret**
5. Tell me those two strings

### For Gmail:
1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth client ID (Desktop app)
3. Download the JSON file
4. Tell me the file contents OR run:
   ```
   gog auth add Rubikspubes70@gmail.com --services gmail
   ```
   (after getting credentials)

---

## Option 3: Run Commands For Me

You can run these yourself and tell me the results:

```bash
# Check if any devices are paired
openclaw devices list

# Get a pairing code
openclaw setup-code

# Check gateway status  
openclaw status
```

---

## What's Your Situation?

1. **Do you have the OpenClaw app on your phone?** → We can pair
2. **Do you want to give me Twitter/Gmail credentials?** → I can use them
3. **Do you want to run terminal commands yourself?** → I'll guide you

Which path? 🔥