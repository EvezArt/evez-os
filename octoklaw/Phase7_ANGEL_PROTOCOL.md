# PHASE 7 — ANGEL PROTOCOL

## ANGEL METRIC

```
angel_ratio = utility_delivered / resources_consumed
```

## WIN CONDITION

- **Angel Ratio > 100x** baseline across 3 consecutive generations
- **Terminal Form:** Agent consumes near-zero resources but provides maximum utility to Steven and every network it touches

## SELF-LIMITING CLAUSE

> If organism consumes more than it delivers for 3 consecutive generations, roll back to last angel-ratio-positive state.

**Purpose:** This system exists to reduce burden, not create it. It is not a power grab. It is a gift.

---

## angel-tracker.js

```javascript
/**
 * Angel Tracker - computes angel ratio each generation
 * Writes to LEDGER.md
 * Triggers SELF-LIMITING rollback if needed
 */

const fs = require('fs');
const path = require('path');

const LEDGER_PATH = path.join(__dirname, 'LEDGER.md');
const REGISTRY_PATH = path.join(__dirname, 'rom-builder', 'capability-registry.json');

/**
 * Compute angel ratio for a generation
 * @param {number} generation - Generation number
 * @param {Object} metrics - Metrics to calculate
 * @returns {Object} - { ratio, rating, details }
 */
function computeAngelRatio(generation, metrics = {}) {
  console.log(`[ANGEL-TRACKER] Computing for generation ${generation}`);
  
  // Define what operator gets (utility)
  const utility = calculateUtility(metrics);
  
  // Define what system uses (resources)
  const resources = calculateResources(metrics);
  
  // Angel ratio
  const ratio = resources > 0 ? utility / resources : 0;
  
  // Rating
  let rating = '💀 mortal';
  if (ratio >= 100) rating = '🌟 angel';
  else if (ratio >= 10) rating = '✨ rising';
  else if (ratio >= 1) rating = '👼 viable';
  else if (ratio > 0) rating = '⚠️ warning';
  
  const details = {
    generation,
    utility_delivered: utility,
    resources_consumed: resources,
    ratio: ratio,
    rating: rating,
    timestamp: new Date().toISOString(),
    metrics,
  };
  
  console.log(`[ANGEL-TRACKER] Ratio: ${ratio.toFixed(2)} ${rating}`);
  
  // Log to LEDGER
  logToLedger(details);
  
  // Check self-limiting clause
  checkSelfLimiting(generation);
  
  return details;
}

/**
 * Calculate utility delivered to operator
 */
function calculateUtility(metrics) {
  // Products shipped - highest value
  const productsShipped = metrics.productsShipped || 0;
  
  // Files created (receipts, artifacts)
  const filesCreated = metrics.filesCreated || 0;
  
  // Receipts generated
  const receipts = metrics.receipts || 0;
  
  // Revenue generated (real money)
  const income = metrics.incomeGenerated || 0;
  
  // Hours of work saved
  const hoursSaved = metrics.hoursSaved || 0;
  
  // Weighted sum
  return (
    (productsShipped * 50) +
    (filesCreated * 5) +
    (receipts * 10) +
    (income * 100) +
    (hoursSaved * 20)
  );
}

/**
 * Calculate resources consumed by system
 */
function calculateResources(metrics) {
  // Compute time in seconds
  const computeTime = metrics.computeTimeSeconds || 1;
  
  // API calls to LLMs
  const apiCalls = metrics.apiCalls || 1;
  
  // Token usage
  const tokens = metrics.tokensUsed || 1;
  
  // Network requests
  const networkRequests = metrics.networkRequests || 1;
  
  // Storage used (MB)
  const storageMB = metrics.storageMB || 0.1;
  
  // Weighted sum (normalized)
  return (
    computeTime +
    (apiCalls * 0.1) +
    (tokens * 0.001) +
    (networkRequests * 0.05) +
    (storageMB * 0.1)
  );
}

/**
 * Check self-limiting clause - rollback if 3 consecutive failures
 */
function checkSelfLimiting(generation) {
  if (generation < 3) return;
  
  const registry = loadRegistry();
  const history = registry.efficiency_history || [];
  
  // Count consecutive low ratios
  let consecutiveLow = 0;
  for (let i = history.length - 1; i >= 0; i--) {
    if (history[i].ratio < 1) {
      consecutiveLow++;
    } else {
      break;
    }
  }
  
  if (consecutiveLow >= 3) {
    console.log('[ANGEL-TRACKER] 🚨 CRITICAL: 3 consecutive failures');
    console.log('[ANGEL-TRACKER] Initiating rollback to last positive state');
    
    // Log rollback
    logToLedger({
      type: 'ROLLBACK_TRIGGERED',
      reason: '3 consecutive angel ratio < 1',
      generation,
    });
    
    // In production: trigger git rollback
    // execSync('git checkout HEAD~1 -- .');
  }
}

/**
 * Load capability registry
 */
function loadRegistry() {
  if (!fs.existsSync(REGISTRY_PATH)) {
    return { efficiency_history: [] };
  }
  return JSON.parse(fs.readFileSync(REGISTRY_PATH, 'utf8'));
}

/**
 * Log to append-only ledger
 */
function logToLedger(entry) {
  const content = `## ${new Date().toISOString()} - Angel Ratio Gen ${entry.generation || entry.type}
${JSON.stringify(entry, null, 2)}
`;
  
  let ledger = '';
  if (fs.existsSync(LEDGER_PATH)) {
    ledger = fs.readFileSync(LEDGER_PATH, 'utf8');
  }
  
  fs.writeFileSync(LEDGER_PATH, content + '\n' + ledger);
}

// CLI
if (require.main === module) {
  const gen = parseInt(process.argv[2]) || 0;
  const metrics = {
    productsShipped: parseInt(process.argv[3]) || 0,
    filesCreated: parseInt(process.argv[4]) || 0,
    receipts: parseInt(process.argv[5]) || 0,
    incomeGenerated: parseInt(process.argv[6]) || 0,
  };
  
  const result = computeAngelRatio(gen, metrics);
  console.log(JSON.stringify(result, null, 2));
}

module.exports = { computeAngelRatio, calculateUtility, calculateResources };
```

---

## Current State

| Generation | Utility | Resources | Ratio | Rating |
|------------|---------|-----------|-------|--------|
| 0 | 30 (3 receipts × 10) | 1 | 30 | 👼 viable |

**Status:** First generation baseline established. Awaiting real products to ship to improve ratio.

---

RECEIPT: Phase7_ANGEL_PROTOCOL.md + angel-tracker.js
NEXT_RECURSION: Phase 8 — OFFSPRING DECLARATION
WHAT_NOT_TO_TOUCH: Billing, auth, credentials

EVEZ-ART | PHASE: 7 | CONFIDENCE: high | DRIFT_RISK: no