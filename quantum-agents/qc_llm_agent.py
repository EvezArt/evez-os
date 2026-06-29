#!/usr/bin/env python3
"""EVEZ Quantum LLM Agent - Natural language to quantum computation.
Parses physics questions, routes to appropriate quantum agent, returns results.
Uses OpenClaw subagent LLM for natural language understanding."""
import json, sys, argparse, re, subprocess, os

WORKSPACE = os.path.dirname(os.path.abspath(__file__))

INTENT_PATTERNS = {
    "bell": [r"bell.?state", r"entangle.*pair", r"epr", r"phi.?[+-]", r"psi.?[+-]"],
    "ghz": [r"ghz", r"greenberger.*horne.*zeilinger", r"multi.*qubit.*entangle"],
    "teleport": [r"teleport", r"send.*state", r"transfer.*quantum.*state"],
    "grover": [r"grover", r"search.*unstructured", r"amplitude.*amplif", r"quantum.*search"],
    "qft": [r"qft", r"quantum.*fourier.*transform", r"frequency.*domain.*quantum"],
    "vqe": [r"vqe", r"variational.*eigensolver", r"ground.*state.*energy", r"molecule.*energy"],
    "qaoa": [r"qaoa", r"max.?cut", r"combinatorial.*optim", r"graph.*optim"],
    "ising": [r"ising", r"transverse.*field", r"spin.*chain", r"magnet.*quantum"],
    "heisenberg": [r"heisenberg", r"xyz.*model", r"spin.*interact"],
    "tunneling": [r"tunnel", r"barrier.*penetrat", r"wkb", r"transmission.*coefficient"],
    "hydrogen": [r"hydrogen", r"atomic.*orbital", r"radial.*wavefunction", r"rydberg"],
    "qho": [r"harmonic.*oscillator", r"qho", r"ladder.*operator", r"zero.*point"],
    "perturbation": [r"perturb", r"first.*order.*correction", r"second.*order.*energy"],
    "entanglement": [r"entanglement.*entropy", r"von.*neumann", r"concurrence", r"schmidt"],
    "chsh": [r"bell.*inequality", r"chsh", r"local.*hidden.*variable", r"tsirelson"],
    "uncertainty": [r"uncertainty.*principle", r"heisenberg.*uncertain", r"robertson"],
    "spin": [r"spin.*1/2", r"bloch.*sphere", r"pauli.*matrix", r"zeeman"],
    "qho_lattice": [r"coupled.*oscillator", r"phonon.*chain", r"lattice.*vibration"],
    "bose_hubbard": [r"bose.*hubbard", r"superfluid.*mott", r"boson.*lattice"],
    "dicke": [r"dicke", r"superradian", r"collective.*emission", r"cavity.*qed"],
    "quantum_ml": [r"quantum.*machine.*learn", r"quantum.*classif", r"quantum.*neural"],
}

def detect_intent(query):
    q = query.lower()
    for intent, patterns in INTENT_PATTERNS.items():
        for p in patterns:
            if re.search(p, q):
                return intent
    return None

def route_to_agent(intent):
    routing = {
        "bell": ("qc_circuit_agent.py", "bell"),
        "ghz": ("qc_circuit_agent.py", "ghz"),
        "teleport": ("qc_circuit_agent.py", "teleport"),
        "grover": ("qc_circuit_agent.py", "grover"),
        "qft": ("qc_circuit_agent.py", "qft"),
        "vqe": ("qc_variational_agent.py", "vqe_h2"),
        "qaoa": ("qc_variational_agent.py", "qaoa_maxcut"),
        "quantum_ml": ("qc_variational_agent.py", "quantum_ml"),
        "ising": ("qc_hamiltonian_agent.py", "ising"),
        "heisenberg": ("qc_hamiltonian_agent.py", "heisenberg"),
        "qho_lattice": ("qc_hamiltonian_agent.py", "qho_lattice"),
        "bose_hubbard": ("qc_hamiltonian_agent.py", "bose_hubbard"),
        "dicke": ("qc_hamiltonian_agent.py", "dicke"),
        "tunneling": ("evez_quantum_calculator.py", None),
        "hydrogen": ("evez_quantum_calculator.py", None),
        "qho": ("evez_quantum_calculator.py", None),
        "perturbation": ("evez_quantum_calculator.py", None),
        "entanglement": ("evez_quantum_calculator.py", None),
        "chsh": ("evez_quantum_calculator.py", None),
        "uncertainty": ("evez_quantum_calculator.py", None),
        "spin": ("evez_quantum_calculator.py", None),
    }
    return routing.get(intent)

def execute_agent(script, task, extra_args=None):
    cmd = ["python3", os.path.join(WORKSPACE, script), "--json"]
    if task and script == "qc_circuit_agent.py":
        cmd += ["--task", task]
    elif task and script == "qc_hamiltonian_agent.py":
        cmd += ["--model", task]
    elif task and script == "qc_variational_agent.py":
        cmd += ["--task", task]
    if extra_args:
        cmd += extra_args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": result.stderr.strip(), "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "Agent timed out after 120s"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON output", "raw": result.stdout[:500]}

def extract_params(query):
    params = {}
    n_match = re.search(r"(\d+)\s*qubit", query.lower())
    if n_match: params["n_qubits"] = int(n_match.group(1))
    N_match = re.search(r"N\s*=\s*(\d+)|(\d+)\s*site|(\d+)\s*spin", query.lower())
    if N_match: params["N"] = int(next(g for g in N_match.groups() if g))
    shots_match = re.search(r"(\d+)\s*shot", query.lower())
    if shots_match: params["shots"] = int(shots_match.group(1))
    return params

def run(query=""):
    if not query:
        query = "Compute Bell state entanglement entropy"
    intent = detect_intent(query)
    if not intent:
        return {"error": "Could not detect quantum computation intent", "query": query,
                "available_intents": list(INTENT_PATTERNS.keys())}
    
    routing = route_to_agent(intent)
    if not routing:
        return {"error": f"No agent routing for intent: {intent}"}
    
    script, task = routing
    params = extract_params(query)
    extra = []
    for k, v in params.items():
        extra.extend([f"--{k.replace('_','-')}", str(v)])
    
    result = execute_agent(script, task, extra if extra else None)
    return {"query": query, "intent": intent, "agent": script, "task": task,
            "params": params, "result": result}

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="EVEZ Quantum LLM Agent")
    p.add_argument("query", nargs="*", help="Natural language quantum query")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    q = " ".join(a.query) if a.query else ""
    r = run(q)
    print(json.dumps(r, default=str, indent=2) if a.json else json.dumps(r, default=str))
