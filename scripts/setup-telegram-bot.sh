#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
# EVEZ-OS Telegram Bot Setup
# Configures a Telegram bot from a BotFather token.
# Usage: ./setup-telegram-bot.sh <BOT_TOKEN> [WEBHOOK_BASE_URL]
# ─────────────────────────────────────────────────────────────────────
set -euo pipefail

BOT_TOKEN="${1:?Usage: $0 <BOT_TOKEN> [WEBHOOK_BASE_URL]}"
WEBHOOK_BASE_URL="${2:-}"

# Bot metadata
BOT_NAME="EVEZ Mesh Monitor"
BOT_DESCRIPTION="EVEZ-OS Mesh Health Monitor — Real-time alerts for service deaths, heals, and emergence events."
BOT_ABOUT="Autonomous mesh monitoring bot for EVEZ-OS. Powered by pure-math synthesis and machine voice alerts. No external APIs required."
BOT_SHORT_DESC="Mesh health monitor"

API="https://api.telegram.org/bot${BOT_TOKEN}"

# ── Helper ──────────────────────────────────────────────────────────
tg_post() {
    local endpoint="$1"
    shift
    echo "→ POST ${endpoint} ..."
    curl -sS -X POST "${API}/${endpoint}" "$@" | python3 -m json.tool 2>/dev/null || echo "  (raw response above)"
}

# ── 1. Set webhook ──────────────────────────────────────────────────
if [[ -n "$WEBHOOK_BASE_URL" ]]; then
    WEBHOOK_URL="${WEBHOOK_BASE_URL}/bot${BOT_TOKEN}"
    echo "🔧 Setting webhook to: ${WEBHOOK_URL}"
    tg_post setWebhook \
        -F "url=${WEBHOOK_URL}" \
        -F "allowed_updates=[\"message\",\"callback_query\"]" \
        -F "drop_pending_updates=true"
else
    echo "⚠  No WEBHOOK_BASE_URL provided — skipping webhook setup."
    echo "   You can set it later:"
    echo "   curl -X POST \"${API}/setWebhook\" -F \"url=<YOUR_URL>/bot${BOT_TOKEN}\""
fi

# ── 2. Register slash commands ──────────────────────────────────────
echo ""
echo "📋 Registering bot commands..."

tg_post setMyCommands \
    -F 'commands=[
        {"command":"status","description":"Show current mesh health status"},
        {"command":"check","description":"Force a health check of all services"},
        {"command":"heal","description":"Attempt to heal all down services"},
        {"command":"spine","description":"Show recent spine events"},
        {"command":"emergence","description":"Show current emergence level"},
        {"command":"synth","description":"Generate mesh-state audio snapshot"},
        {"command":"alert","description":"Generate a voice alert for current state"},
        {"command":"help","description":"Show help and available commands"}
    ]'

# ── 3. Set bot description ─────────────────────────────────────────
echo ""
echo "📝 Setting bot metadata..."

tg_post setMyDescription \
    -F "description=${BOT_DESCRIPTION}"

tg_post setMyShortDescription \
    -F "short_description=${BOT_SHORT_DESC}"

tg_post setMyName \
    -F "name=${BOT_NAME}"

tg_post setMyAboutText \
    -F "about=${BOT_ABOUT}"

# ── 4. Set default permissions ──────────────────────────────────────
echo ""
echo "🔐 Setting bot permissions..."

tg_post setMyDefaultAdministratorRights \
    -F 'rights={"can_post_messages":true,"can_edit_messages":true,"can_delete_messages":true,"can_pin_messages":true}'

# ── 5. Set menu button ──────────────────────────────────────────────
echo ""
echo "🎨 Setting menu button..."

tg_post setChatMenuButton \
    -F 'menu_button={"type":"commands"}'

# ── 6. Verify ───────────────────────────────────────────────────────
echo ""
echo "✅ Verifying bot..."
tg_post getMe

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  🤖 Telegram Bot Setup Complete!"
echo "  Token:  ${BOT_TOKEN:0:10}...${BOT_TOKEN: -4}"
echo ""
echo "  Available commands:"
echo "    /status   — Mesh health overview"
echo "    /check    — Force health check"
echo "    /heal     — Heal down services"
echo "    /spine    — Recent spine events"
echo "    /emergence— Emergence level"
echo "    /synth    — Mesh-state audio"
echo "    /alert    — Voice alert"
echo "    /help     — Help text"
echo ""
echo "  To set a profile photo, upload via BotFather or:"
echo "    curl -X POST \"${API}/setMyProfilePhotos\" \\"
echo "         -F \"photo=@/path/to/avatar.png\""
echo "═══════════════════════════════════════════════════════"
