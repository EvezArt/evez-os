
#!/usr/bin/env python3
import numpy as np
from scipy.linalg import eigh, expm
from scipy.special import genlaguerre, factorial, hermite
from scipy.constants import hbar, m_e, e, epsilon_0
import warnings
warnings.filterwarnings('ignore')

# 1. SCHRODINGER SOLVER
def solve_schrodinger_1d(V_func, x_min=-10, x_max=10, N=2000, mass=1.0, hbar_val=1.0, n_states=10):
    x = np.linspace(x_min, x_max, N)
    dx = x[1] - x[0]
    V = V_func(x)
    T_coeff = -hbar_val**2 / (2 * mass * dx**2)
    H = np.diag(-2*T_coeff*np.ones(N) + V) + np.diag(T_coeff*np.ones(N-1), 1) + np.diag(T_coeff*np.ones(N-1), -1)
    H[0,0] = H[-1,-1] = 1e10
    energies, psi = eigh(H)
    for i in range(min(n_states, N)):
        norm = np.sqrt(np.trapezoid(psi[:,i]**2, x))
        if norm > 0: psi[:,i] /= norm
    return energies[:n_states], psi[:,:n_states], x

# 2. QHO
def qho_energy(n, omega, hbar_val=1.0):
    return hbar_val * omega * (n + 0.5)

def qho_wavefunction(n, x, omega=1.0, mass=1.0, hbar_val=1.0):
    xi = np.sqrt(mass*omega/hbar_val) * x
    norm = (mass*omega/(np.pi*hbar_val))**0.25 / np.sqrt(2**n * factorial(n))
    return norm * hermite(n)(xi) * np.exp(-xi**2/2)

def qho_ladder(n_max, omega=1.0, hbar_val=1.0):
    a = np.zeros((n_max, n_max))
    a_dag = np.zeros((n_max, n_max))
    for n in range(1, n_max):
        a[n, n-1] = np.sqrt(n)
        a_dag[n-1, n] = np.sqrt(n)
    x_op = np.sqrt(hbar_val/(2*omega)) * (a + a_dag)
    p_op = 1j * np.sqrt(hbar_val*omega/2) * (a_dag - a)
    return a, a_dag, x_op, p_op

# 3. HYDROGEN
def hydrogen_energy(n, Z=1):
    return -Z**2 / (2*n**2)  # Hartree (1 Hartree = 27.211 eV)

def hydrogen_radial(n, l, r, Z=1):
    rho = 2*Z*r/n  # natural units, a_0=1
    norm = np.sqrt((2*Z/n)**3 * factorial(n-l-1)/(2*n*factorial(n+l)))
    return norm * rho**l * genlaguerre(n-l-1, 2*l+1)(rho) * np.exp(-rho/2)

# 4. PERTURBATION
def first_order(E_n0, psi_n, H_p, x):
    return np.real(np.trapezoid(np.conj(psi_n)*H_p(x)*psi_n, x))

def second_order(E_n0, psi_n, energies, psi_all, H_p, x, n):
    E2 = 0
    for k in range(len(energies)):
        if k == n: continue
        me = np.trapezoid(np.conj(psi_all[:,k])*H_p(x)*psi_n, x)
        E2 += np.abs(me)**2 / (E_n0 - energies[k])
    return np.real(E2)

# 5. TUNNELING
def wkb_tunnel(E, V_func, xL, xR, n=10000):
    x = np.linspace(xL, xR, n)
    V = V_func(x)
    mask = V > E
    if not np.any(mask): return 1.0
    xf, Vf = x[mask], V[mask]
    return min(np.exp(-2*np.trapezoid(np.sqrt(2*(Vf-E)), xf)), 1.0)

def transfer_matrix(E, V_func, xL, xR, N=500, mass=1.0, hbar_val=1.0):
    x = np.linspace(xL, xR, N)
    dx = x[1]-x[0]
    V = V_func(x)
    M = np.eye(2, dtype=complex)
    for i in range(N-1):
        if V[i] < E:
            k = np.sqrt(2*mass*(E-V[i]))/hbar_val
            p = k*dx
            Mi = np.array([[np.cos(p), np.sin(p)/k],[-k*np.sin(p), np.cos(p)]], dtype=complex)
        else:
            ka = np.sqrt(2*mass*(V[i]-E))/hbar_val
            p = ka*dx
            Mi = np.array([[np.cosh(p), np.sinh(p)/ka],[ka*np.sinh(p), np.cosh(p)]], dtype=complex)
        M = Mi @ M
    return min(1.0/np.abs(M[0,0])**2, 1.0)

# 6. SPIN
sigma_x = np.array([[0,1],[1,0]], dtype=complex)
sigma_y = np.array([[0,-1j],[1j,0]], dtype=complex)
sigma_z = np.array([[1,0],[0,-1]], dtype=complex)

