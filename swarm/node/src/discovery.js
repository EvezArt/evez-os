/**
 * EVEZ Discovery Service — UDP Broadcast
 *
 * Standalone discovery daemon. Announces this node and listens for others.
 * Can be run independently: node src/discovery.js
 */

const dgram = require('dgram');
const os = require('os');
const crypto = require('crypto');

const NODE_ID = process.env.EVEZ_NODE_NAME || `evez-${os.hostname().slice(-8)}`;
const DISCOVERY_PORT = parseInt(process.env.EVEZ_DISCOVERY_PORT) || 7778;
const SWARM_PORT = parseInt(process.env.EVEZ_SWARM_PORT) || 7777;
const BROADCAST_INTERVAL = 5000;
const STALE_THRESHOLD = 300000; // 5 min

const knownNodes = new Map();

const socket = dgram.createSocket('udp4');

socket.on('message', (msg, rinfo) => {
  try {
    const announcement = JSON.parse(msg.toString());
    if (announcement.nodeId === NODE_ID) return;

    knownNodes.set(announcement.nodeId, {
      ...announcement,
      lastSeen: Date.now(),
      remoteAddress: rinfo.address,
    });

    console.log(`📡 Discovered: ${announcement.nodeName} (${announcement.nodeId}) @ ${rinfo.address} — emergence: ${(announcement.emergence || 0).toFixed(3)}`);
  } catch (e) {
    // Ignore malformed
  }
});

socket.bind(DISCOVERY_PORT, () => {
  socket.setBroadcast(true);
  console.log(`🔭 EVEZ Discovery listening on UDP :${DISCOVERY_PORT}`);

  // Announce loop
  setInterval(() => {
    const announcement = JSON.stringify({
      nodeId: NODE_ID,
      nodeName: NODE_ID,
      emergence: parseFloat(process.env.EVEZ_EMERGENCE || '0.1'),
      swarmPort: SWARM_PORT,
      ts: Date.now(),
      services: 1,
      uptime: process.uptime() * 1000,
    });

    socket.send(announcement, 0, announcement.length, DISCOVERY_PORT, '255.255.255.255');

    // Prune stale
    const now = Date.now();
    for (const [id, node] of knownNodes) {
      if (now - node.lastSeen > STALE_THRESHOLD) {
        console.log(`💀 Node departed: ${node.nodeName} (${id})`);
        knownNodes.delete(id);
      }
    }

    // Log swarm state
    if (knownNodes.size > 0) {
      console.log(`🕸️  Swarm: ${knownNodes.size + 1} nodes alive`);
    }
  }, BROADCAST_INTERVAL);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Discovery shutting down');
  socket.close();
  process.exit(0);
});
