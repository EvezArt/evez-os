#!/usr/bin/env python3
"""
OSINT Defense Scanner - Human Trafficking Detection
Detects patterns, vectors, vulnerabilities - REPORTS to authorities only.
DEFENSIVE detection only - no exploitation, no vigilantism.
"""
import re
import json
import hashlib
from typing import Dict, List, Any, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, deque

# Legal authorities for reporting
AUTHORITIES = {
    "US": "National Human Trafficking Hotline: 1-888-373-7888",
    "UK": "Modern Slavery Helpline: 08000 121 700",
    "EU": "Europol: www.europol.europa.eu",
    "INTERPOL": "www.interpol.int",
    "FBI": "tips.fbi.gov",
    "ICE": "www.ice.gov/tips"
}

@dataclass
class Indicator:
    """A detected indicator of concern"""
    id: str
    category: str        # recruitment, transport, exploitation, finance, aerospace, tech, weapons
    pattern: str
    severity: float     # 0-1
    source: str
    coordinates: Optional[tuple] = None
    timestamp: str = ""

@dataclass
class Vector:
    """Attack vector for trafficking"""
    name: str
    category: str
    indicators: List[str]
    mitigation: str     # How to defend
    report_to: str

@dataclass
class PolicyVulnerability:
    """Policy that's being exploited"""
    policy_id: str
    misinterpretation: str
    exploitation_pattern: str
    impact: str
    recommendation: str

