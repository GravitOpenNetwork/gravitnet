from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ProvenanceItem(BaseModel):
    type: str
    src: str
    signed_by: Optional[str] = None

class Claim(BaseModel):
    claim_id: Optional[str] = None
    content: str
    provenance: List[ProvenanceItem]
    method: str
    confidence: Optional[float] = 0.0
    created_at: Optional[str] = None
    expires: Optional[str] = None
    trace: Optional[List[str]] = []

class Attestation(BaseModel):
    attestation_id: str
    claim_id: str
    issuer: str
    signature: str

class Action(BaseModel):
    action_id: Optional[str] = None
    name: str
    params: Dict[str, Any]
    basis: List[str]
    stake: int
    proposed_by: str

class Trace(BaseModel):
    trace_id: str
    action_id: str
    result: str  # ACCEPTED | REJECTED
    reason: str
    final_confidence: float
    gqrvp_rounds: int
    timestamp: str
    merkle_root: str
