from fastapi import FastAPI
from routes.execute import router as execute_router
from routes.vcp import router as vcp_router

app = FastAPI()
app.include_router(execute_router, prefix="/v1")
app.include_router(vcp_router, prefix="/v1")

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/.well-known/vcp")
def get_vcp_metadata():
    import os
    return {
        "node_id": os.getenv("GRAVIT_NODE_ID", "node-1"),
        "vcp_version": "0.1",
        "supported_methods": ["claim", "action/verify", "trace"],
        "endpoints": {
            "claim": "/v1/claim",
            "action_verify": "/v1/action/verify",
            "trace": "/v1/trace"
        },
        "gqrvp_parameters": {
            "learning_rate": float(os.getenv("GRAVIT_ETA", "0.2")),
            "amplification": float(os.getenv("GRAVIT_GAMMA", "1.5")),
            "mixing": float(os.getenv("GRAVIT_EPSILON", "0.1")),
            "threshold": 0.7
        },
        "links": [
            {
                "rel": "https://gravit.network/vcp/schema/claim",
                "href": f"{base_url}/schemas/claim.json",
                "type": "application/schema+json"
            }
        ]
    }
