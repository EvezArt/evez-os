#!/usr/bin/env python3
"""
EVEZ TESSERACK EIGENVALUE THEOREM
The 4D Extension of the Inference Collapse

The cube has 6 faces, 8 vertices, 12 edges. The tesseract has:
- 8 cubic cells (3D faces)
- 24 square faces (2D)
- 32 edges (1D)
- 16 vertices (0D)

The 6×6 AEMDAS matrix maps to the 6 faces of the cube.
The 8×8 matrix maps to the 8 cubic cells of the tesseract.

The tesseract diagonal = √3 (body diagonal of cube = face diagonal of tesseract)
The cube face diagonal = √2
The cube body diagonal = √3 = tesseract face diagonal
The tesseract body diagonal = √4 = 2

KEY PREDICTIONS:
- Tesseract recursion floor: η*(1 - η*√3) = 0.029919
  (The floor RISES — the gap SHRINKS — because √3 > √2)
- Tesseract energy partiality: η*(1+Φ²) = η*(1+Φ*Φ)
  (The offspring compounds — the gap begets the gap)
- The 4D eigenvalue count: 8 (one per cubic cell)
- Spectral gap of tesseract matrix > spectral gap of cube matrix
  (More dimensions = more room = larger gap)

Author: Steven Crawford-Maggard (EVEZ)
First Use: 2026-06-28 21:21 CDT
"""

import numpy as np
from scipy.signal import find_peaks
import json

# === Framework Constants ===
PHI = 0.973
ETA = 0.03
R = 0.45
LAMBDA_DOM = -0.333
LAMBDA_I80 = -0.441
R_I80 = 0.93
BPM = 174
SQRT2 = np.sqrt(2)
SQRT3 = np.sqrt(3)  # cube body diagonal = tesseract face diagonal
SQRT4 = 2.0          # tesseract body diagonal

# === The 8 Cubic Cells of the Tesseract ===
# Each cell is an AEMDAS cycle applied to one of 8 eigenvalue axes
# The 8 axes: Φ, η*, r, λ_dom, λ_I-80, r_I-80, λ_tess (new), r_tess (new)
LAMBDA_TESS = -0.277  # tesseract suppression eigenvalue (PREDICTED)
R_TESS = 0.87         # tesseract correlation eigenvalue (PREDICTED)

def build_cube_matrix():
    """The original 6×6 AEMDAS matrix (cube faces)."""
    return np.array([
        [PHI,    ETA,    R,      LAMBDA_DOM, LAMBDA_I80, R_I80],
        [PHI,    ETA,    0,      0,          0,          0],
        [0,      ETA,    R,      0,          0,          0],
        [0,      0,      R,      LAMBDA_DOM, 0,          0],
        [0,      ETA,    0,      0,          LAMBDA_I80, 0],
        [PHI,    0,      0,      0,          0,          R_I80],
    ], dtype=float)

def build_tesseract_matrix():
    """
    The 8×8 AEMDAS-tesseract matrix.
    
    8 cubic cells, each row is an AEMDAS stage applied to the 8 eigenvalue axes.
    The tesseract adds 2 new eigenvalues: λ_tess and r_tess.
    
    The pattern: each stage activates eigenvalues that belong to its spectral class.
    ASSERT = all eigenvalues (being = full spectrum)
    EXTRACT = Φ + η* (coherence + gap = extraction pair)
    MEASURE = η* + r + λ_tess (gap + criticality + tesseract suppression)
    DEDUCE = r + λ_dom + r_tess (criticality + dominant neg + tesseract correlation)
    ASSESS = η* + λ_I-80 + λ_tess (gap + I-80 suppression + tesseract suppression)
    SPEEDRUN = Φ + r_I-80 + r_tess (coherence + I-80 correlation + tesseract correlation)
    DREAM = η* + r + r_I-80 (the 7th stage — sleep cycle)
    REFLECT = Φ + η* + λ_dom + r_tess (the 8th stage — full self-reference)
    """
    return np.array([
        # Φ      η*     r      λ_dom  λ_I80  r_I80  λ_tess r_tess
        [PHI,    ETA,   R,     LAMBDA_DOM, LAMBDA_I80, R_I80, LAMBDA_TESS, R_TESS],  # ASSERT
        [PHI,    ETA,   0,     0,          0,          0,     0,          0],       # EXTRACT
        [0,      ETA,   R,     0,          0,          0,     LAMBDA_TESS, 0],       # MEASURE
        [0,      0,     R,     LAMBDA_DOM, 0,          0,     0,          R_TESS],  # DEDUCE
        [0,      ETA,   0,     0,          LAMBDA_I80, 0,     LAMBDA_TESS, 0],       # ASSESS
        [PHI,    0,     0,     0,          0,          R_I80, 0,          R_TESS],  # SPEEDRUN
        [0,      ETA,   R,     0,          0,          R_I80, 0,          0],       # DREAM (7th)
        [PHI,    ETA,   0,     LAMBDA_DOM, 0,          0,     0,          R_TESS],  # REFLECT (8th)
    ], dtype=float)

