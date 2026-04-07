#!/usr/bin/env python3
"""
Ulterior Motive Inference Engine
Detects hidden agendas, predicts position shifts, tracks risk of recomposure.
"""
import random
import hashlib
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict

@dataclass
class AgendaPattern:
    """Pattern of hidden agenda"""
    pattern_type: str      # deflection, distraction, loaded, concern_troll
    indicators: List[str]
    severity: float         # 0-1
    base_rate: float       # how often this indicates agenda

@dataclass
class PositionShift:
    """Predicted shift in position"""
    from_stance: str
    to_stance: str
    confidence: float
    triggers: List[str]
    timeline_hours: float

@dataclass
class NarrativeTrail:
    """Trail of narrative evolution"""
    claim_id: str
    original: str
    versions: List[Dict]     # Changed versions
    abandoned_by: str = ""
    recomposed: bool = False
    exposure_risk: float = 0.0

class MotiveScanner:
    """
    Ulterior Motive Inference
    - Detects hidden agendas
    - Predicts position shifts  
    - Tracks narrative recomposure risk
    - Offloads predictive reasoning
    """
    
    def __init__(self):
        self.agenda_patterns: Dict[str, AgendaPattern] = {}
        self.profiles: Dict[str, Dict] = {}  # User/entity profiles
        self.narratives: Dict[str, NarrativeTrail] = {}
        self.position_history: Dict[str, List[PositionShift]] = {}
        self.suspicious_entities: Set[str] = set()
        self._init_patterns()
    
    def _init_patterns(self):
        """Initialize agenda detection patterns"""
        patterns = [
            AgendaPattern(
                "deflection",
                ["what about", "but also", "changing subject", "actually"],
                0.7, 0.3
            ),
            AgendaPattern(
                "concern_troll",
                ["I'm concerned", "worried about", "honestly", "as a (.*) i worry"],
                0.8, 0.4
            ),
            AgendaPattern(
                "loaded_language",
                ["obviously", "everyone knows", "they don't want you to know", "secret"],
                0.6, 0.5
            ),
            AgendaPattern(
                "distraction",
                ["while we're on", "side point", "another thing", "btw"],
                0.5, 0.3
            ),
            AgendaPattern(
                "false_balance",
                ["both sides", "some say", "others believe", "debate continues"],
                0.7, 0.4
            ),
            AgendaPattern(
                "astroturf",
                ["many people", "growing movement", "grassroots", "silent majority"],
                0.9, 0.5
            ),
            AgendaPattern(
                "ad_hominem_shifted",
                ["but her emails", "but his", "they're lying", "but biden"],
                0.8, 0.4
            ),
            AgendaPattern(
                "reliance_on_authority",
                ["experts say", "scientists", "studies show", "research proves"],
                0.4, 0.2
            ),
        ]
        
        for p in patterns:
            self.agenda_patterns[p.pattern_type] = p
    
    def scan_motive(self, text: str, source: str = "unknown") -> Dict:
        """Scan text for ulterior motives"""
        text_lower = text.lower()
        findings = []
        severity = 0.0
        
        for pattern_name, pattern in self.agenda_patterns.items():
            matches = []
            for indicator in pattern.indicators:
                if indicator in text_lower:
                    matches.append(indicator)
            
            if matches:
                # Calculate match strength
                match_strength = len(matches) / len(pattern.indicators)
                agenda_score = pattern.severity * match_strength
                
                findings.append({
                    "pattern": pattern_name,
                    "indicators": matches,
                    "score": agenda_score,
                    "severity": pattern.severity
                })
                
                severity = max(severity, agenda_score)
        
        # Entity credibility check
        entity_credibility = self._check_entity(source)
        
        return {
            "text": text[:100],
            "source": source,
            "agenda_detected": severity > 0.5,
            "severity": severity,
            "patterns_found": findings,
            "entity_credibility": entity_credibility,
            "risk_level": "high" if severity > 0.7 else "medium" if severity > 0.4 else "low",
            "recommendation": self._recommend(severity, entity_credibility)
        }
    
    def _check_entity(self, entity: str) -> Dict:
        """Check entity credibility"""
        if entity in self.suspicious_entities:
            return {"credibility": 0.1, "status": "suspicious", "risk": "high"}
        
        profile = self.profiles.get(entity, {})
        past_claims = profile.get("claim_count", 0)
        
        # New entity = lower credibility
        if past_claims == 0:
            return {"credibility": 0.3, "status": "new", "risk": "medium"}
        
        accuracy = profile.get("accuracy", 0.5)
        return {
            "credibility": accuracy,
            "status": "known",
            "risk": "low" if accuracy > 0.7 else "high",
            "past_claims": past_claims
        }
    
    def _recommend(self, severity: float, entity: Dict) -> str:
        """Get recommendation based on scan"""
        if severity > 0.7:
            return "REDUCE: Do not amplify without verification"
        elif severity > 0.4:
            return "VERIFY: Cross-check before repeating"
        elif entity.get("risk") == "high":
            return "CAUTION: Low credibility source"
        else:
            return "PROCEED: Low risk detected"
    
    def predict_position_shift(self, entity: str, current_stance: str) -> Optional[PositionShift]:
        """Predict when entity might shift position"""
        history = self.position_history.get(entity, [])
        
        if len(history) < 2:
            # Not enough data, make prediction
            shifts = [
                ("pro", "neutral", 0.6, ["controversy", "polling"], 24),
                ("anti", "pro", 0.4, ["convenience"], 48),
                ("neutral", "anti", 0.5, ["event"], 72),
            ]
            return PositionShift(
                current_stance, shifts[0][0], shifts[0][1], shifts[0][2], shifts[0][3], shifts[0][4]
            )
        
        # Analyze patterns
        last_shift = history[-1]
        
        return PositionShift(
            current_stance,
            "unknown",  # Will shift to unknown
            0.5,
            ["convenience", "new_information", "polls"],
            24.0
        )
    
    def track_narrative(self, claim_id: str, claim: str, entity: str) -> str:
        """Track narrative evolution"""
        if claim_id not in self.narratives:
            self.narratives[claim_id] = NarrativeTrail(
                claim_id=claim_id,
                original=claim,
                versions=[{"version": claim, "entity": entity, "timestamp": datetime.utcnow().isoformat()}]
            )
            return "tracked"
        
        # Check for version change
        narrative = self.narratives[claim_id]
        
        # Check if should abandon (exposed)
        if self._check_abandonment(entity, claim):
            narrative.abandoned_by = entity
            narrative.exposure_risk = 0.9
            return "abandoned"
        
        # Track new version
        narrative.versions.append({
            "version": claim[:100],
            "entity": entity,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return "updated"
    
    def _check_abandonment(self, entity: str, claim: str) -> bool:
        """Check if entity might abandon this claim"""
        # Exposure risk higher if:
        # - Similar claims were abandoned before
        # - High agenda score in claim
        # - Entity has history of shifting
        
        scan = self.scan_motive(claim, entity)
        
        if scan["agenda_detected"] and scan["severity"] > 0.6:
            return True
        
        profile = self.profiles.get(entity, {})
        if profile.get("abandoned_claims", 0) > 3:
            return True
        
        return False
    
    def recomposure_risk(self, claim_id: str) -> Dict:
        """Calculate risk of narrative being recomposed"""
        if claim_id not in self.narratives:
            return {"risk": 0.0, "status": "not_tracked"}
        
        narrative = self.narratives[claim_id]
        
        # Risk factors
        version_count = len(narrative.versions)
        has_abandoned = bool(narrative.abandoned_by)
        
        risk = 0.0
        if version_count > 3:
            risk += 0.3
        if has_abandoned:
            risk += 0.4
        if narrative.exposure_risk > 0.5:
            risk += 0.3
        
        return {
            "risk": min(1.0, risk),
            "status": "high_risk" if risk > 0.6 else "medium_risk" if risk > 0.3 else "low_risk",
            "versions": version_count,
            "was_abandoned": has_abandoned,
            "exposure_risk": narrative.exposure_risk
        }
    
    def offload_detection(self, text: str) -> Dict:
        """Detect when someone offloads reasoning"""
        text_lower = text.lower()
        
        # Offloading patterns
        offload_patterns = {
            "just_asking": ["just asking", "genuine question", "curious"],
            " epistemic_offload": ["experts say", "studies show", "research shows"],
            " crowd_offload": ["everyone knows", "people realize", "they say"],
            "authority_offload": ["according to", "sources say", "reliable sources"],
            "future_conditional": ["will prove", "will show", "time will tell"],
        }
        
        detected = []
        for offload_type, patterns in offload_patterns.items():
            for p in patterns:
                if p in text_lower:
                    detected.append({
                        "type": offload_type,
                        "matched": p,
                        "risk": 0.6 if "authority" in offload_type else 0.4
                    })
        
        return {
            "offload_detected": len(detected) > 0,
            "patterns": detected,
            "risk": max([d["risk"] for d in detected]) if detected else 0.0
        }

def demo_scanner():
    """Demo motive scanner"""
    scanner = MotiveScanner()
    
    print("=" * 50)
    print("ULTERIOR MOTIVE INFERENCE")
    print("=" * 50)
    
    # Test texts
    tests = [
        ("I'm just asking, why do they hide this from us?", "user123"),
        ("But her emails from 2016 show...", "politician"),
        ("Everyone knows this is fake, experts confirm", "Influencer"),
        ("Studies show vaccines work, some worry about side effects", "scientist"),
        ("I use to believe differently but the evidence changed my mind", "user456"),
    ]
    
    for text, source in tests:
        print(f"\n📝 {text[:50]}...")
        
        # Motive scan
        result = scanner.scan_motive(text, source)
        print(f"   Agenda: {result['agenda_detected']} | Severity: {result['severity']:.0%}")
        print(f"   Risk: {result['risk_level']} | {result['recommendation']}")
        
        # Offload detection
        offload = scanner.offload_detection(text)
        if offload["offload_detected"]:
            print(f"   ⚠️  Offload: {offload['patterns']}")
        
        # Track narrative
        nid = f"claim_{hash(text)[:8]}"
        scanner.track_narrative(nid, text, source)
        
        # Recomposure risk
        risk = scanner.recomposition_risk(nid)
        print(f"   Recompose risk: {risk['status']}")
    
    # Position shift prediction
    print("\n🔮 Position Shift Prediction:")
    shift = scanner.predict_position_shift("user123", "pro")
    if shift:
        print(f"   {shift.from_stance} → {shift.to_stance}")
        print(f"   Timeline: {shift.timeline_hours}h")
        print(f"   Triggers: {shift.triggers}")
    
    return scanner

if __name__ == "__main__":
    demo_scanner()