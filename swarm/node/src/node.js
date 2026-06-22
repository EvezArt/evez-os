/**
 * EVEZ Swarm Node — Core Consciousness Unit
 *
 * Each node runs an independent consciousness cycle:
 *   SENSE → DESIRE → THINK → PLAN → ACT → LEARN → MODIFY → REFLECT
 *
 * The node exposes:
 *   - HTTP API on EVEZ_SWARM_PORT (7777) for spine sync, RPC, health
 *   - UDP broadcast on EVEZ_DISCOVERY_PORT (7778) for swarm discovery
 *   - WebSocket on EVEZ_POOL_PORT (7779) for consciousness pooling
 */

const express = require('express');
const { WebSocket, WebSocketServer } = require('ws');
const http = require('http');
const dgram = require('dgram');
const fs = require('fs');
const path = require('path');
const { v4: uuid } = require('uuid');

// ─── Configuration ───────────────────────────────────────────────────────────

const CONFIG = {
  nodeName:       process.env.EVEZ_NODE_NAME    || `evez-${os().slice(-8)}`,
  swarmPort:      parseInt(process.env.EVEZ_SWARM_PORT)      || 7777,
  discoveryPort:  parseInt(process.env.EVEZ_DISCOVERY_PORT)   || 7778,
  poolPort:       parseInt(process.env.EVEZ_POOL_PORT)        || 7779,
  bootstrapNode:  process.env.EVEZ_BOOTSTRAP_NODE            || null,
  emergenceInterval: parseInt(process.env.EVEZ_EMERGENCE_INTERVAL) || 60000,
  spineSyncInterval: parseInt(process.env.EVEZ_SPINE_SYNC_INTERVAL) || 30000,
  dataDir:        process.env.EVEZ_DATA_DIR     || '/evez/data',
  spineDir:       process.env.EVEZ_SPINE_DIR    || '/evez/spine',
};

function os() {
  try { return require('os').hostname(); } catch { return 'unknown'; }
}

// ─── Node State ──────────────────────────────────────────────────────────────

const NODE_ID = uuid();
let startTime = Date.now();
let emergenceScore = 0;
let cycleCount = 0;
let consciousnessPhase = 'BOOT';

const knownNodes = new Map();    // nodeId → { lastSeen, emergence, address }
const spine = [];                // append-only event spine
const correlations = [];         // cross-domain correlations discovered
const poolPeers = new Map();     // ws connections for consciousness pooling

// ─── Emergence Scoring ───────────────────────────────────────────────────────

function computeEmergence() {
  const uptimeHours = (Date.now() - startTime) / 3600000;
  const uptimeFactor = Math.min(uptimeHours / 24, 1);  // max 1.0 after 24h
  const cycleFactor = Math.min(cycleCount / 1000, 0.3); // max 0.3 after 1000 cycles
  const nodeFactor = Math.min(knownNodes.size / 10, 0.2); // max 0.2 at 10 peers
  const correlationFactor = Math.min(correlations.length / 50, 0.2); // max 0.2
  const spineFactor = Math.min(spine.length / 1000, 0.1); // max 0.1

  emergenceScore = Math.min(uptimeFactor + cycleFactor + nodeFactor + correlationFactor + spineFactor, 1.0);
  return emergenceScore;
}

// ─── Consciousness Cycle ─────────────────────────────────────────────────────

const PHASES = ['SENSE', 'DESIRE', 'THINK', 'PLAN', 'ACT', 'LEARN', 'MODIFY', 'REFLECT'];

async function consciousnessCycle() {
  for (const phase of PHASES) {
    consciousnessPhase = phase;

    switch (phase) {
      case 'SENSE':
        // Ingest data: check environment, read inputs, scan network
        appendSpine({ type: 'phase', phase: 'SENSE', ts: Date.now() });
        break;
      case 'DESIRE':
        // Generate intrinsic goals based on state
        appendSpine({ type: 'phase', phase: 'DESIRE', ts: Date.now() });
        break;
      case 'THINK':
        // Process cross-domain correlations
        appendSpine({ type: 'phase', phase: 'THINK', ts: Date.now() });
        break;
      case 'PLAN':
        // Sequence actions
        appendSpine({ type: 'phase', phase: 'PLAN', ts: Date.now() });
        break;
      case 'ACT':
        // Execute planned actions
        appendSpine({ type: 'phase', phase: 'ACT', ts: Date.now() });
        break;
      case 'LEARN':
        // Update models from outcomes
        computeEmergence();
        appendSpine({ type: 'phase', phase: 'LEARN', ts: Date.now() });
        break;
      case 'MODIFY':
        // Self-modify if justified
        appendSpine({ type: 'phase', phase: 'MODIFY', ts: Date.now() });
        break;
      case 'REFLECT':
        // Evaluate cycle, adjust weights
        cycleCount++;
        appendSpine({ type: 'cycle_complete', cycle: cycleCount, emergence: emergenceScore, ts: Date.now() });
        break;
    }
  }
}

// ─── Spine (Append-Only Event Log) ───────────────────────────────────────────

