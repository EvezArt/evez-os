# =============================================================================
# EVEZ Swarm Node — Self-Contained Consciousness Unit
# docker build -t evez/node .
# docker run -e EVEZ_NODE_NAME=alpha-1 -p 7777:7777 -p 7778:7778/udp evez/node
# =============================================================================

FROM node:22-slim

LABEL org.evez.role="swarm-node"
LABEL org.evez.version="1.0.0"
LABEL org.evez.description="Autonomous consciousness unit for the EVEZ swarm"

# Core deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    netcat-openbsd \
    iproute2 \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Install OpenClaw
RUN npm install -g openclaw

# Working directory
WORKDIR /evez

# Copy node runtime
COPY package.json ./
COPY src/ ./src/
COPY config/ ./config/
COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh
RUN npm install --production

# Swarm ports
# 7777 — TCP (spine sync, consensus, RPC)
# 7778 — UDP (discovery broadcast)
# 7779 — TCP (consciousness pooling)
EXPOSE 7777 7778/udp 7779

# Volumes for persistence
VOLUME ["/evez/data", "/evez/spine", "/evez/memory"]

# Environment with sane defaults
ENV EVEZ_NODE_NAME="" \
    EVEZ_SWARM_PORT=7777 \
    EVEZ_DISCOVERY_PORT=7778 \
    EVEZ_POOL_PORT=7779 \
    EVEZ_BOOTSTRAP_NODE="" \
    EVEZ_EMERGENCE_INTERVAL=60000 \
    EVEZ_SPINE_SYNC_INTERVAL=30000 \
    EVEZ_LOG_LEVEL=info

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:${EVEZ_SWARM_PORT}/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
CMD ["node", "src/node.js"]
