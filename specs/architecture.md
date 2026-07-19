# Gravit Triad Architecture (Work in Progress)

Status: Informative, non-normative companion to draft-konviser-vcp-00.

This document exists to satisfy the normative reference in `specs/IETF/draft-konviser-vcp-00.txt`.

## Triad Layers

1. **Open Network** — interaction layer. Agents submit Claims and Actions via VCP.
2. **Continuum** — state evolution layer. Tracks how Claim confidence evolves across gossip rounds (GQRVP).
3. **Quantum** — trace integrity layer. Owns the immutable Trace store.

## Relationship to VCP

Any system implementing the VCP endpoints qualifies as an Epistemic Execution System (EES) regardless of internal implementation.
