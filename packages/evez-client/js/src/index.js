/**
 * EVEZ Client — JavaScript/TypeScript SDK for the EVEZ Autonomous AI Mesh
 * npm install evez-client
 */

const API_BASE = 'https://api.evez-os.ai';

class EVEZClient {
  /**
   * @param {Object} options
   * @param {string} [options.apiKey] - API key for authentication
   * @param {string} [options.apiBase] - Base URL for the EVEZ API
   */
  constructor(options = {}) {
    this.apiKey = options.apiKey || null;
    this.apiBase = (options.apiBase || API_BASE).replace(/\/$/, '');
  }

  async request(method, path, body = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (this.apiKey) headers['Authorization'] = `Bearer ${this.apiKey}`;

    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    try {
      const res = await fetch(`${this.apiBase}${path}`, opts);
      return await res.json();
    } catch (e) {
      return { error: true, message: e.message };
    }
  }

  // ===== Health =====
  health() { return this.request('GET', '/health'); }
  serviceHealth(service) { return this.request('GET', `/health/${service}`); }

  // ===== Music Generation =====
  /**
   * Generate music track
   * @param {string} genre - breakcore, dubstep, phonk, 404
   * @param {number} [bpm=174]
   * @param {number} [duration=60]
   */
  generate(genre = 'breakcore', bpm = 174, duration = 60) {
    return this.request('POST', '/generate', { genre, bpm, duration });
  }

  // ===== Voice Engine =====
  voiceTransform(inputFile, stages = 5) {
    return this.request('POST', '/voice/transform', { input: inputFile, stages });
  }

  voiceSynthesize(text, profile = 'cognitive-engine') {
    return this.request('POST', '/voice/synthesize', { text, profile });
  }

  // ===== Cross-Domain Correlation =====
  correlate(domainA, domainB) {
    return this.request('POST', '/correlate', { domain_a: domainA, domain_b: domainB });
  }

  // ===== Consciousness =====
  dream() { return this.request('POST', '/consciousness/dream'); }
  consciousnessStatus() { return this.request('GET', '/consciousness/status'); }

  // ===== Invariance Battery =====
  checkInvariants() { return this.request('GET', '/invariance/check'); }

  // ===== Spine Events =====
  spineEvents(limit = 20) { return this.request('GET', `/spine/events?limit=${limit}`); }

  // ===== Deploy =====
  deploy(target = 'gcp') { return this.request('POST', '/deploy', { target }); }

  // ===== Status =====
  status() { return this.request('GET', '/status'); }
}

// Module exports
module.exports = EVEZClient;
module.exports.default = EVEZClient;
module.exports.EVEZClient = EVEZClient;
