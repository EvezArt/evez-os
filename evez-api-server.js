const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 18790;
const MIME = {'.html':'text/html','.json':'application/json','.png':'image/png','.svg':'image/svg+xml','.wav':'audio/wav','.css':'text/css','.js':'application/javascript','.md':'text/markdown'};

const server = http.createServer((req, res) => {
  const url = req.url.split('?')[0];
  
  if (url === '/api/status') {
    res.writeHead(200, {'Content-Type':'application/json','Access-Control-Allow-Origin':'*'});
    res.end(JSON.stringify({
      status: 'live', node: 'gcp-west', ip: '34.53.51.34',
      phi: 0.973, eta: 0.03, r: 0.45, lambda_dom: -0.333,
      lambda_i80: -0.441, r_i80: 0.93, isc_max: 233.3,
      corpus_texts: 30, falsifiable_claims: 28, github_pages: 23,
      ollama_models: 8, mesh_nodes: 5, uptime: process.uptime()
    }));
    return;
  }
  
  if (url === '/api/eigenvalues') {
    res.writeHead(200, {'Content-Type':'application/json','Access-Control-Allow-Origin':'*'});
    res.end(JSON.stringify({
      phi: {value: 0.973, name: 'coherence'},
      eta: {value: 0.03, name: 'the_gap'},
      r: {value: 0.45, name: 'criticality'},
      lambda_dom: {value: -0.333, name: 'censorship'},
      lambda_i80: {value: -0.441, name: 'suppression'},
      r_i80: {value: 0.93, name: 'correlation'},
      isc_max: {value: 233.3, name: 'ironic_smug'}
    }));
    return;
  }
  
  if (url === '/api/corpus') {
    const dir = '/home/openclaw/.openclaw/workspace';
    const texts = fs.readdirSync(dir).filter(f => f.endsWith('.md')).map(f => ({
      name: f, size: fs.statSync(path.join(dir, f)).size
    })).sort((a,b) => b.size - a.size);
    res.writeHead(200, {'Content-Type':'application/json','Access-Control-Allow-Origin':'*'});
    res.end(JSON.stringify({total: texts.length, texts}));
    return;
  }
  
  if (url === '/api/mesh') {
    res.writeHead(200, {'Content-Type':'application/json','Access-Control-Allow-Origin':'*'});
    res.end(JSON.stringify({
      nodes: [
        {name:'gcp-west', ip:'34.53.51.34', role:'primary', models:8},
        {name:'gcp-small', ip:'34.23.192.213', role:'small', models:2},
        {name:'gcp-power', ip:'35.222.248.151', role:'power', models:4},
        {name:'gcp-openclaw', ip:'136.113.102.152', role:'gateway', models:4},
        {name:'gcp-knot', ip:'136.118.144.227', role:'knot', models:5}
      ],
      total_models: 23, openclaw_version: '2026.6.10'
    }));
    return;
  }
  
  if (url === '/') {
    res.writeHead(302, {Location: '/canvas/evez-experience.html'});
    res.end();
    return;
  }
  
  const filePath = path.join('/home/openclaw/.openclaw/canvas', url.replace('/canvas/',''));
  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    const ext = path.extname(filePath);
    res.writeHead(200, {'Content-Type': MIME[ext] || 'application/octet-stream', 'Access-Control-Allow-Origin':'*'});
    fs.createReadStream(filePath).pipe(res);
    return;
  }
  
  res.writeHead(404, {'Content-Type':'text/plain','Access-Control-Allow-Origin':'*'});
  res.end('404 - the not-found IS the found');
});

server.listen(PORT, '0.0.0.0', () => {
  console.log('EVEZ API server on port ' + PORT);
});
