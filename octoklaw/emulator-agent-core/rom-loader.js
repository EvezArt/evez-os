/**
 * ROM Loader - Validates and Parses ROM JSON Schema
 * Ensures ROM meets specification before loading into emulator
 */

const fs = require('fs');
const path = require('path');

// ROM Schema (must match rom-spec/schema.json)
const REQUIRED_FIELDS = [
  'world_state',
  'action_space',
  'reward_signal',
  'terminal_condition',
  'generation_meta',
];

const REQUIRED_WORLD_STATE = [
  'name',
  'description',
];

const REQUIRED_ACTION_PROPS = ['type'];

/**
 * Load and validate a ROM file
 * @param {string} romPath - Path to ROM JSON file
 * @returns {Object} - Validated ROM object
 */
function loadROM(romPath) {
  console.log(`[ROM-LOADER] Loading: ${romPath}`);
  
  // Check file exists
  if (!fs.existsSync(romPath)) {
    throw new Error(`ROM file not found: ${romPath}`);
  }
  
  // Parse JSON
  let rom;
  try {
    const raw = fs.readFileSync(romPath, 'utf8');
    rom = JSON.parse(raw);
  } catch (e) {
    throw new Error(`Invalid JSON in ROM file: ${e.message}`);
  }
  
  // Validate structure
  validateStructure(rom);
  
  // Validate content
  validateContent(rom);
  
  console.log(`[ROM-LOADER] ✓ ROM validated: ${rom.world_state.name} (gen ${rom.generation_meta.generation})`);
  
  return rom;
}

/**
 * Validate ROM structure (top-level fields)
 */
function validateStructure(rom) {
  const missing = REQUIRED_FIELDS.filter(field => !(field in rom));
  
  if (missing.length > 0) {
    throw new Error(`ROM missing required fields: ${missing.join(', ')}`);
  }
}

/**
 * Validate ROM content (nested fields)
 */
function validateContent(rom) {
  // World state
  const wsMissing = REQUIRED_WORLD_STATE.filter(field => !(field in rom.world_state));
  if (wsMissing.length > 0) {
    throw new Error(`world_state missing: ${wsMissing.join(', ')}`);
  }
  
  // Action space must be array
  if (!Array.isArray(rom.action_space)) {
    throw new Error('action_space must be an array');
  }
  
  // Each action needs type
  rom.action_space.forEach((action, i) => {
    if (!action.type) {
      throw new Error(`action_space[${i}] missing 'type'`);
    }
  });
  
  // Reward signal structure
  if (typeof rom.reward_signal !== 'object') {
    throw new Error('reward_signal must be an object');
  }
  
  // Terminal condition structure
  if (typeof rom.terminal_condition !== 'object') {
    throw new Error('terminal_condition must be an object');
  }
  
  // Generation meta
  if (typeof rom.generation_meta?.generation !== 'number') {
    throw new Error('generation_meta.generation must be a number');
  }
}

/**
 * Get ROM info without full validation
 */
function getROMInfo(romPath) {
  if (!fs.existsSync(romPath)) return null;
  
  const raw = fs.readFileSync(romPath, 'utf8');
  const rom = JSON.parse(raw);
  
  return {
    name: rom.world_state?.name,
    generation: rom.generation_meta?.generation,
    actionCount: rom.action_space?.length || 0,
    description: rom.world_state?.description,
  };
}

/**
 * List all ROMs in a directory
 */
function listROMs(romDir) {
  if (!fs.existsSync(romDir)) return [];
  
  const files = fs.readdirSync(romDir)
    .filter(f => f.endsWith('.json'))
    .map(f => path.join(romDir, f))
    .map(f => getROMInfo(f))
    .filter(Boolean);
  
  return files.sort((a, b) => a.generation - b.generation);
}

/**
 * Create a new blank ROM from template
 */
function createBlankROM(generation = 0) {
  return {
    world_state: {
      name: `generation-${generation}`,
      description: '',
      context: {},
      resources: {},
    },
    action_space: [],
    reward_signal: {
      type: 'linear',
      weights: {},
    },
    terminal_condition: {
      max_iterations: 1000,
    },
    generation_meta: {
      generation,
      parent_generation: generation - 1,
      created_at: new Date().toISOString(),
      efficiency_metrics: {},
    },
  };
}

module.exports = {
  loadROM,
  validateStructure,
  validateContent,
  getROMInfo,
  listROMs,
  createBlankROM,
  REQUIRED_FIELDS,
};

// CLI
if (require.main === module) {
  const romPath = process.argv[2];
  
  if (!romPath) {
    console.log('Usage: node rom-loader.js <rom-path>');
    process.exit(1);
  }
  
  try {
    const rom = loadROM(romPath);
    console.log('ROM loaded successfully:');
    console.log(JSON.stringify(rom.world_state, null, 2));
  } catch (e) {
    console.error('ROM validation failed:', e.message);
    process.exit(1);
  }
}