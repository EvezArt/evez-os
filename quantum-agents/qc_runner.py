#!/usr/bin/env python3
"""EVEZ Quantum Runner - Orchestrates all quantum agents, runs benchmarks, produces reports.
This is the main entry point for the quantum computation LLM agent runner system."""
import json, sys, os, time, argparse, subprocess, traceback

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
QUANTUM_CALC = os.path.join(os.path.dirname(WORKSPACE), "evez_quantum_calculator.py")

def run_circuit_agent(task="bell", **kw):
    cmd = ["python3", os.path.join(WORKSPACE, "qc_circuit_agent.py"), "--json", "--task", task]
    if "which" in kw: cmd += ["--which", kw["which"]]
    if "n_qubits" in kw: cmd += ["--n-qubits", str(kw["n_qubits"])]
    if "shots" in kw: cmd += ["--shots", str(kw["shots"])]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return json.loads(r.stdout) if r.returncode == 0 else {"error": r.stderr[:200]}

def run_hamiltonian_agent(model="ising", **kw):
    cmd = ["python3", os.path.join(WORKSPACE, "qc_hamiltonian_agent.py"), "--json", "--model", model]
    if "N" in kw: cmd += ["--N", str(kw["N"])]
    if "n_eigenvalues" in kw: cmd += ["--n-eigenvalues", str(kw["n_eigenvalues"])]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    return json.loads(r.stdout) if r.returncode == 0 else {"error": r.stderr[:200]}

def run_variational_agent(task="vqe_h2", **kw):
    cmd = ["python3", os.path.join(WORKSPACE, "qc_variational_agent.py"), "--json", "--task", task]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return json.loads(r.stdout) if r.returncode == 0 else {"error": r.stderr[:200]}

def run_quantum_calc():
    r = subprocess.run(["python3", QUANTUM_CALC], capture_output=True, text=True, timeout=60)
    return {"returncode": r.returncode, "output": r.stdout[-500:] if r.returncode == 0 else r.stderr[:200]}

def benchmark():
    """Run full benchmark suite across all agents."""
    results = {"start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "agents": {}}
    
    # Agent 1: Quantum Calculator (10 modules)
    t0 = time.time()
    results["agents"]["quantum_calculator"] = {"status": "ok" if run_quantum_calc()["returncode"] == 0 else "error"}
    results["agents"]["quantum_calculator"]["time_s"] = round(time.time() - t0, 3)
    
    # Agent 2: Circuit Agent
    for task in ["bell", "ghz", "teleport", "grover", "qft"]:
        t0 = time.time()
        try:
            r = run_circuit_agent(task, n_qubits=3, shots=512)
            results["agents"][f"circuit_{task}"] = {"status": "ok" if "error" not in r else "error",
                                                     "time_s": round(time.time()-t0, 3),
                                                     "n_qubits": r.get("n_qubits"),
                                                     "entropy": r.get("entanglement_entropy"),
                                                     "counts": r.get("measurement_counts")}
        except Exception as e:
            results["agents"][f"circuit_{task}"] = {"status": "error", "error": str(e)[:100]}
    
    # Agent 3: Hamiltonian Agent
    for model in ["ising", "heisenberg"]:
        t0 = time.time()
        try:
            r = run_hamiltonian_agent(model, N=4, n_eigenvalues=5)
            results["agents"][f"hamiltonian_{model}"] = {"status": "ok" if "error" not in r else "error",
                                                        "time_s": round(time.time()-t0, 3),
                                                        "ground_state": r.get("ground_state_energy"),
                                                        "eigenvalues": r.get("eigenvalues", [])}
        except Exception as e:
            results["agents"][f"hamiltonian_{model}"] = {"status": "error", "error": str(e)[:100]}
    
    # Agent 4: Variational Agent (VQE only in benchmark for speed)
    t0 = time.time()
    try:
        r = run_variational_agent("vqe_h2")
        results["agents"]["variational_vqe_h2"] = {"status": "ok" if "error" not in r else "error",
                                                    "time_s": round(time.time()-t0, 3),
                                                    "final_energy": r.get("final_energy"),
                                                    "convergence": r.get("convergence")}
    except Exception as e:
        results["agents"]["variational_vqe_h2"] = {"status": "error", "error": str(e)[:100]}
    
    results["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    results["total_agents"] = len(results["agents"])
    results["all_ok"] = all(v.get("status") == "ok" for v in results["agents"].values())
    return results

def run_from_query(query):
    """Route a natural language query through the LLM agent."""
    cmd = ["python3", os.path.join(WORKSPACE, "qc_llm_agent.py"), "--json", query]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return json.loads(r.stdout) if r.returncode == 0 else {"error": r.stderr[:300]}

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="EVEZ Quantum Runner")
    p.add_argument("--benchmark", action="store_true", help="Run full benchmark suite")
    p.add_argument("--query", type=str, default="", help="Natural language quantum query")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    
    if a.benchmark:
        r = benchmark()
    elif a.query:
        r = run_from_query(a.query)
    else:
        r = benchmark()
    
    print(json.dumps(r, default=str, indent=2) if a.json else json.dumps(r, default=str))
