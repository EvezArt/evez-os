# EVEZ Bot

Multi-platform bot for the EVEZ Autonomous AI Mesh.

## Supported Platforms

- **Slack** — Slash commands + app mentions
- **Discord** — Slash commands + interactions
- **Telegram** — Bot commands

## Commands

| Command | Description |
|---------|-------------|
| `/evez health` | Check all 11 mesh services |
| `/evez generate breakcore` | Generate breakcore track |
| `/evez generate dubstep 140` | Generate dubstep at 140 BPM |
| `/evez correlate genetics telemetry` | Run cross-domain correlation |
| `/evez status` | Dashboard summary |

## Setup

### Slack
1. Create app at api.slack.com
2. Enable slash commands: `/evez`
3. Set environment variables:
   ```
   SLACK_SIGNING_SECRET=xxx
   SLACK_BOT_TOKEN=xoxb-xxx
   ```
4. Run: `npm run slack`

### Discord
1. Create app at discord.com/developers
2. Register slash commands
3. Set: `DISCORD_BOT_TOKEN=xxx`
4. Run: `npm run discord`

### Telegram
1. Create bot via @BotFather
2. Set: `TELEGRAM_BOT_TOKEN=xxx`
3. Set webhook to your server
4. Run: `npm run telegram`

## Deploy

```bash
# Docker
docker build -t evez-bot .
docker run -p 3000:3000 -e EVEZ_PLATFORM=slack evez-bot

# Direct
EVEZ_PLATFORM=discord node bot.js
```
