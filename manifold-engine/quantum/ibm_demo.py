#!/usr/bin/env python3
"""
Quantum Computing Demo - IBM Qiskit Integration
Run basic quantum circuits on IBM Quantum simulators.
"""
import json
from pathlib import Path

LEDGER_PATH = Path(__file__).parent.parent / "profit-engine" / "ledger.json"

# Try IBM Qiskit, fallback to simulation
try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    HAS_QISKIT = True
except ImportError:
    HAS_QISKIT = False

def create_bell_state():
    """Create Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2"""
    qc = QuantumCircuit(2)
    qc.h(0)          # Hadamard
    qc.cx(0, 1)     # CNOT
    qc.measure_all()
    return qc

def create_ghz_state(n_qubits=3):
    """Create GHZ state (|000⟩ + |111⟩)/√2"""
    qc = QuantumCircuit(n_qubits)
    qc.h(0)
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc

def create_grover_oracle(target="00"):
    """Simple Grover oracle for 2-qubit search"""
    qc = QuantumCircuit(2)
    # Mark desired state
    if target == "00":
        qc.cz(0, 1)
    elif target == "01":
        qc.x(1)
        qc.cz(0, 1)
        qc.x(1)
    qc.measure_all()
    return qc

def run_circuit(circuit, shots=1000):
    """Run circuit on simulator"""
    if HAS_QISKIT:
        simulator = AerSimulator()
        result = simulator.run(circuit, shots=shots).result()
        return result.get_counts()
    else:
        # Fallback: mock random results
        import random
        return {"00": shots // 2, "11": shots // 2}

def demo_quantum():
    """Run all demos"""
    results = {}
    
    print("=" * 40)
    print("QUANTUM COMPUTING DEMO")
    print("=" * 40)
    
    if not HAS_QISKIT:
        print("\n⚠️  Qiskit not installed - using simulation mode")
        print("   Install with: pip install qiskit qiskit-aer")
    
    # Bell state
    print("\n1. Bell State |Φ+⟩")
    bell = create_bell_state()
    print(bell)
    results["bell"] = run_circuit(bell)
    print(f"Results: {results['bell']}")
    
    # GHZ state
    print("\n2. GHZ State (3 qubits)")
    ghz = create_ghz_state(3)
    print(ghz)
    results["ghz"] = run_circuit(ghz)
    print(f"Results: {results['ghz']}")
    
    return results

if __name__ == "__main__":
    demo_quantum()