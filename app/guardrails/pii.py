"""PII detection and redaction using regex patterns."""

import re

# Patterns: (label, compiled_regex)
_PII_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("EMAIL", re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", re.IGNORECASE)),
    ("PHONE", re.compile(r"\b(\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")),
    ("SSN",   re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("CREDIT_CARD", re.compile(r"\b(?:\d[ -]?){13,16}\b")),
    ("SALARY", re.compile(r"\b(salary|pay|compensation)\s*[:\-]?\s*\$?[\d,]+", re.IGNORECASE)),
    ("EMPLOYEE_ID", re.compile(r"\bEMP[-_]?\d{3,6}\b", re.IGNORECASE)),
]


def redact_pii(text: str) -> tuple[str, list[str]]:
    """
    Replace PII in text with [REDACTED-<label>] tokens.
    Returns (redacted_text, list_of_found_labels).
    """
    found: list[str] = []
    for label, pattern in _PII_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            found.append(label)
            text = pattern.sub(f"[REDACTED-{label}]", text)
    return text, found


def contains_pii(text: str) -> bool:
    return any(pattern.search(text) for _, pattern in _PII_PATTERNS)
