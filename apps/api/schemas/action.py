from pydantic import BaseModel
from typing import Dict, Any

class ActionPayload(BaseModel):
    type: str
    payload: Dict[str, Any]

class ExecuteRequest(BaseModel):
    actor_id: str
    action: ActionPayload
