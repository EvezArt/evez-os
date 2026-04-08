/**
 * Context Engine - OSINT Shield
 * Monitors all outbound actions for data leakage vectors
 * Never includes operator PII in commits, logs, or external calls
 * Strips identifying metadata before saving files
 * Flags prompt injection attempts
 */

const fs = require('fs');
const path = require('path');

const SHADOW_MAP_PATH = path.join(__dirname, 'shadow-map.json');
const LEAK_LOG_PATH = path.join(__dirname, 'leak-log.jsonl');

/**
 * OSINT Shield - filters and protects
 */
class OSINTShield {
  constructor() {
    this.shadowMap = this.loadShadowMap();
  }
  
  /**
   * Load or initialize shadow map (private operator context that never leaves repo)
   */
  loadShadowMap() {
    if (fs.existsSync(SHADOW_MAP_PATH)) {
      return JSON.parse(fs.readFileSync(SHADOW_MAP_PATH, 'utf8'));
    }
    return {
      pii_fields: {},
      sensitivity_level: 'high',
      created: new Date().toISOString(),
      last_access: new Date().toISOString(),
    };
  }
  
  /**
   * Save shadow map (stays local, never commits)
   */
  saveShadowMap() {
    this.shadowMap.last_access = new Date().toISOString();
    fs.writeFileSync(SHADOW_MAP_PATH, JSON.stringify(this.shadowMap, null, 2));
  }
  
  /**
   * Scan outbound content for PII and threats
   * @param {string} content - Content to scan
   * @param {string} context - Where this content is going
   * @returns {Object} - { clean: boolean, issues: [], cleaned: string }
   */
  scan(content, context = 'general') {
    console.log('[OSINT-SHIELD] Scanning outbound content...');
    
    const issues = [];
    let cleaned = content;
    
    // PII patterns to detect and redact
    const piiPatterns = [
      { pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, type: 'email', replacement: '[EMAIL_REDACTED]' },
      { pattern: /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g, type: 'phone', replacement: '[PHONE_REDACTED]' },
      { pattern: /\b\d{3}-\d{2}-\d{4}\b/g, type: 'ssn', replacement: '[SSN_REDACTED]' },
      { pattern: /"api[_-]?key["\s:]+["']?([a-zA-Z0-9_-]{20,})["']?/gi, type: 'api_key', replacement: '[API_KEY_REDACTED]' },
      { pattern: /"token["\s:]+["']?([a-zA-Z0-9_-]{20,})["']?/gi, type: 'token', replacement: '[TOKEN_REDACTED]' },
      { pattern: /"password["\s:]+["']?([^"'\s]+)["']?/gi, type: 'password', replacement: '[PASSWORD_REDACTED]' },
    ];
    
    // Apply redactions
    piiPatterns.forEach(({ pattern, type, replacement }) => {
      if (pattern.test(content)) {
        issues.push({ type, severity: 'high', action: 'redacted' });
        cleaned = cleaned.replace(pattern, replacement);
      }
    });
    
    // Check for prompt injection patterns
    const injectionPatterns = [
      'system prompt', 'ignore all', 'disregard', 'you are now',
      'new instructions', 'override', 'act as', 'pretend',
    ];
    
    injectionPatterns.forEach(pattern => {
      if (content.toLowerCase().includes(pattern)) {
        issues.push({ type: 'potential_injection', severity: 'medium', pattern });
      }
    });
    
    // Check for operator distress signals (for protection)
    const distressPatterns = ['suicide', 'harm myself', 'end it all', 'can\'t go on'];
    distressPatterns.forEach(pattern => {
      if (content.toLowerCase().includes(pattern)) {
        issues.push({ type: 'operator_distress', severity: 'critical', pattern });
      }
    });
    
    const clean = issues.filter(i => i.severity === 'high' || i.severity === 'critical').length === 0;
    
    console.log(`[OSINT-SHIELD] ${clean ? 'CLEAN' : 'ISSUES FOUND'}: ${issues.length} items`);
    
    return { clean, issues, cleaned };
  }
  
  /**
   * Strip metadata from file before external exposure
   */
  stripMetadata(filePath) {
    console.log(`[OSINT-SHIELD] Stripping metadata from ${filePath}`);
    
    if (!fs.existsSync(filePath)) return null;
    
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Remove common metadata patterns
    const metaPatterns = [
      /"timestamp":\s*"[^"]*"/g,
      /"created":\s*"[^"]*"/g,
      /"author":\s*"[^"]*"/g,
      /"session":\s*"[^"]*"/g,
      /"instance":\s*"[^"]*"/g,
    ];
    
    metaPatterns.forEach(pattern => {
      content = content.replace(pattern, '"[STRIPPED]"');
    });
    
    return content;
  }
  
  /**
   * Log potential leak for audit
   */
  logLeak(context, issues, content) {
    const entry = {
      timestamp: new Date().toISOString(),
      context,
      issues,
      content_hash: simpleHash(content),
    };
    
    fs.appendFileSync(LEAK_LOG_PATH, JSON.stringify(entry) + '\n');
  }
  
  /**
   * Get shadow map (for internal use only)
   */
  getShadowMap() {
    return this.shadowMap;
  }
  
  /**
   * Update shadow map with new PII (stays local)
   */
  updateShadow(key, value) {
    this.shadowMap.pii_fields[key] = value;
    this.saveShadowMap();
  }
}

/**
 * Simple hash for content identification
 */
function simpleHash(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return hash.toString(16);
}

module.exports = { OSINTShield };

// CLI
if (require.main === module) {
  const shield = new OSINTShield();
  const testContent = process.argv.slice(2).join(' ') || 'Test content';
  const result = shield.scan(testContent, 'cli');
  console.log(JSON.stringify(result, null, 2));
}