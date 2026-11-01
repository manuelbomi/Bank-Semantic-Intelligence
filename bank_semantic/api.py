"""Optional FastAPI facade. DEMO ONLY: no production authentication middleware.

Never expose this API publicly. Caller-provided role headers are forgeable.
"""
from .assistant import answer
from .config import DATA
try:
    from fastapi import FastAPI, Header, HTTPException
    from pydantic import BaseModel
except ImportError as exc:
    raise RuntimeError("Install fastapi and uvicorn from the full extra") from exc

app = FastAPI(title="Bank Semantic Lab (local-only)")

class Ask(BaseModel):
    """Typed prompt request prevents arbitrary unbounded request structure."""
    question: str
    customer_id: int | None = None

@app.post("/ask")
def ask(payload: Ask, x_demo_role: str = Header(default="analyst")):
    """Use only for local demonstration; replace with verified OIDC identity."""
    if len(payload.question) > 1000:
        raise HTTPException(status_code=400, detail="Question too long")
    try:
        return answer(payload.question, x_demo_role, DATA, payload.customer_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
