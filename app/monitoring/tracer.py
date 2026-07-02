"""LangSmith tracing setup."""

import logging
import os

logger = logging.getLogger(__name__)


def setup_langsmith() -> bool:
    """Configure LangSmith environment variables. Returns True if enabled."""
    api_key = os.getenv("LANGSMITH_API_KEY", "")
    if not api_key:
        logger.info("LangSmith disabled: LANGSMITH_API_KEY not set.")
        return False

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = api_key
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "finsolve-chatbot")
    logger.info("LangSmith tracing enabled for project: %s", os.environ["LANGCHAIN_PROJECT"])
    return True
