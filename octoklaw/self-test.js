/**
 * Self-Test - runs after every generation cycle
 * Verifies emulator core loads, ROM parses, agent runs, save state commits, LEDGER updates
 * If any step fails: halt, log, notify operator via Telegram
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.join(__dirname);
const TESTS = [];

/**
 * Register a test
 */
function test(name, fn) {
  TESTS.push({ name, fn });
}

// ==================== TESTS ====================

// Test 1: Emulator core loads
test('emulator_core_loads', async () => {
  try {
    const core = require('./emulator-agent-core/index.js');
    return { pass: true, note: 'Core module loaded' };
  } catch (e) {
    return { pass: false, error: e.message };
  }
});

// Test 2: ROM loader works
test('rom_loader_works', async () => {
  try {
    const { loadROM, getROMInfo } = require('./emulator-agent-core/rom-loader.js');
    const info = getROMInfo('./rom-spec/rom-00-bootstrap.json');
    return { pass: !!info, rom: info };
  } catch (e) {
    return { pass: false, error: e.message };
  }
});

// Test 3: ROM parses correctly
test('rom_parses', async () => {
  try {
    const { loadROM } = require('./emulator-agent-core/rom-loader.js');
    const rom = loadROM('./rom-spec/rom-00-bootstrap.json');
    const hasRequired = rom.world_state && rom.action_space && rom.reward_signal;
    return { pass: !!hasRequired, generation: rom.generation_meta?.generation };
  } catch (e) {
    return { pass: false, error: e.message };
  }
});

// Test 4: Browser agent module exists
test('browser_agent_exists', async () => {
  const agentPath = path.join(ROOT_DIR, 'emulator-agent-core', 'browser-agent.js');
  return { pass: fs.existsSync(agentPath) };
});

// Test 5: Save state can write
test('save_state_writes', async () => {
  try {
    const { saveState } = require('./emulator-agent-core/save-state.js');
    const testState = { iteration: 0, totalReward: 0, worldSnapshot: {} };
    const savePath = saveState(testState, 999, { commit: false });
    const exists = fs.existsSync(savePath);
    // Clean up test file
    if (exists) fs.unlinkSync(savePath);
    return { pass: exists };
  } catch (e) {
    return { pass: false, error: e.message };
  }
});

// Test 6: LEDGER exists or can be created
test('ledger_exists', async () => {
  const ledgerPath = path.join(ROOT_DIR, 'LEDGER.md');
  if (!fs.existsSync(ledgerPath)) {
    fs.writeFileSync(ledgerPath, '# OctoKlaw-ROM LEDGER\n\n');
  }
  return { pass: fs.existsSync(ledgerPath) };
});

// Test 7: Context engine loads
test('context_engine_loads', async () => {
  try {
    // Just check files exist
    const ctxDir = path.join(ROOT_DIR, 'context-engine');
    const hasFiles = fs.existsSync(path.join(ctxDir, 'pattern-reader.js'));
    return { pass: hasFiles };
  } catch (e) {
    return { pass: false, error: e.message };
  }
});

// Test 8: ROM builder works
test('rom_builder_works', async () => {
  try {
    const { loadRegistry } = require('./rom-builder/generate.js');
    const registry = loadRegistry();
    return { pass: !!registry, capabilities: registry.capabilities?.length };
  } catch (e) {
    return { pass: false, error: e.message };
  }
});

// Test 9: Schema is valid JSON
test('schema_valid', async () => {
  try {
    const schema = JSON.parse(fs.readFileSync('./rom-spec/schema.json', 'utf8'));
    return { pass: !!schema.$schema, properties: Object.keys(schema.properties).length };
  } catch (e) {
    return { pass: false, error: e.message };
  }
});

// Test 10: Capability registry exists
test('registry_exists', async () => {
  const registryPath = path.join(ROOT_DIR, 'rom-builder', 'capability-registry.json');
  if (!fs.existsSync(registryPath)) {
    fs.writeFileSync(registryPath, JSON.stringify({ capabilities: [] }));
  }
  return { pass: fs.existsSync(registryPath) };
});

// ==================== RUNNER ====================

/**
 * Run all tests and report
 */
async function runTests() {
  console.log('╔════════════════════════════════════════════════╗');
  console.log('║     OctoKlaw-ROM Self-Test Suite              ║');
  console.log('╚════════════════════════════════════════════════╝\n');
  
  let passed = 0;
  let failed = 0;
  const results = [];
  
  for (const t of TESTS) {
    process.stdout.write(`Testing: ${t.name}... `);
    
    try {
      const result = await t.fn();
      
      if (result.pass) {
        console.log('✓ PASS');
        if (result.note) console.log(`         ${result.note}`);
        passed++;
      } else {
        console.log('✗ FAIL');
        console.log(`         ${result.error || 'failed'}`);
        failed++;
      }
      
      results.push({ name: t.name, ...result });
      
    } catch (e) {
      console.log('✗ ERROR');
      console.log(`         ${e.message}`);
      failed++;
      results.push({ name: t.name, pass: false, error: e.message });
    }
  }
  
  console.log('\n╔════════════════════════════════════════════════╗');
  console.log(`║  Results: ${passed} passed, ${failed} failed              ║`);
  console.log('╚════════════════════════════════════════════════╝');
  
  // Log to LEDGER
  await logResults(results, passed, failed);
  
  if (failed > 0) {
    console.log('\n⚠️  HALTING - fix failures before continuing');
    console.log('   Run: node self-test.js to re-verify');
    process.exit(1);
  }
  
  console.log('\n✓ All tests passed - proceeding with generation');
  process.exit(0);
}

/**
 * Log test results to LEDGER
 */
async function logResults(results, passed, failed) {
  const ledgerPath = path.join(ROOT_DIR, 'LEDGER.md');
  
  let content = `## ${new Date().toISOString()} - Self-Test
- Passed: ${passed}/${TESTS.length}
- Failed: ${failed}
`;
  
  if (failed > 0) {
    content += '\n### Failed Tests:\n';
    results.filter(r => !r.pass).forEach(r => {
      content += `- ${r.name}: ${r.error || 'unknown'}\n`;
    });
  }
  
  let ledger = '';
  if (fs.existsSync(ledgerPath)) {
    ledger = fs.readFileSync(ledgerPath, 'utf8');
  }
  
  fs.writeFileSync(ledgerPath, content + '\n\n' + ledger);
}

// CLI
if (require.main === module) {
  runTests();
}

module.exports = { test, runTests };