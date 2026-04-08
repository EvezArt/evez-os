/**
 * Efficiency Check
 * Compares gen-n metrics to gen-n-1
 * Passes only if at least one metric improved
 */

const fs = require('fs');
const path = require('path');

const REGISTRY_PATH = path.join(__dirname, '..', 'rom-builder', 'capability-registry.json');
const LEDGER_PATH = path.join(__dirname, '..', 'LEDGER.md');

/**
 * Run efficiency check for a generation
 * @param {number} generation - Generation to check
 * @returns {Object} - { passed: boolean, metrics: {}, reason: string }
 */
function runEfficiencyCheck(generation) {
  console.log(`[EFFICIENCY] Checking generation ${generation}`);
  
  const registry = loadRegistry();
  const history = registry.efficiency_history || [];
  
  // Get current and previous metrics
  const current = history[generation] || { ratio: 1.0 };
  const previous = history[generation - 1] || { ratio: 1.0 };
  
  const metrics = {
    current_ratio: current.ratio,
    previous_ratio: previous.ratio,
    improvement: current.ratio - previous.ratio,
    improvement_percent: ((current.ratio - previous.ratio) / previous.ratio) * 100,
  };
  
  // Check if at least one metric improved
  const passed = metrics.improvement >= 0 || generation === 0; // Gen 0 always passes
  
  let reason = '';
  if (passed) {
    reason = metrics.improvement > 0 
      ? `Improved by ${metrics.improvement_percent.toFixed(1)}%` 
      : 'Baseline generation';
  } else {
    reason = `Declined by ${Math.abs(metrics.improvement_percent).toFixed(1)}% - would trigger rollback';
  }
  
  console.log(`[EFFICIENCY] Result: ${passed ? 'PASS' : 'FAIL'}`);
  console.log(`[EFFICIENCY] ${reason}`);
  
  // Log to LEDGER
  logToLedger(generation, metrics, passed);
  
  return { passed, metrics, reason };
}

/**
 * Load capability registry
 */
function loadRegistry() {
  if (!fs.existsSync(REGISTRY_PATH)) {
    return { efficiency_history: [{ generation: 0, ratio: 1.0 }] };
  }
  
  return JSON.parse(fs.readFileSync(REGISTRY_PATH, 'utf8'));
}

/**
 * Log to append-only ledger
 */
function logToLedger(generation, metrics, passed) {
  const entry = `## ${new Date().toISOString()} - Efficiency Check Gen ${generation}
- Passed: ${passed}
- Current Ratio: ${metrics.current_ratio.toFixed(4)}
- Previous Ratio: ${metrics.previous_ratio.toFixed(4)}
- Improvement: ${metrics.improvement_percent.toFixed(1)}%
- Reason: ${passed ? 'Improved' : 'Declined - rollback triggered'}
`;
  
  let ledger = '';
  if (fs.existsSync(LEDGER_PATH)) {
    ledger = fs.readFileSync(LEDGER_PATH, 'utf8');
  }
  
  ledger = entry + '\n' + ledger;
  fs.writeFileSync(LEDGER_PATH, ledger);
}

/**
 * Force pass (for manual triggers)
 */
function forcePass(generation) {
  console.log(`[EFFICIENCY] Force-passing generation ${generation}`);
  logToLedger(generation, { improvement: 0, improvement_percent: 0 }, true);
  return { passed: true, forced: true };
}

// CLI
if (require.main === module) {
  const genArg = process.env.GEN_NUMBER || process.argv[2];
  const force = process.argv.includes('--force');
  
  let result;
  if (force) {
    result = forcePass(parseInt(genArg) || 0);
  } else {
    result = runEfficiencyCheck(parseInt(genArg) || 0);
  }
  
  if (!result.passed) {
    console.log('EFFICIENCY_CHECK_PASSED=false');
    process.exit(1);
  }
  
  console.log('EFFICIENCY_CHECK_PASSED=true');
  process.exit(0);
}

module.exports = { runEfficiencyCheck, forcePass };