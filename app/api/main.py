"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, chat
from app.models.schemas import HealthResponse
from app.monitoring.tracer import setup_langsmith
from app.rag.vectorstore import build_index, get_collection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: enable LangSmith tracing and build vector index if empty."""
    setup_langsmith()
    try:
        collection = get_collection()
        if collection.count() == 0:
            count = build_index(reset=False)
            print(f"Indexed {count} document chunks into Chroma.")
        else:
            print(f"Chroma collection ready with {collection.count()} chunks.")
    except Exception as exc:
        print(f"Warning: index initialization failed: {exc}")
    yield


app = FastAPI(
    title="FinSolve RBAC RAG Chatbot API",
    description="Role-based internal chatbot for FinSolve Technologies",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", message="FinSolve chatbot API is running")
