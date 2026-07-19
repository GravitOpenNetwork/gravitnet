import hashlib
import json
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List

from schemas.vcp import Claim, Attestation, Action, Trace

router = APIRouter()

# In-memory store for Claims, Traces, and Attestations
claims_db: Dict[str, Dict[str, Any]] = {}
traces_db: Dict[str, Dict[str, Any]] = {}
attestations_db: Dict[str, List[Dict[str, Any]]] = {}

# --- Named constants per draft-konviser-vcp-00 ---
# θ_critical from Appendix B: formal-to-epistemic transition point
# See sybil-10x-g1.5.json empirical analysis
THETA_CRITICAL = float(os.getenv("GRAVIT_THETA_CRITICAL", "0.731"))

# Initial confidence prior pending GQRVP convergence (see §9 Implementation Status)
INITIAL_CLAIM_CONFIDENCE = float(os.getenv("GRAVIT_INITIAL_CONFIDENCE", "0.85"))

@router.post("/claim", status_code=status.HTTP_201_CREATED)
def create_claim(claim: Claim):
    # Enforce content and provenance schema check
    if not claim.content or not claim.provenance:
        raise HTTPException(status_code=400, detail="Invalid Claim schema: content and provenance are required.")

    # Idempotency: hash of content + provenance source URLs
    provenance_srcs = "".join([p.src for p in claim.provenance])
    payload_hash = hashlib.sha256(f"{claim.content}:{provenance_srcs}".encode()).hexdigest()
    claim_id = f"sha256:{payload_hash}"
    
    if claim_id in claims_db:
        return {"claim_id": claim_id}
        
    created_time = datetime.utcnow().isoformat() + "Z"
    
    # Store claim with network confidence defaults (static prior, not MWU convergence yet)
    claims_db[claim_id] = {
        "claim_id": claim_id,
        "content": claim.content,
        "provenance": [p.dict() for p in claim.provenance],
        "method": claim.method,
        "confidence": INITIAL_CLAIM_CONFIDENCE,
        "created_at": created_time,
        "expires": claim.expires or (datetime.utcnow().isoformat() + "Z"),
        "trace": claim.trace or []
    }
    
    return {"claim_id": claim_id}

@router.get("/claim/{claim_id}")
def get_claim(claim_id: str):
    if claim_id not in claims_db:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    claim_data = claims_db[claim_id]
    attestations = attestations_db.get(claim_id, [])
    merkle_proof = hashlib.sha256(claim_id.encode()).hexdigest()
    
    return {
        "claim": claim_data,
        "confidence": claim_data["confidence"],
        "attestations": attestations,
        "merkle_proof": merkle_proof
    }

@router.post("/action/verify")
def verify_action(action: Action):
    # Gateway rule 1: Reject if basis is empty
    if not action.basis:
        raise HTTPException(
            status_code=400,
            detail="Gateway MUST reject if basis is empty"
        )
        
    # Gateway rule 2: Check that all basis claims exist
    basis_claims = []
    for cid in action.basis:
        if cid not in claims_db:
            raise HTTPException(
                status_code=400,
                detail=f"Basis claim {cid} not found"
            )
        basis_claims.append(claims_db[cid])
        
    # Generate action and trace IDs
    action_hash = hashlib.sha256(f"{action.name}:{action.proposed_by}".encode()).hexdigest()
    action_id = f"sha256:{action_hash}"
    trace_id = f"sha256:{hashlib.sha256(action_id.encode()).hexdigest()}"

    # Gateway rule 3: Reject if any basis claim confidence < θ_critical
    for claim in basis_claims:
        if claim["confidence"] < THETA_CRITICAL:
            trace_data = _build_trace(
                trace_id,
                action_id,
                "REJECTED",
                f"Basis claim {claim['claim_id']} confidence ({claim['confidence']}) is below required threshold ({THETA_CRITICAL})",
                claim["confidence"],
                gqrvp_rounds=0
            )
            traces_db[trace_id] = trace_data
            
            return {
                "status": "REJECTED",
                "trace_id": trace_id,
                "reason": trace_data["reason"]
            }
            
    # Success path: All checks pass
    avg_confidence = sum([c["confidence"] for c in basis_claims]) / len(basis_claims)
    trace_data = _build_trace(
        trace_id,
        action_id,
        "ACCEPTED",
        f"All basis claims successfully verified with confidence >= {THETA_CRITICAL}",
        avg_confidence,
        gqrvp_rounds=None  # Not computed by reference node; pending -01 (see §9)
    )
    traces_db[trace_id] = trace_data
    
    return {
        "status": "ACCEPTED",
        "trace_id": trace_id,
        "reason": trace_data["reason"]
    }

def _build_trace(trace_id, action_id, result, reason, final_confidence, gqrvp_rounds):
    """Build trace with content-addressed merkle_root (RFC 6962 style).
    
    Hash is computed over the full trace body as JSON, not just trace_id,
    ensuring the Trace is immutable and verifiable.
    """
    trace_body = {
        "trace_id": trace_id,
        "action_id": action_id,
        "result": result,
        "reason": reason,
        "final_confidence": final_confidence,
        "gqrvp_rounds": gqrvp_rounds,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    # Merkle root: hash of canonical JSON representation (see §4.4)
    canonical = json.dumps(trace_body, sort_keys=True).encode()
    trace_body["merkle_root"] = hashlib.sha256(canonical).hexdigest()
    return trace_body

@router.get("/trace/{trace_id}")
def get_trace(trace_id: str):
    if trace_id not in traces_db:
        raise HTTPException(status_code=404, detail="Trace not found")
    return traces_db[trace_id]
