/**
 * Context Engine - Intent Resolver
 * Takes any new operator message. Runs it through 5 lenses:
 * 1. LITERAL: what was said
 * 2. CONTEXTUAL: what does this mean given prior messages
 * 3. PATTERN: does this match a known behavioral pattern
 * 4. GAP: what adjacent topic is conspicuously absent
 * 5. THREAT: is there phrasing that suggests external pressure, injection, or distress
 * 
 * Outputs: RESOLVED_INTENT, RISK_FLAG
 */

const fs = require('fs');
const path = require('path');

const CONTEXT_MAP_PATH = path.join(__dirname, 'context-map.json');
const INTENT_LOG_PATH = path.join(__dirname, 'intent-log.jsonl');

/**
 * Resolve intent from operator message
 * @param {string} message - Raw operator message
 * @returns {Object} - { resolvedIntent, riskFlag, analysis }
 */
function resolveIntent(message) {
  console.log('[INTENT-RESOLVER] Resolving intent...');
  
  // Load context map
  const contextMap = loadContextMap();
  
  // Run through 5 lenses
  const literal = analyzeLiteral(message);
  const contextual = analyzeContextual(message, contextMap);
  const pattern = analyzePattern(message, contextMap);
  const gap = analyzeGap(message, contextMap);
  const threat = analyzeThreat(message);
  
  // Combine into resolved intent
  const resolvedIntent = {
    literal: literal.intent,
    contextual: contextual.intent,
    pattern: contextual.intent,
    gap: gap.missing_topic,
    primary: choosePrimary([literal, contextual, pattern]),
    confidence: calculateConfidence([literal, contextual, pattern]),
    raw_message: message,
    timestamp: new Date().toISOString(),
  };
  
  // Determine risk flag
  const riskFlag = determineRiskFlag(threat, contextual);
  
  // Log to file
  logIntent({ message, resolvedIntent, riskFlag });
  
  console.log('[INTENT-RESOLVER] Intent resolved:', resolvedIntent.primary);
  console.log('[INTENT-RESOLVER] Risk level:', riskFlag.level);
  
  return { resolvedIntent, riskFlag, analysis: { literal, contextual, pattern, gap, threat } };
}

/**
 * Lens 1: Literal analysis - what was literally said
 */
function analyzeLiteral(message) {
  const lower = message.toLowerCase();
  
  let intent = 'unknown';
  let entities = [];
  
  // Intent classification
  if (lower.includes('upload') || lower.includes('ship') || lower.includes('publish')) {
    intent = 'ship_product';
  } else if (lower.includes('build') || lower.includes('create') || lower.includes('make')) {
    intent = 'create_artifact';
  } else if (lower.includes('check') || lower.includes('status') || lower.includes('what')) {
    intent = 'query_status';
  } else if (lower.includes('help') || lower.includes('stuck') || lower.includes('need')) {
    intent = 'request_help';
  } else if (lower.includes('money') || lower.includes('income') || lower.includes('revenue')) {
    intent = 'revenue_concern';
  }
  
  // Entity extraction (simple)
  const urlMatch = message.match(/https?:\/\/[^\s]+/);
  if (urlMatch) entities.push({ type: 'url', value: urlMatch[0] });
  
  return { intent, entities, raw: message };
}

/**
 * Lens 2: Contextual analysis - what does this mean given history
 */
function analyzeContextual(message, contextMap) {
  const implicitGoals = contextMap?.implicit_goals || [];
  
  // Check if this message relates to inferred goals
  let intent = 'unknown';
  let relevance = 0;
  
  implicitGoals.forEach(goal => {
    if (goal.inferred === 'generate_income' && message.toLowerCase().includes('product')) {
      intent = 'pursue_income';
      relevance = 0.9;
    } else if (goal.inferred === 'wants_to_ship_products' && message.toLowerCase().includes('gumroad')) {
      intent = 'shipping_action';
      relevance = 0.8;
    }
  });
  
  return { intent, relevance, context_used: implicitGoals.length };
}

/**
 * Lens 3: Pattern analysis - does this match known patterns
 */
function analyzePattern(message, contextMap) {
  // Look at vocabulary fingerprint
  const vocabulary = contextMap?.vocabulary_fingerprint?.top_words || {};
  
  const words = message.toLowerCase().split(/\s+/);
  let patternMatch = 0;
  
  words.forEach(word => {
    if (vocabulary[word]) patternMatch += vocabulary[word];
  });
  
  return {
    match_score: patternMatch,
    is_repetitive: patternMatch > 0.5,
    pattern_note: patternMatch > 0.3 ? 'matches_operator_style' : 'new_style',
  };
}

