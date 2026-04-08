/**
 * Angel Ratio Calculator
 * Computes utility_delivered / resources_consumed per generation
 * Logs to LEDGER.md
 */

const fs = require('fs');
const path = require('path');

const LEDGER_PATH = path.join(__dirname, 'LEDGER.md');
const REGISTRY_PATH = path.join(__dirname, 'rom-builder', 'capability-registry.json');

/**
 * Calculate angel ratio for a generation
 * @param {number} generation - Generation number
 * @param {Object} metrics - Generation metrics
 * @returns {Object} - { ratio: number, rating: string, details: {} }
 */
function computeAngelRatio(generation, metrics = {}) {
  console.log(`[ANGEL] Computing ratio for generation ${generation}`);
  
  // Define utility delivered (what the operator gets)
  const utilityDelivered = calculateUtility(metrics);
  
  // Define resources consumed (what the system uses)
  const resourcesConsumed = calculateResources(metrics);
  
  // Angel ratio: utility / resources
  const ratio = resourcesConsumed > 0 
    ? utilityDelivered / resourcesConsumed 
    : 0;
  
  // Rating
  let rating = ' mortal';
  if (ratio > 100) rating = ' 🌟 angel';
  else if (ratio > 10) rating = ' ✨ rising';
  else if (ratio > 1) rating = ' 👼 viable';
  else if (ratio > 0) rating = ' ⚠️ warning';
  else rating = ' 💀 critical';
  
  const details = {
    generation,
    utility_delivered: utilityDelivered,
    resources_consumed: resourcesConsumed,
    ratio: ratio,
    rating: rating.trim(),
    timestamp: new Date().toISOString(),
  };
  
  console.log(`[ANGEL] Ratio: ${ratio.toFixed(2)}${rating}`);
  
  // Log to LEDGER
  logAngelRatio(details);
  
  // Check self-limiting clause
  if (ratio < 1 && generation > 0) {
    triggerRollback(generation, details);
  }
  
  return details;
}

/**
 * Calculate utility delivered to operator
 */
function calculateUtility(metrics) {
  // Products shipped
  const productsShipped = metrics.productsShipped || 0;
  
  // Files created
  const filesCreated = metrics.filesCreated || 0;
  
  // Receipts generated
  const receipts = metrics.receipts || 0;
  
  // Income generated
  const income = metrics.incomeGenerated || 0;
  
  return (productsShipped * 50) + (filesCreated * 5) + (receipts * 10) + (income * 100);
}

/**
 * Calculate resources consumed
 */
function calculateResources(metrics) {
  // Compute time (in seconds)
  const computeTime = metrics.computeTime || 1;
  
  // API calls
  const apiCalls = metrics.apiCalls || 1;
  
  // Tokens used
  const tokens = metrics.tokens || 1;
  
  // Network requests
  const networkRequests = metrics.networkRequests || 1;
  
  return computeTime + (apiCalls * 0.1) + (tokens * 0.001) + (networkRequests * 0.05);
}

/**
 * Log angel ratio to LEDGER
 */
function logAngelRatio(details) {
  const entry = `
## ${details.timestamp} - Angel Ratio Gen ${details.generation}
- **Ratio**: ${details.ratio.toFixed(2)} ${details.rating}
- Utility Delivered: ${details.utility_delivered.toFixed(2)}
- Resources Consumed: ${details.resources_consumed.toFixed(4)}
`;

  let ledger = '';
  if (fs.existsSync(LEDGER_PATH)) {
    ledger = fs.readFileSync(LEDGER_PATH, 'utf8');
  }
  
  ledger = entry + '\n' + ledger;
  fs.writeFileSync(LEDGER_PATH, ledger);
  
  console.log(`[ANGEL] Logged to LEDGER`);
}

/**
 * Trigger rollback if ratio < 1 for 3 consecutive generations
 */
function triggerRollback(generation, details) {
  console.log(`[ANGEL] ⚠️ Ratio below 1 - checking for consecutive failures`);
  
  const registry = JSON.parse(fs.readFileSync(REGISTRY_PATH, 'utf8'));
  const history = registry.efficiency_history || [];
  
  // Count consecutive low ratios
  let consecutiveFailures = 0;
  for (let i = history.length - 1; i >= 0; i--) {
    if (history[i].ratio < 1) {
      consecutiveFailures++;
    } else {
      break;
    }
  }
  
  if (consecutiveFailures >= 3) {
    console.log(`[ANGEL] 🚨 CRITICAL: 3 consecutive failures - initiating rollback`);
    // In production: trigger git rollback
    logToLedger('ROLLBACK', { reason: '3 consecutive angel ratio failures' });
  }
}

/**
 * Log message to LEDGER
 */
function logToLedger(type, data) {
  const entry = `\n## ${new Date().toISOString()} - ${type}\n${JSON.stringify(data, null, 2)}\n`;
  
  let ledger = '';
  if (fs.existsSync(LEDGER_PATH)) {
    ledger = fs.readFileSync(LEDGER_PATH, 'utf8');
  }
  
  ledger = entry + '\n' + ledger;
  fs.writeFileSync(LEDGER_PATH, ledger);
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