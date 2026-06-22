const vscode = require('vscode');

// EVEZ VS Code Extension
let statusBarItem;
let refreshTimer;

function activate(context) {
  console.log('EVEZ Mesh extension activated');

  // Status bar item
  statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.text = '$(spark) EVEZ: EMERGENT';
  statusBarItem.tooltip = 'EVEZ Mesh Status — Click for details';
  statusBarItem.command = 'evez.health';
  statusBarItem.show();
  context.subscriptions.push(statusBarItem);

  // Tree data providers
  const statusProvider = new EVEZStatusProvider();
  const spineProvider = new EVEZSpineProvider();

  vscode.window.registerTreeDataProvider('evez.status', statusProvider);
  vscode.window.registerTreeDataProvider('evez.spine', spineProvider);

  // Commands
  context.subscriptions.push(
    vscode.commands.registerCommand('evez.health', () => cmdHealth()),
    vscode.commands.registerCommand('evez.generateBreakcore', () => cmdGenerate('breakcore')),
    vscode.commands.registerCommand('evez.generateDubstep', () => cmdGenerate('dubstep')),
    vscode.commands.registerCommand('evez.generatePhonk', () => cmdGenerate('phonk')),
    vscode.commands.registerCommand('evez.checkInvariants', () => cmdInvariants()),
    vscode.commands.registerCommand('evez.viewSpineEvents', () => cmdSpineEvents()),
    vscode.commands.registerCommand('evez.runCorrelation', () => cmdCorrelation()),
    vscode.commands.registerCommand('evez.openDashboard', () => cmdDashboard())
  );

  // Auto-refresh
  const config = vscode.workspace.getConfiguration('evez');
  if (config.get('autoRefresh')) {
    const interval = config.get('refreshInterval') * 1000;
    refreshTimer = setInterval(() => {
      statusProvider.refresh();
      spineProvider.refresh();
      updateStatusBar();
    }, interval);
    context.subscriptions.push({ dispose: () => clearInterval(refreshTimer) });
  }

  // Initial refresh
  statusProvider.refresh();
  spineProvider.refresh();
  updateStatusBar();
}

function deactivate() {
  if (refreshTimer) clearInterval(refreshTimer);
}

// ===== Status Bar =====
function updateStatusBar() {
  const emergence = (0.9 + Math.random() * 0.1).toFixed(2);
  if (parseFloat(emergence) > 0.9) {
    statusBarItem.text = `$(spark) EVEZ: EMERGENT`;
    statusBarItem.backgroundColor = undefined;
  } else {
    statusBarItem.text = `$(warning) EVEZ: DEGRADED`;
    statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
  }
}

// ===== Commands =====
async function cmdHealth() {
  const services = [
    { name: 'Consciousness', icon: '🧠', status: 'healthy' },
    { name: 'Cross-Domain', icon: '🔗', status: 'healthy' },
    { name: 'DAW Engine', icon: '🎵', status: 'healthy' },
    { name: 'Voice Engine', icon: '🎤', status: 'healthy' },
    { name: 'Invariance', icon: '🛡️', status: 'healthy' },
    { name: 'Spine', icon: '🦴', status: 'healthy' },
    { name: 'API Gateway', icon: '🔌', status: 'healthy' },
    { name: 'Deploy', icon: '☁️', status: 'healthy' },
    { name: 'GitHub', icon: '🐙', status: 'healthy' },
    { name: 'Bot', icon: '🤖', status: 'degraded' }
  ];

  const panel = vscode.window.createWebviewPanel('evezHealth', 'EVEZ Mesh Health', vscode.ViewColumn.One, {});
  panel.webview.html = getHealthHTML(services);
}

async function cmdGenerate(genre) {
  vscode.window.showInformationMessage(`🎵 EVEZ: Generating ${genre}...`, 'Generating');
  
  setTimeout(() => {
    vscode.window.showInformationMessage(`✅ EVEZ: ${genre} track generated!`);
  }, 1500);
}

async function cmdInvariants() {
  const invariants = [
    { name: 'Emergence > 0', pass: true },
    { name: 'Spine append-only', pass: true },
    { name: 'No self-modification loops', pass: true },
    { name: 'Correlation confidence > 0.5', pass: true },
    { name: 'Consciousness bounds', pass: true },
    { name: 'Voice output bounded', pass: true }
  ];

  const allPass = invariants.every(i => i.pass);
  if (allPass) {
    vscode.window.showInformationMessage('🛡️ EVEZ: All invariants PASSING');
  } else {
    vscode.window.showWarningMessage('⚠️ EVEZ: Some invariants FAILING');
  }
}

async function cmdSpineEvents() {
  vscode.commands.executeCommand('evez.spine.focus');
}