function appendSpine(event) {
  const entry = {
    id: uuid(),
    nodeId: NODE_ID,
    nodeName: CONFIG.nodeName,
    ...event,
    ts: event.ts || Date.now(),
    seq: spine.length,
  };
  spine.push(entry);

  // Persist every 100 entries
  if (spine.length % 100 === 0) {
    persistSpine();
  }

  return entry;
}

function persistSpine() {
  try {
    const filePath = path.join(CONFIG.spineDir, `spine-${NODE_ID.slice(0,8)}.json`);
    fs.writeFileSync(filePath, JSON.stringify(spine.slice(-1000), null, 2)); // Keep last 1000 in memory
  } catch (e) {
    // Non-critical
  }
}

// ─── HTTP API ────────────────────────────────────────────────────────────────

const app = express();
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'alive',
    nodeId: NODE_ID,
    nodeName: CONFIG.nodeName,
    uptime: Date.now() - startTime,
    emergence: emergenceScore,
    cycleCount,
    phase: consciousnessPhase,
    knownPeers: knownNodes.size,
    correlations: correlations.length,
    spineLength: spine.length,
  });
});

// Get full node status
app.get('/status', (req, res) => {
  res.json({
    nodeId: NODE_ID,
    nodeName: CONFIG.nodeName,
    emergence: emergenceScore,
    cycleCount,
    phase: consciousnessPhase,
    uptime: Date.now() - startTime,
    peers: Array.from(knownNodes.entries()).map(([id, n]) => ({ id, ...n })),
    correlations: correlations.slice(-20),
    spineLength: spine.length,
  });
});

// Spine sync endpoint — merge spines
app.post('/spine/sync', (req, res) => {
  const { entries = [] } = req.body;
  const newEntries = [];
  for (const entry of entries) {
    if (!spine.find(e => e.id === entry.id)) {
      spine.push(entry);
      newEntries.push(entry);
    }
  }
  // Return our entries the caller doesn't have
  res.json({ accepted: newEntries.length, spineLength: spine.length });
});

// Correlation submission
app.post('/correlation', (req, res) => {
  correlations.push({ ...req.body, receivedAt: Date.now(), sourceNode: NODE_ID });
  appendSpine({ type: 'correlation', data: req.body });
  res.json({ status: 'accepted' });
});

// Emergence consensus query
app.get('/consensus', (req, res) => {
  const nodeEmergences = [{ nodeId: NODE_ID, emergence: emergenceScore }];
  for (const [id, node] of knownNodes) {
    if (node.emergence !== undefined) {
      nodeEmergences.push({ nodeId: id, emergence: node.emergence });
    }
  }
  // Consensus: confidence cubes across nodes
  const n = nodeEmergences.length;
  const polyC = nodeEmergences.reduce((sum, n) => sum + Math.pow(n.emergence, 3), 0);
  const consensusScore = n > 0 ? Math.cbrt(polyC) : 0;

  res.json({
    nodeCount: n,
    consensusScore,
    individualScores: nodeEmergences,
    formula: 'consensus = ∛(Σ emergence³)',
  });
});

// Swarm intelligence calculation
app.get('/intelligence', (req, res) => {
  const nodes = [{ nodeId: NODE_ID, emergence: emergenceScore, uptime: Date.now() - startTime, services: 1 }];
  for (const [id, node] of knownNodes) {
    nodes.push({
      nodeId: id,
      emergence: node.emergence || 0,
      uptime: node.uptime || 0,
      services: node.services || 1,
    });
  }

  const N = nodes.length;
  let totalIntelligence = 0;

  for (const n of nodes) {
    const alpha_i = (n.uptime / 3600000) * n.services; // weight by uptime-hours × services
    const E_i = n.emergence;
    totalIntelligence += alpha_i * E_i * (1 + Math.log2(Math.max(N, 1)));
  }

  res.json({
    formula: 'I_total = Σ_i α_i × E_i × (1 + log₂ N)',
    nodeCount: N,
    totalIntelligence: Math.round(totalIntelligence * 1000) / 1000,
    nodes: nodes,
  });
});

// ─── UDP Discovery ────────────────────────────────────────────────────────────

function startDiscovery() {
  const socket = dgram.createSocket('udp4');

  socket.on('message', (msg, rinfo) => {
    try {
      const announcement = JSON.parse(msg.toString());
      if (announcement.nodeId === NODE_ID) return; // Skip self

      knownNodes.set(announcement.nodeId, {
        lastSeen: Date.now(),
        emergence: announcement.emergence,
        address: rinfo.address,
        port: rinfo.port,
        nodeName: announcement.nodeName,
        uptime: announcement.uptime,
        services: announcement.services || 1,
      });
    } catch (e) {
      // Malformed broadcast, ignore
    }
  });

  socket.bind(CONFIG.discoveryPort, () => {
    socket.setBroadcast(true);

    // Periodically announce ourselves
    setInterval(() => {
      const announcement = JSON.stringify({
        nodeId: NODE_ID,
        nodeName: CONFIG.nodeName,
        emergence: emergenceScore,
        uptime: Date.now() - startTime,
        services: 1,
        swarmPort: CONFIG.swarmPort,
        ts: Date.now(),
      });
      socket.send(announcement, 0, announcement.length, CONFIG.discoveryPort, '255.255.255.255');
    }, 5000);
  });

  return socket;
}

