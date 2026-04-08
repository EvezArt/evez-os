/**
 * Context Engine - Pattern Reader
 * Reads operator message history from OpenClaw streamchat logs
 * Extracts: vocabulary fingerprint, request frequency, time-of-day patterns,
 * emotional valence markers, topic clustering, implicit goals
 */

const fs = require('fs');
const path = require('path');

const MEMORY_DIR = path.join(__dirname, '../../memory');
const CONTEXT_MAP_PATH = path.join(__dirname, 'context-map.json');

/**
 * Read operator messages and extract patterns
 * @param {number} lookbackMessages - How many recent messages to analyze
 * @returns {Object} - CONTEXT_MAP
 */
function readOperatorPatterns(lookbackMessages = 50) {
  console.log('[CONTEXT-ENGINE] Reading operator patterns...');
  
  const messages = loadRecentMessages(lookbackMessages);
  
  if (!messages.length) {
    return buildDefaultContext();
  }
  
  // Extract patterns
  const vocabulary = extractVocabulary(messages);
  const frequency = calculateFrequency(messages);
  const timePatterns = extractTimePatterns(messages);
  const emotionalValence = detectEmotionalValence(messages);
  const topicClusters = clusterTopics(messages);
  const implicitGoals = detectImplicitGoals(messages, topicClusters);
  
  const contextMap = {
    vocabulary_fingerprint: vocabulary,
    request_frequency: frequency,
    time_patterns: timePatterns,
    emotional_valence: emotionalValence,
    topic_clusters: topicClusters,
    implicit_goals: implicitGoals,
    linguistic_drift: detectLinguisticDrift(messages),
    mathematical_gaps: findMathematicalGaps(topicClusters),
    last_updated: new Date().toISOString(),
    message_count: messages.length,
  };
  
  // Save context map
  fs.writeFileSync(CONTEXT_MAP_PATH, JSON.stringify(contextMap, null, 2));
  console.log('[CONTEXT-ENGINE] Context map saved');
  
  return contextMap;
}

/**
 * Load recent messages from memory directory
 */
function loadRecentMessages(limit) {
  const messages = [];
  
  // Try to read from memory files
  const memoryFiles = fs.readdirSync(MEMORY_DIR).filter(f => f.endsWith('.md'));
  
  // Sort by date (newest first)
  memoryFiles.sort().reverse();
  
  for (const file of memoryFiles.slice(0, 5)) {
    const content = fs.readFileSync(path.join(MEMORY_DIR, file), 'utf8');
    // Simple extraction - in production would parse properly
    const lines = content.split('\n').filter(l => l.trim());
    messages.push(...lines.slice(0, Math.ceil(limit / memoryFiles.length)));
  }
  
  // If no memory files, check session logs
  if (!messages.length) {
    const sessionLog = path.join(__dirname, '../../autonomous_runner.log');
    if (fs.existsSync(sessionLog)) {
      const content = fs.readFileSync(sessionLog, 'utf8');
      const lines = content.split('\n').slice(-limit);
      messages.push(...lines);
    }
  }
  
  return messages.slice(0, limit);
}

/**
 * Extract vocabulary fingerprint (unique words + frequency)
 */
function extractVocabulary(messages) {
  const wordCounts = {};
  const totalWords = messages.length;
  
  messages.forEach(msg => {
    const words = msg.toLowerCase().split(/\s+/).filter(w => w.length > 2);
    words.forEach(word => {
      wordCounts[word] = (wordCounts[word] || 0) + 1;
    });
  });
  
  // Get top words as fingerprint
  const topWords = Object.entries(wordCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 100)
    .reduce((acc, [word, count]) => {
      acc[word] = count / totalWords;
      return acc;
    }, {});
  
  return {
    top_words: topWords,
    unique_count: Object.keys(wordCounts).length,
    avg_length: totalWords,
  };
}

/**
 * Calculate request frequency patterns
 */
function calculateFrequency(messages) {
  return {
    total_messages: messages.length,
    estimated_session_length: messages.length, // proxy
    // In production would track by timestamp
  };
}

/**
 * Extract time-of-day patterns
 */
