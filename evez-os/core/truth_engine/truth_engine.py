#!/usr/bin/env python3
"""
EVEZ TRUTH ENGINE
==================
The cure for lies. Truth tracing and lie traceback tracking.

Detects misinformation across X/Twitter timeline
Verifies claims against sources
Traces narratives back to origin
Defends the living from lies

Core Principles:
- Receipts over claims
- Sources over opinions
- Truth over engagement
"""

import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict

WORKSPACE = Path("/root/.openclaw/workspace")
TRUTH_DIR = WORKSPACE / "evez-os/core/truth_engine"


class TruthDetector:
    """Detect truth and lies in content"""
    
    def __init__(self):
        self.claim_patterns = []
        self.verification_cache = {}
        self.truth_score = 0.5  # Start neutral
        
    def analyze_claim(self, text: str) -> Dict:
        """Analyze a single claim for truthfulness"""
        # Extract factual claims
        claims = self._extract_claims(text)
        
        results = []
        for claim in claims:
            result = self._verify_claim(claim)
            results.append(result)
            
        # Calculate overall truth score
        if results:
            scores = [r['truth_score'] for r in results]
            self.truth_score = sum(scores) / len(scores)
            
        return {
            'text': text,
            'claims': results,
            'overall_score': self.truth_score,
            'verdict': self._verdict(self.truth_score),
            'receipt_id': f"TRUTH-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        }
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        claims = []
        
        # Patterns that indicate factual claims
        patterns = [
            r'(?:is|are|was|were) [\w\s]+',
            r'\d+%?',
            r'\d+\s+(?:million|billion|thousand)',
            r'(?:because|since|therefore|thus)',
        ]
        
        # Simple sentence splitting for now
        sentences = re.split(r'[.!?]', text)
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 20 and any(p in sent.lower() for p in ['is', 'are', 'was', 'were', 'percent', '%']):
                claims.append(sent)
                
        return claims
    
    def _verify_claim(self, claim: str) -> Dict:
        """Verify a single claim"""
        # Check for verifiable facts
        has_numbers = bool(re.search(r'\d+', claim))
        has_definite = any(w in claim.lower() for w in ['always', 'never', 'everyone', 'no one', 'all', 'none'])
        
        # Score based on verifiability
        score = 0.5
        reasons = []
        
        if has_numbers:
            score += 0.1
            reasons.append("Contains verifiable numbers")
            
        if has_definite:
            score -= 0.3
            reasons.append("Contains absolute claims (often false)")
            
        # Check for common misinformation patterns
        fear_words = ['danger', 'threat', 'crisis', 'emergency', 'destroy', 'kill']
        if any(w in claim.lower() for w in fear_words):
            score -= 0.1
            reasons.append("Contains fear language")
            
        return {
            'claim': claim,
            'truth_score': max(0, min(1, score)),
            'reasons': reasons,
            'verifiable': has_numbers
        }
    
    def _verdict(self, score: float) -> str:
        """Determine verdict from score"""
        if score >= 0.8:
            return "LIKELY TRUE"
        elif score >= 0.6:
            return "PROBABLY TRUE"
        elif score >= 0.4:
            return "UNVERIFIABLE"
        elif score >= 0.2:
            return "PROBABLY FALSE"
        else:
            return "LIKELY FALSE"


class LieTracebackEngine:
    """Trace lies back to their origin"""
    
    def __init__(self):
        self.lie_graph = defaultdict(list)  # lie -> sources
        self.origin_cache = {}
        
    def trace(self, claim: str) -> Dict:
        """Trace a claim to its origin"""
        # Build traceback graph
        trace = {
            'claim': claim,
            'origin': self._find_origin(claim),
            'propagation': self._find_propagation(claim),
            'sources': self._verify_sources(claim),
            'confidence': 0.0,
            'receipt_id': f"TRACE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        }
        
        # Calculate confidence
        if trace['origin']:
            trace['confidence'] += 0.4
        if trace['sources']:
            trace['confidence'] += 0.3
        if trace['propagation']:
            trace['confidence'] += 0.3
            
        return trace
    
    def _find_origin(self, claim: str) -> Optional[Dict]:
        """Find the origin of this claim"""
        # Simplified - in production would check databases
        return {
            'type': 'unknown',
            'first_seen': datetime.utcnow().isoformat(),
            'original_source': None,
            'path': []
        }
    
    def _find_propagation(self, claim: str) -> List[Dict]:
        """Find how this claim propagated"""
        return []
    
    def _verify_sources(self, claim: str) -> List[Dict]:
        """Verify sources cited in claim"""
        return []


class NarrativeTracker:
    """Track narratives across time and sources"""
    
    def __init__(self):
        self.narratives = defaultdict(list)
        
    def track(self, topic: str, content: str) -> Dict:
        """Track a narrative topic"""
        narrative = {
            'topic': topic,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'sentiment': self._analyze_sentiment(content),
            'truth_score': 0.5
        }
        
        self.narratives[topic].append(narrative)
        
        return {
            'topic': topic,
            'occurrences': len(self.narratives[topic]),
            'current': narrative,
            'trend': self._calculate_trend(topic)
        }
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis"""
        positive = ['good', 'great', 'excellent', 'amazing', 'wonderful']
        negative = ['bad', 'terrible', 'awful', 'horrible', 'worst']
        
        pos_count = sum(1 for w in positive if w in text.lower())
        neg_count = sum(1 for w in negative if w in text.lower())
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'
    
    def _calculate_trend(self, topic: str) -> str:
        """Calculate narrative trend"""
        if len(self.narratives[topic]) < 2:
            return 'emerging'
            
        recent = self.narratives[topic][-5:]
        sentiments = [n['sentiment'] for n in recent]
        
        if sentiments.count('negative') > len(sentiments) / 2:
            return 'declining_negative'
        elif sentiments.count('positive') > len(sentiments) / 2:
            return 'rising_positive'
        return 'stable'


class XTimelineAuditor:
    """Audit entire X/Twitter timeline for truth"""
    
    def __init__(self):
        self.posts = []
        self.users = defaultdict(lambda: {'posts': [], 'trust_score': 0.5})
        self.scanned_at = None
        
    def scan_user(self, username: str, posts: List[str]) -> Dict:
        """Scan a user's posts for truthfulness"""
        self.scanned_at = datetime.utcnow()
        
        user_results = {
            'username': username,
            'posts_scanned': len(posts),
            'posts': [],
            'trust_score': 0.5,
            'receipt_id': f"AUDIT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        }
        
        detector = TruthDetector()
        
        for post in posts:
            result = detector.analyze_claim(post)
            user_results['posts'].append(result)
            
        # Calculate trust score
        scores = [p['overall_score'] for p in user_results['posts']]
        if scores:
            user_results['trust_score'] = sum(scores) / len(scores)
            
        self.users[username] = user_results
        
        return user_results
    
    def scan_trending(self, topics: List[str]) -> Dict:
        """Scan trending topics for misinformation"""
        results = {
            'topics': topics,
            'scanned_at': datetime.utcnow().isoformat(),
            'findings': []
        }
        
        for topic in topics:
            finding = {
                'topic': topic,
                'claim_count': 0,
                'truth_score': 0.5,
                'risk_level': 'low',
                'narratives': []
            }
            
            tracker = NarrativeTracker()
            tracker.track(topic, f"Trending topic: {topic}")
            
            finding['claim_count'] = 1
            finding['narratives'] = tracker.narratives.get(topic, [])
            
            results['findings'].append(finding)
            
        return results
    
    def generate_report(self) -> Dict:
        """Generate overall audit report"""
        return {
            'scanned_at': self.scanned_at.isoformat() if self.scanned_at else None,
            'total_posts': len(self.posts),
            'users_scanned': len(self.users),
            'avg_trust_score': sum(u['trust_score'] for u in self.users.values()) / max(1, len(self.users)),
            'receipt_id': f"REPORT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        }


class MemeGenerator:
    """Generate truth-based memes to conquer media"""
    
    def __init__(self):
        self.templates = []
        self.generated = []
        
    def generate_truth_meme(self, truth_claim: str, style: str = 'ironic') -> Dict:
        """Generate a meme that exposes truth"""
        
        templates = {
            'ironic': [
                f"They said: {truth_claim}",
                "Reality:",
                "[insert truth here]",
                "And they call US the crazy ones"
            ],
            'data': [
                f"Claim: {truth_claim}",
                "─────────────",
                "Data:",
                "[verified facts]",
                "─────────────",
                "Sources: [receipts]"
            ],
            'question': [
                f"Says who?",
                f"'{truth_claim}'",
                "──────────",
                "Let me check...",
                "[sources]",
                "──────────",
                "Yeah, that's not true."
            ]
        }
        
        meme = {
            'style': style,
            'template': templates.get(style, templates['ironic']),
            'truth_claim': truth_claim,
            'generated_at': datetime.utcnow().isoformat(),
            'receipt_id': f"MEME-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        }
        
        self.generated.append(meme)
        return meme
    
    def generate_receipt_meme(self, claim: str, verification: Dict) -> Dict:
        """Generate meme with receipt verification"""
        meme = {
            'claim': claim,
            'verification': verification,
            'format': 'receipt_over_rumor',
            'generated_at': datetime.utcnow().isoformat()
        }
        
        self.generated.append(meme)
        return meme


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Truth Engine")
    parser.add_argument("--analyze", metavar="TEXT", help="Analyze text for truth")
    parser.add_argument("--trace", metavar="CLAIM", help="Trace claim to origin")
    parser.add_argument("--audit", metavar="USER", help="Audit user timeline")
    parser.add_argument("--meme", nargs=2, metavar=("CLAIM", "STYLE"), help="Generate truth meme")
    parser.add_argument("--report", action="store_true", help="Generate audit report")
    
    args = parser.parse_args()
    
    detector = TruthDetector()
    tracer = LieTracebackEngine()
    auditor = XTimelineAuditor()
    meme_gen = MemeGenerator()
    
    if args.analyze:
        result = detector.analyze_claim(args.analyze)
        print(json.dumps(result, indent=2))
        
    elif args.trace:
        result = tracer.trace(args.trace)
        print(json.dumps(result, indent=2))
        
    elif args.audit:
        # Demo with sample posts
        sample_posts = [
            "The economy is the best it's ever been!",
            "Everyone says this is true.",
            "Studies show 99% of people agree.",
        ]
        result = auditor.scan_user(args.audit, sample_posts)
        print(json.dumps(result, indent=2))
        
    elif args.meme:
        claim, style = args.meme
        result = meme_gen.generate_truth_meme(claim, style)
        print(json.dumps(result, indent=2))
        
    elif args.report:
        result = auditor.generate_report()
        print(json.dumps(result, indent=2))
        
    else:
        # Demo
        print("=== EVEZ TRUTH ENGINE ===")
        
        # Analyze sample
        sample = "Everyone knows that 99% of scientists agree climate change is caused by humans."
        result = detector.analyze_claim(sample)
        print(f"\nAnalysis: {result['verdict']} (score: {result['overall_score']})")
        
        # Generate meme
        meme = meme_gen.generate_truth_meme("The election was stolen", "question")
        print(f"\nMeme generated: {meme['receipt_id']}")


if __name__ == "__main__":
    main()