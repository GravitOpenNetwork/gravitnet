# Gravit Network

## Epistemic Execution System (EES)

[![IETF I-D](https://img.shields.io/badge/IETF-draft--gravit--vcp--01-blue)](https://datatracker.ietf.org/doc/draft-gravit-vcp/)
[![Status](https://img.shields.io/badge/Status-Active%20Internet--Draft%20%28individual%29-green)](https://datatracker.ietf.org/doc/draft-gravit-vcp/)
[![Last Updated](https://img.shields.io/badge/Last%20Updated-2026--07--21-lightgrey)](https://datatracker.ietf.org/doc/draft-gravit-vcp/)
[![License: Spec](https://img.shields.io/badge/License-IETF%20Trust%20BCP%2078%2F79-lightgrey)](./specs/IETF/)
[![License: Code](https://img.shields.io/badge/License-Apache%202.0%20%2B%20Commons%20Clause-orange)](./LICENSE)

Gravit is a distributed, trace-preserving, adversarially resilient computation substrate for verifiable reasoning systems.

> **Gravit is not about making AI smarter. It is about making collective human–machine reasoning durable, traceable and accountable.**

---

## Standards

**The Verifiable Convergence Protocol (VCP) is currently published as an IETF Internet-Draft.**

Current revision: **`draft-gravit-vcp-01`** — Individual Submission, published 2026-07-21.

> **Disclaimer:** This document is an Internet-Draft (I-D). Anyone may submit an I-D to the IETF. This I-D is **not endorsed by the IETF** and has **no formal standing** in the IETF standards process. [IETF standards process](https://www.ietf.org/standards/process/)

## Internet Standardization

Gravit Open Network develops open protocol specifications through the IETF Internet-Draft process.

### Verifiable Convergence Protocol (VCP)

**Current Version**

- **draft-gravit-vcp-01**
- Status: Active Internet-Draft (individual)
- Published: 2026-07-21
- Author: Dr. Alex Konviser — ietf@gravit.space

**Resources**

- Datatracker: https://datatracker.ietf.org/doc/draft-gravit-vcp/
- TXT: https://www.ietf.org/archive/id/draft-gravit-vcp-01.txt
- HTML: https://www.ietf.org/archive/id/draft-gravit-vcp-01.html
- XML (canonical): https://www.ietf.org/archive/id/draft-gravit-vcp-01.xml
- HTMLized: https://datatracker.ietf.org/doc/html/draft-gravit-vcp-01
- Diff from -00: https://author-tools.ietf.org/iddiff?url1=draft-gravit-vcp-00&url2=draft-gravit-vcp-01
- IETF Archive (all versions): https://www.ietf.org/archive/id/draft-gravit-vcp/

**Canonical in repo:**

- `specs/IETF/draft-gravit-vcp-01.xml` (source)
- `specs/IETF/draft-gravit-vcp-01.txt` (rendered)
- Datatracker auto-links: GitHub Repository / Additional Web Page / Mailing List

---

## What changed in -01

Major updates from `-00` (2026-07-20) → `-01` (2026-07-21):

- **Cost model C() formally defined:** `C_validation = k*COSE_Verify + fetch_trace + Merkle_Verify`, `C_manipulation = k'*DID_creation + k'*sign*(1/eta)^gamma`, invariant `C_manipulation > C_validation * 2.0`
- **GQRVP clarified:** Canonical definition = "Gossip with Quadratic Reputation and Verifiable Proofs" (supersedes "Quantum-Ready" informal). MWU + Gossip.
- **Security bound derived, not asserted:** For `gamma=1.5, eta=0.2, eps=0.1` → requires `h > 0.7` honest weight (f < 0.3). Previous `67% Byzantine resilience` in -00 retracted as imprecise.
- **theta_critical:** `MUST 0.731` in -00 → `RECOMMENDED 0.73` in -01, derived via ROC on 100 runs (0.728 ±0.015), range 0.70-0.80 allowed.
- **Empirical validation made reproducible:** `traces/sybil-10x-g1.5.jsonl` (100 runs × 30 claims = 3000 records), `tools/verify_local.sh --trace sybil-10x-g1.5 --theta 0.73`
- **SCITT alignment:** Added normative refs to `draft-ietf-scitt-architecture` (RFC 9943), RFC 9052 (COSE), W3C DID-Core, MWU, Gossip.

## Core Principles

### 1. Triad Model
- **Open Network** (interaction layer) — Gateway, Coordinator
- **Continuum** (state evolution layer) — SCE
- **Quantum** (trace integrity layer) — Ω Trace Store

### 2. GQRVP (Gossip with Quadratic Reputation and Verifiable Proofs)
- `eta = 0.2` (MWU learning rate)
- `gamma = 1.5` (quadratic penalty)
- `eps = 0.1` (gossip fault tolerance / exploration)
- Resilience: derived bound `f < 0.3` weight Byzantine, up to `f < 0.5` under 10x Sybil due to quadratic penalty — see `specs/RFC/GQRVP-security.md` and Section 5 of draft

### 3. History Keeper
Immutable temporal trace system ensuring full provenance.
- Append-Only, Content-Addressed, Hash-Linked (Merkle DAG)
- Formal-to-epistemic threshold: `theta_critical RECOMMENDED 0.73` (calibrated, not fixed)

---

## System Architecture

```
Gateway → Coordinator → SAIL → SCE → Trust Engine → Ω Trace Store
```

### Core Endpoints (VCP-Compatible)

- `POST /v1/claim` — submit Claim
- `GET /v1/claim/{claim_id}` — retrieve with confidence + merkle_proof
- `POST /v1/action/verify` — verify Action against basis Claims (MUST reject if basis empty or min confidence < theta)
- `GET /v1/trace/{trace_id}` — immutable verification history (SCITT Transparent Statement equivalent)

All over HTTPS, `application/json` or `application/cbor`, COSE/JOSE signatures `did:web` / `did:jwk` for -01.

---

## Empirical Traces

This repo contains reproducible datasets referenced in `[TRACE-DATASET]` of draft -01.

Location: `traces/`

- `sybil-10x-g1.5.jsonl` — 3000 records (1500 honest, 1500 sybil), params `eta=0.2 gamma=1.5 eps=0.1 sybil_factor=10 theta=0.73`
  - Canonical URL: https://github.com/GravitOpenNetwork/gravitnet/blob/main/traces/sybil-10x-g1.5.jsonl
  - Commit pinned for -01: `7755f53` (data) + `9f3e5d1` (README) — to be formally pinned in -02
  - Stats in this instance: honest mean 0.839 passes 1401/1500 @0.73, sybil mean 0.412 passes 6/1500

**Reproduction:**

```bash
./tools/verify_local.sh --trace sybil-10x-g1.5 --theta 0.73
```

See `traces/README.md` for full schema and Python verification.

---

## Repository Structure

```
/specs/IETF/               → IETF Internet-Draft canonical (xml2rfc v3) — draft-gravit-vcp-01.xml
/specs/RFC/                → GQRVP-security.md derivation
/specs/                    → formal system definitions
/research/                 → theoretical foundations
/core/                     → abstract system model
/engine/                   → implementation (Rust + Go)
/sdk/                      → external access layer
/traces/                   → reproducible empirical datasets (TRACE-DATASET)
/tools/                    → verify_local.sh and other tooling
/infra/                    → deployment
/security/                 → threat model + redteam
```

Proposed for next iteration (per ChatGPT suggestion, adopted):

```
specs/
├── IETF/
│   ├── draft-gravit-vcp-01.xml
│   ├── draft-gravit-vcp-01.txt
│   ├── README.md
│   └── changelog.md
├── RFC/
└── ...
```

## Changelog

### 2026-07-21 — draft-gravit-vcp-01 Published

Published: IETF Internet-Draft `draft-gravit-vcp-01` (Active, individual)

Major updates:

- clarified security parameter derivation (Section 5.1)
- added empirical validation methodology (Section 6) with reproducible trace `sybil-10x-g1.5`
- formalized cost model definition C_validation / C_manipulation (Section 3)
- retracted imprecise 67% claim, replaced with derived 0.7 honest weight bound
- relaxed theta_critical from MUST 0.731 to RECOMMENDED 0.73
- added SCITT / COSE / DID-Core / MWU / Gossip normative references
- editorial: Zurich (without ü for idnits), abstract clarifies invariant

Links: https://datatracker.ietf.org/doc/draft-gravit-vcp/ / https://www.ietf.org/archive/id/draft-gravit-vcp-01.txt

### 2026-07-20 — draft-gravit-vcp-00

Initial submission as Individual Internet-Draft to SCITT.

---

## License

- **Implementation (engine, sdk, infra):** [Apache 2.0 with Commons Clause](./LICENSE)
- **Specifications & Internet-Drafts (`/specs`, `/specs/IETF`, `/traces`):** IETF Trust Legal Provisions — BCP 78/79 (BSD-like) — **REQUIRED FOR IETF SUBMISSION**

Dual-license structure is intentional to allow IETF adoption while protecting core implementation.

---

## Related Links

- 🌐 Website: https://gravit.space
- 📬 Substack: https://gravitopennetworkfoundation.substack.com
- 🐦 X: @GravitNet · @bensaufer
- 📜 IETF Datatracker: https://datatracker.ietf.org/doc/draft-gravit-gevp-02/
- 📂 GitHub: https://github.com/GravitOpenNetwork/gravitnet

If you are reading this, you are already part of building the Trust Continuum.

Welcome.
