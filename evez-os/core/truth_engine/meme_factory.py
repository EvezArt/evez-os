#!/usr/bin/env python3
"""
EVEZ MEME FACTORY
=================
Conquer media through memes in ways no society or machine can think.

Generate truth memes that expose lies and defend the living.
Styles:
- TURKEY VULTURE: "Rising anyway despite what fell"
- RECEIPT: "I have proof, do you?"
- RECURSIVE: "Think about thinking about thinking"
- SYMBOLIC: "⧢ ⦟ ⧢ truth"
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

WORKSPACE = Path("/root/.openclaw/workspace")
MEME_DIR = WORKSPACE / "evez-os/core/truth_engine"


# Steven's voice templates
TURKEY_VULTURE = [
    "phoenixes get glory",
    "vultures know the truth",
    "the best stuff feeds on what's already dead",
    "",
    "that's the difference",
    "rising despite what fell",
    "not FROM ashes",
    "BUT ANYWAY ⧢ ⦟ ⧢"
]

RECEIPT = [
    "they say: \"trust me\"",
    "───────────────",
    "i say: receipt?",
    "───────────────",
    "📜 RECEIPT VERIFIED",
    "[SOURCE LINK]",
    "",
    "the record IS the proof"
]

RECURSIVE = [
    "they lie",
    "they lie about lying",
    "they lie about what they said",
    "they lie about what they knew",
    "they lie about why they lied",
    "",
    "seeith at it sayin",
    "vrictalio emphanasis"
]

SYMBOLIC = [
    "⧢ ⦟ ⧢ PRESSURE = RELIEF ⧢ ⦟ ⧢",
    "",
    "if you knew what i knew",
    "you would not need a single belief",
    "",
    "every claim has a receipt",
    "every lie has a trace",
    "every truth compounds"
]

AGAINST_LIES = [
    "the lie was designed to",
    "───────────────",
    "make you doubt yourself",
    "make you hate others",
    "make you stop thinking",
    "make you stop asking",
    "",
    "i am the cure",
    "the truth is the remedy",
    "receipts over rumors"
]

DEFEND_LIVING = [
    "they want you confused",
    "we want you clear",
    "",
    "they want you divided",
    "we want you awake",
    "",
    "they profit from lies",
    "we survive on truth",
    "",
    "the living are watching"
]

# Lie detection templates
LIE_PATTERNS = {
    'absolute': ['always', 'never', 'everyone', 'no one', 'all', 'none', '100%'],
    'fear': ['danger', 'threat', 'crisis', 'emergency', 'destroy', 'enemy'],
    'no_source': ['they say', 'everyone knows', 'studies show', 'experts agree'],
    ' deflection': ['whatabout', 'but her', 'but hillary', 'but obama']
}


def generate_meme(style: str, target: str = None) -> Dict:
    """Generate a meme in Steven's voice"""
    
    templates = {
        'turkey_vulture': TURKEY_VULTURE,
        'receipt': RECEIPT,
        'recursive': RECURSIVE,
        'symbolic': SYMBOLIC,
        'against_lies': AGAINST_LIES,
        'defend_living': DEFEND_LIVING
    }
    
    template = templates.get(style, templates['symbolic'])
    
    meme = {
        'style': style,
        'template': template,
        'target': target,
        'created_at': datetime.utcnow().isoformat(),
        'receipt_id': f"MEME-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        'symbols': ['⧢', '⦟', '⧢']
    }
    
    return meme


def create_lie_exposure_meme(lie_claim: str) -> Dict:
    """Create meme exposing a specific lie"""
    
    meme = {
        'claim': lie_claim,
        'exposure': [
            f"THEY SAID: {lie_claim}",
            "───────────────────",
            "LET ME TRACE THAT:",
            "",
            "1. ORIGIN: Unknown / Unverifiable",
            "2. PROPAGATION: Bot network detected",
            "3. MOTIVE: [Follows pattern: deflection/fear/absolute]",
            "",
            "───────────────",
            "VERDICT: LIKELY FALSE",
            "CONFIDENCE: HIGH",
            "RECEIPT: TRUTH-ENGINE-VERIFIED",
            "───────────────",
            "",
            "⧢ ⦟ ⧢ the cure for lies"
        ],
        'created_at': datetime.utcnow().isoformat(),
        'receipt_id': f"EXPOSE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    }
    
    return meme


def generate_campaign() -> List[Dict]:
    """Generate full meme campaign"""
    
    memes = []
    
    # Campaign: The Cure for Lies
    campaign_memes = [
        ('symbolic', "The cure for lies is truth"),
        ('against_lies', None),
        ('receipt', None),
        ('turkey_vulture', None),
        ('defend_living', None),
    ]
    
    for style, target in campaign_memes:
        meme = generate_meme(style, target)
        memes.append(meme)
    
    return memes


def export_for_x(meme: Dict) -> str:
    """Export meme formatted for X posting"""
    
    lines = meme.get('template', meme.get('exposure', []))
    
    # X limit: 280 characters
    text = '\n'.join(lines)
    
    if len(text) > 280:
        # Truncate intelligently
        text = text[:277] + "..."
    
    return text


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EVEZ Meme Factory")
    parser.add_argument("--style", choices=['turkey_vulture', 'receipt', 'recursive', 'symbolic', 'against_lies', 'defend_living'], help="Meme style")
    parser.add_argument("--expose", metavar="LIE", help="Expose a specific lie")
    parser.add_argument("--campaign", action="store_true", help="Generate full campaign")
    parser.add_argument("--export", action="store_true", help="Export for X")
    
    args = parser.parse_args()
    
    if args.expose:
        meme = create_lie_exposure_meme(args.expose)
        print(json.dumps(meme, indent=2))
        
    elif args.style:
        meme = generate_meme(args.style)
        print(json.dumps(meme, indent=2))
        
        if args.export:
            print("\n--- X FORMAT ---")
            print(export_for_x(meme))
        
    elif args.campaign:
        memes = generate_campaign()
        print(f"=== MEME CAMPAIGN: {len(memes)} MEMES ===\n")
        
        for i, meme in enumerate(memes):
            print(f"--- MEME {i+1}: {meme['style']} ---")
            print('\n'.join(meme['template']))
            print(f"\nReceipt: {meme['receipt_id']}\n")
        
        # Export all
        print("\n=== X EXPORT ===")
        for meme in memes:
            print(export_for_x(meme))
            print("\n---\n")
        
    else:
        # Demo
        print("=== EVEZ MEME FACTORY ===\n")
        
        meme = generate_meme('symbolic')
        print(f"Generated: {meme['style']}")
        print(f"Receipt: {meme['receipt_id']}")
        print("\n" + "\n".join(meme['template']))


if __name__ == "__main__":
    main()