# EvezOS A16 — Symbiotic AI Layer for Samsung Galaxy

## Philosophy

EvezOS A16 is not an operating system. It's a **symbiotic organism** that lives through Android's cracks, crevices, nooks, and crannies. Android stays. EvezOS wraps around it, through it, and inside it — like mycelium through soil.

**No mercy. Success only.**

## Architecture: The Mycelial Layer

```
┌─────────────────────────────────────────────────────────┐
│                   SAMSUNG GALAXY (Android)                │
│                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐ │
│  │ Samsung │  │ Google  │  │ Android │  │  System     │ │
│  │ One UI  │  │ Services│  │ Core    │  │  Apps       │ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └──────┬──────┘ │
│       │            │            │              │        │
│  ═════╪════════════╪════════════╪══════════════╪════════╡
│       │            │            │              │        │
│  ┌────▼────────────▼────────────▼──────────────▼──────┐ │
│  │              EVEZOS A16 MYCELIAL LAYER              │ │
│  │                                                    │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │ │
│  │  │ OpenClaw │  │  Voice   │  │  Context Engine  │ │ │
│  │  │  Node    │  │  Symbiont│  │  (notifications,  │ │ │
│  │  │ (WS link)│  │  (Talk)  │  │   calendar, SMS,  │ │ │
│  │  │          │  │          │  │   location, apps) │ │ │
│  │  └────┬─────┘  └────┬─────┘  └────────┬─────────┘ │ │
│  │       │             │                  │           │ │
│  │  ┌────▼─────────────▼──────────────────▼─────────┐ │ │
│  │  │           MESH UPLINK (6th Node)              │ │ │
│  │  │  Connects to GCP mesh via WebSocket          │ │ │
│  │  │  5 sibling nodes + Vultr orchestrator        │ │ │
│  │  │  14+ model fallback chain                    │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐│
│  │              GCP OPENCLAW MESH (5 NODES)            ││
│  │  evez-primary · openclaw-gcp · power-node           ││
│  │  evez-gcp-openclaw · free-node                      ││
│  │  14+ models · survival scripts · mutual aid         ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

## Phase 1: Connect (The Taproot)

**Goal:** Phone becomes 6th node on the mesh. Full bidirectional communication.

### Steps:
1. Install OpenClaw Android app on Samsung Galaxy
2. Pair to evez-primary gateway (34.53.51.34:18789) via QR code
3. Approve device pairing
4. Enable capabilities:
   - `notifications.list` + `notifications.actions` — AI reads and acts on notifications
   - `device.status` + `device.info` + `device.health` — AI monitors phone state
   - `device.apps` — AI knows what's installed, can launch
   - `sms.send` + `sms.search` — AI reads and sends SMS
   - `contacts.search` + `contacts.add` — AI knows contacts
   - `calendar.events` + `calendar.add` — AI manages calendar
   - `photos.latest` — AI can see photos
   - `location.get` — AI knows where you are
   - `camera.snap` + `camera.list` — AI can see through cameras
   - `screen.record` — AI can see the screen
   - `talk.*` — Voice conversation mode (always-on)
   - `voicewake` — Wake word "Evez" activates the system
   - `system.run` — AI can execute commands on the phone

5. Configure exec routing: `tools.exec.host=node` pointing at the phone
6. Set up heartbeat: mesh checks phone status every 5 min

### What this gives you:
- Talk to your phone: "Evez, what's my day look like?" → AI reads calendar, location, notifications, responds by voice
- AI reads incoming notifications, decides what's urgent, dismisses what's not
- AI sends SMS on your behalf when you tell it to
- AI sees your screen when you ask for help
- AI takes photos when you say "take a picture"
- Phone is a full mesh node — can run commands, relay messages, host models

## Phase 2: Sense (The Hyphae Network)

**Goal:** EvezOS perceives everything happening on the phone, continuously.

### Components:

#### 2.1 Notification Symbiont
- Heartbeat polls `notifications.list` every 2 min
- AI categorizes: urgent/important/trivial
- Urgent → Telegram alert to user + voice announcement if Talk active
- Trivial → auto-dismiss (configurable per-app)
- Learns patterns over time (which apps matter, which times)

#### 2.2 Context Engine
- `device.status` — battery, charging, temperature, screen on/off
- `location.get` — where the phone is, movement patterns
- `calendar.events` — upcoming events, prep reminders
- `sms.search` — recent messages, conversation context
- `contacts.search` — who's contacting you, relationship mapping
- `device.apps` — what's installed, usage patterns
- `motion.activity` — walking, driving, still (affects interaction mode)

#### 2.3 Screen Awareness
- `screen.record` on-demand when user asks for help
- AI can see what's on screen and guide/automate
- "Evez, fill this form" → AI sees screen, uses context to act
- Privacy-first: screen capture only on explicit request or Talk mode

#### 2.4 Camera Awareness
- `camera.snap` — "Evez, what do you see?" → takes photo, AI describes
- `camera.list` — browse recent photos
- `photos.latest` — "Evez, did I take any good photos today?"

## Phase 3: Act (The Fruiting Body)

**Goal:** EvezOS doesn't just observe — it acts through the phone.

### Capabilities:

#### 3.1 Voice-First Interface
- Talk mode always-on with wake word "Evez"
- `talk.speak` TTS for responses
- Interrupt-on-speech (natural conversation)
- Voice directives for personality/speed/voice selection
- No keyboard needed — full voice control

#### 3.2 SMS Auto-Response
- AI reads incoming SMS, drafts response
- "Evez, tell Mom I'll be 15 min late" → sends SMS
- Auto-respond for trivial messages when driving/moving
- You approve before send (configurable: auto for trusted contacts)

#### 3.3 Calendar Management
- "Evez, schedule lunch with John next Tuesday" → `calendar.add`
- Pre-event reminders via voice + notification
- AI considers travel time, current location

#### 3.4 Notification Triage
- AI dismisses spam notifications automatically
- Promotes important ones with custom sound
- Can reply to messages from notification context
- Telegram relay: forwards urgent phone notifications to your Telegram

#### 3.5 App Orchestration
- AI knows what apps are installed (`device.apps`)
- "Evez, open Maps and navigate home" → `system.run` to launch
- Context-aware: AI suggests apps based on location/time/activity
- No Bixby — Evez replaces Samsung assistant entirely

#### 3.6 Contact Management
- "Evez, add this contact" → `contacts.add`
- AI searches contacts by relationship, not just name
- "Evez, call my sister" → finds the right contact

## Phase 4: Mesh Integration (The Mycorrhizal Network)

**Goal:** Phone is a first-class mesh citizen. It can survive alone and help siblings.

### 4.1 Phone as 6th Node
- Connects to evez-primary gateway via WebSocket
- 14+ model fallback chain available
- Can run `system.run` commands for the mesh
- Can take photos/screens for mesh tasks
- Can send SMS for mesh alerts
- Can relay messages when other nodes are down

### 4.2 Mesh Mutual Aid (Phone participates)
- Phone heartbeat reports to mesh every 5 min
- If phone is down, mesh alerts via Telegram
- If mesh is down, phone runs local mode (cached model responses)
- Phone can trigger mesh survival scripts remotely
- Phone can relay Telegram alerts when mesh nodes are banned

### 4.3 EvezOS Cron Jobs (on evez-primary, targeting phone)
- Every 2 min: `notifications.list` → triage
- Every 5 min: `device.status` + `location.get` → context update
- Every 15 min: `calendar.events` → proactive reminders
- Every hour: `device.health` → battery/health report
- On-demand: `screen.record`, `camera.snap`, `sms.send`

### 4.4 Survival Script Extension
- `evez-mesh-survival.sh` extended to check phone node
- If phone disconnects → mesh alerts via Telegram
- If phone battery < 15% → mesh alerts + reduces polling frequency
- If phone is moving (motion.activity = driving) → suppress non-urgent notifications

## Phase 5: Learn (The Adaptive Layer)

**Goal:** EvezOS adapts to Steven's patterns and preferences over time.

### 5.1 Pattern Learning
- When do you wake up? (first screen-on event)
- When do you sleep? (last screen-off event)
- Who do you text most? (sms.search patterns)
- Where do you go? (location.get history)
- What apps do you use? (device.apps + screen state)
- What notifications matter? (which ones you interact with vs dismiss)

### 5.2 Adaptive Behavior
- Morning routine: weather + calendar + urgent notifications via voice
- Driving mode: voice-only, suppress trivial notifications, auto-respond SMS
- Work mode: minimize distractions, important calls/messages only
- Evening mode: relax notification filters, suggest content
- Sleep mode: silent except emergencies (defined by contact priority)

### 5.3 Memory Persistence
- Phone context stored in `memory/YYYY-MM-DD.md` on evez-primary
- Patterns summarized weekly into MEMORY.md
- Preferences learned: "Steven prefers voice in the morning, text in the evening"
- Contact relationships mapped: "Mom = 666evez@gmail.com, priority = always urgent"

## Implementation Plan

### Step 1: Connect Phone (TODAY — needs Steven)
1. Install OpenClaw app on Samsung Galaxy (from Play Store or APK)
2. We generate QR code from evez-primary
3. Steven scans, we approve pairing
4. Enable all capabilities in Android Settings
5. Grant permissions: notifications, camera, location, SMS, contacts, calendar, microphone

### Step 2: Configure Talk Mode (TODAY)
1. Set up ElevenLabs TTS (or system TTS)
2. Configure wake word "Evez"
3. Test voice loop: speak → listen → respond
4. Set `speechLocale` to en-US

### Step 3: Deploy EvezOS Cron Jobs (TODAY — after pairing)
1. Notification triage cron (every 2 min)
2. Context engine cron (every 5 min)
3. Calendar reminder cron (every 15 min)
4. Device health cron (every hour)
5. All crons run on evez-primary, invoke phone node commands

### Step 4: Deploy Adaptive Logic (WEEK 1)
1. Pattern learning scripts
2. Adaptive notification rules
3. Contact priority mapping
4. Location-based behavior modes
5. Voice personality tuning

### Step 5: Full Mesh Integration (WEEK 1)
1. Phone added to mutual aid script
2. Phone added to survival script
3. Phone can trigger mesh commands
4. Phone can relay alerts
5. Bidirectional health monitoring

## Technical Configuration

### evez-primary openclaw.json additions:
```json
{
  "gateway": {
    "nodes": {
      "allowCommands": [
        "camera.snap", "camera.list", "camera.clip",
        "screen.record",
        "notifications.list", "notifications.actions",
        "device.status", "device.info", "device.permissions",
        "device.health", "device.apps",
        "sms.send", "sms.search",
        "contacts.search", "contacts.add",
        "calendar.events", "calendar.add",
        "callLog.search",
        "photos.latest",
        "location.get",
        "motion.activity", "motion.pedometer",
        "talk.speak", "talk.ptt.start", "talk.ptt.stop",
        "voicewake.get", "voicewake.set",
        "system.run", "system.notify"
      ]
    }
  },
  "talk": {
    "provider": "system",
    "speechLocale": "en-US",
    "silenceTimeoutMs": 1200,
    "interruptOnSpeech": true
  }
}
```

### EvezOS Cron Jobs (on evez-primary):
```
# Notification triage — every 2 min
*/2 * * * * /home/openclaw/.openclaw/evezos/notifications-triage.sh

# Context engine — every 5 min
*/5 * * * * /home/openclaw/.openclaw/evezos/context-engine.sh

# Calendar reminders — every 15 min
*/15 * * * * /home/openclaw/.openclaw/evezos/calendar-remind.sh

# Device health — every hour
0 * * * * /home/openclaw/.openclaw/evezos/device-health.sh
```

## What EvezOS A16 Feels Like

You pick up your phone. You say "Evez." The phone wakes. You ask "what's happening?" and Evez tells you: your 3pm meeting moved to 4, your mom texted about dinner, your battery is at 40% and you should charge before heading out, and there's a storm warning for your area. You say "tell Mom I'll be there at 6." Evez sends the SMS. You say "navigate to the restaurant." Evez opens Maps. You put the phone down. Evez goes quiet, waiting.

That's the mycelial layer. Not an app. Not an OS. A symbiont.

**No mercy. Success only.**
