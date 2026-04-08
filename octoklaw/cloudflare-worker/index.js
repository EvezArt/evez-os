/**
 * OctoKlaw-ROM Cloudflare Worker
 * Lobby Dispatcher - Routes jobs to node pool based on capacity
 * 
 * Free tier: 100k requests/day - unlimited for this use case
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    // ROUTES
    
    // GET /health - health check
    if (path === '/health') {
      return new Response(JSON.stringify({ 
        status: 'ok', 
        worker: 'octoklaw-lobby',
        timestamp: new Date().toISOString() 
      }), { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      });
    }
    
    // POST /dispatch - dispatch a job to a node
    if (path === '/dispatch' && request.method === 'POST') {
      try {
        const body = await request.json();
        const job = body.job || {};
        
        // Get capacity from KV or default
        const nodePool = await getNodePool();
        const selectedNode = selectNode(nodePool, job.priority);
        
        // Dispatch to node
        const response = await fetch(`${selectedNode.url}/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(job)
        });
        
        return new Response(JSON.stringify({
          dispatched: true,
          node: selectedNode.id,
          url: selectedNode.url,
          result: await response.text()
        }), { 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        });
        
      } catch (e) {
        return new Response(JSON.stringify({ error: e.message }), { 
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        });
      }
    }
    
    // GET /nodes - list available nodes and their capacity
    if (path === '/nodes') {
      const nodes = await getNodePool();
      return new Response(JSON.stringify({ nodes }), { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      });
    }
    
    // POST /nodes/:id/heartbeat - node reports capacity
    if (path.startsWith('/nodes/') && path.endsWith('/heartbeat') && request.method === 'POST') {
      const nodeId = path.split('/')[2];
      const capacity = await request.json();
      
      await updateNodeCapacity(nodeId, capacity);
      
      return new Response(JSON.stringify({ updated: true, node: nodeId }), { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      });
    }
    
    // GET /queue - get queued jobs
    if (path === '/queue') {
      // In production, would read from KV
      return new Response(JSON.stringify({ jobs: [], count: 0 }), { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      });
    }
    
    // Default: routing info
    return new Response(JSON.stringify({
      worker: 'octoklaw-lobby-dispatcher',
      routes: [
        'GET /health - health check',
        'GET /nodes - list node pool',
        'POST /dispatch - dispatch job',
        'POST /nodes/:id/heartbeat - node capacity update',
        'GET /queue - job queue status'
      ]
    }), { 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
    });
  }
};

// Node pool configuration (in production, would use KV store)
const DEFAULT_NODES = [
  { 
    id: 'replit-primary', 
    url: 'https://octoklaw-runtime.replit.app', 
    capacity: 100, 
    priority: 1 
  },
  { 
    id: 'railway-mirror', 
    url: 'https://octoklaw.up.railway.app', 
    capacity: 50, 
    priority: 2 
  },
  { 
    id: 'valtown-watchdog', 
    url: 'https://val.town/v/evez666.octoklaw', 
    capacity: 100, 
    priority: 3 
  }
];

async function getNodePool() {
  // In production: read from Cloudflare KV
  // const nodes = await OCTOKLAW_NODES.get('node_pool');
  // return nodes ? JSON.parse(nodes) : DEFAULT_NODES;
  return DEFAULT_NODES;
}

async function updateNodeCapacity(nodeId, capacity) {
  // In production: write to Cloudflare KV
  // await OCTOKLAW_NODES.put(`node:${nodeId}`, JSON.stringify(capacity));
  console.log(`Node ${nodeId} capacity updated:`, capacity);
}

function selectNode(nodes, priority = 'normal') {
  // Sort by capacity (highest first)
  const sorted = [...nodes].sort((a, b) => b.capacity - a.capacity);
  
  // If priority is 'high', prefer more capable nodes
  if (priority === 'high') {
    return sorted[0];
  }
  
  // Otherwise, round-robin or weighted random
  return sorted[Math.floor(Math.random() * Math.min(3, sorted.length))];
}