function extractTimePatterns(messages) {
  // Would parse actual timestamps in production
  return {
    // Placeholder - would track actual times
    observed_patterns: [],
  };
}

/**
 * Detect emotional valence (positive/negative/neutral)
 */
function detectEmotionalValence(messages) {
  const positiveWords = ['good', 'great', 'thanks', 'helpful', 'love', 'perfect', 'yes', 'ok', 'sure'];
  const negativeWords = ['no', 'not', 'wrong', 'bad', 'fail', 'stuck', 'help', 'urgent', 'desperate'];
  
  let positive = 0, negative = 0, neutral = 0;
  
  messages.forEach(msg => {
    const lower = msg.toLowerCase();
    if (positiveWords.some(w => lower.includes(w))) positive++;
    else if (negativeWords.some(w => lower.includes(w))) negative++;
    else neutral++;
  });
  
  const total = messages.length || 1;
  
  return {
    positive_ratio: positive / total,
    negative_ratio: negative / total,
    neutral_ratio: neutral / total,
    overall: positive > negative ? 'positive' : negative > positive ? 'negative' : 'neutral',
  };
}

/**
 * Cluster topics from messages
 */
function clusterTopics(messages) {
  const topicKeywords = {
    'income': ['money', 'revenue', 'income', 'sales', 'dollar', 'gumroad', 'pay'],
    'shipping': ['upload', 'product', 'ship', 'publish', 'release'],
    'code': ['code', 'file', 'python', 'script', 'build', 'run'],
    'system': ['system', 'architecture', 'twin', 'node', 'layer'],
    'help': ['help', 'need', 'urgent', 'stuck', 'problem'],
  };
  
  const topicCounts = {};
  
  messages.forEach(msg => {
    const lower = msg.toLowerCase();
    Object.keys(topicKeywords).forEach(topic => {
      if (topicKeywords[topic].some(w => lower.includes(w))) {
        topicCounts[topic] = (topicCounts[topic] || 0) + 1;
      }
    });
  });
  
  return Object.entries(topicCounts)
    .sort((a, b) => b[1] - a[1])
    .map(([topic, count]) => ({ topic, count }));
}

/**
 * Detect implicit goals (things asked sideways)
 */
function detectImplicitGoals(messages, topicClusters) {
  const goals = [];
  
  // High-frequency topic clusters that might indicate goals
  const topTopics = topicClusters.slice(0, 3).map(c => c.topic);
  
  if (topTopics.includes('income')) {
    goals.push({ explicit: false, inferred: 'wants_to_generate_income', confidence: 'high' });
  }
  if (topTopics.includes('shipping')) {
    goals.push({ explicit: false, inferred: 'wants_to_ship_products', confidence: 'medium' });
  }
  if (topTopics.includes('help')) {
    goals.push({ explicit: false, inferred: 'needs_help_with_current_task', confidence: 'high' });
  }
  
  return goals;
}

/**
 * Detect linguistic drift (phrasing changes over time)
 */
function detectLinguisticDrift(messages) {
  // Placeholder - would analyze actual drift
  return {
    detected: false,
    notes: 'Would require message timestamps to analyze properly',
  };
}

/**
 * Find mathematical gaps (topics close but not connected)
 */
function findMathematicalGaps(topicClusters) {
  // Topics that cluster near each other but are never directly connected
  const gapTopics = [];
  
  // For example: if "income" and "code" both appear but never together
  const topics = topicClusters.map(c => c.topic);
  
  // Placeholder for gap detection
  return {
    gaps: gapTopics,
    notes: 'Would require co-occurrence analysis',
  };
}

/**
 * Build default context for cold start
 */
function buildDefaultContext() {
  return {
    vocabulary_fingerprint: { 'income': 0.3, 'product': 0.2, 'ship': 0.15, 'help': 0.1 },
    implicit_goals: [
      { explicit: false, inferred: 'generate_income', confidence: 'high' },
    ],
    last_updated: new Date().toISOString(),
    message_count: 0,
    is_default: true,
  };
}

module.exports = { readOperatorPatterns, loadRecentMessages, extractVocabulary };

// CLI
if (require.main === module) {
  const result = readOperatorPatterns(50);
  console.log(JSON.stringify(result, null, 2));
}