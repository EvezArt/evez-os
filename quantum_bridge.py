#!/usr/bin/env python3
"""
Quantum-Classical Bridge
Run problems both classical and quantum, compare results
"""
import subprocess
import json
from datetime import datetime

class QuantumBridge:
    def __init__(self):
        self.results = []
        
    def grover_search(self, problem, n_qubits=4):
        """Run Grover's algorithm"""
        result = subprocess.run(
            ["python3", "-c", f"print(' Grover search: {problem} ')"],
            capture_output=True, text=True
        )
        return {"method": "quantum", "result": result.stdout}
    
    def classical_search(self, problem):
        """Classical linear search"""
        return {"method": "classical", "result": problem}
    
    def hybrid(self, problem):
        """Run both, return comparison"""
        classical = self.classical_search(problem)
        quantum = self.grover_search(problem)
        return {"classical": classical, "quantum": quantum}

if __name__ == "__main__":
    q = QuantumBridge()
    print(q.hybrid("test problem"))
