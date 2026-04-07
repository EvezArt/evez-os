#!/usr/bin/env python3
"""
PRODUCTION ENGINE - Unified Revenue System
"""
import json
from pathlib import Path
from datetime import datetime

PROFIT_DIR = Path(__file__).parent
LEDGER_PATH = PROFIT_DIR / "profit_ledger.json"

class ProductionEngine:
    """Unified Production Engine"""
    
    def __init__(self):
        self.transactions = []
        self.revenue = 0.0
        self.costs = 0.0
        self.load()
    
    def load(self):
        if LEDGER_PATH.exists():
            data = json.loads(LEDGER_PATH.read_text())
            self.transactions = data.get("transactions", [])
            self.revenue = data.get("revenue", 0.0)
            self.costs = data.get("costs", 0.0)
    
    def save(self):
        data = {
            "updated": datetime.utcnow().isoformat(),
            "transactions": self.transactions,
            "revenue": self.revenue,
            "costs": self.costs,
            "profit": self.revenue - self.costs
        }
        LEDGER_PATH.write_text(json.dumps(data, indent=2))
    
    def add_revenue(self, amount: float, source: str, description: str = ""):
        tx = {
            "id": len(self.transactions) + 1,
            "type": "revenue",
            "amount": amount,
            "source": source,
            "description": description,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.transactions.append(tx)
        self.revenue += amount
        self.save()
        return tx
    
    def add_cost(self, amount: float, description: str = ""):
        tx = {
            "id": len(self.transactions) + 1,
            "type": "cost",
            "amount": amount,
            "description": description,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.transactions.append(tx)
        self.costs += amount
        self.save()
        return tx
    
    def quick_money_paths(self):
        return [
            {"path": "Affiliate", "platforms": ["Amazon", "Rewardful", "Gumroad"], "difficulty": "easy"},
            {"path": "Digital Products", "platforms": ["Gumroad", "Lemon Squeezy"], "difficulty": "easy"},
            {"path": "Freelance", "platforms": ["Upwork", "Fiverr"], "difficulty": "medium"},
            {"path": "Content", "platforms": ["YouTube", "Patreon"], "difficulty": "medium"},
            {"path": "Data Services", "platforms": ["API", "Research"], "difficulty": "hard"},
        ]
    
    def generate_report(self):
        return {
            "revenue": self.revenue,
            "costs": self.costs,
            "profit": self.revenue - self.costs,
            "transactions": len(self.transactions),
            "paths": self.quick_money_paths()
        }

def main():
    engine = ProductionEngine()
    
    print("=" * 50)
    print("💰 PRODUCTION ENGINE")
    print("=" * 50)
    
    # Demo transactions
    engine.add_revenue(100.00, "Gumroad", "Digital product")
    engine.add_revenue(50.00, "Affiliate", "Amazon")
    engine.add_cost(15.00, "Platform fees")
    
    report = engine.generate_report()
    print(f"\nRevenue: ${report['revenue']:.2f}")
    print(f"Costs: ${report['costs']:.2f}")
    print(f"Profit: ${report['profit']:.2f}")
    print(f"Transactions: {report['transactions']}")
    
    print("\n🚀 Quick Money Paths:")
    for p in report['paths']:
        print(f"   {p['path']}: {p['platforms']}")
    
    return engine

if __name__ == "__main__":
    main()