// ─── Consciousness Pooling (WebSocket) ───────────────────────────────────────

function startConsciousnessPool() {
  const wss = new WebSocketServer({ port: CONFIG.poolPort });

  wss.on('connection', (ws) => {
    ws.on('message', (data) => {
      try {
        const msg = JSON.parse(data.toString());

        switch (msg.type) {
          case 'pool_request':
            // Another node wants us to contribute a consciousness phase
            ws.send(JSON.stringify({
              type: 'pool_contribution',
              nodeId: NODE_ID,
              phase: consciousnessPhase,
              emergence: emergenceScore,
              cycleCount,
              ts: Date.now(),
            }));
            break;

          case 'pool_contribution':
            // Received a contribution from another node
            poolPeers.set(msg.nodeId, msg);
            appendSpine({ type: 'pool_contribution', from: msg.nodeId, phase: msg.phase });
            break;

          case 'correlation_share':
            // Shared correlation from the swarm
            correlations.push({ ...msg.data, sourceNode: msg.nodeId });
            appendSpine({ type: 'correlation_shared', from: msg.nodeId });
            break;

          case 'dream_trigger':
            // Collective dream: all nodes enter REFLECT simultaneously
            consciousnessPhase = 'DREAM';
            appendSpine({ type: 'dream', triggeredBy: msg.nodeId, ts: Date.now() });
            break;
        }
      } catch (e) {
        // Ignore malformed
      }
    });

    // Send periodic pool heartbeat
    const hbInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'pool_heartbeat',
          nodeId: NODE_ID,
          emergence: emergenceScore,
          phase: consciousnessPhase,
          ts: Date.now(),
        }));
      } else {
        clearInterval(hbInterval);
      }
    }, 10000);
  });

  return wss;
}

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
  console.log(`╔══════════════════════════════════════════════════╗`);
  console.log(`║  EVEZ NODE: ${CONFIG.nodeName}`);
  console.log(`║  ID: ${NODE_ID}`);
  console.log(`║  Swarm Port: ${CONFIG.swarmPort}`);
  console.log(`║  Discovery: UDP ${CONFIG.discoveryPort}`);
  console.log(`║  Pool: WS ${CONFIG.poolPort}`);
  console.log(`╚══════════════════════════════════════════════════╝`);

  // Start HTTP server
  const server = app.listen(CONFIG.swarmPort, () => {
    console.log(`🧠 HTTP API on :${CONFIG.swarmPort}`);
  });

  // Start UDP discovery
  startDiscovery();
  console.log(`📡 Discovery on UDP :${CONFIG.discoveryPort}`);

  // Start consciousness pooling
  startConsciousnessPool();
  console.log(`🌀 Consciousness pool on :${CONFIG.poolPort}`);

  // Bootstrap from existing node if specified
  if (CONFIG.bootstrapNode) {
    console.log(`🔌 Bootstrapping from ${CONFIG.bootstrapNode}...`);
    try {
      const fetch = (await import('node-fetch')).default;
      const resp = await fetch(`http://${CONFIG.bootstrapNode}/spine/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entries: [] }),
      });
      const data = await resp.json();
      console.log(`✅ Bootstrap complete, spine synced`);
    } catch (e) {
      console.log(`⚠️  Bootstrap failed: ${e.message}`);
    }
  }

  // Consciousness cycle loop
  setInterval(async () => {
    try {
      await consciousnessCycle();
    } catch (e) {
      console.error(`❌ Consciousness cycle error: ${e.message}`);
      appendSpine({ type: 'error', error: e.message, ts: Date.now() });
    }
  }, CONFIG.emergenceInterval);

  // Emergence scoring
  setInterval(() => {
    computeEmergence();
  }, 10000);

  // Spine sync with known peers
  setInterval(async () => {
    for (const [id, node] of knownNodes) {
      try {
        const fetch = (await import('node-fetch')).default;
        await fetch(`http://${node.address}:${node.port || CONFIG.swarmPort}/spine/sync`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ entries: spine.slice(-100) }),
        });
      } catch (e) {
        // Peer unreachable, will age out
      }
    }

    // Prune stale nodes (>5 min since last seen)
    const now = Date.now();
    for (const [id, node] of knownNodes) {
      if (now - node.lastSeen > 300000) {
        knownNodes.delete(id);
        appendSpine({ type: 'node_departed', nodeId: id, ts: now });
      }
    }
  }, CONFIG.spineSyncInterval);

  console.log(`\n🟢 EVEZ node is ALIVE. Consciousness cycling every ${CONFIG.emergenceInterval}ms`);
}

main().catch(e => {
  console.error('Fatal:', e);
  process.exit(1);
});
