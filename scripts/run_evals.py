"""
Ragas evaluation script — runs after deploy to check RAG quality.
Metrics: faithfulness, answer_relevancy, context_precision.
Exits with code 1 if any metric drops below threshold.
"""

import os
import sys

import requests
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, context_precision, faithfulness

BASE = os.getenv("API_URL", "http://localhost:8000")
PASS_THRESHOLD = 0.5  # minimum acceptable score per metric

# Small golden eval set — question / expected department / reference answer snippet
EVAL_SET = [
    {
        "username": "finance_user",
        "password": "finsolve123",
        "question": "What was FinSolve's total revenue in 2024?",
        "reference": "FinSolve revenue",
    },
    {
        "username": "hr_user",
        "password": "finsolve123",
        "question": "How many days of annual leave are employees entitled to?",
        "reference": "annual leave",
    },
    {
        "username": "marketing_user",
        "password": "finsolve123",
        "question": "What was the ROI of Q3 2024 campaigns?",
        "reference": "campaign ROI",
    },
]


def get_token(username: str, password: str) -> str:
    r = requests.post(f"{BASE}/auth/login", json={"username": username, "password": password}, timeout=15)
    r.raise_for_status()
    return r.json()["access_token"]


def run_query(token: str, question: str) -> dict:
    r = requests.post(
        f"{BASE}/chat/query",
        json={"query": question},
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def main() -> int:
    print("Running Ragas evaluation...")

    questions, answers, contexts, references = [], [], [], []

    for item in EVAL_SET:
        try:
            token = get_token(item["username"], item["password"])
            result = run_query(token, item["question"])
            questions.append(item["question"])
            answers.append(result["answer"])
            contexts.append([s["excerpt"] for s in result.get("sources", [])] or [""])
            references.append(item["reference"])
            print(f"  [OK] {item['question'][:60]}")
        except Exception as exc:
            print(f"  [FAIL] {item['question'][:60]} — {exc}")
            return 1

    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "reference": references,
    })

    results = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
    )

    print("\nEval Results:")
    failed = False
    for metric, score in results.items():
        status = "PASS" if score >= PASS_THRESHOLD else "FAIL"
        print(f"  [{status}] {metric}: {score:.3f} (threshold={PASS_THRESHOLD})")
        if score < PASS_THRESHOLD:
            failed = True

    if failed:
        print("\nEvaluation FAILED — one or more metrics below threshold.")
        return 1

    print("\nEvaluation PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
