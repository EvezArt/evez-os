/**
 * Browser Agent - Playwright-powered agent for DOM interaction
 * Reads DOM state, maps to ROM world_state, selects action from action_space,
 * applies it, reads reward
 */

const { chromium } = require('playwright');

class BrowserAgent {
  constructor(options = {}) {
    this.browser = null;
    this.context = null;
    this.page = null;
    this.options = {
      headless: options.headless !== false,
      timeout: options.timeout || 30000,
      targetUrl: options.targetUrl || 'about:blank',
    };
    this.actionResults = [];
  }
  
  /**
   * Initialize browser and navigate to target
   */
  async init() {
    console.log('[BROWSER-AGENT] Launching browser...');
    
    this.browser = await chromium.launch({
      headless: this.options.headless,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });
    
    this.context = await this.browser.newContext({
      viewport: { width: 1280, height: 720 },
    });
    
    this.page = await this.context.newPage();
    
    if (this.options.targetUrl !== 'about:blank') {
      await this.page.goto(this.options.targetUrl, { waitUntil: 'domcontentloaded' });
    }
    
    console.log('[BROWSER-AGENT] Browser ready');
  }
  
  /**
   * Read current DOM state and map to world_state format
   */
  async readState() {
    if (!this.page) throw new Error('Browser not initialized');
    
    const state = {
      url: this.page.url(),
      title: await this.page.title(),
      timestamp: Date.now(),
    };
    
    // Extract DOM elements for agent decision-making
    try {
      // Get interactive elements
      const elements = await this.page.evaluate(() => {
        const interactive = [];
        const selectors = ['button', 'a', 'input', 'select', 'textarea'];
        
        selectors.forEach(sel => {
          document.querySelectorAll(sel).forEach(el => {
            if (el.offsetParent !== null) { // visible only
              interactive.push({
                tag: el.tagName.toLowerCase(),
                text: el.textContent?.trim().substring(0, 100),
                id: el.id,
                classes: el.className,
                visible: el.offsetParent !== null,
              });
            }
          });
        });
        
        return interactive.slice(0, 50); // limit
      });
      
      state.elements = elements;
      state.elementCount = elements.length;
      
    } catch (e) {
      state.elements = [];
      state.elementError = e.message;
    }
    
    return state;
  }
  
  /**
   * Execute an action from action_space
   * @param {Object} action - Action object with type and params
   */
  async execute(action) {
    if (!this.page) throw new Error('Browser not initialized');
    
    const actionStart = Date.now();
    let reward = 0;
    let result = {};
    
    try {
      switch (action.type) {
        case 'navigate':
          await this.page.goto(action.params.url, { waitUntil: 'domcontentloaded' });
          result = { status: 'success', url: this.page.url() };
          reward = 10;
          break;
          
        case 'click':
          const selector = action.params.selector;
          if (selector) {
            await this.page.click(selector, { timeout: 5000 });
            result = { status: 'success', selector };
            reward = 5;
          }
          break;
          
        case 'type':
          const { selector, text } = action.params;
          if (selector && text) {
            await this.page.fill(selector, text);
            result = { status: 'success', selector, textLength: text.length };
            reward = 3;
          }
          break;
          
        case 'select':
          const { selector: sel, value } = action.params;
          if (sel && value) {
            await this.page.selectOption(sel, value);
            result = { status: 'success', selector: sel, value };
            reward = 3;
          }
          break;
          
        case 'evaluate':
          // Run arbitrary JavaScript in page context
          const evalResult = await this.page.evaluate(action.params.script);
          result = { status: 'success', result: evalResult };
          reward = 5;
          break;
          
        case 'screenshot':
          const screenshot = await this.page.screenshot();
          result = { status: 'success', size: screenshot.length };
          reward = 2;
          break;
          
        case 'wait':
          await this.page.waitForTimeout(action.params.duration || 1000);
          result = { status: 'success', duration: action.params.duration };
          reward = 1;
          break;
          
        case 'read':
          // Read specific elements
          const readResult = await this.page.evaluate((sel) => {
            const el = document.querySelector(sel);
            return el ? el.textContent?.trim() : null;
          }, action.params.selector);
          result = { status: 'success', content: readResult };
          reward = 2;
          break;
          
        case 'noop':
          // No operation
          result = { status: 'skipped' };
          reward = 0;
          break;
          
        default:
          result = { status: 'unknown-action', actionType: action.type };
          reward = -1;
      }
      
    } catch (e) {
      result = { status: 'error', message: e.message };
      reward = -5; // Penalty for failure
    }
    
    const actionDuration = Date.now() - actionStart;
    
    this.actionResults.push({
      action,
      result,
      reward,
      duration: actionDuration,
      timestamp: Date.now(),
    });
    
    return { reward, result, state: await this.readState() };
  }
  
  /**
   * Map current DOM state to ROM action space
   * Returns available actions based on current context
   */
  async getAvailableActions(actionSpace) {
    const currentState = await this.readState();
    const available = [];
    
    actionSpace.forEach(action => {
      // Check if action is applicable in current context
      if (action.type === 'navigate') {
        available.push(action);
      } else if (action.type === 'click' && action.params.selector) {
        // Check if target element exists
        available.push(action);
      } else if (action.type === 'read') {
        available.push(action);
      } else {
        // Generic actions always available
        available.push(action);
      }
    });
    
    return available;
  }
  
  /**
   * Get action history
   */
  getHistory() {
    return this.actionResults;
  }
  
  /**
   * Cleanup browser resources
   */
  async cleanup() {
    if (this.context) await this.context.close();
    if (this.browser) await this.browser.close();
    console.log('[BROWSER-AGENT] Cleanup complete');
  }
}

module.exports = BrowserAgent;

// Example usage
if (require.main === module) {
  (async () => {
    const agent = new BrowserAgent({
      targetUrl: 'https://example.com',
    });
    
    await agent.init();
    
    const state = await agent.readState();
    console.log('Current state:', JSON.stringify(state, null, 2));
    
    // Execute a test action
    const { reward, result } = await agent.execute({
      type: 'noop',
      params: {},
    });
    console.log('Action result:', { reward, result });
    
    await agent.cleanup();
    process.exit(0);
  })();
}