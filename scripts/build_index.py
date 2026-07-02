"""Build or rebuild the Chroma vector index."""

import argparse

from app.config.settings import get_settings
from app.rag.vectorstore import build_index


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Chroma vector index")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing collection before re-indexing",
    )
    args = parser.parse_args()

    settings = get_settings()
    print(f"Data directory: {settings.data_dir}")
    print(f"Chroma directory: {settings.chroma_dir}")

    count = build_index(settings=settings, reset=args.reset)
    print(f"Successfully indexed {count} document chunks.")


if __name__ == "__main__":
    main()
