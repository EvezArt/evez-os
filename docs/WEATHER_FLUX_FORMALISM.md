# Formal Weather-Chemistry-Network State Space

## 1. Three typed planes

The experiment is not one undifferentiated "flux."

Physical state:

  P(t) = [T(t), RH(t), p(t), u(t), q(t), R_n(t), ...]

These are environmental observables.

Chemical/thermodynamic state:

  C(t) = [e_s, e, VPD, a_w, mu_w, ...]

At vapor-liquid equilibrium, atmospheric relative humidity can supply an
approximation to water activity. That is a thermodynamic boundary condition,
not a universal substitute for direct measurement of a biological substrate.

The relative water chemical-potential term is

  Delta mu_w = R T ln(a_w).

Information state:

  I(t) = [x(t), theta(t), r(t), tau, ...]

This can represent graph-state, phase, or information flow. It does not assert
that an information graph is a nervous system.

## 2. Transport operator

For an incidence matrix B and diagonal mobility matrix M:

  J = -M B^T mu
  dc/dt = B J + s

This produces the expected sign reversal when the potential gradient reverses.
The linear approximation is a near-equilibrium hypothesis that must be tested,
not assumed to explain every biological transport regime.

## 3. Candidate information coupling

A deliberately falsifiable phase model is

  d theta_i/dt =
      omega_i
      + K(t) sum_j A_ij sin(theta_j - theta_i)
      + eta_i

with

  K(t) = K0 [1 + beta z(t)]

where z(t) is a standardized, predeclared environmental covariate.

The scientifically interesting parameter is beta:

  beta = 0    -> no detected weather modulation
  beta > 0    -> coupling increases with z
  beta < 0    -> coupling decreases with z

A fitted nonzero beta is not enough. It must improve out-of-sample prediction
against null models.

## 4. Falsification matrix

N0: permutation null

Randomly permute weather timestamps while retaining the marginal distribution.
A genuine time-locked coupling should degrade.

N1: phase null

Randomize phases while preserving amplitude and spectral structure.
A phase-specific effect should collapse.

N2: lag null

Predeclare a finite lag window. Do not search arbitrary lags until the effect
appears. A peak created by unrestricted lag selection is selection bias.

N3: topology null

Randomize graph edges while preserving degree sequence. If topology matters,
the effect should weaken when the hypothesized topology is destroyed.

N4: instrument null

Substitute a physically irrelevant sensor channel. A comparable effect size
indicates confounding rather than mechanism.

## 5. Identifiability hierarchy

The bridge contains three separate hypotheses:

H1: weather -> thermodynamic/chemical state
H2: chemical state -> material transport
H3: chemical state -> information synchrony

H3 must not inherit evidence merely because H1 and H2 fit.

Each layer needs its own observation model, residuals, and falsifier.

## 6. Mobile swarm architecture

The Galaxy A16/Termux node is the provenance anchor.

  raw observation
       |
       v
  canonical packet
       |
       +----> local hash chain
       |
       v
  swarm job
       |
       +----> independent model fit
       +----> null model
       +----> replication
       |
       v
  promotion gate

Workers may analyze. Workers may not redefine the evidence semantics.

## 7. Promotion

MODEL_ONLY -> MEASURED -> REPLICATED

MEASURED requires raw sensor provenance, acquisition timestamps, calibration
metadata, and an intact evidence chain.

REPLICATED requires an independent run or vantage that did not participate in
feature, lag, threshold, or hypothesis selection.

No coherence number, including a Kuramoto order parameter, identifies causality.

## 8. Stopping rule

If the independent verification surface does not return a reproducible test
result, the cycle stops at PENDING.

The absence of evidence is stored as a state of the system, not converted into
a confidence score.