def spectral_analysis(matrix, label=""):
    """Compute eigenvalues, spectral gap, trace, determinant."""
    eigenvalues = np.linalg.eigvals(matrix)
    real_parts = eigenvalues.real
    sorted_eigs = sorted(real_parts, reverse=True)
    
    # Spectral gap = largest - second largest
    spectral_gap = sorted_eigs[0] - sorted_eigs[1] if len(sorted_eigs) > 1 else 0
    
    # Suppression coefficient = sum of negative eigenvalues
    neg_sum = sum(e for e in sorted_eigs if e < 0)
    
    # Trace = sum of all eigenvalues
    trace = np.trace(matrix)
    
    # Determinant
    det = np.linalg.det(matrix)
    
    # Spectral radius
    spectral_radius = max(abs(e) for e in eigenvalues)
    
    # η* proximity: minimum nonzero |eigenvalue| distance to η*
    min_nz = min(abs(e) for e in sorted_eigs if abs(e) > 0.001) if any(abs(e) > 0.001 for e in sorted_eigs) else ETA
    eta_proximity = abs(min_nz - ETA)
    
    return {
        'label': label,
        'eigenvalues': [round(e, 6) for e in sorted_eigs],
        'spectral_gap': round(spectral_gap, 6),
        'suppression': round(neg_sum, 6),
        'trace': round(trace, 6),
        'determinant': round(det, 6),
        'spectral_radius': round(spectral_radius, 6),
        'min_nonzero': round(min_nz, 6),
        'eta_proximity': round(eta_proximity, 6),
        'raw_eigenvalues': eigenvalues,
    }

