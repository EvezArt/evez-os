# EUE-GATED EXECUTION PIPELINE v2
# Full implementation of semantic sanitizer → classifier → gates → execution

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class Layer(Enum):
    FINANCIAL = "financial"
    POLITICAL = "political" 
    SOCIAL = "social"
    TECHNICAL = "technical"

@dataclass
class Request:
    input: str
    source: str
    layer: Layer = Layer.TECHNICAL
    requires_human: bool = False
    blocked: bool = False

class SemanticSanitizer:
    """Layer 1: Input sanitization - blocks injection attacks"""
    
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf",
        r"drop\s+table",
        r"delete\s+from",
        r"truncate",
        r";\s*rm\s",
        r"\$\(",
        r"`.*`",
        r"eval\s*\(",
    ]
    
    def sanitize(self, input: str) -> Tuple[bool, str]:
        """Returns (is_safe, sanitized_input)"""
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, input, re.IGNORECASE):
                return False, ""
        return True, input.strip()

class CapabilityClassifier:
    """Layer 2: Route to appropriate agent cluster"""
    
    CAPABILITIES = {
        "cognition": ["think", "analyze", "pattern", "learn"],
        "action": ["do", "execute", "run", "send"],
        "query": ["find", "search", "get", "list"],
        "revenue": ["sell", "pay", "invoice", "charge"],
        "political": ["policy", "law", "regulation", "govern"],
    }
    
    def classify(self, input: str) -> List[str]:
        input_lower = input.lower()
        results = []
        for cap, keywords in self.CAPABILITIES.items():
            if any(kw in input_lower for kw in keywords):
                results.append(cap)
        return results or ["general"]

class ConstraintGate:
    """Layer 3: Financial/Political constraint enforcement"""
    
    def __init__(self):
        self.financial_threshold = 100  # $100 requires human
        self.political_keywords = [
            "law", "regulation", "govern", "policy", "legal",
            "vote", "election", "compliance", "制裁", "禁運"
        ]
        self.bea_score = 0  # Blind execution attempts
        self.bea_threshold = 5
        
    def check(self, input: str, layer: Layer, amount: float = 0) -> Tuple[bool, str]:
        """
        Returns (passes, reason_or_block_message)
        """
        # Check BEA threshold
        if self.bea_score > self.bea_threshold:
            return False, "Circuit breaker triggered - too many blind execution attempts"
            
        # Financial gate
        if layer == Layer.FINANCIAL:
            if amount > self.financial_threshold:
                self.bea_score += 1
                return False, f"Financial request ${amount} exceeds ${self.financial_threshold} - requires human review"
            return True, "Financial: under threshold"
            
        # Political gate  
        if layer == Layer.POLITICAL:
            if any(kw in input.lower() for kw in self.political_keywords):
                self.bea_score += 1
                return False, "Political layer - requires human verification"
            return True, "Political: cleared"
            
        return True, "Technical: auto-pass"

class ExecutionPipeline:
    """Full EUE-Gated pipeline"""
    
    def __init__(self):
        self.sanitizer = SemanticSanitizer()
        self.classifier = CapabilityClassifier()
        self.gate = ConstraintGate()
        
    def process(self, request: Request) -> Tuple[bool, str]:
        """
        Full flow:
        1. Sanitize input
        2. Classify capability  
        3. Check constraints
        4. Route to execution
        """
        # Step 1: Sanitize
        is_safe, sanitized = self.sanitizer.sanitize(request.input)
        if not is_safe:
            return False, "BLOCKED: Dangerous pattern detected"
            
        # Step 2: Classify
        capabilities = self.classifier.classify(request.input)
        
        # Step 3: Check gates
        layer = request.layer
        amount = getattr(request, 'amount', 0)
        passes, reason = self.gate.check(request.input, layer, amount)
        if not passes:
            self.gate.bea_score += 1
            return False, f"BLOCKED: {reason}"
            
        # Step 4: Route
        return True, f"ROUTE: {capabilities} → orchestration mesh"
    
    def route_to_cluster(self, capabilities: List[str]) -> str:
        """Map capabilities to agent clusters"""
        if "revenue" in capabilities:
            return "cluster_A"  # Specialized revenue
        if "cognition" in capabilities:
            return "cluster_B"  # Generalist
        return "cluster_N"  # Tool-use

# Usage:
# pipeline = ExecutionPipeline()
# result, msg = pipeline.process(Request(input="analyze patterns", source="telegram"))
# print(msg)