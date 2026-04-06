#!/usr/bin/env python3
"""
EVEZ API Server - HTTP API for all EVEZ assets
Provides REST endpoints for autonomous operations
"""

import json
import time
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
from datetime import datetime

# Import EVEZ modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spine import EventSpine
from autonomous_agent import ContextualBanditAgent
from memory_store import UnifiedMemory
from cognition_engine import CognitionEngine
from autonomous_loop import AutonomousLoop
from swarm_orchestrator import SwarmOrchestrator, TaskPriority
from finance_engine import FinanceEngine

# Initialize all systems
spine = EventSpine("./api_spine.jsonl")
agent = ContextualBanditAgent("API-Agent")
memory = UnifiedMemory("./api_memory.jsonl")
cognition = CognitionEngine()
loop = AutonomousLoop()
swarm = SwarmOrchestrator()
finance = FinanceEngine(10000)

class EVEZHandler(BaseHTTPRequestHandler):
    
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _get_json(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            return json.loads(self.wfile.read(content_length))
        return {}
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == "/health":
            self._send_json({
                "status": "running",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "systems": {
                    "spine": len(spine.chain),
                    "agent_decisions": len(agent.history),
                    "memories": len(memory.memories),
                    "cognition_events": len(cognition.events),
                    "loop_cycles": loop.cycle_count,
                    "swarm_agents": len(swarm.agents),
                    "finance_equity": finance.get_equity()
                }
            })
            
        elif path == "/spine":
            self._send_json(spine.get_state())
            
        elif path == "/agent":
            self._send_json(agent.get_stats())
            
        elif path == "/memory":
            self._send_json(memory.get_stats())
            
        elif path == "/cognition":
            self._send_json(cognition.get_topology())
            
        elif path == "/loop":
            self._send_json(loop.get_status())
            
        elif path == "/swarm":
            self._send_json(swarm.get_status())
            
        elif path == "/finance":
            self._send_json(finance.get_performance())
            
        elif path == "/full":
            # Run full system cycle
            loop.run_cycle()
            result = loop.run_cycle()
            
            # Log to spine
            spine.append("SYSTEM_CYCLE", {
                "cycle": loop.cycle_count,
                "state": result["orientation"]["state"]
            })
            
            # Store in memory
            memory.store(
                f"Cycle {loop.cycle_count}: {result['orientation']['state']}",
                tags=["cycle", result['orientation']['state'].lower()]
            )
            
            # Create cognition event
            cognition.F(
                f"System cycle {loop.cycle_count} completed with state {result['orientation']['state']}",
                evidence=[str(loop.cycle_count)],
                falsifiers=["cycle hung", "state unknown"],
                confidence=0.85
            )
            
            # Finance cycle
            finance_result = finance.auto_trade_cycle()
            
            self._send_json({
                "loop": loop.get_status(),
                "finance": finance_result,
                "spine": spine.get_state(),
                "cognition": cognition.get_topology()
            })
            
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        data = self._get_json()
        
        if path == "/agent/decide":
            complexity = data.get("complexity", 25.0)
            confidence = data.get("confidence", 0.8)
            decision = agent.decide(complexity, confidence)
            self._send_json({
                "backend": decision.backend.value,
                "latency": decision.estimated_latency,
                "qubits": decision.qubits_required
            })
            
        elif path == "/memory/store":
            content = data.get("content", "")
            tags = data.get("tags", [])
            memory.store(content, tags=tags)
            self._send_json({"status": "stored"})
            
        elif path == "/memory/search":
            query = data.get("query", "")
            results = memory.search(query)
            self._send_json({
                "results": [
                    {"id": r.id, "content": r.content[:100], "tags": r.tags}
                    for r in results
                ]
            })
            
        elif path == "/cognition/fire":
            event_type = data.get("type", "F")
            claim = data.get("claim", "")
            evidence = data.get("evidence", [])
            falsifiers = data.get("falsifiers", [])
            confidence = data.get("confidence", 0.8)
            
            if event_type == "F":
                event = cognition.F(claim, evidence, falsifiers, confidence)
            elif event_type == "I":
                event = cognition.I(claim, evidence, falsifiers, confidence)
            elif event_type == "R":
                event = cognition.R(claim, evidence, falsifiers, confidence)
            else:
                event = cognition.E(claim, evidence, falsifiers, confidence)
                
            self._send_json({"id": event.id, "type": event.type})
            
        elif path == "/swarm/register":
            agent_id = data.get("id", "")
            name = data.get("name", "")
            capabilities = data.get("capabilities", [])
            swarm.register_agent(agent_id, name, capabilities)
            self._send_json({"status": "registered"})
            
        elif path == "/swarm/task":
            description = data.get("description", "")
            priority = data.get("priority", "medium")
            priority_map = {"low": TaskPriority.LOW, "medium": TaskPriority.MEDIUM,
                          "high": TaskPriority.HIGH, "critical": TaskPriority.CRITICAL}
            task = swarm.submit_task(description, priority_map.get(priority, TaskPriority.MEDIUM))
            self._send_json({"id": task.id, "status": task.status})
            
        elif path == "/finance/order":
            symbol = data.get("symbol", "BTC")
            side = data.get("side", "long")
            from finance_engine import PositionSide, OrderType
            order = finance.submit_order(
                symbol,
                OrderType.MARKET,
                PositionSide.LONG if side == "long" else PositionSide.SHORT,
                0.1
            )
            if order:
                finance.fill_order(order.id)
                self._send_json({"order_id": order.id, "status": "filled"})
            else:
                self._send_json({"error": "Order rejected"}, 400)
                
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def log_message(self, format, *args):
        print(f"[EVEZ-API] {args[0]}")


def run_server(port=8765):
    server = HTTPServer(("0.0.0.0", port), EVEZHandler)
    print(f"EVEZ API Server running on http://0.0.0.0:{port}")
    print("\nEndpoints:")
    print("  GET  /health         - System health")
    print("  GET  /spine          - Event spine state")
    print("  GET  /agent          - Agent stats")
    print("  GET  /memory         - Memory stats")
    print("  GET  /cognition      - Cognition topology")
    print("  GET  /loop           - Autonomous loop status")
    print("  GET  /swarm          - Swarm status")
    print("  GET  /finance        - Finance performance")
    print("  GET  /full           - Run full system cycle")
    print("  POST /agent/decide   - Make decision")
    print("  POST /memory/store   - Store memory")
    print("  POST /memory/search  - Search memory")
    print("  POST /cognition/fire - Create FIRE event")
    print("  POST /swarm/register - Register agent")
    print("  POST /swarm/task     - Submit task")
    print("  POST /finance/order  - Place order")
    server.serve_forever()


if __name__ == "__main__":
    run_server()