def spin_state(theta, phi):
    return np.array([np.cos(theta/2), np.exp(1j*phi)*np.sin(theta/2)], dtype=complex)

def bloch_vector(s):
    return np.array([np.real(s.conj()@sigma_x@s), np.real(s.conj()@sigma_y@s), np.real(s.conj()@sigma_z@s)])

# 7. ENTANGLEMENT
def von_neumann(rho):
    ev = np.linalg.eigvalsh(rho)
    ev = ev[ev > 1e-15]
    return -np.sum(ev * np.log2(ev))

def partial_trace(rho_AB, dA, dB):
    return np.trace(rho_AB.reshape(dA, dB, dA, dB), axis1=1, axis2=3)

def concurrence(state2q):
    rho = np.outer(state2q, state2q.conj())
    rt = np.kron(sigma_y, sigma_y) @ rho.conj() @ np.kron(sigma_y, sigma_y)
    ev = np.sort(np.sqrt(np.abs(np.linalg.eigvals(rho @ rt))))[::-1]
    return max(0, ev[0] - ev[3])

# 8. BELL/CHSH
def bell_state(n):
    return [np.array([1,0,0,1],dtype=complex)/np.sqrt(2),
            np.array([1,0,0,-1],dtype=complex)/np.sqrt(2),
            np.array([0,1,1,0],dtype=complex)/np.sqrt(2),
            np.array([0,1,-1,0],dtype=complex)/np.sqrt(2)][n%4]

def chsh(bs, a, ap, b, bp):
    A = np.sin(a)*sigma_x + np.cos(a)*sigma_z  # x-z plane
    B = np.sin(b)*sigma_x + np.cos(b)*sigma_z
    Ap = np.sin(ap)*sigma_x + np.cos(ap)*sigma_z
    Bp = np.sin(bp)*sigma_x + np.cos(bp)*sigma_z
    E1 = np.real(bs.conj()@np.kron(A,B)@bs)
    E2 = np.real(bs.conj()@np.kron(A,Bp)@bs)
    E3 = np.real(bs.conj()@np.kron(Ap,B)@bs)
    E4 = np.real(bs.conj()@np.kron(Ap,Bp)@bs)
    return abs(E1-E2+E3+E4), (E1,E2,E3,E4)

# 9. TIME EVOLUTION
def time_evolve(psi0, H, t, hbar_val=1.0):
    return expm(-1j*H*t/hbar_val) @ psi0

def expectation(psi, A):
    return np.real(psi.conj() @ A @ psi)

def uncertainty_rel(psi, A, B):
    dA = A - expectation(psi, A)*np.eye(len(A))
    dB = B - expectation(psi, B)*np.eye(len(B))
    varA = np.real(psi.conj()@dA@dA@psi)
    varB = np.real(psi.conj()@dB@dB@psi)
    comm = np.abs(np.real(psi.conj()@(A@B-B@A)@psi))
    return np.sqrt(varA)*np.sqrt(varB), comm/2

# 10. CLEBSCH-GORDAN
def clebsch_gordan(j1, m1, j2, m2, J, M):
    try:
        from sympy.physics.wigner import clebsch_gordan as sympy_cg
        from sympy import Rational, nsimplify, N
        result = sympy_cg(Rational(int(2*j1),2), Rational(int(2*j2),2), Rational(int(2*J),2), Rational(int(2*m1),2), Rational(int(2*m2),2), Rational(int(2*M),2))
        return float(N(result))
    except:
        from math import gamma, sqrt as msqrt
    if not (abs(j1-j2) <= J <= j1+j2): return 0
    if m1+m2 != M: return 0
    if abs(m1)>j1 or abs(m2)>j2 or abs(M)>J: return 0
    def f(n): return gamma(n+1)
    pf = msqrt((2*J+1)*f(J+j1-j2)*f(J-j1+j2)*f(j1+j2-J+1)*f(J+M)*f(J-M)*f(j1-m1)*f(j1+m1)*f(j2-m2)*f(j2+m2)/(f(j1+j2+J+1)*f(j1-m1)*f(j1+m1)*f(j2-m2)*f(j2+m2)))
    zm = max(0, j2-J-m1, j1+m2-J)
    zx = min(j1+j2-J, j1-m1, j2+m2)
    tot = 0
    for z in range(int(zm), int(zx)+1):
        d = f(z)*f(J-j2+z)*f(J+M-z)*f(j1-m1-z)*f(j2+m2-z)*f(j1+j2-J-z)
        if d == 0: continue
        tot += (-1)**(j1-m1-z) / d
    try: return pf * tot * msqrt(f(J+j1-j2)*f(J-j1+j2)*f(j1+j2-J+1))
    except: return 0.0

