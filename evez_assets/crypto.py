#!/usr/bin/env python3
"""
EVEZ Crypto - Cryptocurrency trading, portfolio, DeFi operations
Trading, yield farming simulation, portfolio management
"""

import json
import random
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class CryptoAsset(Enum):
    BTC = "BTC"
    ETH = "ETH"
    SOL = "SOL"
    USDC = "USDC"
    EVEZ = "EVEZ"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class PriceQuote:
    asset: str
    price: float
    change_24h: float
    volume_24h: float
    timestamp: str

@dataclass
class Order:
    order_id: str
    asset: CryptoAsset
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float]  # None for market orders
    status: str = "pending"
    filled_at: Optional[str] = None

@dataclass
class Position:
    asset: CryptoAsset
    quantity: float
    avg_entry_price: float
    current_price: float
    pnl: float = 0.0
    pnl_pct: float = 0.0

class CryptoEngine:
    """EVEZ Crypto - Cryptocurrency operations"""
    
    def __init__(self):
        self.model_name = "EVEZ-Crypto-v1"
        
        # Initialize prices
        self.prices = {
            CryptoAsset.BTC: 45000.0,
            CryptoAsset.ETH: 2500.0,
            CryptoAsset.SOL: 100.0,
            CryptoAsset.USDC: 1.0,
            CryptoAsset.EVEZ: 0.01
        }
        
        # Portfolio
        self.balances = {
            CryptoAsset.BTC: 0.5,
            CryptoAsset.ETH: 5.0,
            CryptoAsset.SOL: 50.0,
            CryptoAsset.USDC: 1000.0,
            CryptoAsset.EVEZ: 10000.0
        }
        
        # Open orders
        self.orders: List[Order] = []
        
        # History
        self.price_history: Dict[str, List[float]] = {a.value: [] for a in CryptoAsset}
        self.trade_history: List[Dict] = []
    
    def get_quote(self, asset: CryptoAsset) -> PriceQuote:
        """Get current price quote"""
        price = self.prices[asset]
        
        # Simulate price movement
        change_pct = random.uniform(-5, 5)
        price *= (1 + change_pct / 100)
        self.prices[asset] = price
        
        # Record history
        self.price_history[asset.value].append(price)
        if len(self.price_history[asset.value]) > 100:
            self.price_history[asset.value] = self.price_history[asset.value][-100:]
        
        return PriceQuote(
            asset=asset.value,
            price=price,
            change_24h=change_pct,
            volume_24h=random.uniform(1e6, 1e9),
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    def place_order(self, asset: CryptoAsset, side: OrderSide, order_type: OrderType,
                   quantity: float, price: Optional[float] = None) -> Optional[Order]:
        """Place an order"""
        # Check balance for buy orders
        if side == OrderSide.BUY:
            required = quantity * (price or self.prices[asset])
            if self.balances.get(CryptoAsset.USDC, 0) < required:
                return None
        
        # Check balance for sell orders
        if side == OrderSide.SELL:
            if self.balances.get(asset, 0) < quantity:
                return None
        
        order = Order(
            order_id=f"ord_{random.randint(100000, 999999)}",
            asset=asset,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        
        self.orders.append(order)
        return order
    
    def fill_order(self, order_id: str) -> bool:
        """Fill an order"""
        for order in self.orders:
            if order.order_id == order_id and order.status == "pending":
                price = order.price or self.prices[order.asset]
                
                if order.side == OrderSide.BUY:
                    # Deduct USDC, add asset
                    cost = price * order.quantity
                    self.balances[CryptoAsset.USDC] -= cost
                    self.balances[order.asset] = self.balances.get(order.asset, 0) + order.quantity
                else:
                    # Deduct asset, add USDC
                    proceeds = price * order.quantity
                    self.balances[order.asset] -= order.quantity
                    self.balances[CryptoAsset.USDC] = self.balances.get(CryptoAsset.USDC, 0) + proceeds
                
                order.status = "filled"
                order.filled_at = datetime.utcnow().isoformat() + "Z"
                
                self.trade_history.append({
                    "order_id": order_id,
                    "asset": order.asset.value,
                    "side": order.side.value,
                    "quantity": order.quantity,
                    "price": price,
                    "timestamp": order.filled_at
                })
                
                return True
        
        return False
    
    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value in USD"""
        total = self.balances.get(CryptoAsset.USDC, 0)
        
        for asset, qty in self.balances.items():
            if asset != CryptoAsset.USDC and qty > 0:
                total += qty * self.prices[asset]
        
        return total
    
    def calculate_positions(self) -> List[Position]:
        """Calculate current positions with P&L"""
        positions = []
        
        for asset, qty in self.balances.items():
            if asset != CryptoAsset.USDC and qty > 0:
                current_price = self.prices[asset]
                # Assume avg entry = current for simplicity
                entry_price = current_price * random.uniform(0.8, 1.2)
                
                pnl = (current_price - entry_price) * qty
                pnl_pct = (current_price - entry_price) / entry_price * 100
                
                positions.append(Position(
                    asset=asset,
                    quantity=qty,
                    avg_entry_price=entry_price,
                    current_price=current_price,
                    pnl=pnl,
                    pnl_pct=pnl_pct
                ))
        
        return positions
    
    def get_market_stats(self) -> Dict:
        """Get overall market statistics"""
        return {
            "total_value": self.get_portfolio_value(),
            "balances": {a.value: q for a, q in self.balances.items() if q > 0},
            "open_orders": len([o for o in self.orders if o.status == "pending"]),
            "total_trades": len(self.trade_history)
        }


# Demo
if __name__ == "__main__":
    crypto = CryptoEngine()
    print("=== EVEZ Crypto ===")
    
    # Get quotes
    for asset in [CryptoAsset.BTC, CryptoAsset.ETH, CryptoAsset.SOL]:
        quote = crypto.get_quote(asset)
        print(f"{asset.value}: ${quote.price:.2f} ({quote.change_24h:+.2f}%)")
    
    # Place orders
    order = crypto.place_order(CryptoAsset.BTC, OrderSide.BUY, OrderType.MARKET, 0.1)
    if order:
        crypto.fill_order(order.order_id)
    
    print(f"\nPortfolio value: ${crypto.get_portfolio_value():.2f}")
    print(f"Positions: {len(crypto.calculate_positions())}")
    print(json.dumps(crypto.get_market_stats(), indent=2))