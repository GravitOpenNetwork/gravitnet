import os
from fastapi import FastAPI, Request
from routes.execute import router as execute_router
from routes.vcp import router as vcp_router

app = FastAPI()
app.include_router(execute_router, prefix="/v1")
app.include_router(vcp_router, prefix="/v1")

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/.well-known/vcp")
def get_vcp_metadata(request: Request):
    # Retrieve base URL dynamically (e.g., http://localhost:8000/ or https://testnet.gravit.space/)
    base_url = str(request.base_url).rstrip("/")
    node_id = os.getenv("GRAVIT_NODE_ID", "node-1")
    
    return {
        "subject": f"did:gravit:{node_id}",
        "vcp_version": "0.1",
        "supported_methods": ["grover"],
        "endpoints": {
            "claim": f"{base_url}/v1/claim",
            "action_verify": f"{base_url}/v1/action/verify",
            "trace": f"{base_url}/v1/trace/{{trace_id}}"
        },
        "gqrvp_parameters": {
            "eta": float(os.getenv("GRAVIT_ETA", "0.2")),
            "gamma": float(os.getenv("GRAVIT_GAMMA", "1.5")),
            "epsilon": float(os.getenv("GRAVIT_EPSILON", "0.1"))
        }
    }
