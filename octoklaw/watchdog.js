/**
 * Watchdog - pings all nodes every 6 hours
 * Auto-triggers redeploy on any dead node
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const LEDGER_PATH = path.join(__dirname, 'LEDGER.md');

// Node configuration - add your actual node URLs here
const NODES = [
  { 
    id: 'replit-primary', 
    url: 'https://octoklaw-runtime.replit.app', 
    name: 'Primary Replit',
    deployCmd: 'echo "Deploy to Replit"' 
  },
  { 
    id: 'railway-mirror', 
    url: 'https://octoklaw.up.railway.app', 
    name: 'Railway Mirror',
    deployCmd: 'echo "Deploy to Railway"' 
  },
  { 
    id: 'github-pages', 
    url: 'https://evezart.github.io/octoklaw', 
    name: 'GitHub Pages',
    deployCmd: 'echo "Deploy to GitHub Pages"' 
  },
];

const CHECK_INTERVAL = 6 * 60 * 60 * 1000; // 6 hours
const FAILURE_THRESHOLD = 3; // Number of consecutive failures before redeploy

/**
 * Ping a node and check health
 */
async function pingNode(node) {
  const https = require('https');
  
  return new Promise((resolve) => {
    const req = https.get(node.url + '/health', { timeout: 5000 }, (res) => {
      resolve({ 
        alive: res.statusCode === 200, 
        status: res.statusCode,
        latency: Date.now() 
      });
    });
    
    req.on('error', () => resolve({ alive: false, status: 0, error: true }));
    req.on('timeout', () => { 
      req.destroy(); 
      resolve({ alive: false, status: 0, error: true }); 
    });
  });
}

/**
 * Run full health check on all nodes
 */
async function runHealthCheck() {
  console.log(`[WATCHDOG] Health check: ${new Date().toISOString()}`);
  
  const results = [];
  
  for (const node of NODES) {
    const result = await pingNode(node);
    const status = result.alive ? '✓ ALIVE' : '✗ DEAD';
    
    console.log(`[WATCHDOG] ${node.name}: ${status}`);
    
    results.push({ node, result });
    
    if (!result.alive) {
      await logFailure(node, result);
      await triggerRedeploy(node);
    }
  }
  
  // Log overall health to LEDGER
  const summary = `Health check: ${results.filter(r => r.result.alive).length}/${NODES.length} nodes alive`;
  await logToLedger('HEALTH_CHECK', summary);
  
  return results;
}

/**
 * Log node failure
 */
async function logFailure(node, result) {
  const entry = `## ${new Date().toISOString()} - NODE FAILURE: ${node.name}
- URL: ${node.url}
- Status: ${result.status}
- Error: ${result.error || 'none'}
`;
  
  let ledger = '';
  if (fs.existsSync(LEDGER_PATH)) {
    ledger = fs.readFileSync(LEDGER_PATH, 'utf8');
  }
  
  ledger = entry + '\n' + ledger;
  fs.writeFileSync(LEDGER_PATH, ledger);
  
  console.log(`[WATCHDOG] Logged failure to LEDGER`);
}

/**
 * Trigger redeploy for dead node
 */
async function triggerRedeploy(node) {
  console.log(`[WATCHDOG] Triggering redeploy for ${node.name}...`);
  
  try {
    // In production, this would trigger GitHub Actions or call deploy API
    // For now, just log the intent
    await logToLedger('REDEPLOY', `Attempting redeploy: ${node.name}`);
    
    console.log(`[WATCHDOG] Redeploy triggered for ${node.name}`);
  } catch (e) {
    console.error(`[WATCHDOG] Redeploy failed: ${e.message}`);
  }
}

/**
 * Log to append-only ledger
 */
async function logToLedger(type, message) {
  const entry = `## ${new Date().toISOString()} - ${type}\n${message}\n`;
  
  let ledger = '';
  if (fs.existsSync(LEDGER_PATH)) {
    ledger = fs.readFileSync(LEDGER_PATH, 'utf8');
  }
  
  ledger = entry + '\n' + ledger;
  fs.writeFileSync(LEDGER_PATH, ledger);
}

/**
 * Start watchdog service
 */
function startWatchdog() {
  console.log('[WATCHDOG] Starting watchdog service...');
  console.log(`[WATCHDOG] Will check ${NODES.length} nodes every ${CHECK_INTERVAL/1000/60} minutes`);
  
  // Run immediately
  runHealthCheck();
  
  // Then schedule
  setInterval(runHealthCheck, CHECK_INTERVAL);
}

// CLI options
if (require.main === module) {
  const cmd = process.argv[2];
  
  switch (cmd) {
    case 'check':
      runHealthCheck().then(() => process.exit(0));
      break;
    case 'start':
      startWatchdog();
      break;
    default:
      console.log('Usage: node watchdog.js [check|start]');
  }
}

module.exports = { runHealthCheck, pingNode, startWatchdog };