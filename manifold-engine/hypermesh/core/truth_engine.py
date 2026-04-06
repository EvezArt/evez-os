#!/usr/bin/env python3
"""
Precausal Tracing Engine - Origin Chain Verification
Traces causal chains, identifies origins, exposes false narratives.
"""
import hashlib
import time
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque, defaultdict

@dataclass
class CausalNode:
    """A node in the causal chain"""
    id: str
    content: str              # The claim/statement/action
    source: str              # Origin of this node
    timestamp: str
    is_verified: bool = False
    verification_level: float = 0.0  # 0-1
    refutes: List[str] = field(default_factory=list)  # IDs this node refutes
    supported_by: List[str] = field(default_factory=list)  # IDs supporting this

@dataclass
class Allegation:
    """A claim or allegation needing verification"""
    id: str
    claim: str
    source: str
    asserted_by: str
    timestamp: str
    risk_level: float       # 0-1
    harm_potential: float  # 0-1
    evidence_required: List[str] = field(default_factory=list)

@dataclass
class TruthTrace:
    """Complete trace of a causal chain"""
    root_id: str
    nodes: Dict[str, CausalNode]
    path: List[str]           # Ordered causal path
    confidence: float        # Overall confidence in chain
    allegations_found: List[str]
    origin_confirmed: bool=False

