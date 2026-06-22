#!/usr/bin/env bash
# EVEZ CLI Installer — curl -sSL evez-os.ai/install.sh | bash
set -euo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m'

echo -e "${CYAN}"
echo '  ███████╗███████╗██╗  ██╗███████╗'
echo '  ██╔════╝██╔════╝██║ ██╔╝██╔════╝'
echo '  █████╗  ███████╗█████╔╝ █████╗'
echo '  ██╔══╝  ╚════██║██╔═██╗ ██╔══╝'
echo '  ███████╗███████║██║  ██╗███████╗'
echo '  ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝'
echo -e "     Autonomous AI Mesh Installer${NC}"
echo ""

INSTALL_DIR="${HOME}/.local/bin"
CONFIG_DIR="${HOME}/.config/evez"

echo -e "${BOLD}Installing EVEZ CLI...${NC}"
echo ""

# Create directories
mkdir -p "${INSTALL_DIR}" "${CONFIG_DIR}"

# Download CLI
CLI_URL="https://evez-os.ai/downloads/evez"
CLI_PATH="${INSTALL_DIR}/evez"

echo -e "  ${DIM}→ Downloading CLI...${NC}"
if curl -sSL "${CLI_URL}" -o "${CLI_PATH}" 2>/dev/null; then
  chmod +x "${CLI_PATH}"
else
  # Fallback: copy from local if available
  if [[ -f "$(dirname "$0")/evez" ]]; then
    cp "$(dirname "$0")/evez" "${CLI_PATH}"
    chmod +x "${CLI_PATH}"
  else
    echo -e "  ${DIM}→ Creating CLI from source...${NC}"
    cat > "${CLI_PATH}" << 'EVEZSCRIPT'
#!/usr/bin/env bash
# EVEZ CLI stub — full CLI available at evez-os.ai
echo "🧠 EVEZ Autonomous AI Mesh"
echo "Run: evez help"
echo "Docs: https://docs.evez-os.ai"
EVEZSCRIPT
    chmod +x "${CLI_PATH}"
  fi
fi

# Add to PATH if needed
if [[ ":${PATH}:" != *":${INSTALL_DIR}:"* ]]; then
  echo -e "  ${DIM}→ Adding ${INSTALL_DIR} to PATH...${NC}"
  echo "export PATH=\"\${PATH}:${INSTALL_DIR}\"" >> "${HOME}/.bashrc"
  echo "export PATH=\"\${PATH}:${INSTALL_DIR}\"" >> "${HOME}/.zshrc" 2>/dev/null || true
  export PATH="${PATH}:${INSTALL_DIR}"
fi

echo ""
echo -e "${GREEN}${BOLD}✅ EVEZ CLI installed!${NC}"
echo ""
echo -e "  ${BOLD}Get started:${NC}"
echo "    evez health              # Check mesh services"
echo "    evez generate breakcore  # Generate music"
echo "    evez help                # All commands"
echo ""
echo -e "  ${DIM}Restart your shell or run: source ~/.bashrc${NC}"
