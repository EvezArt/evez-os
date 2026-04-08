/**
 * ROM Builder - Generative Engine
 * Reads learned-pattern-{n}.json -> outputs rom-{n+1}.json
 * with one new capability, tighter efficiency constraint,
 * new world_state elements from gen-n discoveries,
 * and updated reward signal
 */

const fs = require('fs');
const path = require('path');

const PATTERNS_DIR = path.join(__dirname, '..', 'patterns');
const ROMS_DIR = path.join(__dirname, '..', 'roms');
const CAPABILITY_REGISTRY = path.join(__dirname, 'capability-registry.json');

/**
 * Generate next generation ROM from current generation's patterns
 * @param {number} currentGen - Current generation number
 * @returns {Object} - New ROM object
 */
function generateNextROM(currentGen) {
  console.log(`[ROM-BUILDER] Generating ROM for generation ${currentGen + 1}`);
  
  // Load patterns from current generation
  const patterns = loadPatterns(currentGen);
  
  // Load capability registry
  const registry = loadRegistry();
  
  // Identify new capability to add
  const newCapability = selectNewCapability(registry, patterns);
  
  // Build new ROM
  const newROM = buildROM(currentGen, patterns, newCapability, registry);
  
  // Save new ROM
  const romPath = path.join(ROMS_DIR, `rom-${currentGen + 1}-${newCapability.replace(/\s+/g, '-').toLowerCase()}.json`);
  fs.writeFileSync(romPath, JSON.stringify(newROM, null, 2));
  
  // Update registry with new capability
  addCapabilityToRegistry(newCapability, newROM);
  
  console.log(`[ROM-BUILDER] ROM generated: ${romPath}`);
  
  return newROM;
}

/**
 * Load learned patterns from previous generation
 */
function loadPatterns(gen) {
  const patternFile = path.join(PATTERNS_DIR, `learned-pattern-${gen}.json`);
  
  if (!fs.existsSync(patternFile)) {
    // Return default patterns if none exist
    return {
      efficiency_gains: [],
      errors_encountered: [],
      successful_actions: [],
      insights: [],
    };
  }
  
  return JSON.parse(fs.readFileSync(patternFile, 'utf8'));
}

/**
 * Load capability registry
 */
function loadRegistry() {
  if (!fs.existsSync(CAPABILITY_REGISTRY)) {
    return {
      capabilities: [],
      by_generation: {},
      efficiency_history: [],
    };
  }
  
  return JSON.parse(fs.readFileSync(CAPABILITY_REGISTRY, 'utf8'));
}

/**
 * Select a new capability based on patterns and registry
 */
function selectNewCapability(registry, patterns) {
  const existing = registry.capabilities || [];
  
  // Capabilities we might want to add
  const candidates = [
    { name: 'auto_post_generator', description: 'Generate link-specific X posts' },
    { name: 'health_monitor', description: 'Continuous health checks' },
    { name: 'revenue_tracker', description: 'Track and predict income' },
    { name: 'context_learner', description: 'Learn operator patterns' },
    { name: 'redundancy_manager', description: 'Manage multi-host failover' },
  ];
  
  // Filter out existing capabilities
  const available = candidates.filter(c => !existing.includes(c.name));
  
  if (!available.length) {
    // If all exist, improve an existing one
    return `improve_${existing[0]}`;
  }
  
  // Select based on patterns - if we have shipping errors, pick auto_post
  if (patterns.errors_encountered?.some(e => e.includes('gumroad'))) {
    return available.find(c => c.name === 'auto_post_generator')?.name || available[0].name;
  }
  
  return available[0].name;
}

/**
 * Build complete ROM for next generation
 */
