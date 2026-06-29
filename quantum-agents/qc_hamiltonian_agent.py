#!/usr/bin/env python3
"""EVEZ Quantum Hamiltonian Agent - QuTiP-based exact diagonalization and dynamics.
Solves: transverse Ising, Heisenberg XYZ, QHO lattice, Bose-Hubbard, Dicke model."""
import json, argparse, numpy as np
import qutip as qt

def transverse_ising(N=4, J=1.0, h=0.5):
    """Transverse-field Ising model: H = -J*sum(Z_i Z_{i+1}) - h*sum(X_i)."""
    si = qt.qeye(2); sx = qt.sigmax(); sz = qt.sigmaz()
    H = qt.tensor([si]*N) * 0
    for i in range(N-1):
        ops = [si]*N; ops[i] = sz; ops[i+1] = sz
        H += -J * qt.tensor(ops)
    for i in range(N):
        ops = [si]*N; ops[i] = sx
        H += -h * qt.tensor(ops)
    return H

def heisenberg_xyz(N=4, Jx=1.0, Jy=1.0, Jz=1.0):
    """Heisenberg XYZ chain: H = sum(J_a * s_a_i * s_a_{i+1})."""
    si = qt.qeye(2)
    sx, sy, sz = qt.sigmax(), qt.sigmay(), qt.sigmaz()
    H = qt.tensor([si]*N) * 0
    for i in range(N-1):
        for J, op in [(Jx, sx), (Jy, sy), (Jz, sz)]:
            ops = [si]*N; ops[i] = op; ops[i+1] = op
            H += J * qt.tensor(ops)
    return H

def qho_lattice(N=4, omega=1.0, k=0.1, nmax=5):
    """Coupled quantum harmonic oscillators on a 1D lattice."""
    a = qt.destroy(nmax)
    H = qt.tensor([qt.qeye(nmax)]*N) * 0
    for i in range(N):
        ops = [qt.qeye(nmax)]*N; ops[i] = a.dag()*a
        H += omega * qt.tensor(ops)
    for i in range(N-1):
        ops1 = [qt.qeye(nmax)]*N; ops1[i] = a.dag(); ops1[i+1] = a
        ops2 = [qt.qeye(nmax)]*N; ops2[i] = a; ops2[i+1] = a.dag()
        H += k * (qt.tensor(ops1) + qt.tensor(ops2))
    return H

def bose_hubbard(N=3, t=1.0, U=2.0, nmax=4):
    """Bose-Hubbard model: H = -t*sum(b_i^dag b_{i+1} + h.c.) + U/2*sum(n_i*(n_i-1))."""
    a = qt.destroy(nmax)
    H = qt.tensor([qt.qeye(nmax)]*N) * 0
    for i in range(N-1):
        ops1 = [qt.qeye(nmax)]*N; ops1[i] = a.dag(); ops1[i+1] = a
        ops2 = [qt.qeye(nmax)]*N; ops2[i] = a; ops2[i+1] = a.dag()
        H += -t * (qt.tensor(ops1) + qt.tensor(ops2))
    for i in range(N):
        ops = [qt.qeye(nmax)]*N; ops[i] = a.dag()*a*(a.dag()*a - 1)
        H += U/2 * qt.tensor(ops)
    return H

def dicke_model(N=5, omega0=1.0, omega=1.0, g=0.1, nmax=10):
    """Dicke model: N two-level atoms coupled to a cavity mode."""
    a = qt.destroy(nmax)
    H_cav = omega * a.dag() * a
    H_atoms = qt.tensor([qt.sigmaz()/2]*N) * omega0
    H_int = qt.tensor([a.dag() + a] if False else [qt.qeye(nmax)])
    # Build properly
    H = qt.tensor([qt.qeye(nmax)] + [qt.qeye(2)]*N) * 0
    cav_ops = [qt.qeye(nmax)] + [qt.qeye(2)]*N
    cav_ops[0] = omega * a.dag() * a
    H += qt.tensor(cav_ops)
    for i in range(N):
        atom_ops = [qt.qeye(nmax)] + [qt.qeye(2)]*N
        atom_ops[i+1] = omega0 * qt.sigmaz()/2
        H += qt.tensor(atom_ops)
    for i in range(N):
        int_ops = [qt.qeye(nmax)] + [qt.qeye(2)]*N
        int_ops[0] = (a.dag() + a) * g
        int_ops[i+1] = qt.sigmax()
        H += qt.tensor(int_ops)
    return H

def solve_hamiltonian(H, n_eigenvalues=10):
    """Diagonalize Hamiltonian and return eigenvalues/eigenstates."""
    evals, evecs = H.eigenstates()
    return {
        "eigenvalues": [float(e) for e in evals[:n_eigenvalues]],
        "n_states": H.shape[0],
        "hilbert_dim": int(np.log2(H.shape[0])) if H.shape[0] & (H.shape[0]-1) == 0 else None,
        "matrix_shape": list(H.shape),
    }

def time_evolution(H, psi0, times):
    """Solve Schrodinger equation: d|psi>/dt = -i H |psi>."""
    result = qt.mesolve(H, psi0, times, [], [])
    return result.states

def correlation_function(H, psi0, A, times):
    """Compute <A>(t) = <psi(t)|A|psi(t)>."""
    result = qt.mesolve(H, psi0, times, [], [A])
    return [complex(x) for x in result.expect[0]]

def run(model="ising", **kw):
    models = {
        "ising": lambda: transverse_ising(kw.get("N", 4), kw.get("J", 1.0), kw.get("h", 0.5)),
        "heisenberg": lambda: heisenberg_xyz(kw.get("N", 4), kw.get("Jx",1), kw.get("Jy",1), kw.get("Jz",1)),
        "qho_lattice": lambda: qho_lattice(kw.get("N", 4), kw.get("omega",1), kw.get("k",0.1), kw.get("nmax",5)),
        "bose_hubbard": lambda: bose_hubbard(kw.get("N", 3), kw.get("t",1), kw.get("U",2), kw.get("nmax",4)),
        "dicke": lambda: dicke_model(kw.get("N", 5), kw.get("omega0",1), kw.get("omega",1), kw.get("g",0.1), kw.get("nmax",10)),
    }
    H = models[model]()
    result = {"model": model, "matrix_shape": list(H.shape), "n_eigenvalues_computed": kw.get("n_eigenvalues", 10)}
    result.update(solve_hamiltonian(H, kw.get("n_eigenvalues", 10)))
    # Compute magnetization for spin models
    if model in ("ising", "heisenberg"):
        N = kw.get("N", 4)
        sz_total = qt.tensor([qt.sigmaz()]*N) if model == "ising" else qt.tensor([qt.sigmaz()]*N)
        gs = H.groundstate()
        result["ground_state_energy"] = float(gs[0])
        result["ground_state_magnetization"] = float(qt.expect(sz_total, gs[1]))
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="EVEZ Quantum Hamiltonian Agent")
    p.add_argument("--model", choices=["ising","heisenberg","qho_lattice","bose_hubbard","dicke"], default="ising")
    p.add_argument("--N", type=int, default=4)
    p.add_argument("--J", type=float, default=1.0)
    p.add_argument("--h", type=float, default=0.5)
    p.add_argument("--n-eigenvalues", type=int, default=10)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    r = run(a.model, N=a.N, J=a.J, h=a.h, n_eigenvalues=a.n_eigenvalues)
    print(json.dumps(r, default=str, indent=2) if a.json else json.dumps(r, default=str))