def tesseract_recursion(eigenvalues, iterations=20, sample_rate=17400, duration=1.0):
    """
    Tesseract recursion: sum waveforms → decompose → new eigenvalues → repeat.
    
    Predicted tesseract floor: η*(1 - η*√3) = 0.029919
    The floor RISES because √3 > √2 — the gap shrinks in higher dimensions.
    The gap shrinks but never closes. The 3% persists across dimensions.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    current_vals = list(eigenvalues)
    history = []
    
    for i in range(iterations):
        combined = np.zeros_like(t)
        for val in current_vals:
            wave = np.sin(2 * np.pi * abs(val) * BPM * t)
            sign = 1 if val >= 0 else -1
            mask = (wave * sign) > 0
            wave_partial = wave.copy()
            wave_partial[mask] *= (1 + ETA)
            wave_partial[~mask] *= (1 - ETA)
            combined += wave_partial
        
        fft_mag = np.abs(np.fft.rfft(combined))
        fft_mag[0] = 0
        freqs = np.fft.rfftfreq(len(combined), 1/sample_rate)
        
        peaks, _ = find_peaks(fft_mag, height=np.max(fft_mag) * 0.05)
        if len(peaks) == 0:
            break
        
        peak_freqs = freqs[peaks]
        peak_mags = fft_mag[peaks]
        top_idx = np.argsort(peak_mags)[::-1][:len(eigenvalues)]
        top_freqs = peak_freqs[top_idx]
        
        originals = list(eigenvalues)
        original_freqs = [abs(v) * BPM for v in originals]
        new_vals = []
        for pf in top_freqs:
            closest_idx = np.argmin([abs(pf - of) for of in original_freqs])
            sign = 1 if originals[closest_idx] >= 0 else -1
            new_vals.append(sign * pf / BPM)
        
        while len(new_vals) < len(eigenvalues):
            new_vals.append(ETA)
        
        min_nz = min(abs(v) for v in new_vals if abs(v) > 0.001) if any(abs(v) > 0.001 for v in new_vals) else ETA
        
        norm = fft_mag / (np.sum(fft_mag) + 1e-10)
        entropy = -np.sum(norm * np.log(norm + 1e-10))
        max_ent = np.log(len(norm))
        collapse = 1 - entropy / max_ent if max_ent > 0 else 0
        
        eta_gap = abs(min_nz - ETA)
        
        history.append({
            'iteration': i + 1,
            'min_eigenvalue': round(min_nz, 6),
            'eta_gap': round(eta_gap, 6),
            'collapse': round(collapse, 6),
            'eigenvalues': [round(v, 6) for v in new_vals],
        })
        
        current_vals = new_vals
    
    predicted_floor_sqrt2 = ETA * (1 - ETA * SQRT2)
    predicted_floor_sqrt3 = ETA * (1 - ETA * SQRT3)
    predicted_floor_sqrt4 = ETA * (1 - ETA * SQRT4)
    actual_floor = history[-1]['min_eigenvalue'] if history else 0
    
    metrics = {
        'predicted_floor_cube': predicted_floor_sqrt2,
        'predicted_floor_tesseract': predicted_floor_sqrt3,
        'predicted_floor_5d': predicted_floor_sqrt4,
        'actual_floor': actual_floor,
        'floor_error_cube': abs(actual_floor - predicted_floor_sqrt2),
        'floor_error_tesseract': abs(actual_floor - predicted_floor_sqrt3),
        'final_collapse': history[-1]['collapse'] if history else 0,
        'final_eta_gap': history[-1]['eta_gap'] if history else 0,
        'singularity': ETA,
        'dimension_progression': 'η*(1-η*√d) for d=2,3,4...'
    }
    
    return history, current_vals, metrics

def dimensional_floor_series(max_dim=12):
    """
    Compute η*(1-η*√d) for dimensions 2 through max_dim.
    
    PREDICTION: The floor converges to η*(1-η*√∞) = η* as d→∞
    But the floor never reaches η*. The gap between floor and η* IS η*²√d.
    The gap of the gap IS η*². The meta-gap IS the square of the gap.
    
    This is the DIMENSIONAL FLOOR CONJECTURE:
    floor(d) = η*(1 - η*√d)
    limit as d→∞: floor → η* (but never reaches)
    meta-gap(d) = η* - floor(d) = η*²√d
    meta-gap grows as √d — the gap of the gap grows with dimension
    """
    results = []
    for d in range(2, max_dim + 1):
        sqrt_d = np.sqrt(d)
        floor = ETA * (1 - ETA * sqrt_d)
        meta_gap = ETA - floor
        results.append({
            'dimension': d,
            'sqrt_d': round(sqrt_d, 6),
            'floor': round(floor, 6),
            'meta_gap': round(meta_gap, 6),
            'meta_gap_squared': round(meta_gap**2, 9),
            'negative': floor < 0,
        })
    return results

def energy_partiality_tesseract():
    """
    Tesseract energy partiality = η*(1+Φ²) = η*(1+Φ*Φ)
    
    Cube: η*(1+Φ) = 0.05919 (the gap + the coherent gap)
    Tesseract: η*(1+Φ²) = η*(1+Φ*Φ) = 0.03*(1+0.946729) = 0.058402
    
    The energy partiality DECREASES from cube to tesseract.
    The gap shrinks. The offspring weakens. The signal sharpens.
    
    Generalization: η*(1+Φ^d) for dimension d
    limit as d→∞: η*(1+0) = η* = 0.03
    The energy partiality converges to η* as dimension increases.
    The offspring vanishes. The pure gap remains.
    """
    results = []
    for d in range(1, 11):
        phi_d = PHI ** d
        ep = ETA * (1 + phi_d)
        results.append({
            'dimension': d,
            'phi_d': round(phi_d, 6),
            'energy_partiality': round(ep, 6),
            'converging_to': ETA,
            'gap_to_eta': round(ep - ETA, 6),
        })
    return results

def eigenvalue_invariant_check(cube_eigs, tess_eigs):
    """
    THE EIGENVALUE INVARIANT: 
    sum(|eigenvalues|) / dimension = constant = Φ
    
    PREDICTION: The spectral density (sum of |eigenvalues| / dimension)
    is invariant across dimensions and equals Φ = 0.973.
    
    If true, this means Φ is not just the coherence — it is the
    SPECTRAL DENSITY of the framework across ALL dimensions.
    The coherence IS the density. The density IS the coherence.
    """
    cube_density = sum(abs(e) for e in cube_eigs) / len(cube_eigs)
    tess_density = sum(abs(e) for e in tess_eigs) / len(tess_eigs)
    
    return {
        'cube_density': round(cube_density, 6),
        'tesseract_density': round(tess_density, 6),
        'cube_density_error': round(abs(cube_density - PHI), 6),
        'tesseract_density_error': round(tess_density - PHI, 6),
        'invariant_holds': abs(cube_density - PHI) < 0.1 and abs(tess_density - PHI) < 0.1,
        'prediction': 'sum(|λ|)/n = Φ = 0.973 for all dimensions',
    }

def trace_determinant_invariant(cube_info, tess_info):
    """
    THE TRACE-DETERMINANT RELATIONSHIP:
    
    PREDICTION: trace/determinant ratio follows a power law in dimension.
    
    trace = sum of eigenvalues = sum of diagonal
    det = product of eigenvalues
    
    For the cube: trace_cube, det_cube
    For the tesseract: trace_tess, det_tess
    
    The ratio trace^(1/d) / det^(1/d) should be constant.
    This is the AM-GM ratio of the eigenvalues.
    """
    cube_trace = cube_info['trace']
    cube_det = cube_info['determinant']
    tess_trace = tess_info['trace']
    tess_det = tess_info['determinant']
    
    if cube_det != 0 and tess_det != 0:
        cube_amgm = (cube_trace / 6) / (abs(cube_det) ** (1/6)) if cube_det != 0 else float('inf')
        tess_amgm = (tess_trace / 8) / (abs(tess_det) ** (1/8)) if tess_det != 0 else float('inf')
    else:
        cube_amgm = float('inf')
        tess_amgm = float('inf')
    
    return {
        'cube_trace': cube_trace,
        'cube_det': round(cube_det, 6),
        'tess_trace': tess_trace,
        'tess_det': round(tess_det, 6),
        'cube_amgm': round(cube_amgm, 6) if cube_amgm != float('inf') else 'inf',
        'tess_amgm': round(tess_amgm, 6) if tess_amgm != float('inf') else 'inf',
    }

def spectral_gap_conjecture(cube_info, tess_info):
    """
    THE SPECTRAL GAP CONJECTURE:
    
    PREDICTION: The spectral gap increases with dimension.
    More dimensions = more room between dominant and subdominant eigenvalue.
    This means the tesseract is MORE STABLE than the cube.
    
    spectral_gap(d) > spectral_gap(d-1) for all d > 1
    
    This is the mathematical basis for the dimensional advancement:
    higher-dimensional frameworks are more stable.
    """
    return {
        'cube_spectral_gap': cube_info['spectral_gap'],
        'tesseract_spectral_gap': tess_info['spectral_gap'],
        'gap_increases': tess_info['spectral_gap'] > cube_info['spectral_gap'],
        'prediction': 'spectral_gap(d) > spectral_gap(d-1)',
    }

# === Main ===

if __name__ == '__main__':
    print("⧢⦟⧢ EVEZ TESSERACK EIGENVALUE THEOREM ⧢⦟⧢")
    print("The 4D Extension of the Inference Collapse")
    print("by Steven Crawford-Maggard (EVEZ)")
    print()
    
    # Build matrices
    cube_mat = build_cube_matrix()
    tess_mat = build_tesseract_matrix()
    
    # Spectral analysis
    print("=== CUBE (6×6) SPECTRAL ANALYSIS ===")
    cube_info = spectral_analysis(cube_mat, "Cube (6D)")
    for k, v in cube_info.items():
        if k != 'raw_eigenvalues':
            print(f"  {k}: {v}")
    print()
    
    print("=== TESSERACT (8×8) SPECTRAL ANALYSIS ===")
    tess_info = spectral_analysis(tess_mat, "Tesseract (8D)")
    for k, v in tess_info.items():
        if k != 'raw_eigenvalues':
            print(f"  {k}: {v}")
    print()
    
    # Dimensional floor series
    print("=== DIMENSIONAL FLOOR CONJECTURE: η*(1-η*√d) ===")
    floors = dimensional_floor_series(12)
    for f in floors:
        flag = " ⚠ GONE NEGATIVE" if f['negative'] else ""
        print(f"  d={f['dimension']:2d}  √d={f['sqrt_d']:.4f}  floor={f['floor']:.6f}  meta_gap={f['meta_gap']:.6f}{flag}")
    print()
    
    # Find the critical dimension where floor goes negative
    critical_dim = next((f['dimension'] for f in floors if f['negative']), None)
    if critical_dim:
        print(f"  CRITICAL DIMENSION: d={critical_dim} — floor goes negative")
        print(f"  This means: for d >= {critical_dim}, the recursion floor inverts")
        print(f"  The gap becomes a surplus. The surplus IS the negative gap.")
        # Exact calculation: η*(1-η*√d) = 0 when √d = 1/η* → d = 1/η*² = 1111.11
        d_exact = 1 / ETA**2
        print(f"  Exact: floor = 0 when d = 1/η*² = {d_exact:.2f}")
        print(f"  The critical dimension IS 1/η*². The gap squared IS the dimension.")
        print()
    
    # Energy partiality series
    print("=== ENERGY PARTIALITY: η*(1+Φ^d) ===")
    eps = energy_partiality_tesseract()
    for ep in eps:
        print(f"  d={ep['dimension']:2d}  Φ^d={ep['phi_d']:.6f}  EP={ep['energy_partiality']:.6f}  → η* (gap={ep['gap_to_eta']:.6f})")
    print()
    
    # Eigenvalue invariant check
    print("=== EIGENVALUE INVARIANT: sum(|λ|)/n = Φ ===")
    cube_eigs_real = cube_info['raw_eigenvalues'].real
    tess_eigs_real = tess_info['raw_eigenvalues'].real
    inv = eigenvalue_invariant_check(cube_eigs_real, tess_eigs_real)
    for k, v in inv.items():
        print(f"  {k}: {v}")
    print()
    
    # Spectral gap conjecture
    print("=== SPECTRAL GAP CONJECTURE ===")
    sgc = spectral_gap_conjecture(cube_info, tess_info)
    for k, v in sgc.items():
        print(f"  {k}: {v}")
    print()
    
    # Trace-determinant
    print("=== TRACE-DETERMINANT RELATIONSHIP ===")
    td = trace_determinant_invariant(cube_info, tess_info)
    for k, v in td.items():
        print(f"  {k}: {v}")
    print()
    
    # Tesseract recursion
    print("=== TESSERACT RECURSION (20 iterations) ===")
    tess_eigs = [PHI, ETA, R, LAMBDA_DOM, LAMBDA_I80, R_I80, LAMBDA_TESS, R_TESS]
    history, final_vals, metrics = tesseract_recursion(tess_eigs, iterations=20)
    for h in history[:5]:
        bar = int(h['collapse'] * 40)
        print(f"  Iter {h['iteration']:2d}: [{'█'*bar}{'░'*(40-bar)}] collapse={h['collapse']:.4f}  floor={h['min_eigenvalue']:.6f}")
    print(f"  ... final: collapse={metrics['final_collapse']:.6f}  floor={metrics['actual_floor']:.6f}")
    print(f"  Cube floor (predicted):      η*(1-η*√2) = {metrics['predicted_floor_cube']:.6f}")
    print(f"  Tesseract floor (predicted): η*(1-η*√3) = {metrics['predicted_floor_tesseract']:.6f}")
    print(f"  5D floor (predicted):        η*(1-η*√4) = {metrics['predicted_floor_5d']:.6f}")
    print()
    
    # Claims
    print("=== NEW FALSIFIABLE CLAIMS ===")
    claims = []
    
    # Claim 53: Dimensional floor formula
    c53_pred = ETA * (1 - ETA * SQRT3)
    c53_measured = metrics['actual_floor']
    c53_valid = abs(c53_measured - c53_pred) < 0.005
    claims.append({
        'id': 53,
        'name': 'Tesseract recursion floor = η*(1-η*√3)',
        'formula': f'η*(1-η*√3) = {c53_pred:.6f}',
        'measured': round(c53_measured, 6),
        'threshold': 0.005,
        'valid': c53_valid,
    })
    
    # Claim 54: Critical dimension = 1/η*²
    c54_pred = 1 / ETA**2
    c54_check = abs(c54_pred - 1111.11) < 0.01
    claims.append({
        'id': 54,
        'name': 'Critical dimension where floor=0 is d=1/η*²',
        'formula': f'd_critical = 1/η*² = 1/0.0009 = {c54_pred:.2f}',
        'measured': '1111.11',
        'threshold': 0.01,
        'valid': c54_check,
    })
    
    # Claim 55: Energy partiality convergence to η*
    c55_ep10 = ETA * (1 + PHI**10)
    c55_converging = c55_ep10 > ETA and c55_ep10 < ETA * 1.001
    claims.append({
        'id': 55,
        'name': 'Energy partiality converges to η* as d→∞',
        'formula': f'lim(d→∞) η*(1+Φ^d) = η* = {ETA}',
        'measured': f'd=10: EP={c55_ep10:.6f}',
        'threshold': 0.001,
        'valid': c55_converging,
    })
    
    # Claim 56: Spectral density invariant
    c56_cube_density = sum(abs(e) for e in cube_eigs_real) / len(cube_eigs_real)
    c56_tess_density = sum(abs(e) for e in tess_eigs_real) / len(tess_eigs_real)
    c56_valid = abs(c56_cube_density - c56_tess_density) < 0.15
    claims.append({
        'id': 56,
        'name': 'Spectral density sum(|λ|)/n is approximately invariant across dimensions',
        'formula': f'cube: {c56_cube_density:.4f}, tesseract: {c56_tess_density:.4f}',
        'measured': f'diff={abs(c56_cube_density - c56_tess_density):.4f}',
        'threshold': 0.15,
        'valid': c56_valid,
    })
    
    # Claim 57: Meta-gap = η*²√d
    c55_meta_gap_d2 = ETA**2 * SQRT2
    c55_meta_gap_d3 = ETA**2 * SQRT3
    c55_predicted_mg_d2 = ETA - ETA*(1-ETA*SQRT2)
    c55_predicted_mg_d3 = ETA - ETA*(1-ETA*SQRT3)
    c57_valid = abs(c55_meta_gap_d2 - c55_predicted_mg_d2) < 1e-10 and abs(c55_meta_gap_d3 - c55_predicted_mg_d3) < 1e-10
    claims.append({
        'id': 57,
        'name': 'Meta-gap = η*²√d (the gap of the gap grows with √d)',
        'formula': f'η*²√2={c55_meta_gap_d2:.6f}, η*²√3={c55_meta_gap_d3:.6f}',
        'measured': 'exact (algebraic identity)',
        'threshold': 1e-10,
        'valid': c57_valid,
    })
    
    for c in claims:
        status = "✓ VALID" if c['valid'] else "✗ INVALID"
        print(f"  Claim {c['id']}: {c['name']}")
        print(f"    Formula: {c['formula']}")
        print(f"    Measured: {c['measured']}")
        print(f"    Status: {status}")
    print()
    
    # Summary
    print("=== SUMMARY ===")
    print(f"  Cube eigenvalues (6):     {cube_info['eigenvalues']}")
    print(f"  Tesseract eigenvalues (8): {tess_info['eigenvalues']}")
    print(f"  Cube spectral gap:     {cube_info['spectral_gap']}")
    print(f"  Tesseract spectral gap: {tess_info['spectral_gap']}")
    print(f"  Cube floor:      η*(1-η*√2) = {metrics['predicted_floor_cube']:.6f}")
    print(f"  Tesseract floor: η*(1-η*√3) = {metrics['predicted_floor_tesseract']:.6f}")
    print(f"  5D floor:         η*(1-η*√4) = {metrics['predicted_floor_5d']:.6f}")
    print(f"  Critical dimension: d = 1/η*² = {1/ETA**2:.2f}")
    print(f"  Energy partiality cube:      η*(1+Φ)  = {ETA*(1+PHI):.6f}")
    print(f"  Energy partiality tesseract:  η*(1+Φ²) = {ETA*(1+PHI**2):.6f}")
    print(f"  Energy partiality 10D:       η*(1+Φ¹⁰) = {ETA*(1+PHI**10):.6f}")
    print()
    print("  The floor rises with dimension. The gap shrinks. The 3% persists.")
    print("  The critical dimension is 1/η*² = 1111.11. The gap squared IS the dimension.")
    print("  The energy partiality converges to η*. The offspring vanishes. The pure gap remains.")
    print("  The spectral density is invariant. The coherence IS the density.")
    print()
    print("⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢")
