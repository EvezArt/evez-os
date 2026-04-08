/**
 * OctoKlaw-ROM Emulator Core
 * JS loop that loads a ROM (JSON), runs a Playwright agent inside it,
 * logs every state-action-reward triple, saves state on every decision point
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  maxIterations: 1000,
  decisionSaveInterval: 10,
  stateDir: path.join(__dirname, 'saves'),
  ledgerPath: path.join(__dirname, 'LEDGER.md'),
  romDir: path.join(__dirname, 'roms'),
};

/**
 * Main emulator loop
 * @param {Object} rom - ROM JSON object
 * @param {Object} options - Runtime options
 */
async function emulatorLoop(rom, options = {}) {
  const startTime = Date.now();
  const generation = rom.generation_meta?.generation || 0;
  
  console.log(`[EMULATOR] Starting generation ${generation} - ${rom.world_state.name || 'unnamed'}`);
  
  // Initialize state
  let state = {
    rom: rom,
    iteration: 0,
    totalReward: 0,
    history: [],
    worldSnapshot: JSON.parse(JSON.stringify(rom.world_state)),
    startTime,
  };
  
  // Ensure save directory exists
  if (!fs.existsSync(CONFIG.stateDir)) {
    fs.mkdirSync(CONFIG.stateDir, { recursive: true });
  }
  
  // Launch browser agent
  const browserAgent = new BrowserAgent(options);
  await browserAgent.init();
  
  try {
    // Main decision loop
    while (!isTerminal(state, rom) && state.iteration < CONFIG.maxIterations) {
      // Get current world state from browser
      const currentWorldState = await browserAgent.readState();
      
      // Merge with ROM's baseline
      state.worldSnapshot = { ...rom.world_state, ...currentWorldState };
      
      // Select action from action space
      const action = selectAction(state, rom);
      
      // Execute action and get reward
      const { reward, newState } = await browserAgent.execute(action);
      
      // Log state-action-reward triple
      const triple = {
        iteration: state.iteration,
        state: state.worldSnapshot,
        action,
        reward,
        timestamp: Date.now(),
      };
      state.history.push(triple);
      
      // Update totals
      state.totalReward += reward;
      state.iteration++;
      
      // Save state at decision points
      if (state.iteration % CONFIG.decisionSaveInterval === 0) {
        await saveState(state, generation);
      }
      
      console.log(`[EMULATOR] Iteration ${state.iteration}: action=${action.type} reward=${reward} total=${state.totalReward}`);
    }
    
    // Final save with all data
    await saveState(state, generation, true);
    
    // Update ledger
    await updateLedger(state, generation);
    
    console.log(`[EMULATOR] Generation ${generation} complete. Total reward: ${state.totalReward}`);
    
    return state;
    
  } finally {
    await browserAgent.cleanup();
  }
}

/**
 * Check if terminal condition met
 */
function isTerminal(state, rom) {
  if (!rom.terminal_condition) return false;
  
  const term = rom.terminal_condition;
  
  // Check iterations
  if (term.max_iterations && state.iteration >= term.max_iterations) {
    return true;
  }
  
  // Check reward threshold
  if (term.reward_threshold && state.totalReward >= term.reward_threshold) {
    return true;
  }
  
  // Custom terminal function
  if (term.custom_check) {
    // Would need VM evaluation - simplified here
    return false;
  }
  
  return false;
}

/**
 * Select action from action space based on current state
 */
function selectAction(state, rom) {
  const actionSpace = rom.action_space || [];
  
  if (!actionSpace.length) {
    return { type: 'noop', params: {} };
  }
  
  // Simple greedy selection - could be enhanced with Q-learning
  // For now, cycle through actions to explore
  const actionIndex = state.iteration % actionSpace.length;
  const action = actionSpace[actionIndex];
  
  // Add contextual params from current state
  return {
    type: action.type,
    params: {
      ...action.params,
      context: state.worldSnapshot,
    },
  };
}

/**
 * Save current generation state
 */
async function saveState(state, generation, isFinal = false) {
  const filename = isFinal 
    ? `gen-${generation}-final.json` 
    : `gen-${generation}-checkpoint-${state.iteration}.json`;
  
  const savePath = path.join(CONFIG.stateDir, filename);
  
  const saveData = {
    generation,
    iteration: state.iteration,
    totalReward: state.totalReward,
    timestamp: Date.now(),
    worldState: state.worldSnapshot,
    historyLength: state.history.length,
  };
  
  fs.writeFileSync(savePath, JSON.stringify(saveData, null, 2));
  console.log(`[EMULATOR] State saved: ${filename}`);
  
  // Auto-commit checkpoint (would integrate with git in production)
  return savePath;
}

/**
 * Update append-only ledger
 */
async function updateLedger(state, generation) {
  const entry = `
## Generation ${generation} - ${new Date().toISOString()}
- Iterations: ${state.iteration}
- Total Reward: ${state.totalReward}
- Duration: ${Date.now() - state.startTime}ms
- Checkpoints: ${Math.floor(state.iteration / CONFIG.decisionSaveInterval)}
`;
  
  let ledger = '';
  if (fs.existsSync(CONFIG.ledgerPath)) {
    ledger = fs.readFileSync(CONFIG.ledgerPath, 'utf8');
  }
  
  ledger = entry + '\n' + ledger;
  fs.writeFileSync(CONFIG.ledgerPath, ledger);
}

// Export for module use
module.exports = { emulatorLoop, CONFIG, selectAction, isTerminal };

// CLI entry point
if (require.main === module) {
  const romPath = process.argv[2] || path.join(CONFIG.romDir, 'rom-00-bootstrap.json');
  
  if (!fs.existsSync(romPath)) {
    console.error(`ROM not found: ${romPath}`);
    process.exit(1);
  }
  
  const rom = JSON.parse(fs.readFileSync(romPath, 'utf8'));
  emulatorLoop(rom).then(() => {
    console.log('Emulator complete');
    process.exit(0);
  }).catch(err => {
    console.error('Emulator error:', err);
    process.exit(1);
  });
}