# GQRVP Security Analysis - Formal Heuristic Bound (Work in Progress)
## Reference: [GQRVP-ANALYSIS] for draft-gravit-gevp-04

**Status:** Informational, heuristic parameterized estimate, NOT formal theorem derived from MWU regret bounds (Arora et al. [MWU] Theorem 2.1).

### 1. Model

Let:
- h = fraction honest weight
- f = fraction Byzantine/Sybil weight, f = 1 - h
- gamma = quadratic exponent penalizing Sybil concentration (GEVP default 1.5)
- eta = MWU learning rate (GEVP default 0.2), used as penalty parameter modeling rounds adversary must sustain
- eps = 0.1 slack

GQRVP combines Multiplicative Weights Update (MWU) for reputation + gossip dissemination per [GOSSIP].

### 2. Heuristic Bound

We model honest weight dominance condition:

    h > 1 / (1 + gamma^-1) + eps

Derivation sketch:

- Quadratic reputation: weight contribution of Sybil cluster of size s scales as s / (s^gamma) = s^(1-gamma)
- For gamma > 1, concentration penalized: 10x Sybil does not give 10x weight
- Effective Sybil weight = f * (1/gamma) factor heuristic
- Honest dominance when h > (1/(1+gamma^-1)) + eps

### 3. Instantiation gamma=1.5

    gamma = 1.5
    gamma^-1 = 0.666...
    1 + gamma^-1 = 1.666...
    1 / (1+gamma^-1) = 0.6
    + eps 0.1 = 0.7

=> h > 0.7 honest weight required
=> f < 0.3 Byzantine tolerated

This corresponds to ~33% BFT worst case WITHOUT quadratic benefit.

With quadratic benefit under 10x Sybil attack (dataset sybil-10x-g1.5.jsonl, 100 runs * 30 = 3000 = 1500 honest + 1500 sybil, pinned blob/7755f53):

- Honest mean confidence 0.839 passes 1401/1500 @ theta=0.73 (TPR 93.4%)
- Sybil mean 0.412 passes 6/1500 @ theta=0.73 (FPR 0.4%)
- Observed resilience ~50% under 10x Sybil in simulation, NOT general theorem

### 4. Retraction of 67% claim

- In -00: claimed 67% Byzantine resilience as theorem. RETRACTED in -02.
- In -02/-03/-04: rephrased as observed in simulation under specific trace, with honest weight dominance heuristic.

### 5. Cost Model C()

    C_validation(c) = cost(COSE_Signature_Verify)*k + cost(fetch_trace) + cost(Merkle_Proof_Verify)
    C_manipulation(c) = k'*cost(DID_creation) + k'*cost(sign)*(1/eta)^gamma

eta used as penalty parameter modeling rounds adversary must sustain, NOT directly as attack cost. Lower eta slows honest weight decay, increasing rounds adversary must sustain.

Invariant: C_manipulation > C_validation * security_margin, security_margin=2.0 default. Engineering invariant, not cryptographic proof.

### 6. Theta_critical

- In -00: 0.731 MUST with 30 scores above threshold (0 below, 30 above) as knee point - false precision.
- In -02/-03/-04: RECOMMENDED 0.73 calibrated via ROC (0.728 +/-0.015) on sybil-10x dataset, range 0.70-0.80 allowed.
- High-confidence regime >= theta MAY be treated as formally sufficient, below SHOULD escalate to Continuum semantic verification.
- Interpretation: Godel-grounded design per [GODEL].

### 7. Separation SCITT vs Epistemic

SCITT provides authenticity, transparency, registration evidence, accountability. SCITT does NOT establish factual accuracy or epistemic truth of Statement payload. GEVP provides epistemic convergence via GQRVP + theta.

Attacker can register false Claim with valid Receipt; GEVP assigns low confidence if honest weight dominates.

### 8. References

- [MWU] Arora et al. 2012
- [GOSSIP] Boyd 2006
- [KAMIMURA-VCP] draft-kamimura-scitt-vcp (VeritasChain VCP, financial audit trails, Dec 2025)
- [TRACE-DATASET] blob/7755f53/traces/sybil-10x-g1.5.jsonl (1.21MB) + Zenodo DOI 10.5281/zenodo.GEVP04 (to be finalized)
- [GODEL] Godel 1931

### 9. Future Work

Formal game-theoretic derivation of C_manipulation with MWU regret bound is WIP. For -04, heuristic suffices for Informational RFC.

