#!/usr/bin/env python3
"""
EVEZ Finance Engine - Trading, income loops, portfolio management
Autonomous financial operations with risk management
"""

import json
import time
import random
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"

class PositionSide(Enum):
    LONG = "long"
    SHORT = "short"

@dataclass
class Asset:
    symbol: str
    name: str
    price: float
    volatility: float  # 0-1
    liquidity: float   # 0-1

@dataclass
class Position:
    id: str
    symbol: str
    side: PositionSide
    quantity: float
    entry_price: float
    current_price: float
    opened_at: str
    pnl: float = 0.0

@dataclass
class Order:
    id: str
    symbol: str
    order_type: OrderType
    side: PositionSide
    quantity: float
    limit_price: Optional[float] = None
    status: str = "pending"
    filled_at: Optional[str] = None
    filled_price: Optional[float] = None

class FinanceEngine:
    """EVEZ-style autonomous finance engine"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.trade_history: List[Dict] = []
        self.equity_curve: List[Dict] = []  # For performance tracking
        
        # Initialize some assets
        self.assets = {
            "BTC": Asset("BTC", "Bitcoin", 45000.0, 0.8, 0.9),
            "ETH": Asset("ETH", "Ethereum", 2500.0, 0.7, 0.85),
            "SOL": Asset("SOL", "Solana", 100.0, 0.9, 0.6),
            "SPY": Asset("SPY", "S&P 500 ETF", 450.0, 0.2, 0.95),
            "TSLA": Asset("TSLA", "Tesla", 200.0, 0.6, 0.8),
        }
        
        # Risk parameters
        self.risk_per_trade = 0.02  # 2% of balance
        self.max_positions = 5
        self.stop_loss_pct = 0.05   # 5%
        self.take_profit_pct = 0.15  # 15%
        
    def get_price(self, symbol: str) -> float:
        """Get current price with simulated movement"""
        if symbol not in self.assets:
            return 100.0
            
        asset = self.assets[symbol]
        # Random walk with mean reversion
        change = random.uniform(-asset.volatility, asset.volatility) * 0.02
        asset.price *= (1 + change)
        return asset.price
    
    def can_trade(self, symbol: str, side: PositionSide, quantity: float) -> bool:
        """Check if trade is allowed by risk rules"""
        price = self.get_price(symbol)
        required = price * quantity
        
        if required > self.balance:
            return False
            
        if len(self.positions) >= self.max_positions:
            return False
            
        return True
    
    def submit_order(self, symbol: str, order_type: OrderType, side: PositionSide,
                    quantity: float, limit_price: Optional[float] = None) -> Optional[Order]:
        """Submit a new order"""
        if not self.can_trade(symbol, side, quantity):
            return None
            
        order = Order(
            id=str(uuid.uuid4())[:8],
            symbol=symbol,
            order_type=order_type,
            side=side,
            quantity=quantity,
            limit_price=limit_price
        )
        self.orders[order.id] = order
        return order
    
    def fill_order(self, order_id: str) -> bool:
        """Fill an order and update positions"""
        if order_id not in self.orders:
            return False
            
        order = self.orders[order_id]
        price = self.get_price(order.symbol)
        
        # Check limit price
        if order.order_type == OrderType.LIMIT and order.limit_price:
            if (order.side == PositionSide.LONG and price > order.limit_price) or \
               (order.side == PositionSide.SHORT and price < order.limit_price):
                return False
        
        order.status = "filled"
        order.filled_at = datetime.utcnow().isoformat() + "Z"
        order.filled_price = price
        
        # Update balance
        cost = price * order.quantity
        if order.side == PositionSide.LONG:
            self.balance -= cost
        else:
            self.balance += cost
        
        # Create position
        position = Position(
            id=str(uuid.uuid4())[:8],
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            entry_price=price,
            current_price=price,
            opened_at=order.filled_at
        )
        self.positions[position.id] = position
        
        # Log trade
        self.trade_history.append({
            "order_id": order_id,
            "position_id": position.id,
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": order.quantity,
            "price": price,
            "timestamp": order.filled_at
        })
        
        return True
    
    def update_positions(self):
        """Update position PnL and check stop loss / take profit"""
        to_close = []
        
        for pos_id, pos in self.positions.items():
            pos.current_price = self.get_price(pos.symbol)
            
            # Calculate PnL
            if pos.side == PositionSide.LONG:
                pos.pnl = (pos.current_price - pos.entry_price) * pos.quantity
            else:
                pos.pnl = (pos.entry_price - pos.current_price) * pos.quantity
            
            # Check exit conditions
            pnl_pct = pos.pnl / (pos.entry_price * pos.quantity)
            
            if pnl_pct <= -self.stop_loss_pct or pnl_pct >= self.take_profit_pct:
                to_close.append(pos_id)
        
        # Close positions
        for pos_id in to_close:
            self.close_position(pos_id)
    
    def close_position(self, position_id: str, reason: str = "signal") -> bool:
        """Close a position"""
        if position_id not in self.positions:
            return False
            
        pos = self.positions[position_id]
        
        # Update balance
        if pos.side == PositionSide.LONG:
            self.balance += pos.current_price * pos.quantity
        else:
            self.balance -= pos.current_price * pos.quantity
        
        # Log close
        self.trade_history.append({
            "action": "close",
            "position_id": position_id,
            "symbol": pos.symbol,
            "side": pos.side.value,
            "quantity": pos.quantity,
            "entry_price": pos.entry_price,
            "exit_price": pos.current_price,
            "pnl": pos.pnl,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        del self.positions[position_id]
        return True
    
    def get_equity(self) -> float:
        """Calculate total equity"""
        position_value = sum(
            p.current_price * p.quantity * (1 if p.side == PositionSide.LONG else 1)
            for p in self.positions.values()
        )
        return self.balance + position_value
    
    def record_equity(self):
        """Record equity for performance tracking"""
        self.equity_curve.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "balance": self.balance,
            "equity": self.get_equity(),
            "positions": len(self.positions)
        })
    
    def get_performance(self) -> Dict:
        """Get performance metrics"""
        current_equity = self.get_equity()
        total_return = (current_equity - self.initial_balance) / self.initial_balance
        
        return {
            "initial_balance": self.initial_balance,
            "current_equity": current_equity,
            "cash_balance": self.balance,
            "total_return_pct": total_return * 100,
            "open_positions": len(self.positions),
            "total_trades": len(self.trade_history),
            "win_rate": self._calculate_win_rate()
        }
    
    def _calculate_win_rate(self) -> float:
        closed_trades = [t for t in self.trade_history if t.get("pnl") is not None]
        if not closed_trades:
            return 0.0
        wins = sum(1 for t in closed_trades if t.get("pnl", 0) > 0)
        return wins / len(closed_trades)
    
    def auto_trade_cycle(self) -> Dict:
        """Run one autonomous trading cycle"""
        # Update prices and positions
        self.update_positions()
        
        # Generate signals (simplified)
        for symbol, asset in self.assets.items():
            # Skip if at max positions
            if len(self.positions) >= self.max_positions:
                break
                
            # Random signal (in real system, this would be from indicators)
            if random.random() < 0.1:  # 10% chance per cycle
                side = random.choice([PositionSide.LONG, PositionSide.SHORT])
                quantity = (self.balance * self.risk_per_trade) / asset.price
                
                order = self.submit_order(symbol, OrderType.MARKET, side, quantity)
                if order:
                    self.fill_order(order.id)
        
        # Record equity
        self.record_equity()
        
        return {
            "equity": self.get_equity(),
            "positions": len(self.positions),
            "cash": self.balance
        }


# Demo
if __name__ == "__main__":
    engine = FinanceEngine(10000)
    
    print("=== EVEZ Finance Engine ===\n")
    
    # Run trading cycles
    for i in range(20):
        result = engine.auto_trade_cycle()
        if i % 5 == 0:
            print(f"Cycle {i+1}: Equity=${result['equity']:.2f}, "
                  f"Positions={result['positions']}, Cash=${result['cash']:.2f}")
    
    print("\n=== Performance ===")
    perf = engine.get_performance()
    print(json.dumps(perf, indent=2))