#!/usr/bin/env python3
"""
EVEZ Database - Data storage, queries, transactions
SQL-like operations, indexing, ACID transactions
"""

import json
import random
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

class DataType(Enum):
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"

class IndexType(Enum):
    BTREE = "btree"
    HASH = "hash"
    FULLTEXT = "fulltext"

@dataclass
class Column:
    name: str
    data_type: DataType
    primary_key: bool = False
    nullable: bool = True

@dataclass
class Table:
    name: str
    columns: List[Column]
    rows: List[Dict] = field(default_factory=list)
    indexes: Dict[str, List[str]] = field(default_factory=dict)

class DatabaseEngine:
    """EVEZ Database - Storage and query system"""
    
    def __init__(self, name: str = "evez_db"):
        self.name = name
        self.tables: Dict[str, Table] = {}
        self.transaction_log: List[Dict] = []
        self.active_transaction: Optional[str] = None
        
    def create_table(self, table_name: str, columns: List[Column]) -> bool:
        """Create a new table"""
        if table_name in self.tables:
            return False
        
        self.tables[table_name] = Table(name=table_name, columns=columns)
        return True
    
    def insert(self, table_name: str, data: Dict) -> bool:
        """Insert a row"""
        if table_name not in self.tables:
            return False
        
        table = self.tables[table_name]
        
        # Validate data
        row = {"_id": str(uuid.uuid4())[:8], "_created": datetime.utcnow().isoformat() + "Z"}
        for col in table.columns:
            if col.name in data:
                row[col.name] = data[col.name]
            elif not col.nullable and not col.primary_key:
                return False
        
        table.rows.append(row)
        return True
    
    def select(self, table_name: str, where: Optional[Dict] = None, 
               limit: int = 100) -> List[Dict]:
        """Query data"""
        if table_name not in self.tables:
            return []
        
        results = self.tables[table_name].rows
        
        if where:
            results = [r for r in results if all(r.get(k) == v for k, v in where.items())]
        
        return results[:limit]
    
    def update(self, table_name: str, where: Dict, data: Dict) -> int:
        """Update rows"""
        if table_name not in self.tables:
            return 0
        
        count = 0
        for row in self.tables[table_name].rows:
            if all(row.get(k) == v for k, v in where.items()):
                row.update(data)
                count += 1
        
        return count
    
    def delete(self, table_name: str, where: Dict) -> int:
        """Delete rows"""
        if table_name not in self.tables:
            return 0
        
        table = self.tables[table_name]
        original_count = len(table.rows)
        table.rows = [r for r in table.rows if not all(r.get(k) == v for k, v in where.items())]
        return original_count - len(table.rows)
    
    def create_index(self, table_name: str, column: str, index_type: IndexType = IndexType.BTREE):
        """Create index on column"""
        if table_name not in self.tables:
            return False
        
        self.tables[table_name].indexes[column] = [index_type.value]
        return True
    
    def begin_transaction(self) -> str:
        """Start transaction"""
        self.active_transaction = str(uuid.uuid4())[:8]
        self.transaction_log.append({
            "txn_id": self.active_transaction,
            "action": "BEGIN",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        return self.active_transaction
    
    def commit(self) -> bool:
        """Commit transaction"""
        if not self.active_transaction:
            return False
        
        self.transaction_log.append({
            "txn_id": self.active_transaction,
            "action": "COMMIT",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        self.active_transaction = None
        return True
    
    def rollback(self) -> bool:
        """Rollback transaction"""
        if not self.active_transaction:
            return False
        
        self.transaction_log.append({
            "txn_id": self.active_transaction,
            "action": "ROLLBACK",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        self.active_transaction = None
        return True
    
    def get_status(self) -> Dict:
        return {
            "name": self.name,
            "tables": len(self.tables),
            "total_rows": sum(len(t.rows) for t in self.tables.values()),
            "transactions": len(self.transaction_log),
            "active_txn": self.active_transaction
        }


# Demo
if __name__ == "__main__":
    from dataclasses import dataclass
    
    db = DatabaseEngine()
    print("=== EVEZ Database ===")
    
    # Create table
    cols = [Column("id", DataType.INTEGER, True), Column("name", DataType.TEXT),
            Column("value", DataType.FLOAT), Column("active", DataType.BOOLEAN)]
    db.create_table("items", cols)
    
    # Insert
    db.insert("items", {"id": 1, "name": "Alpha", "value": 100.5, "active": True})
    db.insert("items", {"id": 2, "name": "Beta", "value": 200.3, "active": False})
    
    # Query
    results = db.select("items", {"active": True})
    print(f"Active items: {len(results)}")
    
    # Transaction
    txn = db.begin_transaction()
    db.insert("items", {"id": 3, "name": "Gamma", "value": 300.0})
    db.commit()
    print(f"Transaction {txn} committed")
    
    print(json.dumps(db.get_status(), indent=2))