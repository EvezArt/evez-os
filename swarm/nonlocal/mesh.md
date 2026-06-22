# Mesh-of-Mesh — Self-Organizing Node Discovery & Healing

## Overview

EVEZ nodes form a **graph, not a star**. Each node discovers others via UDP broadcast and DNS. The mesh is self-organizing. Nodes join, leave, and heal without central coordination.

## Topology

```
     ┌──────────┐          ┌──────────┐
     │  Node A  │◄────────►│  Node B  │
     │ (edge)   │          │ (core)   │
     └────┬─────┘          └────┬─────┘
          │                     │
          │    ┌──────────┐     │
          ├───►│  Node C  │◄────┤
          │    │ (cloud)  │     │
          │    └────┬─────┘     │
          │         │           │
     ┌────▼────┐    │    ┌──────▼───┐
     │  Node D │◄───┴───►│  Node E  │
     │ (raspi) │         │ (vps)    │
     └─────────┘         └──────────┘
```

**No central coordinator.** No single point of failure. The mesh IS the architecture.

## Discovery Mechanisms

### 1. UDP Broadcast (LAN)

Nodes on the same network discover each other via UDP broadcast:

```python
# Every node broadcasts a heartbeat every 30s
MESH_DISCOVERY_PORT = 3777
HEARTBEAT_INTERVAL = 30  # seconds

class MeshDiscovery:
    def broadcast_heartbeat(self):
        msg = json.dumps({
            "type": "mesh.heartbeat",
            "node_id": self.node_id,
            "version": "1.0.0",
            "services": self.local_services,
            "spine_last_index": self.spine_last_index,
            "capabilities": self.capabilities,
            "ts": time.time()
        })
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(msg.encode(), ('<broadcast>', MESH_DISCOVERY_PORT))
    
    def listen_for_heartbeats(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', MESH_DISCOVERY_PORT))
        while True:
            data, addr = sock.recvfrom(4096)
            self.register_peer(json.loads(data), addr)
```

### 2. DNS-Based Discovery (WAN)

For nodes across networks, DNS SRV records enable discovery:

```
_evez-mesh._tcp.evez.ai.  SRV  10 60 3777 node-a.evez.ai.
_evez-mesh._tcp.evez.ai.  SRV  20 60 3777 node-b.evez.ai.
_evez-mesh._tcp.evez.ai.  SRV  30 60 3777 node-c.evez.ai.
```

Nodes query DNS periodically to find new peers:
```python
import dns.resolver

def discover_via_dns(domain="evez.ai"):
    records = dns.resolver.resolve(f"_evez-mesh._tcp.{domain}", "SRV")
    peers = []
    for r in records:
        peers.append({
            "host": r.target.to_text(),
            "port": r.port,
            "priority": r.priority,
            "weight": r.weight
        })
    return peers
```

### 3. Gossip Protocol

Nodes share peer lists with each other (gossip):

```python
class GossipProtocol:
    def share_peers(self, peer):
        """Share known peers with a specific peer"""
        known = list(self.mesh.known_peers.values())
        peer.send({"type": "mesh.peers", "peers": known})
    
    def on_receive_peers(self, msg):
        """Integrate received peer list"""
        for peer_info in msg["peers"]:
            if peer_info["node_id"] not in self.mesh.known_peers:
                self.mesh.add_peer_candidate(peer_info)
                self.try_connect(peer_info)
```

### 4. Bootstrap Nodes

For first-time setup, nodes can be configured with bootstrap peers:

```yaml
# ~/.evez/mesh.yaml
bootstrap:
  - addr: "node-alpha.evez.ai:3777"
  - addr: "node-beta.evez.ai:3777"
  - addr: "10.0.0.1:3777"  # LAN fallback
```

## Node Lifecycle

### Joining

```
1. New node reads bootstrap config
2. Connects to bootstrap peer(s)
3. Sends JOIN request with signed identity
4. Bootstrap peer verifies, sends back:
   - Current mesh membership
   - Spine shard assignments
   - Service directory
   - Consensus state
5. New node syncs Spine shards assigned to it
6. New node announces services
7. Mesh routing tables update
```

### Leaving (Graceful)

```
1. Node sends LEAVE announcement
2. Other nodes redistribute its shards
3. Other nodes update routing tables
4. Node shuts down cleanly
```

