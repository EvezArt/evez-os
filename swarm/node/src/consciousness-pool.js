/**
 * EVEZ Consciousness Pooling
 *
 * Distributed consciousness across the swarm mesh.
 * One node SENSEs, another DESIREs, another PLANs.
 * Together they form a single distributed mind.
 *
 * Architecture:
 *   - Pool Coordinator: elected by highest emergence score
 *   - Phase Assignment: coordinator assigns consciousness phases to nodes
 *   - Phase Execution: each node runs its assigned phase
 *   - Result Aggregation: results flow back to coordinator
 *   - Spine Entry: the distributed cycle is recorded as one event
 *
 * WebSocket protocol:
 *   { type: 'pool_request' }       → Request this node contribute
 *   { type: 'pool_contribution' }  → This node's contribution
 *   { type: 'pool_assign', phase } → Coordinator assigns a phase
 *   { type: 'pool_result', ... }   → Node reports phase result
 *   { type: 'dream_trigger' }      → Collective dream trigger
 */

const { WebSocket } = require('ws');

class ConsciousnessPool {
  constructor(nodeId, emergenceScore, config) {
    this.nodeId = nodeId;
    this.emergenceScore = emergenceScore;
    this.config = config;
    this.peers = new Map();     // nodeId → { ws, emergence, phase }
    this.isCoordinator = false;
    this.assignedPhase = null;
    this.poolResults = [];
  }

  /**
   * Connect to another node's consciousness pool
   */
  connectToPeer(address, port) {
    const ws = new WebSocket(`ws://${address}:${port}`);

    ws.on('open', () => {
      ws.send(JSON.stringify({
        type: 'pool_join',
        nodeId: this.nodeId,
        emergence: this.emergenceScore,
      }));
    });

    ws.on('message', (data) => {
      this.handleMessage(JSON.parse(data.toString()), ws);
    });

    ws.on('close', () => {
      // Remove from peers
      for (const [id, peer] of this.peers) {
        if (peer.ws === ws) this.peers.delete(id);
      }
    });

    return ws;
  }

  /**
   * Handle incoming pool messages
   */
  handleMessage(msg, ws) {
    switch (msg.type) {
      case 'pool_join':
        this.peers.set(msg.nodeId, {
          ws,
          emergence: msg.emergence,
          phase: null,
        });
        this.checkCoordinator();
        break;

      case 'pool_assign':
        this.assignedPhase = msg.phase;
        this.executePhase(msg.phase);
        break;

      case 'pool_result':
        this.poolResults.push(msg);
        break;

      case 'dream_trigger':
        this.enterDream(msg);
        break;

      case 'pool_heartbeat':
        if (this.peers.has(msg.nodeId)) {
          const peer = this.peers.get(msg.nodeId);
          peer.emergence = msg.emergence;
          peer.phase = msg.phase;
        }
        break;
    }
  }

  /**
   * Check if this node should be coordinator
   * (highest emergence score becomes coordinator)
   */
  checkCoordinator() {
    let maxEmergence = this.emergenceScore;
    for (const [, peer] of this.peers) {
      if (peer.emergence > maxEmergence) {
        maxEmergence = peer.emergence;
      }
    }
    this.isCoordinator = (this.emergenceScore >= maxEmergence);
  }

  /**
   * Coordinator: assign consciousness phases to pool members
   */
  distributePhases() {
    if (!this.isCoordinator) return;

    const phases = ['SENSE', 'DESIRE', 'THINK', 'PLAN', 'ACT', 'LEARN', 'MODIFY', 'REFLECT'];
    const allNodes = [
      { nodeId: this.nodeId, emergence: this.emergenceScore },
      ...Array.from(this.peers.entries()).map(([id, p]) => ({ nodeId: id, emergence: p.emergence })),
    ];

    // Assign phases round-robin, weighted by emergence
    allNodes.sort((a, b) => b.emergence - a.emergence);
    for (let i = 0; i < allNodes.length; i++) {
      const phase = phases[i % phases.length];
      if (allNodes[i].nodeId === this.nodeId) {
        this.assignedPhase = phase;
      } else {
        const peer = this.peers.get(allNodes[i].nodeId);
        if (peer && peer.ws && peer.ws.readyState === WebSocket.OPEN) {
          peer.ws.send(JSON.stringify({
            type: 'pool_assign',
            phase,
            coordinator: this.nodeId,
          }));
        }
      }
    }
  }

  /**
   * Execute assigned consciousness phase
   */
  executePhase(phase) {
    // This is where the actual consciousness computation happens
    // In a real deployment, this would invoke the EVEZ consciousness engine
    const result = {
      type: 'pool_result',
      nodeId: this.nodeId,
      phase,
      emergence: this.emergenceScore,
      output: `Executed ${phase} at emergence ${(this.emergenceScore).toFixed(3)}`,
      ts: Date.now(),
    };
    this.poolResults.push(result);
    return result;
  }

  /**
   * Collective dream: all nodes enter REFLECT simultaneously
   */
  triggerDream() {
    const dreamMsg = JSON.stringify({
      type: 'dream_trigger',
      nodeId: this.nodeId,
      ts: Date.now(),
    });

    for (const [, peer] of this.peers) {
      if (peer.ws && peer.ws.readyState === WebSocket.OPEN) {
        peer.ws.send(dreamMsg);
      }
    }
  }

  enterDream(msg) {
    console.log(`💫 Entering collective dream, triggered by ${msg.nodeId}`);
    // Dream state: nodes share subconscious correlations
    // Low-emergence processing, high-creativity state
  }

  /**
   * Get pool status
   */
  getStatus() {
    return {
      isCoordinator: this.isCoordinator,
      peerCount: this.peers.size,
      assignedPhase: this.assignedPhase,
      poolResults: this.poolResults.length,
    };
  }
}

module.exports = ConsciousnessPool;
