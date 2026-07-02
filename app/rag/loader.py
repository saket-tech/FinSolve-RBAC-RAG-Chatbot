"""Load and chunk documents from the data directory."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import Settings


@dataclass
class DocumentChunk:
    content: str
    department: str
    source: str


def _chunk_text(text: str, settings: Settings) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return splitter.split_text(text)


def _load_markdown(file_path: Path, department: str, settings: Settings) -> list[DocumentChunk]:
    text = file_path.read_text(encoding="utf-8")
    chunks = _chunk_text(text, settings)
    return [
        DocumentChunk(
            content=chunk,
            department=department,
            source=file_path.name,
        )
        for chunk in chunks
    ]


def _load_csv(file_path: Path, department: str) -> list[DocumentChunk]:
    """Convert HR CSV rows into searchable text chunks."""
    df = pd.read_csv(file_path)
    chunks: list[DocumentChunk] = []

    # Batch rows for broader workforce queries
    batch_size = 10
    for start in range(0, len(df), batch_size):
        batch = df.iloc[start : start + batch_size]
        lines = []
        for _, row in batch.iterrows():
            lines.append(
                "Employee: {full_name} | ID: {employee_id} | Role: {role} | "
                "Department: {department} | Salary: {salary} | Leave balance: {leave_balance} | "
                "Leaves taken: {leaves_taken} | Attendance: {attendance_pct}% | "
                "Performance rating: {performance_rating}/5 | Last review: {last_review_date}".format(
                    **row.to_dict()
                )
            )
        chunks.append(
            DocumentChunk(
                content="\n".join(lines),
                department=department,
                source=file_path.name,
            )
        )

    return chunks


def load_all_documents(settings: Settings) -> list[DocumentChunk]:
    """Load all documents from department subfolders."""
    all_chunks: list[DocumentChunk] = []
    data_dir = settings.data_dir

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    for department_dir in sorted(data_dir.iterdir()):
        if not department_dir.is_dir():
            continue
        department = department_dir.name

        for file_path in sorted(department_dir.iterdir()):
            if file_path.suffix.lower() == ".md":
                all_chunks.extend(_load_markdown(file_path, department, settings))
            elif file_path.suffix.lower() == ".csv":
                all_chunks.extend(_load_csv(file_path, department))

    return all_chunks
