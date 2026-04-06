#!/usr/bin/env python3
"""
EVEZ Blockchain - Distributed ledger with consensus
Blocks, transactions, mining simulation, smart contracts
"""

import json
import random
import hashlib
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class TransactionType(Enum):
    TRANSFER = "transfer"
    STAKE = "stake"
    CONTRACT = "contract"

@dataclass
class Transaction:
    tx_id: str
    sender: str
    recipient: str
    amount: float
    tx_type: TransactionType
    timestamp: str
    signature: str
    data: Dict = field(default_factory=dict)

@dataclass
class Block:
    index: int
    timestamp: str
    transactions: List[Transaction]
    prev_hash: str
    hash: str
    nonce: int
    validator: str

class BlockchainEngine:
    """EVEZ Blockchain - Distributed ledger system"""
    
    def __init__(self, name: str = "EVEZ-Chain"):
        self.name = name
        self.chain: List[Block] = []
        self.pending_txs: List[Transaction] = []
        self.validators: Dict[str, float] = {}  # address -> stake
        self.accounts: Dict[str, float] = {}   # address -> balance
        
        # Create genesis block
        self._create_genesis()
    
    def _create_genesis(self):
        """Create genesis block"""
        genesis = Block(
            index=0,
            timestamp=datetime.utcnow().isoformat() + "Z",
            transactions=[],
            prev_hash="0" * 64,
            hash=self._hash_block(0, [], "0" * 64, 0),
            nonce=0,
            validator="system"
        )
        self.chain.append(genesis)
        
        # Initialize validator
        self.validators["system"] = 1000.0
        self.accounts["system"] = 10000.0
    
    def _hash_block(self, index: int, txs: List, prev_hash: str, nonce: int) -> str:
        content = f"{index}:{json.dumps([(t.tx_id, t.sender, t.recipient, t.amount, t.tx_type.value) for t in txs], sort_keys=True)}:{prev_hash}:{nonce}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def create_transaction(self, sender: str, recipient: str, amount: float,
                          tx_type: TransactionType = TransactionType.TRANSFER,
                          data: Optional[Dict] = None) -> Optional[Transaction]:
        """Create a new transaction"""
        # Check balance
        if self.accounts.get(sender, 0) < amount:
            return None
        
        tx = Transaction(
            tx_id=f"tx_{random.randint(100000, 999999)}",
            sender=sender,
            recipient=recipient,
            amount=amount,
            tx_type=tx_type,
            timestamp=datetime.utcnow().isoformat() + "Z",
            signature=self._sign(sender, amount),
            data=data or {}
        )
        
        # Deduct from sender (simulation - no actual balance check in pending)
        if sender in self.accounts:
            self.accounts[sender] -= amount
        
        self.pending_txs.append(tx)
        return tx
    
    def _sign(self, sender: str, amount: float) -> str:
        return hashlib.sha256(f"{sender}:{amount}".encode()).hexdigest()[:16]
    
    def add_validator(self, address: str, stake: float):
        """Add a validator with stake"""
        self.validators[address] = stake
        self.accounts[address] = self.accounts.get(address, 0) + stake
    
    def select_validator(self) -> str:
        """Select validator based on stake (weighted random)"""
        stakes = list(self.validators.values())
        addresses = list(self.validators.keys())
        total = sum(stakes)
        
        r = random.random() * total
        cumulative = 0
        
        for i, stake in enumerate(stakes):
            cumulative += stake
            if cumulative >= r:
                return addresses[i]
        
        return addresses[-1]
    
    def mine_block(self, validator: str) -> Block:
        """Create a new block (simplified proof-of-stake)"""
        # Select transactions
        txs = self.pending_txs[:10]  # Max 10 txs per block
        self.pending_txs = self.pending_txs[10:]
        
        # Create block
        prev_hash = self.chain[-1].hash
        index = len(self.chain)
        
        # Find valid hash (simplified - just random nonce)
        nonce = random.randint(0, 100000)
        block_hash = self._hash_block(index, txs, prev_hash, nonce)
        
        block = Block(
            index=index,
            timestamp=datetime.utcnow().isoformat() + "Z",
            transactions=txs,
            prev_hash=prev_hash,
            hash=block_hash,
            nonce=nonce,
            validator=validator
        )
        
        self.chain.append(block)
        
        # Reward validator
        self.accounts[validator] = self.accounts.get(validator, 0) + 1.0
        
        return block
    
    def verify_chain(self) -> bool:
        """Verify blockchain integrity"""
        for i in range(1, len(self.chain)):
            prev = self.chain[i - 1]
            curr = self.chain[i]
            
            if curr.prev_hash != prev.hash:
                return False
            
            expected_hash = self._hash_block(curr.index, curr.transactions, curr.prev_hash, curr.nonce)
            if curr.hash != expected_hash:
                return False
        
        return True
    
    def get_balance(self, address: str) -> float:
        """Get account balance"""
        return self.accounts.get(address, 0.0)
    
    def get_block(self, index: int) -> Optional[Block]:
        """Get block by index"""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def get_status(self) -> Dict:
        return {
            "name": self.name,
            "blocks": len(self.chain),
            "pending_txs": len(self.pending_txs),
            "validators": len(self.validators),
            "chain_valid": self.verify_chain()
        }


# Demo
if __name__ == "__main__":
    bc = BlockchainEngine()
    print("=== EVEZ Blockchain ===")
    
    # Add validators
    bc.add_validator("alice", 500)
    bc.add_validator("bob", 300)
    
    # Create transactions
    bc.create_transaction("system", "alice", 100)
    bc.create_transaction("alice", "bob", 50)
    bc.create_transaction("bob", "system", 25)
    
    print(f"Pending txs: {len(bc.pending_txs)}")
    
    # Mine blocks
    for _ in range(3):
        validator = bc.select_validator()
        block = bc.mine_block(validator)
        print(f"Block {block.index} mined by {block.validator}")
    
    print(f"\nBalances: system=${bc.get_balance('system'):.2f}, alice=${bc.get_balance('alice'):.2f}, bob=${bc.get_balance('bob'):.2f}")
    print(json.dumps(bc.get_status(), indent=2))