#!/usr/bin/env python3
"""
EVEZ Game Theory - Strategy, decision theory, game mechanics
Nash equilibrium, minimax, evolutionary strategies, auctions
"""

import json
import random
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from itertools import product

class StrategyType(Enum):
    COOPERATE = "cooperate"
    DEFECT = "defect"
    TIT_FOR_TAT = "tit_for_tat"
    RANDOM = "random"
    GRIM = "grim"

@dataclass
class GameState:
    players: List[str]
    payoff_matrix: Dict[Tuple[str, str], Tuple[float, float]]
    history: List[Dict] = field(default_factory=list)

@dataclass
class AgentStrategy:
    name: str
    strategy_type: StrategyType
    score: float = 0.0
    moves: List[str] = field(default_factory=list)

class GameTheoryEngine:
    """EVEZ Game Theory - Strategy and decision systems"""
    
    def __init__(self):
        self.model_name = "EVEZ-GameTheory-v1"
        self.games: Dict[str, GameState] = {}
    
    def create_prisoners_dilemma(self) -> GameState:
        """Create Prisoner's Dilemma game"""
        # (P1 payoff, P2 payoff)
        # Both cooperate = (3, 3), Both defect = (1, 1)
        # P1 cooperates, P2 defects = (0, 5), P1 defects, P2 cooperates = (5, 0)
        payoff_matrix = {
            (StrategyType.COOPERATE.value, StrategyType.COOPERATE.value): (3, 3),
            (StrategyType.COOPERATE.value, StrategyType.DEFECT.value): (0, 5),
            (StrategyType.DEFECT.value, StrategyType.COOPERATE.value): (5, 0),
            (StrategyType.DEFECT.value, StrategyType.DEFECT.value): (1, 1)
        }
        
        return GameState(players=["player1", "player2"], payoff_matrix=payoff_matrix)
    
    def play_round(self, game: GameState, move1: str, move2: str) -> Tuple[float, float]:
        """Play one round of a game"""
        payoff = game.payoff_matrix.get((move1, move2), (0, 0))
        
        game.history.append({
            "player1_move": move1,
            "player2_move": move2,
            "payoffs": payoff
        })
        
        return payoff
    
    def get_optimal_move(self, game: GameState, player: str) -> str:
        """Find optimal move using maximin strategy"""
        # For player 1 (rows), find move that maximizes minimum payoff
        moves = [StrategyType.COOPERATE.value, StrategyType.DEFECT.value]
        
        min_payoffs = {}
        for move in moves:
            opponent_moves = [StrategyType.COOPERATE.value, StrategyType.DEFECT.value]
            payoffs = [game.payoff_matrix.get((move, om), (0, 0))[0] for om in opponent_moves]
            min_payoffs[move] = min(payoffs)
        
        return max(min_payoffs.items(), key=lambda x: x[1])[0]
    
    def simulate_tournament(self, strategies: List[AgentStrategy], rounds: int = 10) -> List[AgentStrategy]:
        """Simulate a tournament between strategies"""
        # Each agent plays against every other agent
        for i, agent1 in enumerate(strategies):
            for j, agent2 in enumerate(strategies):
                if i >= j:
                    continue
                
                # Play rounds
                for _ in range(rounds):
                    move1 = self._get_strategy_move(agent1, agent2)
                    move2 = self._get_strategy_move(agent2, agent1)
                    
                    payoff1, payoff2 = self.play_round(
                        self.create_prisoners_dilemma(), move1, move2
                    )
                    
                    agent1.score += payoff1
                    agent2.score += payoff2
        
        return sorted(strategies, key=lambda x: x.score, reverse=True)
    
    def _get_strategy_move(self, agent: AgentStrategy, opponent: AgentStrategy) -> str:
        """Get move based on agent's strategy type"""
        if agent.strategy_type == StrategyType.COOPERATE:
            return StrategyType.COOPERATE.value
        
        elif agent.strategy_type == StrategyType.DEFECT:
            return StrategyType.DEFECT.value
        
        elif agent.strategy_type == StrategyType.TIT_FOR_TAT:
            # Copy opponent's last move
            if opponent.moves:
                return opponent.moves[-1]
            return StrategyType.COOPERATE.value
        
        elif agent.strategy_type == StrategyType.RANDOM:
            return random.choice([StrategyType.COOPERATE.value, StrategyType.DEFECT.value])
        
        elif agent.strategy_type == StrategyType.GRIM:
            # Cooperate until opponent defects, then always defect
            if StrategyType.DEFECT.value in opponent.moves:
                return StrategyType.DEFECT.value
            return StrategyType.COOPERATE.value
        
        return StrategyType.COOPERATE.value
    
    def calculate_nash_equilibrium(self, payoff_matrix: Dict) -> List[Tuple]:
        """Find Nash equilibrium points (simplified for 2x2)"""
        # Find best responses for each player
        equilibria = []
        
        for (m1, m2), (p1, p2) in payoff_matrix.items():
            # Check if m1 is best response to m2
            row_payoffs = [payoff_matrix[(m1, om)][0] for om in [StrategyType.COOPERATE.value, StrategyType.DEFECT.value]]
            is_best_1 = p1 == max(row_payoffs)
            
            # Check if m2 is best response to m1  
            col_payoffs = [payoff_matrix[(om, m2)][1] for om in [StrategyType.COOPERATE.value, StrategyType.DEFECT.value]]
            is_best_2 = p2 == max(col_payoffs)
            
            if is_best_1 and is_best_2:
                equilibria.append((m1, m2))
        
        return equilibria
    
    def auction(self, item_value: float, bidders: List[Dict], auction_type: str = "second_price") -> Dict:
        """
        Simulate an auction
        auction_type: "first_price" (sealed bid), "second_price" (Vickrey), " dutch"
        """
        results = []
        
        for bidder in bidders:
            # Bidders have private values with some noise
            true_value = item_value * random.uniform(0.8, 1.2)
            private_value = true_value * random.uniform(0.9, 1.1)
            
            # Calculate bid based on strategy
            if bidder.get("strategy") == "aggressive":
                bid = private_value * random.uniform(0.9, 1.1)
            elif bidder.get("strategy") == "conservative":
                bid = private_value * random.uniform(0.6, 0.8)
            else:
                bid = private_value * random.uniform(0.7, 0.9)
            
            results.append({"bidder": bidder["name"], "bid": bid, "value": private_value})
        
        # Sort by bid
        results.sort(key=lambda x: x["bid"], reverse=True)
        
        if not results:
            return {"winner": None, "price": 0}
        
        winner = results[0]
        
        if auction_type == "second_price" and len(results) > 1:
            price = results[1]["bid"]
        else:
            price = winner["bid"]
        
        return {
            "winner": winner["bidder"],
            "winning_bid": winner["bid"],
            "price_paid": price,
            "item_value": item_value,
            "profit": winner["value"] - price if winner["bidder"] else 0,
            "all_bids": [{"b": r["bid"], "v": r["value"]} for r in results]
        }
    
    def minimax_decision(self, game_tree: Dict, is_maximizer: bool = True, depth: int = 0) -> Any:
        """Minimax algorithm for perfect information games"""
        # Terminal state
        if "value" in game_tree:
            return game_tree["value"]
        
        if is_maximizer:
            best_value = float('-inf')
            for child in game_tree.get("children", []):
                value = self.minimax_decision(child, False, depth + 1)
                best_value = max(best_value, value)
            return best_value
        else:
            best_value = float('inf')
            for child in game_tree.get("children", []):
                value = self.minimax_decision(child, True, depth + 1)
                best_value = min(best_value, value)
            return best_value
    
    def get_status(self) -> Dict:
        return {
            "model": self.model_name,
            "games": len(self.games),
            "available_strategies": [s.value for s in StrategyType]
        }


# Demo
if __name__ == "__main__":
    gt = GameTheoryEngine()
    print("=== EVEZ Game Theory ===")
    
    # Create tournament
    strategies = [
        AgentStrategy("Cooperator", StrategyType.COOPERATE),
        AgentStrategy("Defector", StrategyType.DEFECT),
        AgentStrategy("TFT", StrategyType.TIT_FOR_TAT),
        AgentStrategy("Grim", StrategyType.GRIM),
        AgentStrategy("Random", StrategyType.RANDOM)
    ]
    
    winners = gt.simulate_tournament(strategies, rounds=20)
    print("Tournament results:")
    for w in winners:
        print(f"  {w.name}: {w.score} points")
    
    # Auction
    auction_result = gt.auction(100, [
        {"name": "Alice", "strategy": "aggressive"},
        {"name": "Bob", "strategy": "conservative"},
        {"name": "Charlie", "strategy": "normal"}
    ], "second_price")
    print(f"\nAuction winner: {auction_result['winner']}, price: ${auction_result['price_paid']:.2f}")
    
    print(json.dumps(gt.get_status(), indent=2))