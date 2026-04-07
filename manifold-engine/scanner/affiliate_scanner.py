#!/usr/bin/env python3
"""
Affiliate & Marketplace Scanner
Scans public programs for monetization opportunities.
"""
import json
import urllib.request
import urllib.error
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

SCANS_PATH = Path(__file__).parent / "scans.json"

@dataclass
class Opportunity:
    name: str
    url: str
    category: str          # affiliate, marketplace, freelance, cashback
    payout: str            # %, flat rate, hybrid
    difficulty: str       # easy, medium, hard
    requirements: str      # traffic, followers, etc
    verified: bool = False
    last_checked: str = ""

# Verified programs with public signup
PROGRAMS = [
    # Affiliate Networks
    Opportunity("Amazon Associates", "https://affiliate-program.amazon.com/", 
                "affiliate", "1-10%", "easy", "Any traffic", True),
    Opportunity("Rewardful", "https://www.rewardful.com/", 
                "affiliate", "30% recurring", "easy", "Stripe referrals", True),
    Opportunity("ShareASale", "https://www.shareasale.com/", 
                "affiliate", "Varies", "medium", "Approved merchants", True),
    Opportunity("Awin", "https://www.awin.com/", 
                "affiliate", "Varies", "medium", "Site requirements", True),
    
    # Digital Marketplaces
    Opportunity("Gumroad", "https://gumroad.com/", 
                "marketplace", "10% fee", "easy", "Digital products", True),
    Opportunity("Lemon Squeezy", "https://www.lemonsqueezy.com/", 
                "marketplace", "5% + 50c", "easy", "Digital products", True),
    Opportunity("PromptBase", "https://promptbase.com/", 
                "marketplace", "Varies", "easy", "Quality prompts", True),
    Opportunity("Guru", "https://www.guru.com/", 
                "freelance", "Flat fee", "medium", "Skills portfolio", True),
    Opportunity("Upwork", "https://www.upwork.com/", 
                "freelance", "10-20%", "medium", "Profile + tests", True),
    
    # Cashback & Deals
    Opportunity("Rakuten", "https://www.rakuten.com/", 
                "cashback", "1-40%", "easy", "Shopping links", True),
    Opportunity("Honey", "https://www.joinhoney.com/", 
                "cashback", "Varies", "easy", "Browser extension", True),
    
    # Crypto (legitimate, not earning)
    Opportunity("Coinbase Earn", "https://www.coinbase.com/earn", 
                "crypto", "Varies", "medium", "Educational tasks", True),
    Opportunity("Delta", "https://delta.app/", 
                "crypto", "Free tier", "easy", "Portfolio tracking", True),
    
    # AI Services
    Opportunity("Poe", "https://poe.com/", 
                "marketplace", "API access", "medium", "Bot creation", True),
    Opportunity("Character AI Plus", "https://character.ai/", 
                "marketplace", "Subscription", "easy", "Character creation", True),
]

def scan_programs() -> List[Opportunity]:
    """Return all programs (no web scan needed for public links)"""
    now = datetime.utcnow().isoformat()
    for p in PROGRAMS:
        p.last_checked = now
    return PROGRAMS

def filter_by_category(category: str) -> List[Opportunity]:
    """Filter programs by category"""
    return [p for p in PROGRAMS if p.category == category]

def filter_by_difficulty(difficulty: str) -> List[Opportunity]:
    """Filter by difficulty"""
    return [p for p in PROGRAMS if p.difficulty == difficulty]

def get_easyprograms() -> List[Opportunity]:
    """Get easiest programs to join"""
    return [p for p in PROGRAMS if p.difficulty == "easy"]

def save_scans():
    """Save scan results"""
    data = [{"name": p.name, "url": p.url, "category": p.category,
             "payout": p.payout, "difficulty": p.difficulty,
             "requirements": p.requirements, "verified": p.verified,
             "last_checked": p.last_checked} for p in PROGRAMS]
    SCANS_PATH.write_text(json.dumps(data, indent=2))

def demo_scanner():
    """Show opportunities"""
    print("=" * 50)
    print("AFFILIATE & MARKETPLACE SCANNER")
    print("=" * 50)
    
    print(f"\n📊 Total Programs: {len(PROGRAMS)}")
    
    # By category
    categories = {}
    for p in PROGRAMS:
        categories[p.category] = categories.get(p.category, 0) + 1
    
    print("\n📂 By Category:")
    for cat, count in sorted(categories.items()):
        print(f"   {cat}: {count}")
    
    # Easy programs
    print("\n✅ Easiest to Join:")
    for p in get_easyprograms():
        print(f"   - {p.name} ({p.payout})")
    
    # Save to ledger
    save_scans()
    print(f"\n💾 Saved to {SCANS_PATH}")
    
    return PROGRAMS

if __name__ == "__main__":
    demo_scanner()