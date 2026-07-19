# Gravit Triad Architecture (Work in Progress)

Status: Informative, non-normative companion to draft-konviser-vcp-00.

This document exists to satisfy the normative reference in `specs/IETF/draft-konviser-vcp-00.txt` §8 References.

## Triad Layers

1. **Open Network** — interaction layer. Agents submit Claims and Actions via VCP (`POST /v1/claim`, `POST /v1/action/verify`).
2. **Continuum** — state evolution layer. Tracks how Claim confidence evolves across gossip rounds (GQRVP, §5 of draft-konviser-vcp-00).
3. **Quantum** — trace integrity layer. Owns the immutable Trace store and its content-addressing guarantees (§4.4 of draft-konviser-vcp-00).

## Relationship to VCP

Any system implementing the four VCP endpoints and the GQRVP parameter contract in draft-konviser-vcp-00 §2 (Conformance) qualifies as an Epistemic Execution System (EES) regardless of how it implements the Triad internally. The Triad is Gravit's reference architecture, not a conformance requirement of VCP itself.
