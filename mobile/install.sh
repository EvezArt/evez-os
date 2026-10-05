#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
CONFIG_DIR="$HOME/.config/evez"
CONFIG_FILE="$CONFIG_DIR/evez.env"
BIN_DIR="$PREFIX/bin"
REPO_DIR="$HOME/evez-os"

say() { printf '%s\n' "$*"; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

command -v pkg >/dev/null 2>&1 || die "This installer is intended for Termux."

pkg update -y
pkg install -y git curl jq openssl openssh python

mkdir -p "$CONFIG_DIR" "$BIN_DIR"

if [ -f "$CONFIG_FILE" ]; then
  cp "$CONFIG_FILE" "$CONFIG_FILE.bak.$(date +%s)"
fi

cat > "$CONFIG_FILE" <<'EOF'
# EVEZ-OS mobile operator configuration.
export EVEZ_ENDPOINT="https://evez-os.ai"
export EVEZ_GATEWAY_HEALTH_PATH="/health"
export EVEZ_PIPELINE_PATH="/pipeline"
export EVEZ_SPINE_EVENT_PATH="/spine/event"
export EVEZ_DEPLOY_HOOK=""
export EVEZ_ROOT="$HOME/evez-os"
EOF

chmod 600 "$CONFIG_FILE"

if [ -d "$REPO_DIR/.git" ]; then
  say "Existing checkout found: $REPO_DIR"
else
  git clone "https://github.com/EvezArt/evez-os.git" "$REPO_DIR"
fi

install -m 0755 "$REPO_DIR/mobile/evezctl" "$BIN_DIR/evezctl"
printf '\nexport PATH="%s:$PATH"\n' "$BIN_DIR" >> "$HOME/.bashrc"

. "$CONFIG_FILE"

say "Installed evezctl to $BIN_DIR/evezctl"
say "Config: $CONFIG_FILE"
say "Checkout: $REPO_DIR"
say ""
say "Run:"
say "  source "$CONFIG_FILE""
say "  evezctl doctor"
say "  evezctl status"