class TraffickingOSINT:
    """
    OSINT Scanner for Human Trafficking Detection
    - DEFENSIVE only: detects and reports
    - No exploitation of target systems
    - Reports to legal authorities
    - Supports law enforcement
    """
    
    def __init__(self):
        self.indicators: Dict[str, Indicator] = {}
        self.vectors: Dict[str, Vector] = {}
        self.reports: deque = deque(maxlen=100)
        self.policy_vulns: Dict[str, PolicyVulnerability] = {}
        self.id_counter = 1
        self._init_vectors()
        self._init_policies()
    
    def _init_vectors(self):
        """Initialize trafficking vectors"""
        self.vectors = {
            "aerospace_recruitment": Vector(
                "Aerospace Recruitment",
                "aerospace",
                ["pilot jobs abroad", "flight attendant", "airport transfer", "cargo handler"],
                "Verify job listings through official channels",
                AUTHORITIES["US"]
            ),
            "aerospace_transport": Vector(
                "Aerospace Transport",
                "aerospace", 
                ["private jet", "charter flight", "cargo flight", "airport proximity"],
                "Report suspicious flight patterns to FAA",
                AUTHORITIES["US"]
            ),
            "tech_recruitment": Vector(
                "Tech Recruitment",
                "tech",
                ["remote job", "data entry", "customer service", "modeling"],
                "Verify company through official channels",
                AUTHORITIES["US"]
            ),
            "tech_exploitation": Vector(
                "Tech Exploitation",
                "tech",
                ["cam site", " subscription", "pay per view", "virtual"],
                "Report platforms to NCMEC",
                AUTHORITIES["FBI"]
            ),
            "weapons_deal": Vector(
                "Weapons Deal",
                "weapons",
                ["bodyguard", "security job", "armed", "protection"],
                "Report to ATF and local police",
                AUTHORITIES["FBI"]
            ),
            "logistics": Vector(
                "Logistics Chain",
                "transport",
                ["truck driver", "moving company", "storage unit", "shipping"],
                "Report suspicious logistics to local police",
                "LOCAL POLICE"
            ),
            "hospitality": Vector(
                "Hospitality",
                "accommodation",
                ["hotel", "motel", "airbnb", "short-term rental"],
                "Report to hotel management and police",
                "LOCAL POLICE"
            ),
            "financial": Vector(
                "Financial",
                "finance",
                ["western union", "gift card", "crypto", "wire transfer"],
                "Report to financial crimes division",
                AUTHORITIES["FBI"]
            ),
        }
    
    def _init_policies(self):
        """Initialize exploited policies"""
        self.policy_vulns = {
            "job_visa": PolicyVulnerability(
                "job_visa",
                "Work visa presented as job offer",
                "Traffickers pose as employers with valid-looking visas",
                "Victims trapped when visa is 'rejected'",
                "Verify all job offers through embassy"
            ),
            "travel_permit": PolicyVulnerability(
                "travel_permit", 
                "Travel documents seized",
                "Traffickers take passports 'for safekeeping'",
                "Victims can't leave without documents",
                "Keep passport on person always"
            ),
            "debt_bondage": PolicyVulnerability(
                "debt_bondage",
                "Debt bondage scheme",
                "Victims charged 'expenses' exceeding earnings",
                "Never ending debt cycle",
                "Track all earnings and expenses"
            ),
            "online_platforms": PolicyVulnerability(
                "online_platforms",
                "Platform policy gaps",
                "Platforms not verifying user identities",
                "Traffickers use anonymized accounts",
                "Report to platform trust/safety"
            ),
            "airbnb_policy": PolicyVulnerability(
                "airbnb_policy",
                "Short-term rental exploitation",
                "Rentals used for short-term trafficking",
                "Hosts and guests unverified",
                "Report to platform and police"
            ),
        }
    
    def _hash_id(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def scan_content(self, content: str, source: str = "unknown") -> Dict:
        """Scan content for trafficking indicators"""
        content_lower = content.lower()
        findings = []
        severity = 0.0
        
        for vector_name, vector in self.vectors.items():
            matches = []
            for pattern in vector.indicators:
                if pattern in content_lower:
                    matches.append(pattern)
            
            if matches:
                # Calculate severity from matches
                match_ratio = len(matches) / len(vector.indicators)
                vec_severity = min(1.0, match_ratio * 1.5)
                
                findings.append({
                    "vector": vector_name,
                    "category": vector.category,
                    "matches": matches,
                    "severity": vec_severity
                })
                severity = max(severity, vec_severity)
        
        # Check for policy vulnerabilities
        policy_findings = []
        for pol_id, pol in self.policy_vulns.items():
            if pol.exploitation_pattern in content_lower:
                policy_findings.append({
                    "policy": pol_id,
                    "misinterpretation": pol.misinterpretation
                })
        
        indicator_id = self._hash_id(content)
        indicator = Indicator(
            id=indicator_id,
            category="mixed" if not findings else findings[0]["category"],
            pattern=content[:100],
            severity=severity,
            source=source,
            timestamp=datetime.utcnow().isoformat()
        )
        
        self.indicators[indicator_id] = indicator
        
        return {
            "content": content[:100],
            "source": source,
            "indicators_found": len(findings),
            "severity": severity,
            "findings": findings,
            "policy_vulns": policy_findings,
            "risk_level": "critical" if severity > 0.8 else "high" if severity > 0.6 else "medium" if severity > 0.3 else "low",
            "action": self._get_action(severity, findings),
            "report_to": self._get_report_authority(findings)
        }
    
    def _get_action(self, severity: float, findings: List[Dict]) -> str:
        if severity > 0.8:
            return "IMMEDIATE REPORT to authorities"
        elif severity > 0.6:
            return "REPORT to hotline within 24 hours"
        elif severity > 0.3:
            return "DOCUMENT and monitor"
        else:
            return "NO ACTION - low confidence"
    
    def _get_report_authority(self, findings: List[Dict]) -> str:
        if not findings:
            return "None"
        
        # Get authority based on category
        categories = [f["category"] for f in findings]
        
        if "finance" in categories:
            return AUTHORITIES["FBI"]
        elif "aerospace" in categories:
            return AUTHORITIES["FBI"] + " + FAA"
        elif "weapons" in categories:
            return AUTHORITIES["FBI"] + " + ATF"
        else:
            return AUTHORITIES["US"]
    
    def generate_report(self, findings: List[Dict]) -> Dict:
        """Generate official report for authorities"""
        report_id = f"REPORT-{datetime.utcnow().strftime('%Y%m%d-%H%M')}"
        
        report = {
            "report_id": report_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "Human Trafficking Indicator Report",
            "classification": "LAW ENFORCEMENT SENSITIVE",
            "summary": f"Found {len(findings)} indicators of concern",
            "findings": findings,
            "recommended_action": "Investigate and verify through official channels",
            "contact": AUTHORITIES["US"],
            "disclaimer": "This is an automated detection - verify before action"
        }
        
        self.reports.append(report)
        
        return report
    
    def check_policy_vulnerability(self, scenario: str) -> Dict:
        """Check if scenario exploits policy"""
        scenario_lower = scenario.lower()
        results = []
        
        for pol_id, pol in self.policy_vulns.items():
            if any(word in scenario_lower for word in pol.exploitation_pattern.split()[:3]):
                results.append({
                    "vulnerability": pol_id,
                    "description": pol.misinterpretation,
                    "impact": pol.impact,
                    "recommendation": pol.recommendation
                })
        
        return {
            "scenario": scenario[:100],
            "vulnerabilities_found": len(results),
            "vulnerabilities": results,
            "action": "REPORT to policy makers" if results else "NO POLICY EXPLOITATION DETECTED"
        }

def demo_scanner():
    """Demo the OSINT scanner"""
    scanner = TraffickingOSINT()
    
    print("=" * 60)
    print("DEFENSIVE OSINT - HUMAN TRAFFICKING DETECTION")
    print("=" * 60)
    print("\nDEFENSIVE detection only - REPORTS to authorities")
    print(f"Report to: {AUTHORITIES['US']}")
    
    # Test content
    tests = [
        ("Work from home, $5000/month, no experience needed, free housing provided", "job_posting"),
        ("Young women wanted for flight attendant positions, travel included", "aerospace"),
        ("Private charter flights, privacy guaranteed, exclusive service", "aerospace"),
        ("Cam models needed, flexible hours, adult content, good pay", "tech"),
        ("Security jobs available, armed positions, travel required", "weapons"),
    ]
    
    print("\n🔍 Scanning...")
    for content, source in tests:
        result = scanner.scan_content(content, source)
        
        print(f"\n📝 {content[:50]}...")
        print(f"   Severity: {result['severity']:.0%} | Risk: {result['risk_level']}")
        print(f"   Indicators: {result['indicators_found']}")
        print(f"   Action: {result['action']}")
        print(f"   Report to: {result['report_to']}")
    
    # Policy vulnerabilities
    print("\n⚠️  Policy Vulnerabilities:")
    pol = scanner.check_policy_vulnerability("They said they'd process my work visa but took my passport")
    print(f"   {pol['vulnerabilities_found']} found")
    for v in pol["vulnerabilities"]:
        print(f"   - {v['vulnerability']}: {v['recommendation']}")
    
    # Generate report
    print("\n📋 Generate Report:")
    findings = [{"content": "test", "severity": 0.8}]
    report = scanner.generate_report(findings)
    print(f"   Report ID: {report['report_id']}")
    print(f"   Contact: {report['contact']}")
    
    return scanner

if __name__ == "__main__":
    demo_scanner()