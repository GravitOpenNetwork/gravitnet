from fastapi import FastAPI
from routes.execute import router as execute_router
from routes.vcp import router as vcp_router

app = FastAPI()
app.include_router(execute_router, prefix="/v1")
app.include_router(vcp_router, prefix="/v1")

@app.get("/")
def root():
    return {"status": "ok"}