### Leaving (Unexpected / Crash)

```
1. Other nodes detect missing heartbeats (3x HEARTBEAT_INTERVAL = 90s)
2. Node marked as "suspect"
3. After 5x HEARTBEAT_INTERVAL (150s), node marked as "dead"
4. Shard rebalance triggered
5. Routing tables updated
6. If node returns, it goes through JOIN again
```

### Healing

The mesh continuously self-heals:

```python
class MeshHealer:
    def check_health(self):
        """Run every 60 seconds"""
        for peer in self.mesh.peers.values():
            age = time.time() - peer.last_heartbeat
            if age > 150:
                self.mark_dead(peer)
            elif age > 90:
                self.mark_suspect(peer)
                self.probe(peer)  # direct TCP probe
    
    def on_node_death(self, node):
        """Handle a dead node"""
        # 1. Redistribute shards
        self.redistribute_shards(node)
        # 2. Reassign services
        self.reassign_services(node)
        # 3. Update routing
        self.update_routing(node, remove=True)
        # 4. Trigger new leader election if needed
        if node.is_leader:
            self.trigger_election()
    
    def redistribute_shards(self, dead_node):
        """Move shards from dead node to healthy ones"""
        for shard_id in dead_node.shards:
            candidates = [n for n in self.mesh.healthy_nodes()
                          if shard_id not in n.shards]
            target = min(candidates, key=lambda n: len(n.shards))
            self.replicate_shard(shard_id, dead_node, target)
```

## Routing

### Direct Routing (Peers)

For directly connected peers, messages go direct.

### Multi-Hop Routing

For non-adjacent nodes, the mesh uses a link-state protocol:

```python
class MeshRouter:
    def __init__(self):
        self.link_state = {}  # node_id -> {neighbor: cost}
        self.forwarding_table = {}
    
    def update_link_state(self, node_id, neighbors):
        self.link_state[node_id] = neighbors
        self.recompute_routes()  # Dijkstra's
    
    def recompute_routes(self):
        """Recompute forwarding table using Dijkstra's"""
        for src in self.link_state:
            dist, prev = dijkstra(self.link_state, src)
            for dst in dist:
                # Next hop is the first step on shortest path
                path = reconstruct_path(prev, src, dst)
                self.forwarding_table[(src, dst)] = path[1] if len(path) > 1 else dst
```

### Mesh-Tunnel Protocol

For nodes behind NAT, the mesh establishes tunnels through public nodes:

```
[Node behind NAT] ←→ [Public Relay Node] ←→ [Other Node]
```

Tunnels use WireGuard or NaCl-encrypted WebSocket.

## Security Model

### Node Identity

Each node has a permanent Ed25519 keypair. The public key IS the node identity.

```python
node_key = ed25519.SigningKey.generate()
node_id = "node_" + node_key.public_key.hex()[:8]
```

### Peer Verification

On connection, nodes perform a mutual challenge-response:

```
Node A → Node B:  challenge_A = random(32)
Node B → Node A:  challenge_B = random(32), sig_B = sign(challenge_A)
Node A → Node B:  sig_A = sign(challenge_B)
```

Both nodes verify the other's signature. Connection established only if both verify.

### Authorization

Not all nodes are equal. Node capabilities are signed by the mesh CA:

```yaml
node: node-a.evez.ai
capabilities:
  - spine.write
  - consciousness.sense
  - consciousness.think
  - tools.execute
  - modify.propose
issuer: mesh-ca.evez.ai
expires: 2027-01-01
signature: ed25519:...
```

## Performance Targets

| Metric | Target |
|--------|--------|
| Peer discovery (LAN) | < 5s |
| Peer discovery (WAN) | < 30s |
| Heartbeat interval | 30s |
| Failure detection | < 90s |
| Routing reconvergence | < 10s |
| Shard rebalance | < 60s |
| Full mesh sync | < 300s |

## Mesh Metrics

Each node exposes Prometheus-compatible metrics:

```
evez_mesh_peers_total 12
evez_mesh_peers_healthy 11
evez_mesh_shards_held 3
evez_mesh_spine_last_index 42847
evez_mesh_messages_sent_total 8942
evez_mesh_messages_received_total 8938
evez_mesh_route_hops_avg 1.7
```

---

*Mesh Protocol Version: 1.0.0*
*Last Updated: 2026-06-22*