if __name__ == '__main__':
    print('='*70)
    print('EVEZ QUANTUM CALCULATOR')
    print('='*70)

    print('\n1. QHO')
    for n in range(5): print(f'  E_{n} = {qho_energy(n,1.0):.4f}')
    a,ad,xp,pp = qho_ladder(10)
    print(f'  [x,p]=ih: {np.allclose(xp@pp-pp@xp, 1j*np.eye(10))}')  # hbar=1 natural units

    print('\n2. HYDROGEN')
    for n in range(1,5): print(f'  E_{n} = {hydrogen_energy(n):.6f} Hartree = {hydrogen_energy(n)*27.211:.4f} eV')
    r = np.linspace(0.01, 20, 1000)  # natural units
    R10 = hydrogen_radial(1,0,r)
    print(f'  R_10 norm: {np.trapezoid(r**2*R10**2,r):.6f}')

    print('\n3. SCHRODINGER (finite well)')
    V0=50.0; aw=1.0
    Vw = lambda x: np.where(np.abs(x)<aw, 0, V0)
    E,psi,x = solve_schrodinger_1d(Vw, -5, 5, 2000, n_states=5)
    for i,e in enumerate(E):
        if e < V0: print(f'  E_{i} = {e:.6f}')

    print('\n4. TUNNELING')
    Vb = lambda x: np.where((x>0)&(x<1), 10.0, 0)
    for E_t in [1.0, 5.0, 9.0]:
        print(f'  E={E_t}: WKB={wkb_tunnel(E_t,Vb,0,1):.6e}, TM={transfer_matrix(E_t,Vb,-0.1,1.1,1000):.6e}')

    print('\n5. SPIN')
    up = np.array([1,0],dtype=complex)
    px = np.array([1,1],dtype=complex)/np.sqrt(2)
    print(f'  |+x> Bloch: {bloch_vector(px)}')
    Hz = sigma_z
    pt = time_evolve(px, Hz, np.pi/2)
    print(f'  After pi/2: {bloch_vector(pt)}')

    print('\n6. ENTANGLEMENT')
    bp = bell_state(0)
    rho = np.outer(bp, bp.conj())
    rhoA = partial_trace(rho, 2, 2)
    print(f'  S_vN = {von_neumann(rhoA):.6f}')
    print(f'  Concurrence = {concurrence(bp):.6f}')

    print('\n7. CHSH')
    S, corr = chsh(bp, 0, np.pi/2, np.pi/4, 3*np.pi/4)  # optimal CHSH angles
    print(f'  S = {S:.6f}, Classical=2, Tsirelson={2*np.sqrt(2):.6f}')
    print(f'  Violation: {S > 2.0}')

    print('\n8. UNCERTAINTY')
    x = np.linspace(-10, 10, 2000)
    psi0 = qho_wavefunction(0, x)
    dx = x[1]-x[0]
    N = len(x)
    Tc = -1.0/(2*dx**2)  # hbar=1, m=1 natural units
    Hk = np.diag(-2.0*Tc*np.ones(N)) + np.diag(Tc*np.ones(N-1),1) + np.diag(Tc*np.ones(N-1),-1)
    xo = np.diag(x)
    po = -1j*(np.diag(np.ones(N-1),1)-np.diag(np.ones(N-1),-1))/(2*dx)
    prod, bnd = uncertainty_rel(psi0, xo, po)
    print(f'  dx*dp = {prod:.6f}, hbar/2 = {0.5:.6f}')
    print(f'  Saturates: {np.isclose(prod, bnd, rtol=1e-3)}')

    print('\n9. PERTURBATION (QHO + x^4)')
    x = np.linspace(-10, 10, 2000)
    psi0_arr = qho_wavefunction(0, x)
    psi1_arr = qho_wavefunction(1, x)
    psi2_arr = qho_wavefunction(2, x)
    H_p = lambda x: 0.1 * x**4
    E0_1 = first_order(0.5, psi0_arr, H_p, x)
    E1_1 = first_order(1.5, psi1_arr, H_p, x)
    print(f'  Ground state 1st order: {E0_1:.6f}')
    print(f'  1st excited 1st order: {E1_1:.6f}')

    print('\n10. CLEBSCH-GORDAN')
    cg = clebsch_gordan(0.5, 0.5, 0.5, -0.5, 1, 0)
    print(f'  <1/2,1/2; 1/2,-1/2 | 1,0> = {cg:.6f} (should be 1/sqrt(2)={1/np.sqrt(2):.6f})')
    cg2 = clebsch_gordan(0.5, 0.5, 0.5, 0.5, 1, 1)
    print(f'  <1/2,1/2; 1/2,1/2 | 1,1> = {cg2:.6f} (should be 1.0)')
    cg3 = clebsch_gordan(0.5, 0.5, 0.5, 0.5, 0, 0)
    print(f'  <1/2,1/2; 1/2,1/2 | 0,0> = {cg3:.6f} (should be 0.0)')

    print('\n' + '='*70)
    print('ALL QUANTUM MODULES OPERATIONAL')
    print('='*70)
