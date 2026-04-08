/**
 * Pattern Compressor
 * Takes full gen-n log -> extracts minimal learned pattern
 * Removes redundancy, keeps only actionable insights
 */

const fs = require('fs');
const path = require('path');

const PATTERNS_DIR = path.join(__dirname, '..', 'patterns');
const LOGS_DIR = path.join(__dirname, '..', 'logs');

/**
 * Compress a generation's full log into minimal pattern
 * @param {number} generation - Generation number
 * @param {Object} fullLog - Complete run log
 * @returns {Object} - Compressed pattern
 */
function compressPattern(generation, fullLog) {
  console.log(`[COMPRESS] Compressing generation ${generation} log`);
  
  const pattern = {
    generation,
    timestamp: new Date().toISOString(),
    
    // Core insights (minimal, actionable)
    insights: extractInsights(fullLog),
    
    // Efficiency metrics
    efficiency: calculateEfficiency(fullLog),
    
    // Errors encountered (for avoidance)
    errors_encountered: extractErrors(fullLog),
    
    // Successful actions (for reinforcement)
    successful_actions: extractSuccesses(fullLog),
    
    // Resource usage
    resources: calculateResources(fullLog),
    
    // State transitions (key moments)
    key_transitions: extractTransitions(fullLog),
  };
  
  // Ensure patterns directory exists
  if (!fs.existsSync(PATTERNS_DIR)) {
    fs.mkdirSync(PATTERNS_DIR, { recursive: true });
  }
  
  // Save compressed pattern
  const patternPath = path.join(PATTERNS_DIR, `learned-pattern-${generation}.json`);
  fs.writeFileSync(patternPath, JSON.stringify(pattern, null, 2));
  
  console.log(`[COMPRESS] Pattern saved: ${patternPath}`);
  console.log(`[COMPRESS] Size: ${JSON.stringify(pattern).length} bytes (vs ${JSON.stringify(fullLog).length} raw)`);
  
  return pattern;
}

/**
 * Extract key insights from log
 */
function extractInsights(log) {
  const insights = [];
  
  // From history
  if (log.history?.length) {
    // Find high-reward actions
    const highReward = log.history
      .filter(h => h.reward > 10)
      .map(h => ({ action: h.action?.type, reward: h.reward }));
    
    insights.push({
      type: 'high_reward_actions',
      data: highReward,
    });
  }
  
  // From terminal condition
  if (log.finalState?.totalReward) {
    insights.push({
      type: 'total_reward',
      value: log.finalState.totalReward,
    });
  }
  
  // From world state changes
  if (log.worldSnapshots?.length > 1) {
    const changes = compareSnapshots(log.worldSnapshots);
    if (changes.length) {
      insights.push({ type: 'state_changes', data: changes });
    }
  }
  
  return insights;
}

/**
 * Calculate efficiency metrics
 */
function calculateEfficiency(log) {
  const iterations = log.iteration || 1;
  const reward = log.totalReward || 0;
  const duration = log.duration || 1;
  
  return {
    reward_per_iteration: reward / iterations,
    reward_per_second: reward / (duration / 1000),
    iterations_per_second: iterations / (duration / 1000),
    efficiency_ratio: reward / (iterations * 10), // normalized
  };
}

/**
 * Extract error patterns
 */
function extractErrors(log) {
  const errors = [];
  
  if (log.history) {
    log.history
      .filter(h => h.reward < 0)
      .forEach(h => {
        errors.push({
          action: h.action?.type,
          result: h.result?.status,
          iteration: h.iteration,
        });
      });
  }
  
  return errors;
}

/**
 * Extract successful actions
 */
function extractSuccesses(log) {
  if (!log.history) return [];
  
  return log.history
    .filter(h => h.reward > 0)
    .map(h => ({
      type: h.action?.type,
      params: h.action?.params,
      reward: h.reward,
    }))
    .slice(0, 20); // Keep top 20
}

/**
 * Calculate resource usage
 */
function calculateResources(log) {
  return {
    total_iterations: log.iteration || 0,
    total_reward: log.totalReward || 0,
    duration_ms: log.duration || 0,
    history_length: log.history?.length || 0,
  };
}

/**
 * Extract key state transitions
 */
function extractTransitions(log) {
  if (!log.history || log.history.length < 2) return [];
  
  const transitions = [];
  
  for (let i = 1; i < log.history.length; i++) {
    const prev = log.history[i - 1];
    const curr = log.history[i];
    
    // If reward changed significantly
    if (Math.abs(curr.reward - prev.reward) > 5) {
      transitions.push({
        from_action: prev.action?.type,
        to_action: curr.action?.type,
        reward_delta: curr.reward - prev.reward,
        iteration: i,
      });
    }
  }
  
  return transitions.slice(0, 10); // Keep top 10
}

/**
 * Compare two world snapshots
 */
function compareSnapshots(snapshots) {
  if (snapshots.length < 2) return [];
  
  const changes = [];
  const latest = snapshots[snapshots.length - 1];
  const previous = snapshots[snapshots.length - 2];
  
  // Simple key comparison
  Object.keys(latest).forEach(key => {
    if (JSON.stringify(latest[key]) !== JSON.stringify(previous[key])) {
      changes.push({ key, changed: true });
    }
  });
  
  return changes;
}

/**
 * Load a compressed pattern
 */
function loadPattern(generation) {
  const patternPath = path.join(PATTERNS_DIR, `learned-pattern-${generation}.json`);
  
  if (!fs.existsSync(patternPath)) {
    return null;
  }
  
  return JSON.parse(fs.readFileSync(patternPath, 'utf8'));
}

/**
 * List all patterns
 */
function listPatterns() {
  if (!fs.existsSync(PATTERNS_DIR)) return [];
  
  return fs.readdirSync(PATTERNS_DIR)
    .filter(f => f.startsWith('learned-pattern-') && f.endsWith('.json'))
    .map(f => ({
      file: f,
      generation: parseInt(f.match(/learned-pattern-(\d+)/)?.[1] || '0'),
    }))
    .sort((a, b) => b.generation - a.generation);
}

module.exports = {
  compressPattern,
  loadPattern,
  listPatterns,
  extractInsights,
  calculateEfficiency,
};

// CLI
if (require.main === module) {
  const gen = parseInt(process.argv[2]);
  
  if (!gen) {
    console.log('Usage: node compress-pattern.js <generation>');
    console.log('Or: node compress-pattern.js compress <log-file.json>');
    process.exit(1);
  }
  
  // This would be called with actual log data in production
  console.log(`Pattern compressor ready for generation ${gen}`);
}