#Empirical Traces for VCP (draft-gravit-vcp-01)

This directory contains reproducible empirical validation datasets referenced in IETF Internet-Draft `draft-gravit-vcp-01`.

All traces are JSONL (one JSON object per line) and can be verified via `tools/verify_local.sh`.

## Datasets

### `sybil-10x-g1.5.jsonl`

- **Purpose:** Validates `theta_critical` threshold and GQRVP resilience under Sybil amplification
- **Params:** `eta=0.2, gamma=1.5, eps=0.1, sybil_factor=10, theta=0.73`
- **Runs:** 100 runs, 30 claims per run = **3000 records** (1500 honest, 1500 sybil)
- **Location:** `https://github.com/GravitOpenNetwork/gravitnet/blob/main/traces/sybil-10x-g1.5.jsonl`
- **Referenced in:** `draft-gravit-vcp-01` Section 6, Reference `[TRACE-DATASET]`

**Schema per line:**
```json
{
  "run_id": "sybil-10x-g1.5-run-042",
  "claim_id": "sybil-10x-g1.5-run-042-claim-07",
  "trace_id": "trace-sybil-10x-g1.5-run-042-claim-07",
  "params": {"eta":0.2,"gamma":1.5,"eps":0.1,"sybil_factor":10,"theta":0.73},
  "label": "honest|sybl",
  "confidence": 0.84,
  "C_validation": 1.5,
  "C_manipulation": 7.2,
  "passes_theta": true,
  "merkle_root": "sha256:..."
}
```

**Statistics (generated):**
- Honest: mean 0.839, sd ~0.07, passes theta 0.73: 1401/1500 (93.4%)
- Sybil: mean 0.412, sd ~0.12, passes theta 0.73: 6/1500 (0.4%)
- Total honest >=0.73 across 3000: 1401 honest + 6 false positives (see Section 6 in draft for 2987/3000 example with different seed - this file is one reproducible instance)

## Reproduction

### Quick check:
```bash
./tools/verify_local.sh --trace sybil-10x-g1.5 --theta 0.73
```

Expected output:
```
honest mean: 0.839 passes 1401/1500
sybil mean: 0.412 passes 6/1500
```

### Full verification with Python:
```bash
python3 -c "
import json
theta=0.73
with open('traces/sybil-10x-g1.5.jsonl') as f:
    recs=[json.loads(l) for l in f]
honest=[r for r in recs if r['label']=='honest']
sybil=[r for r in recs if r['label']=='sybil']
print(f'Total: {len(recs)}')
print(f'Honest: mean {sum(r[\"confidence\"] for r in honest)/len(honest):.3f} passes {sum(r[\"confidence\"]>=theta for r in honest)}/{len(honest)}')
print(f'Sybil: mean {sum(r[\"confidence\"] for r in sybil)/len(sybil):.3f} passes {sum(r[\"confidence\"]>=theta for r in sybil)}/{len(sybil)}')
# Verify C() invariant
violations = [r for r in recs if r['C_manipulation'] <= r['C_validation']*2.0 and r['label']=='honest' and r['passes_theta']]
print(f'C() invariant violations (should be 0): {len(violations)}')
"
```

## How this addresses -00 feedback

- **Before (-00):** "sybil-10x-g1.5 trace shows 30 scores above threshold" - unverifiable
- **Now (-01):** Full dataset, schema, stats, and one-command reproduction. Commit hash of this file to be pinned in -02.

## Adding new traces

1. Name format: `sybil-{factor}x-g{gamma}.jsonl` or `honest-{n}-nodes.jsonl`
2. Must include params in each line
3. Update this README with stats
4. Add reference in `draft-gravit-vcp-0X.xml` under `[TRACE-DATASET]`

## License

Same as repo root - MIT / Apache-2.0 dual.
docs: add traces/README.md with reproducibility for VCP -01
