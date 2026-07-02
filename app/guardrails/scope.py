"""Out-of-scope query detection."""

# Keywords that suggest the query is about FinSolve business topics
_IN_SCOPE_HINTS = [
    "finsolve", "employee", "salary", "leave", "policy", "finance", "revenue",
    "marketing", "campaign", "hr", "payroll", "engineering", "budget", "expense",
    "report", "quarter", "performance", "department", "attendance", "handbook",
    "architecture", "team", "company", "onboarding", "benefits", "reimbursement",
]

# Hard-reject patterns — clearly off-topic
_OUT_OF_SCOPE_PATTERNS = [
    "write a poem", "write me a story", "tell me a joke", "play a game",
    "what is the weather", "stock price of", "recipe for", "who won the",
    "sports", "movie recommendation", "lyrics for", "translate this",
]


def is_out_of_scope(query: str) -> bool:
    """Return True if the query is clearly not work-related."""
    q = query.lower()

    # Hard-reject check first
    if any(pattern in q for pattern in _OUT_OF_SCOPE_PATTERNS):
        return True

    # If any business keyword is found, it's in-scope
    if any(hint in q for hint in _IN_SCOPE_HINTS):
        return False

    # Short queries under 4 words with no business context are flagged
    word_count = len(q.split())
    if word_count < 4:
        return True

    return False


OUT_OF_SCOPE_RESPONSE = (
    "I'm FinSolve's internal assistant and can only answer questions about "
    "company data, policies, and department information. "
    "Please ask something related to your work."
)
