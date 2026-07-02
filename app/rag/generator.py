"""Groq LLM response generation with LangSmith tracing and token tracking."""

from groq import Groq
from langsmith import traceable

from app.config.settings import get_settings


@traceable(name="finsolve-rag-generate", run_type="llm")
def generate_answer(query: str, context_chunks: list[dict], role: str) -> dict:
    """
    Generate a response using Groq with retrieved context.
    Returns dict with 'answer', 'prompt_tokens', 'completion_tokens'.
    """
    settings = get_settings()

    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is not set. Add it to your .env file.")

    if not context_chunks:
        return {
            "answer": (
                "I could not find relevant information in the documents you are "
                "permitted to access. Please rephrase your question or contact "
                "your department administrator if you believe you need additional access."
            ),
            "prompt_tokens": 0,
            "completion_tokens": 0,
        }

    context_block = "\n\n".join(
        f"[Source: {chunk['source']} | Department: {chunk['department']}]\n{chunk['content']}"
        for chunk in context_chunks
    )

    system_prompt = f"""You are FinSolve Technologies' internal assistant.
The current user role is: {role}.

Rules:
1. Answer ONLY using the provided context. Do not invent facts.
2. If the context is insufficient, say so clearly.
3. Always cite source document names in your answer.
4. Be concise, professional, and helpful.
5. Do not reveal data the user should not access based on their role."""

    user_prompt = f"""Context documents:
{context_block}

User question: {query}

Provide a clear answer with references to source documents."""

    client = Groq(api_key=settings.groq_api_key)
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=1024,
    )

    usage = response.usage
    return {
        "answer": response.choices[0].message.content or "No response generated.",
        "prompt_tokens": usage.prompt_tokens if usage else 0,
        "completion_tokens": usage.completion_tokens if usage else 0,
    }