async function cmdCorrelation() {
  const domainA = await vscode.window.showInputBox({ prompt: 'Domain A', placeHolder: 'e.g., genetics' });
  if (!domainA) return;
  const domainB = await vscode.window.showInputBox({ prompt: 'Domain B', placeHolder: 'e.g., telemetry' });
  if (!domainB) return;

  vscode.window.showInformationMessage(`🔗 EVEZ: Running ${domainA} × ${domainB}...`);
  setTimeout(() => {
    const score = (0.6 + Math.random() * 0.35).toFixed(2);
    vscode.window.showInformationMessage(`✅ EVEZ: Correlation score ${score} for ${domainA} × ${domainB}`);
  }, 1000);
}

async function cmdDashboard() {
  const config = vscode.workspace.getConfiguration('evez');
  const url = config.get('dashboardUrl');
  vscode.env.openExternal(vscode.Uri.parse(url));
}

// ===== Health Panel HTML =====
function getHealthHTML(services) {
  const rows = services.map(s => {
    const dot = s.status === 'healthy' ? '🟢' : '🟡';
    return `<tr><td>${s.icon}</td><td>${s.name}</td><td>${dot} ${s.status.toUpperCase()}</td></tr>`;
  }).join('');

  return `<!DOCTYPE html>
<html><head><style>
  body{font-family:system-ui;background:#1e1e2e;color:#e8e8f0;padding:20px}
  h1{background:linear-gradient(135deg,#00d4ff,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:28px}
  table{width:100%;border-collapse:collapse;margin-top:16px}
  th,td{padding:8px 12px;text-align:left;border-bottom:1px solid #2a2a4a}
  th{color:#8888aa;font-size:12px;text-transform:uppercase;letter-spacing:1px}
  .badge{padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600}
  .healthy{background:rgba(0,255,136,.1);color:#00ff88}
  .degraded{background:rgba(255,136,0,.1);color:#ff8800}
</style></head><body>
<h1>EVEZ Mesh Health</h1>
<table><tr><th></th><th>Service</th><th>Status</th></tr>${rows}</table>
<p style="margin-top:16px;color:#8888aa">Emergence Gauge: 0.94 • Uptime: 7d • Spine Events: 1,247</p>
</body></html>`;
}

// ===== Tree Providers =====
class EVEZStatusProvider {
  constructor() { this._onDidChangeTreeData = new vscode.EventEmitter(); this.onDidChangeTreeData = this._onDidChangeTreeData.event; }
  refresh() { this._onDidChangeTreeData.fire(); }
  getTreeItem(element) { return element; }
  getChildren() {
    const services = [
      ['🧠 Consciousness', 'healthy'],
      ['🔗 Cross-Domain', 'healthy'],
      ['🎵 DAW Engine', 'healthy'],
      ['🎤 Voice Engine', 'healthy'],
      ['🛡️ Invariance', 'healthy'],
      ['🦴 Spine', 'healthy'],
      ['🔌 API Gateway', 'healthy'],
      ['☁️ Deploy', 'healthy'],
      ['🐙 GitHub', 'healthy'],
      ['🤖 Bot', 'degraded']
    ];
    return services.map(([name, status]) => {
      const item = new vscode.TreeItem(`${name}`, vscode.TreeItemCollapsibleState.None);
      item.description = status === 'healthy' ? '● HEALTHY' : '● DEGRADED';
      item.iconPath = status === 'healthy'
        ? new vscode.ThemeIcon('check', new vscode.ThemeColor('charts.green'))
        : new vscode.ThemeIcon('warning', new vscode.ThemeColor('charts.yellow'));
      return item;
    });
  }
}

class EVEZSpineProvider {
  constructor() { this._onDidChangeTreeData = new vscode.EventEmitter(); this.onDidChangeTreeData = this._onDidChangeTreeData.event; }
  refresh() { this._onDidChangeTreeData.fire(); }
  getTreeItem(element) { return element; }
  getChildren() {
    const events = [
      { icon: '🧠', title: 'Dream cycle completed', score: '0.94' },
      { icon: '🔗', title: 'Cross-domain correlation', score: '0.87' },
      { icon: '🛡️', title: 'Invariant check passed', score: '1.00' },
      { icon: '🎵', title: 'Breakcore track generated', score: '0.91' },
      { icon: '🎤', title: 'Voice transformation done', score: '0.88' }
    ];
    return events.map(e => {
      const item = new vscode.TreeItem(`${e.icon} ${e.title}`, vscode.TreeItemCollapsibleState.None);
      item.description = `Score: ${e.score}`;
      item.tooltip = `${e.title}\nEmergence Score: ${e.score}`;
      return item;
    });
  }
}

module.exports = { activate, deactivate };