function buildROM(parentGen, patterns, newCapability, registry) {
  // Extract efficiency constraints from parent
  const efficiency = registry.efficiency_history?.[parentGen] || { ratio: 1.0 };
  const newConstraint = Math.min(efficiency.ratio * 0.9, 0.5); // 10% improvement or minimum 0.5
  
  // Build world state with discoveries from parent
  const worldState = {
    name: `gen-${parentGen + 1}-${newCapability}`,
    description: `Generation ${parentGen + 1} - adding ${newCapability}`,
    context: {
      previous_generation: parentGen,
      new_capability: newCapability,
      parent_efficiency_ratio: efficiency.ratio,
    },
    resources: {
      patterns_discovered: patterns.insights?.length || 0,
      errors_from_parent: patterns.errors_encountered?.length || 0,
    },
    initial_state: {
      capability_installed: false,
      efficiency_ratio: newConstraint,
    },
    constraints: {
      no_credentials: true,
      no_billing_access: true,
      phone_only: true,
    },
  };
  
  // Build action space
  const actions = buildActionSpace(newCapability, patterns);
  
  // Build reward signal
  const rewardSignal = buildRewardSignal(newCapability, patterns);
  
  return {
    world_state: worldState,
    action_space: actions,
    reward_signal: rewardSignal,
    terminal_condition: {
      max_iterations: 500,
      reward_threshold: 500,
      custom_check: `capability_installed && efficiency_ratio >= ${newConstraint}`,
    },
    generation_meta: {
      generation: parentGen + 1,
      parent_generation: parentGen,
      created_at: new Date().toISOString(),
      efficiency_metrics: {
        parent_ratio: efficiency.ratio,
        target_ratio: newConstraint,
      },
      capabilities_added: [newCapability],
      notes: `Auto-generated from gen ${parentGen} patterns`,
    },
  };
}

/**
 * Build action space for new capability
 */
function buildActionSpace(capability, patterns) {
  const baseActions = [
    { type: 'noop', params: {}, weight: 0.1 },
  ];
  
  // Add capability-specific actions
  const capabilityActions = {
    auto_post_generator: [
      { type: 'read', params: { path: '/root/.openclaw/workspace/profit-engine/products/*.md' }, weight: 1.0 },
      { type: 'write', params: { path: '/root/.openclaw/workspace/octoklaw/posts/generated-post.md' }, weight: 2.0 },
    ],
    health_monitor: [
      { type: 'exec', params: { command: 'curl -s -o /dev/null -w "%{http_code}" https://api.github.com' }, weight: 1.0 },
      { type: 'write', params: { path: '/root/.openclaw/workspace/octoklaw/health.json' }, weight: 1.5 },
    ],
    revenue_tracker: [
      { type: 'read', params: { path: '/root/.openclaw/workspace/revenue_log.jsonl' }, weight: 1.0 },
      { type: 'write', params: { path: '/root/.openclaw/workspace/octoklaw/revenue-forecast.json' }, weight: 2.0 },
    ],
    context_learner: [
      { type: 'read', params: { path: '/root/.openclaw/workspace/memory/*.md' }, weight: 1.0 },
      { type: 'write', params: { path: '/root/.openclaw/workspace/octoklaw/context-map.json' }, weight: 2.0 },
    ],
    redundancy_manager: [
      { type: 'exec', params: { command: 'echo "ping"' }, weight: 0.5 },
      { type: 'write', params: { path: '/root/.openclaw/workspace/octoklaw/redundancy-status.json' }, weight: 1.5 },
    ],
  };
  
  const specific = capabilityActions[capability] || [];
  
  return [...baseActions, ...specific];
}

/**
 * Build reward signal for new capability
 */
function buildRewardSignal(capability, patterns) {
  return {
    type: 'linear',
    weights: {
      capability_installed: 50,
      efficiency_improved: 30,
      file_generated: 10,
      error_free: 10,
    },
    components: {
      installation: { weight: 50, formula: 'capability_installed ? 50 : 0' },
      efficiency: { weight: 30, formula: '(new_ratio / old_ratio) * 30' },
      output: { weight: 20, formula: 'files_created * 5' },
    },
  };
}

/**
 * Add new capability to registry
 */
function addCapabilityToRegistry(capability, rom) {
  let registry = loadRegistry();
  
  if (!registry.capabilities) {
    registry.capabilities = [];
  }
  
  if (!registry.capabilities.includes(capability)) {
    registry.capabilities.push(capability);
  }
  
  if (!registry.by_generation) {
    registry.by_generation = {};
  }
  
  const gen = rom.generation_meta.generation;
  registry.by_generation[gen] = capability;
  
  if (!registry.efficiency_history) {
    registry.efficiency_history = [];
  }
  
  registry.efficiency_history.push({
    generation: gen,
    capability,
    ratio: rom.world_state.initial_state.efficiency_ratio,
  });
  
  fs.writeFileSync(CAPABILITY_REGISTRY, JSON.stringify(registry, null, 2));
}

module.exports = { generateNextROM, loadPatterns, loadRegistry };

// CLI
if (require.main === module) {
  const gen = parseInt(process.argv[2]) || 0;
  generateNextROM(gen);
}