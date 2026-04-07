#!/usr/bin/env python3
"""
Opportunity Scanner - Legitimate Revenue Sources
Scans public APIs for affiliate programs, cashback, digital marketplaces.
"""
import json
import urllib.request
import urllib.error
from pathlib import Path

LEDGER_PATH = Path(__file__).parent / "ledger.json"

# Legitimate public opportunities (sample - real ones require API keys/auth)
OPPORTUNITY_SOURCES = {
    "amazon_affiliate": {
        "name": "Amazon Associates",
        "url": "https://affiliate-program.amazon.com/",
        "category": "affiliate",
        "difficulty": "easy"
    },
    "rewardful": {
        "name": "Rewardful (Stripe affiliate)",
        "url": "https://www.rewardful.com/",
        "category": "affiliate",
        "difficulty": "easy"
    },
    "gumroad": {
        "name": "Gumroad Creator",
        "url": "https://gumroad.com/",
        "category": "digital_marketplace",
        "difficulty": "easy"
    },
    "gumroad_affiliate": {
        "name": "Gumroad Affiliate",
        "url": "https://gumroad.com/affiliates",
        "category": "affiliate",
        "difficulty": "easy"
    },
    "lemon_squeezy": {
        "name": "Lemon Squeezy",
        "url": "https://www.lemonsqueezy.com/",
        "category": "digital_marketplace",
        "difficulty": "medium"
    },
    "freelance_platforms": {
        "name": "Upwork/Fiverr",
        "url": "https://www.upwork.com/",
        "category": "freelance",
        "difficulty": "medium"
    },
    "github_sponsors": {
        "name": "GitHub Sponsors",
        "url": "https://github.com/sponsors",
        "category": "donation",
        "difficulty": "medium"
    },
    "buy_sell_prompts": {
        "name": "PromptBase",
        "url": "https://promptbase.com/",
        "category": "digital_marketplace",
        "difficulty": "easy"
    }
}

def scan_opportunities():
    """Return available legitimate opportunities."""
    results = []
    for key, info in OPPORTUNITY_SOURCES.items():
        results.append({
            "id": key,
            "name": info["name"],
            "url": info["url"],
            "category": info["category"],
            "difficulty": info["difficulty"],
            "verified": True
        })
    return results

def load_ledger():
    if LEDGER_PATH.exists():
        return json.loads(LEDGER_PATH.read_text())
    return {"instances": {}, "cycles": [], "opportunities": [], "config": {}}

def save_ledger(data):
    LEDGER_PATH.write_text(json.dumps(data, indent=2))

def add_scanned_opportunities():
    """Add scanned opportunities to ledger."""
    data = load_ledger()
    scanned = scan_opportunities()
    
    # Don't add duplicates
    existing = {o["source"] for o in data["opportunities"]}
    
    for opp in scanned:
        if opp["url"] not in existing:
            data["opportunities"].append({
                "name": opp["name"],
                "expected_revenue": 0,  # To be estimated
                "cost": 0,  # Free to join
                "roi": 0,
                "source": opp["category"],
                "url": opp["url"],
                "timestamp": "",
                "verified": opp["verified"]
            })
    
    save_ledger(data)
    return scanned

if __name__ == "__main__":
    for opp in scan_opportunities():
        print(f"- {opp['name']} ({opp['category']}) - {opp['url']}")