class PrecausalTracer:
    """
    Precausal Tracing Engine
    - Traces causal chains to origins
    - Identifies source of claims/allegations
    - Verifies truth through evidence chains
    - Exposes manipulation
    - Tracks lies across time
    """
    
    def __init__(self):
        self.nodes: Dict[str, CausalNode] = {}
        self.allegations: Dict[str, Allegation] = {}
        self.chain_history: Dict[str, TruthTrace] = {}
        self.refutations: deque = deque(maxlen=100)
        self.id_counter = 1
        self.origin_whitelist: Set[str] = set()
        self.blacklist: Set[str] = set()
        
        # Initialize with known origins
        self._init_whitelist()
    
    def _init_whitelist(self):
        """Initialize trusted origins"""
        self.origin_whitelist = {
            "verified_expert", "peer_reviewed", "official_api", 
            "primary_source", "direct_observation", "cryptographic"
        }
        self.blacklist = {
            "anonymous", "unverified", "social_media_rumor", 
            "astroturf", "deepfake", "fabricated"
        }
    
    def _hash_id(self, content: str) -> str:
        """Create deterministic ID from content"""
        return hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def add_node(self, content: str, source: str, parent_id: str = None) -> str:
        """Add a node to the causal chain"""
        node_id = self._hash_id(content)
        
        if node_id in self.nodes:
            # Update existing
            node = self.nodes[node_id]
            if parent_id and parent_id not in node.supported_by:
                node.supported_by.append(parent_id)
            return node_id
        
        node = CausalNode(
            id=node_id,
            content=content,
            source=source,
            timestamp=datetime.utcnow().isoformat(),
            is_verified=source in self.origin_whitelist,
            verification_level=1.0 if source in self.origin_whitelist else 0.0
        )
        
        # Link to parent
        if parent_id and parent_id in self.nodes:
            self.nodes[parent_id].supported_by.append(node_id)
            # Update parent verification
            self._update_verification(parent_id)
        
        self.nodes[node_id] = node
        return node_id
    
    def _update_verification(self, node_id: str):
        """Update verification level based on source chain"""
        node = self.nodes.get(node_id)
        if not node:
            return
        
        # Calculate verification from sources
        sources = [self.nodes[s].source for s in node.supported_by if s in self.nodes]
        verified_sources = sum(1 for s in sources if s in self.origin_whitelist)
        
        if sources:
            node.verification_level = verified_sources / len(sources)
            node.is_verified = node.verification_level > 0.7
    
    def add_allegation(self, claim: str, source: str, asserted_by: str, 
                     risk: float = 0.5, harm: float = 0.0) -> str:
        """Add an allegation to track"""
        alleg_id = f"alleg_{self.id_counter}"
        self.id_counter += 1
        
        alleg = Allegation(
            id=alleg_id,
            claim=claim,
            source=source,
            asserted_by=asserted_by,
            timestamp=datetime.utcnow().isoformat(),
            risk_level=risk,
            harm_potential=harm,
            evidence_required=[]
        )
        
        self.allegations[alleg_id] = alleg
        
        # Auto-add as node
        self.add_node(claim, source)
        
        return alleg_id
    
    def trace_origin(self, node_id: str) -> TruthTrace:
        """Trace full causal chain to origin"""
        if node_id not in self.nodes:
            return None
        
        # Build path
        path = [node_id]
        visited = {node_id}
        
        while True:
            current = self.nodes[path[-1]]
            
            # Find parent (source of this claim)
            if current.supported_by:
                parent = current.supported_by[0]
                if parent not in visited and parent in self.nodes:
                    path.append(parent)
                    visited.add(parent)
                    continue
            
            # Check for origin
            if current.source in self.origin_whitelist:
                origin_confirmed = True
                break
            
            # No more parents
            break
        
        # Calculate confidence
        confidence = sum(self.nodes[n].verification_level for n in path) / len(path) if path else 0
        
        # Find allegations in path
        allegations = []
        for n in path:
            for a_id, a in self.allegations.items():
                node = self.nodes.get(n)
                if node and a.claim in node.content:
                    allegations.append(a_id)
        
        trace = TruthTrace(
            root_id=node_id,
            nodes={n: self.nodes[n] for n in path if n in self.nodes},
            path=path,
            confidence=confidence,
            allegations_found=allegations,
            origin_confirmed=any(self.nodes.get(n).source in self.origin_whitelist for n in path if n in self.nodes)
        )
        
        self.chain_history[node_id] = trace
        return trace
    
    def verify_claim(self, claim: str, evidence: List[str]) -> Dict:
        """Verify a claim against evidence"""
        claim_id = self._hash_id(claim)
        self.add_node(claim, "user_assertion")
        
        # Check each evidence item
        evidence_checks = []
        for evidence_item in evidence:
            evid_id = self._hash_id(evidence_item)
            self.add_node(evidence_item, "evidence", claim_id)
            
            evid_node = self.nodes.get(evid_id)
            evidence_checks.append({
                "evidence": evidence_item[:50],
                "verified": evid_node.is_verified if evid_node else False,
                "level": evid_node.verification_level if evid_node else 0
            })
        
        # Calculate overall verification
        verified_count = sum(1 for e in evidence_checks if e["verified"])
        overall = verified_count / len(evidence) if evidence else 0
        
        return {
            "claim": claim[:50],
            "verified": overall > 0.7,
            "confidence": overall,
            "evidence": evidence_checks,
            "risk_flags": self._check_risk_flags(claim)
        }
    
    def _check_risk_flags(self, claim: str) -> List[str]:
        """Check for risk flags"""
        flags = []
        claim_lower = claim.lower()
        
        # High risk patterns
        if any(w in claim_lower for w in ["always", "never", "everyone", "noone"]):
            flags.append("absolute_language")
        if any(w in claim_lower for w in ["fake", "hoax", "lie", "conspiracy"]):
            flags.append("manipulation_keyword")
        if "anonymous" in claim_lower or "unverified sources" in claim_lower:
            flags.append("untraceable_source")
        if any(w in claim_lower for w in ["don't verify", "can't prove", "refuses to"]):
            flags.append("obstruction")
        
        return flags
    
    def refute(self, node_id: str, refutation: str, refuter: str = "tracer") -> str:
        """Add refutation to a claim"""
        ref_id = self._hash_id(refutation)
        
        ref_node = CausalNode(
            id=ref_id,
            content=refutation,
            source=refuter,
            timestamp=datetime.utcnow().isoformat(),
            is_verified=True,
            verification_level=1.0
        )
        
        if node_id in self.nodes:
            self.nodes[node_id].refutes.append(ref_id)
        
        self.nodes[ref_id] = ref_node
        self.refutations.append({
            "refuted": node_id,
            "refutation": ref_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return ref_id
    
    def get_chain_report(self, node_id: str) -> Dict:
        """Generate full chain report"""
        trace = self.trace_origin(node_id)
        if not trace:
            return {"status": "not_found"}
        
        path_details = []
        for n in trace.path:
            node = self.nodes.get(n)
            if node:
                path_details.append({
                    "id": n[:8],
                    "source": node.source,
                    "verified": node.is_verified,
                    "level": node.verification_level,
                    "content": node.content[:50]
                })
        
        return {
            "node_id": node_id[:8],
            "path_length": len(trace.path),
            "origin_confirmed": trace.origin_confirmed,
            "confidence": trace.confidence,
            "allegations_in_chain": len(trace.allegations_found),
            "path": path_details,
            "risk_assessment": self._assess_risk(trace)
        }
    
    def _assess_risk(self, trace: TruthTrace) -> Dict:
        """Assess risk level of chain"""
        risk = 0.0
        
        for n in trace.path:
            node = self.nodes.get(n)
            if not node:
                continue
            
            # Low verification = higher risk
            if node.verification_level < 0.3:
                risk += 0.3
            
            # Untrusted source = higher risk
            if node.source in self.blacklist:
                risk += 0.5
            
            # Has refutations = suspicious
            if node.refutes:
                risk -= 0.2
        
        return {
            "risk_level": min(1.0, max(0.0, risk)),
            "verdict": "high_risk" if risk > 0.6 else "medium_risk" if risk > 0.3 else "low_risk",
            "action": "investigate" if risk > 0.5 else "track" if risk > 0.2 else "verified"
        }

def demo_tracer():
    """Demo the precausal tracer"""
    tracer = PrecausalTracer()
    
    print("=" * 50)
    print("PRECAUSAL TRACING ENGINE")
    print("=" * 50)
    
    # Add causal chain
    print("\n📍 Building Causal Chain:")
    
    # Root claim
    root_id = tracer.add_node("Climate change is caused by solar cycles", "unverified_blog")
    print(f"   Claim 1: {root_id[:8]} - unverified_blog")
    
    # Supporting claim
    support_id = tracer.add_node("Scientists say it's the sun", "anonymous_source", root_id)
    print(f"   → Claim 2: {support_id[:8]} - anonymous_source")
    
    # More support
    support2_id = tracer.add_node("Data shows solar increase", "verified_nasa", support_id)
    print(f"   → Claim 3: {support2_id[:8]} - verified_nasa")
    
    # Add allegation
    print("\n⚠️ Adding Allegation:")
    alleg_id = tracer.add_allegation(
        "Vaccines cause autism",
        "social_media",
        "user123",
        risk=0.9,
        harm=0.8
    )
    print(f"   Allegation: {alleg_id} - Risk: 0.9, Harm: 0.8")
    
    # Verify a claim
    print("\n✅ Claim Verification:")
    result = tracer.verify_claim(
        "The earth is round",
        ["Photos from space", "Gravity measurements", "Circumnavigation"]
    )
    print(f"   Claim: {result['claim']}")
    print(f"   Verified: {result['verified']} ({result['confidence']:.0%})")
    print(f"   Risk flags: {result['risk_flags']}")
    
    # Trace
    print("\n🔍 Chain Trace:")
    report = tracer.get_chain_report(root_id)
    print(f"   Path length: {report['path_length']}")
    print(f"   Origin confirmed: {report['origin_confirmed']}")
    print(f"   Confidence: {report['confidence']:.0%}")
    print(f"   Risk: {report['risk_assessment']['verdict']}")
    
    return tracer

if __name__ == "__main__":
    demo_tracer()