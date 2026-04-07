#!/usr/bin/env python3
"""
Consumer AI Identity Protection System
Defends against: AI manipulation, data exploitation, identity theft, dark patterns.
LEGITIMATE DEFENSE ONLY - No offensive capabilities.
"""
import hashlib
import json
import re
from typing import Dict, List, Any, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

@dataclass
class IdentityAsset:
    """An identity asset to protect"""
    asset_type: str      # email, phone, address, biometric, ssn
    sensitivity: int     # 1-5
    exposed: bool = False
    last_checked: str = ""

@dataclass  
class Threat:
    """Identified threat to consumer"""
    threat_type: str     # doxxing, deepfake, phishing, social_engineering
    severity: int       # 1-5
    source: str        # Where detected
    mitigation: str    # How to defend

@dataclass
class ConsumerRight:
    """Consumer protection right"""
    law: str           # GDPR, CCPA, etc
    protection: str
    how_to_activate: str

class ConsumerIdentityDefense:
    """
    Consumer AI Identity Protection
    - Protects digital identity
    - Detects dark patterns  
    - Enforces consumer rights
    - Defends against AI manipulation
    """
    
    def __init__(self):
        self.assets: Dict[str, IdentityAsset] = {}
        self.threats: Dict[str, Threat] = {}
        self.rights: Dict[str, ConsumerRight] = {}
        self.dark_patterns: Dict[str, Dict] = {}
        self._init_assets()
        self._init_rights()
        self._init_dark_patterns()
    
    def _init_assets(self):
        """Initialize identity assets to track"""
        self.assets = {
            "email": IdentityAsset("email", 3, False),
            "phone": IdentityAsset("phone", 4, False),
            "address": IdentityAsset("address", 5, False),
            "biometric": IdentityAsset("biometric", 5, False),  
            "ssn": IdentityAsset("ssn", 5, False),
            "payment": IdentityAsset("payment", 5, False),
            "device_id": IdentityAsset("device_id", 3, False),
            "ip_address": IdentityAsset("ip_address", 2, False),
        }
    
    def _init_rights(self):
        """Initialize consumer protection rights"""
        self.rights = {
            "gdpr": ConsumerRight(
                "GDPR (EU)",
                "Right to access, delete, port data",
                "Request via company privacy page or email dpo@company.com"
            ),
            "ccpa": ConsumerRight(
                "CCPA (California)",
                "Right to know, delete, opt-out of sale",
                "Submit via state attorney general"
            ),
            "vcta": ConsumerRight(
                "VCTA (Virginia)", 
                "Right to opt-out of sale/profiling",
                "Request via company"
            ),
            "ferpa": ConsumerRight(
                "FERPA (Education)",
                "Access to education records",
                "Request from school district"
            ),
            "hipaa": ConsumerRight(
                "HIPAA (Health)",
                "Access to health data", 
                "Request from healthcare provider"
            ),
        }
    
    def _init_dark_patterns(self):
        """Initialize dark pattern detection"""
        self.dark_patterns = {
            "confirm_shaming": {
                "patterns": ["no, i dont want", "not now", "maybe later"],
                "severity": 3,
                "mitigation": "Use neutral language buttons"
            },
            "forced_action": {
                "patterns": ["you must", "required", "mandatory"],
                "severity": 4, 
                "mitigation": "Real choice without penalty"
            },
            "roach_motel": {
                "patterns": ["easy to join", "hard to leave", "cancel anytime"],
                "severity": 3,
                "mitigation": "Same effort to cancel as join"
            },
            "privacy_zuckering": {
                "patterns": ["share with friends", "connect socially"],
                "severity": 4,
                "mitigation": "Clear privacy controls"
            },
            "misdirection": {
                "patterns": ["gotcha", "oops", "accidentally"],
                "severity": 3,
                "mitigation": "Explicit opt-in"
            },
            "forced_continuity": {
                "patterns": ["free trial", "cancel anytime", "reminder"],
                "severity": 4,
                "mitigation": "Clear cancellation path"
            },
            "credit_hiding": {
                "patterns": ["no credit card", "free forever"],
                "severity": 3,
                "mitigation": "Full cost disclosure"
            },
        }
    
    def check_exposure(self, asset: str) -> Dict:
        """Check if identity asset is exposed"""
        if asset not in self.assets:
            return {"status": "unknown_asset"}
        
        a = self.assets[asset]
        
        return {
            "asset": asset,
            "sensitivity": a.sensitivity,
            "exposed": a.exposed,
            "last_checked": a.last_checked,
            "risk": "critical" if a.sensitivity > 4 and a.exposed else "high" if a.exposed else "low",
            "protection": self._get_protection(asset)
        }
    
    def _get_protection(self, asset: str) -> List[str]:
        """Get protection steps for asset"""
        protections = {
            "email": ["Use unique email", "Enable 2FA", "Check haveibeenpwned"],
            "phone": ["Use VoIP number", "Enable screening", "Check reversephone"],
            "ssn": ["Freeze credit", "Monitor credit", "Only provide when required"],
            "address": ["Use USPS mail forwarding", "Use privacy mail service"],
            "biometric": ["Opt-out where possible", "Use alternatives"],
            "payment": ["Use virtual cards", "Use single-use cards"],
        }
        return protections.get(asset, ["Limit sharing"])
    
    def scan_dark_patterns(self, text: str) -> Dict:
        """Scan for dark patterns in UI/text"""
        text_lower = text.lower()
        findings = []
        severity = 0
        
        for pattern_name, pattern_data in self.dark_patterns.items():
            matches = []
            for p in pattern_data["patterns"]:
                if p in text_lower:
                    matches.append(p)
            
            if matches:
                findings.append({
                    "pattern": pattern_name,
                    "matched": matches,
                    "severity": pattern_data["severity"],
                    "mitigation": pattern_data["mitigation"]
                })
                severity = max(severity, pattern_data["severity"])
        
        return {
            "text": text[:50],
            "dark_patterns_found": len(findings),
            "severity": severity,
            "findings": findings,
            "risk": "high" if severity > 3 else "medium" if severity > 1 else "low",
            "action": "DOCUMENT and REPORT" if severity > 3 else "DOCUMENT" if severity > 1 else "NO ACTION"
        }
    
    def check_ai_manipulation(self, content: str, context: str = "unknown") -> Dict:
        """Check for AI manipulation tactics"""
        content_lower = content.lower()
        
        # Manipulation patterns
        manipulations = {
            "urgency": {
                "patterns": ["limited time", "act now", "only today", "expires"],
                "severity": 3,
                "defense": "Take time to decide"
            },
            "scarcity": {
                "patterns": ["only 2 left", "sold out", "last chance"],
                "severity": 3,
                "defense": "Verify actual availability"
            },
            "social_proof": {
                "patterns": ["10,000 users", "best selling", "trusted by"],
                "severity": 2,
                "defense": "Check independent reviews"
            },
            "authority_claims": {
                "patterns": ["expert", "doctor", "professor", "scientific"],
                "severity": 2,
                "defense": "Verify credentials"
            },
            "fear": {
                "patterns": ["dont miss", "worst", "never", "miss out"],
                "severity": 3,
                "defense": "Verify the threat"
            },
            "reciprocity": {
                "patterns": ["free gift", "bonus", "just for you"],
                "severity": 1,
                "defense": "Return only if needed"
            },
        }
        
        findings = []
        severity = 0
        
        for manip, data in manipulations.items():
            matches = [p for p in data["patterns"] if p in content_lower]
            if matches:
                findings.append({
                    "type": manip,
                    "matches": matches,
                    "severity": data["severity"],
                    "defense": data["defense"]
                })
                severity = max(severity, data["severity"])
        
        return {
            "content": content[:50],
            "source": context,
            "manipulation_found": len(findings) > 0,
            "severity": severity,
            "findings": findings,
            "risk": "high" if severity > 2 else "medium" if severity > 0 else "low",
            "action": "VERIFY before acting" if severity > 0 else "PROCEED"
        }
    
    def request_data_deletion(self, company: str, jurisdiction: str = "gdpr") -> Dict:
        """Generate data deletion request"""
        right = self.rights.get(jurisdiction.lower())
        
        if not right:
            return {"error": "Unknown jurisdiction"}
        
        return {
            "type": f"{jurisdiction.upper()} Data Deletion Request",
            "to": company,
            "legal_basis": right.protection,
            "how": right.how_to_activate,
            "template": f"Under {right.law}, I request all my personal data be deleted within 30 days."
        }
    
    def generate_protection_report(self) -> Dict:
        """Generate consumer protection report"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "assets_tracked": len(self.assets),
            "assets_exposed": sum(1 for a in self.assets.values() if a.exposed),
            "rights_available": list(self.rights.keys()),
            "dark_patterns": len(self.dark_patterns),
            "contact": {
                "US_FTC": "reportfraud.ftc.gov",
                "EU": "edpb.europa.eu",
                "UK": "ico.org.uk"
            }
        }

def demo_defense():
    """Demo consumer defense"""
    defense = ConsumerIdentityDefense()
    
    print("=" * 50)
    print("CONSUMER IDENTITY PROTECTION")
    print("=" * 50)
    
    # Check exposure
    print("\n🔐 Asset Exposure:")
    for asset in ["email", "ssn", "biometric"]:
        result = defense.check_exposure(asset)
        print(f"   {asset}: {result.get('risk', 'unknown')}")
    
    # Scan dark patterns
    print("\n🌑 Dark Patterns:")
    test_ui = "Click YES to continue! You must act now - this offer expires!"
    result = defense.scan_dark_patterns(test_ui)
    print(f"   Found: {result['dark_patterns_found']} | Severity: {result['severity']}")
    for f in result["findings"]:
        print(f"   - {f['pattern']}: {f['mitigation']}")
    
    # AI manipulation
    print("\n🤖 AI Manipulation:")
    test_content = "Act now! Only 2 left! This expires today! Dont miss out!"
    result = defense.check_ai_manipulation(test_content)
    print(f"   Found: {result['manipulation_found']} | Severity: {result['severity']}")
    for f in result["findings"]:
        print(f"   - {f['type']}: {f['defense']}")
    
    # Request deletion
    print("\n📨 Deletion Request:")
    req = defense.request_data_deletion("Company.com", "gdpr")
    print(f"   {req['type']}")
    print(f"   Template: {req['template']}")
    
    # Report
    print("\n📋 Report:")
    report = defense.generate_protection_report()
    print(f"   Assets: {report['assets_tracked']}")
    print(f"   Rights: {report['rights_available']}")
    
    return defense

if __name__ == "__main__":
    demo_defense()