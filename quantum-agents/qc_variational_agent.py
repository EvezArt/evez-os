#!/usr/bin/env python3
"""EVEZ Quantum Variational Agent - PennyLane VQE/QAOA/quantum ML.
Optimizes variational circuits for ground state energy, combinatorial optimization."""
import json, argparse, numpy as np
import pennylane as qml
from pennylane import numpy as pnp

def vqe_h2(r=0.74):
    """VQE for H2 molecule using minimal basis (2 qubits)."""
    # H2 Hamiltonian in STO-3G (hardcoded for r=0.74)
    coeffs = [-0.810547980537 + 0.0, 0.17218393212, -0.225753492224,
              0.17218393212, 0.12092029854, 0.04523279997, 0.04523279997,
              0.16586802491, 0.12092029854, 0.04523279997, 0.04523279997,
              0.16586802491, 0.17434844283, -0.225753492224]
    obs = [qml.Identity(0), qml.PauliZ(0), qml.PauliZ(1),
           qml.PauliZ(0) @ qml.PauliZ(1), qml.PauliY(0) @ qml.PauliY(1),
           qml.PauliX(0) @ qml.PauliY(1), qml.PauliY(0) @ qml.PauliX(1),
           qml.PauliZ(0) @ qml.PauliZ(1), qml.PauliX(0) @ qml.PauliX(1),
           qml.PauliX(0) @ qml.PauliZ(1), qml.PauliZ(0) @ qml.PauliX(1),
           qml.PauliY(0) @ qml.PauliY(1), qml.PauliZ(0) @ qml.PauliZ(1), qml.PauliZ(1)]
    H = qml.Hamiltonian(coeffs, obs)
    dev = qml.device("lightning.qubit", wires=2)
    
    @qml.qnode(dev)
    def circuit(params):
        qml.RY(params[0], wires=0)
        qml.RY(params[1], wires=1)
        qml.CNOT(wires=[0, 1])
        qml.RY(params[2], wires=0)
        qml.RY(params[3], wires=1)
        qml.CNOT(wires=[0, 1])
        return qml.expval(H)
    
    opt = qml.GradientDescentOptimizer(stepsize=0.4)
    params = pnp.array([0.1, 0.1, 0.1, 0.1], requires_grad=True)
    energies = []
    for i in range(100):
        params, e = opt.step_and_cost(circuit, params)
        energies.append(float(e))
    return {"task": "vqe_h2", "final_energy": energies[-1], "n_iterations": len(energies),
            "convergence": energies[-5:], "optimal_params": [float(p) for p in params]}

def qaoa_maxcut(n=4, edges=None):
    """QAOA for MaxCut on a graph."""
    if edges is None:
        edges = [(0,1), (1,2), (2,3), (3,0), (0,2)]
    dev = qml.device("lightning.qubit", wires=n)
    
    def cost_hamiltonian():
        coeffs = []; obs = []
        for i, j in edges:
            coeffs.append(0.5)
            obs.append(qml.PauliZ(i) @ qml.PauliZ(j))
        return qml.Hamiltonian(coeffs, obs)
    
    H_cost = cost_hamiltonian()
    H_mix = qml.Hamiltonian([1.0]*n, [qml.PauliX(i) for i in range(n)])
    
    @qml.qnode(dev)
    def qaoa_circuit(params):
        p = len(params) // 2
        gammas = params[:p]; betas = params[p:]
        for i in range(n): qml.Hadamard(wires=i)
        for layer in range(p):
            qml.templates.ApproxTimeEvolution(H_cost, gammas[layer], 1)
            qml.templates.ApproxTimeEvolution(H_mix, betas[layer], 1)
        return qml.expval(H_cost)
    
    opt = qml.AdamOptimizer(stepsize=0.05)
    p_layers = 2
    params = pnp.array([0.1]*(2*p_layers), requires_grad=True)
    costs = []
    for i in range(50):
        params, c = opt.step_and_cost(qaoa_circuit, params)
        costs.append(float(c))
    return {"task": "qaoa_maxcut", "n_qubits": n, "n_edges": len(edges),
            "final_cost": costs[-1], "n_iterations": len(costs),
            "convergence": costs[-5:], "optimal_params": [float(p) for p in params]}

def quantum_ml_classifier(n_qubits=2, n_samples=20):
    """Quantum ML classifier using angle embedding + variational circuit."""
    dev = qml.device("lightning.qubit", wires=n_qubits)
    
    @qml.qnode(dev)
    def circuit(x, weights):
        for i in range(n_qubits): qml.AngleEmbedding(features=x, wires=range(n_qubits))
        qml.StronglyEntanglingLayers(weights, wires=range(n_qubits))
        return qml.expval(qml.PauliZ(0))
    
    # Generate synthetic data
    np.random.seed(42)
    X = np.random.randn(n_samples, n_qubits)
    Y = np.sign(X[:, 0] * X[:, 1])  # Nonlinear classification
    
    # Simple gradient descent
    weights = pnp.randn(2, n_qubits, 3, requires_grad=True)
    opt = qml.GradientDescentOptimizer(stepsize=0.1)
    losses = []
    for epoch in range(30):
        epoch_loss = 0
        for i in range(n_samples):
            def loss_fn(w, x=X[i], y=Y[i]):
                pred = circuit(x, w)
                return (pred - y)**2
            weights, l = opt.step_and_cost(loss_fn, weights)
            epoch_loss += float(l)
        losses.append(epoch_loss / n_samples)
    return {"task": "quantum_ml", "n_qubits": n_qubits, "n_samples": n_samples,
            "final_loss": losses[-1], "loss_convergence": losses[-5:]}

def run(task="vqe_h2", **kw):
    tasks = {
        "vqe_h2": lambda: vqe_h2(kw.get("r", 0.74)),
        "qaoa_maxcut": lambda: qaoa_maxcut(kw.get("n", 4), kw.get("edges")),
        "quantum_ml": lambda: quantum_ml_classifier(kw.get("n_qubits", 2), kw.get("n_samples", 20)),
    }
    return tasks[task]()

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="EVEZ Quantum Variational Agent")
    p.add_argument("--task", choices=["vqe_h2", "qaoa_maxcut", "quantum_ml"], default="vqe_h2")
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    r = run(a.task, n=a.n)
    print(json.dumps(r, default=str, indent=2) if a.json else json.dumps(r, default=str))
