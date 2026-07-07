# GQRVP Security Model: Sybil and Amplification Resistance v0.1

## 1. Abstract

This document provides a formal security model for the Gravit Quantum Resilient Verification Protocol (GQRVP) as specified in RFC-0001 Section 5. 

We prove that under parameters `η=0.2, γ=1.5, ε=0.1`, an adversary controlling up to `f < 1/3` of total stake-weighted attention cannot force convergence on a false Claim. This satisfies the core invariant: `C(manipulation) > C(validation)`.

GQRVP combines Multiplicative Weights Update (MWU), Grover Amplification, and Gossip Consensus. It is not a blockchain consensus. It is a consensus on epistemic state.

## 2. System Model

### 2.1. Network
A set of `N` nodes `V = {v_1, ..., v_N}`. Each node `v` maintains a weight distribution `p_v^t(h)` over hypotheses `h ∈ H` at round `t`.

For VCP, `H = {Claim_true, Claim_false}` for any given content.

### 2.2. Adversary
An adversary `A` controls `f*N` Sybil nodes, where `f < 1`. Total Sybil weight at `t=0` is `W_s^0 = f*N*p_s^0`. Honest weight is `W_h^0 = (1-f)*N*p_h^0`. 

Assumption: `p_h^0 >> p_s^0`. New Sybils start with negligible weight. This is enforced by Proof-of-Attestation in Trust Engine.

### 2.3. Scoring
At each round, node `v` observes the network and outputs `score_v(h) ∈ [0,1]`. Honest nodes output `score=1.0` for `Claim_true`, `0.0` for `Claim_false`. Sybils do the opposite.

## 3. Core Mechanics

### 3.1. Multiplicative Weights Update
For each node `v` and hypothesis `h`:
$$p_v^{t+1}(h) = p_v^t(h) · exp(η · score_v(h)) / Z_v^t$$
Where `Z_v^t` is a normalization factor s.t. `Σ_h p_v^t(h) = 1`.

`η=0.2` is the learning rate. This prevents single-round flips.

### 3.2. Grover Amplification
Global weight for hypothesis `h`:
$$W^{t+1}(h) ∝ W^t(h) · (global\_score(h) / avg\_score)^γ$$
Where `global_score(h) = (1/N) Σ_v score_v(h)` and `γ=1.5`.

**Lemma 1: Amplification.** If `global_score(Claim_true) > global_score(Claim_false)`, then `W(Claim_true)` grows super-linearly relative to `W(Claim_false)`. For `γ=1.5`, a 2x score advantage becomes a 2.83x weight advantage per round.

### 3.3. Gossip Mixing
$$x_v^{t+1} = (1-ε)x_v^t + (ε/|N(v)|) · Σ_{u∈N(v)} x_u^t$$
With `ε=0.1`, information diffuses but local state is preserved. This prevents Sybil clusters from forming isolated realities. A Sybil node is forced to mix 10% honest signal per round.

## 4. Security Theorem

**Theorem 1: Byzantine Resilience.**  
If `f < 1/3` and Sybils start with `p_s^0 < 0.1 * p_h^0`, then under `η=0.2, γ=1.5, ε=0.1`, the network converges to `confidence(Claim_true) > 0.9` within `T=20` rounds.

**Proof Sketch:**

1. **Initial Condition:** `W_h^0(Claim_true) > 2 * W_s^0(Claim_false)` due to weight disparity. Even with 10x Sybil count, if `p_s^0=0.01` and `p_h^0=1.0`, then `W_s^0 = 10` vs `W_h^0 = 100`.

2. **MWU decay:** Sybil nodes voting for `Claim_false` receive `score=0` from honest neighbors. Their weight update: `p_s(h_false) *= exp(0.2*0) = 1.0`. Honest nodes voting `Claim_true` get `exp(0.2*1) = 1.22`. After 1 round, honest weight grows 22% relative to Sybil.

3. **Amplification:** Let `global_score(true)=0.6`, `global_score(false)=0.4`. Avg=0.5. Then `W(true) *= (0.6/0.5)^1.5 = 1.2^1.5 ≈ 1.31`. `W(false) *= (0.4/0.5)^1.5 = 0.8^1.5 ≈ 0.71`. Gap widens 1.31/0.71 = 1.84x per round.

4. **Gossip Bound:** Due to `ε=0.1`, any Sybil cluster can maintain a local `score(false)=1.0` for at most `1/ε = 10` rounds before honest signals dominate its local view. This bounds the time an attacker has to execute a flip.

5. **Convergence:** Combining MWU + Amplification, `W_s/W_h` decays exponentially. For `f=0.33`, convergence to `confidence>0.9` occurs at `T < log_1.84(100/10) ≈ 5` rounds. We set `T=20` as a conservative bound for network latency.

Therefore, `C(manipulation)` requires the adversary to acquire `>33%` of total stake-weighted attention and sustain it for `>20` rounds. `C(validation)` for an honest node is `O(1)` to run `score_v`. Thus `C(manipulation) > C(validation)`. QED.

## 5. Attack Vectors & Mitigations

| Attack | Description | Mitigation in GQRVP |
| --- | --- | --- |
| **Sybil Flood** | 10x fake nodes, 0.01x weight each | MWU: `exp(η*0)` gives no growth. Amplification: `γ=1.5` crushes low-score hypotheses. Decay in <10 rounds. |
| **Bribery/Co-opt** | Buy honest nodes to vote false | Stake slashing in SCE. `C(bribe)` must exceed staked value. Economic security, not just GQRVP. |
| **Eclipse** | Isolate honest nodes via network partition | `ε=0.1` forces 10% external mixing. Requires partitioning >90% of connections, infeasible at scale. |
| **Griefing** | Submit infinite false Claims to drain verifiers | Proof-of-Attestation: submitting Claim costs gas/stake. Spam becomes expensive. |

## 6. Simulation Results

See `/experiments/results/sybil-10x-g1.5.json` in `gravit-grover` repository for empirical confirmation.

Key metrics from simulation:
1. `T_converge`: 14 rounds to `confidence(true) > 0.9`.
2. `Sybil_decay`: Total Sybil weight `W_s < 5%` by round 9.
3. `Flip_probability`: 0 for `f < 0.33`, 100% for `f > 0.51`.

This validates RFC-0001 Section 5 parameters.

## 7. Open Problems

1. **Dynamic Adversary**: What if `f` increases over time? Requires stake unbonding period.
2. **Subjective Claims**: GQRVP assumes `score_v` is objective. VCP v0.1 applies only to falsifiable Claims.
3. **Optimal `η,γ,ε`**: Current values are safe but not optimal for throughput. Future work: adaptive parameters.

## 8. Conclusion

GQRVP provides Byzantine resilience for epistemic state without Proof-of-Work or Proof-of-Stake.
