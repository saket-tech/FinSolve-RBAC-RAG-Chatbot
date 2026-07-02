"""End-to-end RAG pipeline with RBAC, guardrails, and cost tracking."""

from langsmith import traceable

from app.auth.rbac import Role, get_allowed_departments
from app.guardrails.pii import redact_pii
from app.guardrails.scope import OUT_OF_SCOPE_RESPONSE, is_out_of_scope
from app.monitoring.cost import get_tracker
from app.rag.generator import generate_answer
from app.rag.vectorstore import retrieve_documents


@traceable(name="finsolve-rag-pipeline", run_type="chain")
def run_rag_pipeline(query: str, role: Role, username: str = "unknown") -> dict:
    """Process a query: guardrails → retrieval → generation → cost tracking."""

    # 1. Out-of-scope guard
    if is_out_of_scope(query):
        return {
            "answer": OUT_OF_SCOPE_RESPONSE,
            "sources": [],
            "role": role.value,
            "allowed_departments": get_allowed_departments(role),
            "guardrail_triggered": "out_of_scope",
        }

    # 2. Retrieve role-filtered context
    allowed = get_allowed_departments(role)
    chunks = retrieve_documents(query, allowed)

    # 3. Generate answer
    from app.config.settings import get_settings
    settings = get_settings()

    result = generate_answer(query, chunks, role.value)
    answer_raw = result["answer"]

    # 4. Redact PII from answer before returning
    answer, pii_found = redact_pii(answer_raw)
    guardrail = "pii_redacted" if pii_found else None

    # 5. Track token cost
    get_tracker().record(
        username=username,
        role=role.value,
        model=settings.groq_model,
        prompt_tokens=result["prompt_tokens"],
        completion_tokens=result["completion_tokens"],
    )

    sources = [
        {
            "document": chunk["source"],
            "department": chunk["department"],
            "relevance_score": chunk["score"],
            "excerpt": chunk["content"][:300] + "..."
            if len(chunk["content"]) > 300
            else chunk["content"],
        }
        for chunk in chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
        "role": role.value,
        "allowed_departments": allowed,
        "guardrail_triggered": guardrail,
    }
