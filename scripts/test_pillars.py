"""
Unit tests for the 3 new pillars:
  1. Guardrails - scope detection & PII redaction
  2. Cost tracker - token recording & alert threshold
  3. Tracer - LangSmith setup (env var check)

Run: python scripts/test_pillars.py
"""

import sys
import os

# Ensure app package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check(name: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
    return ok


results = []

# ── Pillar 1: Scope guardrail ────────────────────────────────────────────────
print("\n[Guardrail] Out-of-scope detection")
from app.guardrails.scope import is_out_of_scope

results.append(check("poem request blocked",       is_out_of_scope("write a poem for me")))
results.append(check("joke request blocked",       is_out_of_scope("tell me a joke")))
results.append(check("weather blocked",            is_out_of_scope("what is the weather today")))
results.append(check("finance query allowed",      not is_out_of_scope("What was the revenue in 2024?")))
results.append(check("leave policy allowed",       not is_out_of_scope("What is the annual leave policy?")))
results.append(check("HR query allowed",           not is_out_of_scope("Show me employee attendance records")))
results.append(check("short vague query blocked",  is_out_of_scope("hello")))
results.append(check("marketing query allowed",    not is_out_of_scope("Summarize Q3 campaign performance")))

# ── Pillar 1: PII redaction ──────────────────────────────────────────────────
print("\n[Guardrail] PII redaction")
from app.guardrails.pii import contains_pii, redact_pii

email_text = "Contact john.doe@finsolve.com for details"
redacted, labels = redact_pii(email_text)
results.append(check("email redacted",        "EMAIL" in labels, f"labels={labels}"))
results.append(check("email not in output",   "john.doe@finsolve.com" not in redacted))

salary_text = "His salary: $95,000 per year"
redacted2, labels2 = redact_pii(salary_text)
results.append(check("salary redacted",       "SALARY" in labels2, f"labels={labels2}"))

clean_text = "The Q3 revenue grew by 12%."
results.append(check("clean text unchanged",  not contains_pii(clean_text)))

emp_id_text = "Employee EMP-00123 submitted the request"
redacted3, labels3 = redact_pii(emp_id_text)
results.append(check("employee ID redacted",  "EMPLOYEE_ID" in labels3, f"labels={labels3}"))

# ── Pillar 3: Cost tracker ───────────────────────────────────────────────────
print("\n[Cost Tracker] Token recording & alert")
from app.monitoring.cost import CostTracker

tracker = CostTracker()
rec = tracker.record(
    username="finance_user",
    role="finance",
    model="llama-3.3-70b-versatile",
    prompt_tokens=500,
    completion_tokens=200,
)
results.append(check("record created",        rec.total_tokens == 700, f"tokens={rec.total_tokens}"))
results.append(check("cost estimated > 0",    rec.estimated_cost_usd > 0, f"cost=${rec.estimated_cost_usd}"))

summary = tracker.summary()
results.append(check("summary total=1",       summary["total_requests"] == 1))
results.append(check("summary tokens=700",    summary["total_tokens"] == 700))

# Check alert fires when threshold exceeded (inject large usage)
import logging
import io
log_capture = io.StringIO()
handler = logging.StreamHandler(log_capture)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.WARNING)

tracker.record("exec", "executive", "llama-3.3-70b-versatile", 1_000_000, 1_000_000)
log_output = log_capture.getvalue()
results.append(check("cost alert logged",     "COST_ALERT" in log_output, f"log={log_output[:80]}"))

# ── Pillar 2: LangSmith tracer ───────────────────────────────────────────────
print("\n[LangSmith] Tracer setup")
from app.monitoring.tracer import setup_langsmith

# With key set
os.environ["LANGSMITH_API_KEY"] = "test-key"
enabled = setup_langsmith()
results.append(check("tracer enabled with key",        enabled))
results.append(check("LANGCHAIN_TRACING_V2 set",       os.environ.get("LANGCHAIN_TRACING_V2") == "true"))
results.append(check("LANGCHAIN_PROJECT set",          os.environ.get("LANGCHAIN_PROJECT") == "finsolve-chatbot"))

# Without key
del os.environ["LANGSMITH_API_KEY"]
os.environ.pop("LANGCHAIN_TRACING_V2", None)
disabled = setup_langsmith()
results.append(check("tracer disabled without key",    not disabled))

# ── Summary ──────────────────────────────────────────────────────────────────
passed = sum(results)
total = len(results)
print(f"\nResult: {passed}/{total} checks passed")
sys.exit(0 if passed == total else 1)
