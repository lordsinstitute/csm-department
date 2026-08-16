from pathlib import Path

import chromadb
import yaml
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

SNIPPETS_DIR = Path(__file__).resolve().parent / "snippets"
COLLECTION_NAME = "knowledge_snippets"

_client = chromadb.EphemeralClient()
_collection = None


def _parse_snippet(path: Path) -> dict:
    _, frontmatter, body = path.read_text(encoding="utf-8").split("---", 2)
    meta = yaml.safe_load(frontmatter)
    return {
        "id": path.stem,
        "content": body.strip(),
        "title": meta["title"],
        "source": meta["source"],
        "problem_tags": meta["problem_tags"],
    }


def build_index():
    """Parse every snippet and (re)load them into the in-memory Chroma collection."""
    global _collection
    _collection = _client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=DefaultEmbeddingFunction(),
    )
    if _collection.count() > 0:
        _collection.delete(ids=_collection.get()["ids"])

    snippets = [_parse_snippet(p) for p in sorted(SNIPPETS_DIR.glob("*.md"))]
    _collection.add(
        ids=[s["id"] for s in snippets],
        documents=[s["content"] for s in snippets],
        metadatas=[
            {
                "title": s["title"],
                "source": s["source"],
                "problem_tags": ",".join(s["problem_tags"]),
            }
            for s in snippets
        ],
    )
    return _collection


def get_collection():
    if _collection is None:
        build_index()
    return _collection
