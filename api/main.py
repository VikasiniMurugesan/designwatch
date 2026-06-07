from fastapi import FastAPI
from api.routes import level1, level2

app = FastAPI(title="Designwatch API", version="1.0.0")

app.include_router(level1.router, prefix="/level1", tags=["Level 1 — Design Audit"])
app.include_router(level2.router, prefix="/level2", tags=["Level 2 — Before/After Regression"])
