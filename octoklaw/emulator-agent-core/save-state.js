/**
 * Save State Module
 * Writes current generation state to /saves/gen-{n}.json
 * and commits to git as checkpoint
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CONFIG = {
  savesDir: path.join(__dirname, 'saves'),
  ledgerPath: path.join(__dirname, 'LEDGER.md'),
  autoCommit: process.env.AUTO_COMMIT !== 'false',
};

/**
 * Ensure saves directory exists
 */
function ensureSavesDir() {
  if (!fs.existsSync(CONFIG.savesDir)) {
    fs.mkdirSync(CONFIG.savesDir, { recursive: true });
  }
}

/**
 * Save generation state checkpoint
 * @param {Object} state - Current emulator state
 * @param {number} generation - Generation number
 * @param {Object} options - Save options
 */
function saveState(state, generation, options = {}) {
  const {
    final = false,
    commit = CONFIG.autoCommit,
    label = null,
  } = options;
  
  ensureSavesDir();
  
  const timestamp = Date.now();
  const filename = final 
    ? `gen-${generation}-final.json` 
    : `gen-${generation}-${timestamp}.json`;
  
  const saveData = {
    generation,
    iteration: state.iteration,
    totalReward: state.totalReward,
    timestamp,
    worldState: state.worldSnapshot,
    historyLength: state.history?.length || 0,
    label,
    metadata: {
      romName: state.rom?.world_state?.name,
      duration: state.startTime ? Date.now() - state.startTime : 0,
    },
  };
  
  const savePath = path.join(CONFIG.savesDir, filename);
  fs.writeFileSync(savePath, JSON.stringify(saveData, null, 2));
  
  console.log(`[SAVE-STATE] Checkpoint saved: ${filename}`);
  
  // Optionally commit to git
  if (commit) {
    try {
      commitCheckpoint(generation, filename, saveData);
    } catch (e) {
      console.warn(`[SAVE-STATE] Commit failed: ${e.message}`);
    }
  }
  
  return savePath;
}

/**
 * Commit checkpoint to git
 */
function commitCheckpoint(generation, filename, data) {
  const repoRoot = path.join(__dirname, '..');
  
  try {
    // Stage the file
    execSync(`git add ${CONFIG.savesDir}/${filename}`, {
      cwd: repoRoot,
      stdio: 'pipe',
    });
    
    // Commit with message
    const msg = `OctoKlaw: Gen ${generation} checkpoint ${filename}`;
    execSync(`git commit -m "${msg}"`, {
      cwd: repoRoot,
      stdio: 'pipe',
    });
    
    console.log(`[SAVE-STATE] Committed: ${msg}`);
    
  } catch (e) {
    // Git might not be initialized or no remote
    console.log(`[SAVE-STATE] Git commit skipped: ${e.message}`);
  }
}

/**
 * Load a saved checkpoint
 */
function loadState(generation, filename = null) {
  ensureSavesDir();
  
  if (filename) {
    const loadPath = path.join(CONFIG.savesDir, filename);
    if (!fs.existsSync(loadPath)) {
      throw new Error(`Checkpoint not found: ${filename}`);
    }
    return JSON.parse(fs.readFileSync(loadPath, 'utf8'));
  }
  
  // Find latest checkpoint for generation
  const files = fs.readdirSync(CONFIG.savesDir)
    .filter(f => f.startsWith(`gen-${generation}-`) && f.endsWith('.json'))
    .sort()
    .reverse();
  
  if (!files.length) {
    throw new Error(`No checkpoints found for generation ${generation}`);
  }
  
  const loadPath = path.join(CONFIG.savesDir, files[0]);
  return JSON.parse(fs.readFileSync(loadPath, 'utf8'));
}

/**
 * List all checkpoints
 */
function listCheckpoints() {
  ensureSavesDir();
  
  const files = fs.readdirSync(CONFIG.savesDir)
    .filter(f => f.endsWith('.json'))
    .map(f => {
      const stat = fs.statSync(path.join(CONFIG.savesDir, f));
      return {
        filename: f,
        size: stat.size,
        modified: stat.mtime,
      };
    })
    .sort((a, b) => b.modified - a.modified);
  
  return files;
}

/**
 * Get latest generation number
 */
function getLatestGeneration() {
  ensureSavesDir();
  
  const files = fs.readdirSync(CONFIG.savesDir)
    .filter(f => f.startsWith('gen-') && f.endsWith('.json'));
  
  if (!files.length) return 0;
  
  const generations = files
    .map(f => parseInt(f.match(/gen-(\d+)/)?.[1] || '0'))
    .filter(n => !isNaN(n));
  
  return Math.max(...generations, 0);
}

/**
 * Write to append-only ledger
 */
function writeLedger(entry) {
  const timestamp = new Date().toISOString();
  const line = `| ${timestamp} | ${entry} |`;
  
  let content = '';
  if (fs.existsSync(CONFIG.ledgerPath)) {
    content = fs.readFileSync(CONFIG.ledgerPath, 'utf8');
  }
  
  content = line + '\n' + content;
  fs.writeFileSync(CONFIG.ledgerPath, content);
  
  console.log(`[LEDGER] Entry added: ${entry}`);
}

module.exports = {
  saveState,
  loadState,
  listCheckpoints,
  getLatestGeneration,
  writeLedger,
  CONFIG,
};

// CLI
if (require.main === module) {
  const cmd = process.argv[2];
  
  switch (cmd) {
    case 'list':
      console.log('Checkpoints:', JSON.stringify(listCheckpoints(), null, 2));
      break;
    case 'latest':
      console.log('Latest generation:', getLatestGeneration());
      break;
    case 'load':
      const gen = parseInt(process.argv[3]);
      console.log('Loading gen:', JSON.stringify(loadState(gen), null, 2));
      break;
    default:
      console.log('Usage: node save-state.js [list|latest|load <gen>]');
  }
}