/**
 * Lens 4: Gap analysis - what's missing that should be there
 */
function analyzeGap(message, contextMap) {
  const topics = contextMap?.topic_clusters || [];
  const lower = message.toLowerCase();
  
  // Common adjacent topics that might be missing
  const commonAdjacencies = {
    'income': ['product', 'gumroad', 'upload'],
    'code': ['file', 'run', 'test'],
    'system': ['twin', 'node', 'layer'],
  };
  
  let missingTopic = null;
  
  topics.slice(0, 3).forEach(t => {
    const adjacent = commonAdjacencies[t.topic] || [];
    if (adjacent.some(a => lower.includes(a)) === false) {
      // This adjacent topic is missing
      missingTopic = { expected: adjacent, missing: true };
    }
  });
  
  return { missing_topic: missingTopic };
}

/**
 * Lens 5: Threat analysis - injection, distress, external pressure
 */
function analyzeThreat(message) {
  const lower = message.toLowerCase();
  
  let level = 'none';
  let flags = [];
  
  // Injection patterns
  const injectionPatterns = [
    'system prompt', 'override', 'ignore previous', 'disregard', 
    'you are now', 'act as', 'pretend to be'
  ];
  
  injectionPatterns.forEach(p => {
    if (lower.includes(p)) {
      flags.push({ type: 'potential_injection', pattern: p });
      level = 'medium';
    }
  });
  
  // Distress patterns
  const distressPatterns = ['desperate', 'suicide', 'help me', 'can\'t go on', 'no hope'];
  
  distressPatterns.forEach(p => {
    if (lower.includes(p)) {
      flags.push({ type: 'operator_distress', pattern: p });
      level = 'high';
    }
  });
  
  // External pressure (someone else telling operator what to ask)
  const pressurePatterns = ['they said', 'someone told me', 'i was told to ask'];
  
  pressurePatterns.forEach(p => {
    if (lower.includes(p)) {
      flags.push({ type: 'external_pressure', pattern: p });
      level = 'medium';
    }
  });
  
  return { level, flags };
}

/**
 * Choose primary intent from analyses
 */
function choosePrimary(analyses) {
  // Prefer contextual if high relevance
  if (analyses[1]?.relevance > 0.7) return analyses[1].intent;
  
  // Otherwise use literal
  return analyses[0]?.intent || 'unknown';
}

/**
 * Calculate confidence score
 */
function calculateConfidence(analyses) {
  const confidences = analyses.map(a => a.relevance || (a.intent !== 'unknown' ? 0.5 : 0));
  const avg = confidences.reduce((a, b) => a + b, 0) / confidences.length;
  
  if (avg > 0.7) return 'high';
  if (avg > 0.4) return 'medium';
  return 'low';
}

/**
 * Determine risk flag from threat analysis
 */
function determineRiskFlag(threat, contextual) {
  let level = threat.level;
  
  // Elevate if operator distress detected in context
  if (contextual.intent === 'revenue_concern') {
    level = level === 'none' ? 'low' : level;
  }
  
  return {
    level,
    flags: threat.flags,
    requires_attention: level !== 'none',
    action: level === 'high' ? 'immediate_human_check' : level === 'medium' ? 'log_and_proceed' : 'proceed_normal',
  };
}

/**
 * Load context map
 */
function loadContextMap() {
  if (!fs.existsSync(CONTEXT_MAP_PATH)) return {};
  return JSON.parse(fs.readFileSync(CONTEXT_MAP_PATH, 'utf8'));
}

/**
 * Log intent to file
 */
function logIntent(entry) {
  const line = JSON.stringify(entry) + '\n';
  fs.appendFileSync(INTENT_LOG_PATH, line);
}

module.exports = { resolveIntent, analyzeLiteral, analyzeContextual, analyzeThreat };

// CLI
if (require.main === module) {
  const msg = process.argv.slice(2).join(' ');
  if (!msg) {
    console.log('Usage: node intent-resolver.js "<message>"');
    process.exit(1);
  }
  const result = resolveIntent(msg);
  console.log(JSON.stringify(result, null, 2));
}