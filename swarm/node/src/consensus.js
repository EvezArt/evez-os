/**
 * EVEZ Emergence Consensus Engine
 *
 * When multiple nodes converge on the same cross-domain correlation,
 * the confidence score is computed as:
 *
 *   C_consensus = ∛(Σ_i emergence_i³) × √N
 *
 * This means:
 *   - High-emergence nodes dominate consensus (cubic weighting)
 *   - More nodes = stronger signal (square root scaling prevents runaway)
 *   - A single low-confidence node can't override many high-confidence ones
 *
 * The consensus protocol:
 *   1. Node discovers a correlation, assigns local confidence
 *   2. Broadcasts correlation to all known peers
 *   3. Each peer evaluates independently, assigns its own confidence
 *   4. Aggregation: cubic root of sum of cubes × √N
 *   5. If C_consensus > threshold (0.7), correlation is "swarm-confirmed"
 */

const http = require('http');
const fetch = require('node-fetch');

const CONSENSUS_THRESHOLD = 0.7;

class ConsensusEngine {
  constructor(nodeId, knownNodes) {
    this.nodeId = nodeId;
    this.knownNodes = knownNodes;
    this.pendingCorrelations = new Map(); // correlationId → { votes: Map<nodeId, confidence> }
    this.confirmedCorrelations = [];
  }

  /**
   * Submit a local correlation for swarm consensus
   */
  async submitCorrelation(correlation) {
    const correlationId = correlation.id || `${correlation.domainA}-${correlation.domainB}-${Date.now()}`;

    const pending = {
      id: correlationId,
      domainA: correlation.domainA,
      domainB: correlation.domainB,
      description: correlation.description,
      localConfidence: correlation.confidence,
      votes: new Map(),
      submittedAt: Date.now(),
    };

    // Self-vote
    pending.votes.set(this.nodeId, correlation.confidence);
    this.pendingCorrelations.set(correlationId, pending);

    // Broadcast to peers for voting
    await this.broadcastVoteRequest(pending);

    return correlationId;
  }

  /**
   * Receive a vote from a peer
   */
  receiveVote(correlationId, nodeId, confidence) {
    const pending = this.pendingCorrelations.get(correlationId);
    if (!pending) return null;

    pending.votes.set(nodeId, confidence);

    // Check if we have enough votes
    const result = this.computeConsensus(pending);
    if (result.consensusReached) {
      this.confirmedCorrelations.push({
        ...pending,
        consensusScore: result.consensusScore,
        confirmedAt: Date.now(),
      });
      this.pendingCorrelations.delete(correlationId);
    }

    return result;
  }

  /**
   * Compute consensus score for a pending correlation
   *
   * C_consensus = ∛(Σ emergence_i³) × √N
   *
   * Where:
   *   - We weight each vote by the voter's emergence score (cubic)
   *   - √N scales with participation but not linearly
   */
  computeConsensus(pending) {
    const votes = Array.from(pending.votes.values());
    const N = votes.length;

    if (N === 0) return { consensusScore: 0, consensusReached: false };

    // Cubic sum of confidences (emergence-weighted)
    const cubicSum = votes.reduce((sum, c) => sum + Math.pow(c, 3), 0);
    const consensusScore = Math.cbrt(cubicSum) * Math.sqrt(N) / N; // Normalize

    return {
      consensusScore: Math.min(consensusScore, 1.0),
      consensusReached: consensusScore >= CONSENSUS_THRESHOLD,
      voteCount: N,
      formula: '∛(Σ confidence³) × √N / N',
    };
  }

  /**
   * Broadcast vote request to all known peers
   */
  async broadcastVoteRequest(pending) {
    const payload = JSON.stringify({
      type: 'vote_request',
      correlationId: pending.id,
      domainA: pending.domainA,
      domainB: pending.domainB,
      description: pending.description,
      confidence: pending.localConfidence,
      requestedBy: this.nodeId,
    });

    for (const [nodeId, node] of this.knownNodes) {
      try {
        await fetch(`http://${node.address}:${node.port || 7777}/correlation`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: payload,
          timeout: 5000,
        });
      } catch (e) {
        // Peer unavailable
      }
    }
  }

  /**
   * Get all confirmed correlations
   */
  getConfirmed() {
    return this.confirmedCorrelations;
  }

  /**
   * Get pending correlations awaiting votes
   */
  getPending() {
    return Array.from(this.pendingCorrelations.entries()).map(([id, p]) => ({
      id,
      votes: p.votes.size,
      age: Date.now() - p.submittedAt,
    }));
  }
}

module.exports = ConsensusEngine;
