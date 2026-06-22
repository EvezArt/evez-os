#!/bin/bash
# EVEZ-OS Stream Entrypoint — picks the right renderer from STREAM_ID env
SCRIPTS=(
  ""
  "scripts/evez-livestream.py"
  "scripts/evez-cognition-stream.py"
  "scripts/evez-cortex-stream.py"
  "scripts/evez-quantum-stream.py"
  "scripts/evez-dreams-stream.py"
)
STREAM_KEY_VAR="YOUTUBE_STREAM_KEY_${STREAM_ID}"
STREAM_KEY="${!STREAM_KEY_VAR}"
SCRIPT="${SCRIPTS[$STREAM_ID]}"

echo "▶ Starting Stream ${STREAM_ID}: $SCRIPT → rtmp://a.rtmp.youtube.com/live2/[key]"

exec python3 "$SCRIPT"   --rtmp-url "${YOUTUBE_RTMP_BASE}/${STREAM_KEY}"   --width 1920 --height 1080 --fps 24
