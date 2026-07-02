"""Chat API routes."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_role, get_current_user
from app.auth.rbac import Role, get_allowed_departments
from app.models.schemas import ChatRequest, ChatResponse, SourceReference
from app.monitoring.cost import get_tracker
from app.rag.pipeline import run_rag_pipeline

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/query", response_model=ChatResponse)
def chat_query(
    request: ChatRequest,
    role: Role = Depends(get_current_role),
    user: dict = Depends(get_current_user),
) -> ChatResponse:
    result = run_rag_pipeline(
        query=request.query.strip(),
        role=role,
        username=user["username"],
    )
    return ChatResponse(
        answer=result["answer"],
        sources=[SourceReference(**s) for s in result["sources"]],
        role=user["role"].value,
        allowed_departments=get_allowed_departments(role),
    )


@router.get("/cost-summary", tags=["Monitoring"])
def cost_summary() -> dict:
    """Returns aggregated token usage and cost for the current session."""
    return get_tracker().summary()
