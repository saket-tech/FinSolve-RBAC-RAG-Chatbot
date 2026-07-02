"""Quick smoke test for FinSolve chatbot API."""

import json
import sys

import requests

BASE = "http://127.0.0.1:8000"
DEMO_PASSWORD = "finsolve123"


def check(name: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    return ok


def main() -> int:
    results: list[bool] = []

    # Health
    try:
        r = requests.get(f"{BASE}/health", timeout=10)
        results.append(check("Health endpoint", r.status_code == 200, r.json().get("message", "")))
    except requests.RequestException as exc:
        check("Health endpoint", False, str(exc))
        print("\nAPI is not running. Start it with:")
        print("  uvicorn app.api.main:app --host 0.0.0.0 --port 8000")
        return 1

    # Login — invalid credentials
    r = requests.post(
        f"{BASE}/auth/login",
        json={"username": "bad_user", "password": "wrong"},
        timeout=10,
    )
    results.append(check("Login rejects bad credentials", r.status_code == 401))

    # Login — finance user
    r = requests.post(
        f"{BASE}/auth/login",
        json={"username": "finance_user", "password": DEMO_PASSWORD},
        timeout=10,
    )
    if r.status_code != 200:
        results.append(check("Finance login", False, r.text))
        return 1

    finance_token = r.json()["access_token"]
    allowed = r.json()["allowed_departments"]
    results.append(check("Finance login", True, f"departments={allowed}"))

    # Chat — finance question as finance user
    r = requests.post(
        f"{BASE}/chat/query",
        json={"query": "What was revenue growth in 2024?"},
        headers={"Authorization": f"Bearer {finance_token}"},
        timeout=90,
    )
    if r.status_code == 200:
        data = r.json()
        has_answer = len(data.get("answer", "")) > 20
        has_sources = len(data.get("sources", [])) > 0
        results.append(check("Finance chat response", has_answer, f"{len(data['answer'])} chars"))
        results.append(check("Finance chat sources", has_sources, f"{len(data['sources'])} sources"))
        if has_answer:
            print(f"  Sample answer: {data['answer'][:120]}...")
    else:
        results.append(check("Finance chat response", False, f"{r.status_code}: {r.text[:200]}"))

    # Login — employee user
    r = requests.post(
        f"{BASE}/auth/login",
        json={"username": "employee_user", "password": DEMO_PASSWORD},
        timeout=10,
    )
    employee_token = r.json()["access_token"]
    results.append(check("Employee login", r.status_code == 200))

    # Chat — finance question as employee (RBAC: only general docs)
    r = requests.post(
        f"{BASE}/chat/query",
        json={"query": "What was revenue growth in 2024?"},
        headers={"Authorization": f"Bearer {employee_token}"},
        timeout=90,
    )
    if r.status_code == 200:
        data = r.json()
        sources = data.get("sources", [])
        only_general = all(s.get("department") == "general" for s in sources) if sources else True
        results.append(
            check(
                "Employee RBAC (no finance sources)",
                only_general or len(sources) == 0,
                f"sources={[s.get('department') for s in sources]}",
            )
        )
    else:
        results.append(check("Employee RBAC chat", False, f"{r.status_code}: {r.text[:200]}"))

    # Employee handbook question
    r = requests.post(
        f"{BASE}/chat/query",
        json={"query": "What is the annual leave policy?"},
        headers={"Authorization": f"Bearer {employee_token}"},
        timeout=90,
    )
    results.append(check("Employee handbook query", r.status_code == 200 and len(r.json().get("answer", "")) > 10))

    passed = sum(results)
    total = len(results)
    print(f"\nResult: {passed}/{total} checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
