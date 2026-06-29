#!/usr/bin/env python3
"""EVEZ Quantum Circuit Agent - Qiskit circuits: Bell, GHZ, teleport, Grover, QFT, VQE."""
import json, argparse, numpy as np, math
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace as qk_pt

try:
    from qiskit_aer import AerSimulator; HAS_AER = True
except ImportError:
    from qiskit.providers.basic_provider import BasicSimulator; HAS_AER = False

def get_sim():
    return AerSimulator() if HAS_AER else BasicSimulator()

def bell_circuit(which="phi+"):
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    if which in ("phi-", "psi-"): qc.z(0)
    qc.cx(0, 1)
    if which in ("psi+", "psi-"): qc.x(1)
    qc.measure([0,1], [0,1])
    return qc

def ghz_circuit(n=3):
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for i in range(1, n): qc.cx(0, i)
    qc.measure(range(n), range(n))
    return qc

def teleport_circuit():
    qc = QuantumCircuit(3, 3)
    qc.x(0); qc.h(1); qc.cx(1, 2)
    qc.cx(0, 1); qc.h(0)
    qc.measure(0, 0); qc.measure(1, 1)
    qc.cx(1, 2); qc.cz(0, 2); qc.measure(2, 2)
    return qc

def grover_oracle(n, marked):
    """Build a phase oracle for the marked state."""
    oracle = QuantumCircuit(n)
    for i, b in enumerate(marked):
        if b == "0": oracle.x(i)
    oracle.h(n-1)
    if n == 1:
        oracle.z(0)
    elif n == 2:
        oracle.cz(0, 1)
    else:
        oracle.mcx(list(range(n-1)), n-1)
    oracle.h(n-1)
    for i, b in enumerate(marked):
        if b == "0": oracle.x(i)
    return oracle

def grover_diffuser(n):
    """Build the Grover diffuser (inversion about the mean)."""
    diff = QuantumCircuit(n)
    for i in range(n): diff.h(i)
    for i in range(n): diff.x(i)
    diff.h(n-1)
    if n == 1:
        diff.z(0)
    elif n == 2:
        diff.cz(0, 1)
    else:
        diff.mcx(list(range(n-1)), n-1)
    diff.h(n-1)
    for i in range(n): diff.x(i)
    for i in range(n): diff.h(i)
    return diff

def grover_circuit(n=3, marked="101"):
    marked = marked.zfill(n)[:n]  # ensure correct length
    qc = QuantumCircuit(n, n)
    # Initialize uniform superposition
    for i in range(n): qc.h(i)
    # Optimal iterations: pi/4 * sqrt(2^n / num_marked)
    n_iter = max(1, int(round(math.pi / 4 * math.sqrt(2**n))))
    oracle = grover_oracle(n, marked)
    diffuser = grover_diffuser(n)
    for _ in range(n_iter):
        qc.compose(oracle, inplace=True)
        qc.compose(diffuser, inplace=True)
    qc.measure(range(n), range(n))
    return qc

def qft_circuit(n=3):
    """Manual QFT implementation."""
    qc = QuantumCircuit(n, n)
    for i in range(n): qc.h(i)
    # QFT
    for i in range(n):
        for j in range(i):
            qc.cp(math.pi / (2**(i-j)), j, i)
        qc.h(i)
    # Swap qubits for correct ordering
    for i in range(n//2):
        qc.swap(i, n-1-i)
    qc.measure(range(n), range(n))
    return qc

def vqe_ansatz(n=2, layers=2):
    from qiskit.circuit import Parameter
    qc = QuantumCircuit(n); params = []
    for L in range(layers):
        for i in range(n):
            t = Parameter(f"t_{L}_{i}"); qc.ry(t, i); params.append(t)
        for i in range(n-1): qc.cx(i, i+1)
    return qc, params

def simulate(qc, shots=1024):
    sim = get_sim(); tqc = transpile(qc, sim)
    return dict(sim.run(tqc, shots=shots).result().get_counts())

def entanglement_entropy(qc):
    qc_nm = qc.remove_final_measurements(inplace=False) if qc.num_clbits > 0 else qc.copy()
    sv = Statevector.from_instruction(qc_nm)
    dm = DensityMatrix(sv)
    n = qc.num_qubits
    traced = qk_pt(dm, list(range(n//2)))
    evals = np.linalg.eigvalsh(traced.data)
    evals = evals[evals > 1e-15]
    return float(-np.sum(evals * np.log2(evals)))

def run(task="bell", **kw):
    if task == "vqe":
        qc, params = vqe_ansatz(kw.get("n_qubits", 2), kw.get("layers", 2))
        return {"task": "vqe", "n_qubits": qc.num_qubits, "n_parameters": len(params),
                "depth": qc.depth(), "params": [str(p) for p in params]}
    builders = {
        "bell": lambda: bell_circuit(kw.get("which", "phi+")),
        "ghz": lambda: ghz_circuit(kw.get("n_qubits", 3)),
        "teleport": lambda: teleport_circuit(),
        "grover": lambda: grover_circuit(kw.get("n_qubits", 3), kw.get("marked", "101")),
        "qft": lambda: qft_circuit(kw.get("n_qubits", 3)),
    }
    qc = builders[task]()
    result = {"task": task, "n_qubits": qc.num_qubits, "depth": qc.depth(),
              "gate_counts": dict(qc.count_ops()),
              "measurement_counts": simulate(qc, kw.get("shots", 1024))}
    try:
        result["entanglement_entropy"] = entanglement_entropy(qc)
    except Exception as e:
        result["entanglement_error"] = str(e)
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="EVEZ Quantum Circuit Agent")
    p.add_argument("--task", choices=["bell","ghz","teleport","grover","qft","vqe"], default="bell")
    p.add_argument("--which", default="phi+")
    p.add_argument("--n-qubits", type=int, default=3)
    p.add_argument("--marked", default="101")
    p.add_argument("--shots", type=int, default=1024)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    r = run(a.task, which=a.which, n_qubits=a.n_qubits, marked=a.marked, shots=a.shots)
    print(json.dumps(r, default=str, indent=2) if a.json else json.dumps(r, default=str))
