"""
Improved embedding service with semantic context enrichment.
Enriches chunks with code analysis metadata before embedding.

Migration note: Uses groq_client.embed() (sentence-transformers, 768-dim)
instead of ollama_client.embed(). The enrichment logic and metadata extraction
are unchanged — only the underlying embed() call is swapped.
"""

from typing import Dict, List
import re

# ── Swapped: groq_client replaces ollama_client ──────────────────────────────
from backend.app.core.groq_client import embed


def extract_semantic_metadata(chunk: Dict) -> Dict:
    """
    Extract semantic metadata from a code chunk for richer embeddings.
    Returns structured metadata that will be included in embedding context.
    """
    metadata = {
        "chunk_type": chunk.get("chunk_type"),
        "name": chunk.get("name"),
        "language": chunk.get("language"),
        "file_path": chunk.get("file_path", ""),
        "risk_level": chunk.get("risk_level", "low"),
        "keywords": [],
        "dependencies": [],
        "public_api": [],
        "complexity": "low",
        "imports": [],
        "annotations": [],
    }

    text = chunk.get("text", "").lower()
    full_text = chunk.get("text", "")

    code_keywords = {
        "async", "await", "class", "function", "def", "return", "if", "for", "while",
        "try", "except", "finally", "import", "from", "export", "const", "let", "var",
        "interface", "type", "enum", "decorator", "@", "property", "staticmethod",
        "classmethod", "raise", "yield", "lambda", "switch", "case",
    }
    for keyword in code_keywords:
        if keyword in text:
            metadata["keywords"].append(keyword)

    import_pattern = r"(?:from|import)\s+[\w._]+|require\([\"'][\w._/]+[\"']\)"
    imports = re.findall(import_pattern, full_text, re.IGNORECASE)
    metadata["imports"] = imports[:5]

    if chunk.get("chunk_type") in {"class", "function", "method"}:
        name_parts = chunk.get("name", "").split("::")
        if len(name_parts) >= 2:
            metadata["public_api"] = [name_parts[-1]]

    complexity_score = 0
    complexity_score += text.count("if ") * 2
    complexity_score += text.count("for ") * 2
    complexity_score += text.count("while ") * 2
    complexity_score += text.count("try") * 1
    complexity_score += text.count("lambda") * 1
    complexity_score += text.count("async") * 1

    if complexity_score > 15:
        metadata["complexity"] = "high"
    elif complexity_score > 5:
        metadata["complexity"] = "medium"
    else:
        metadata["complexity"] = "low"

    decorator_pattern = r"@\w+|:\s*\w+(?:\[.*?\])?"
    decorators = re.findall(decorator_pattern, full_text)
    metadata["annotations"] = list(set(decorators))[:5]

    patterns_detected = []
    if "def __init__" in full_text or "constructor" in text:
        patterns_detected.append("initialization")
    if "test" in chunk.get("name", "").lower():
        patterns_detected.append("test_code")
    if "exception" in text or "error" in text:
        patterns_detected.append("error_handling")
    if "api" in text or "endpoint" in text:
        patterns_detected.append("api_handler")
    if "database" in text or "query" in text or "sql" in text:
        patterns_detected.append("database_interaction")
    if "authentication" in text or "auth" in text:
        patterns_detected.append("authentication")
    if "logging" in text or "log" in text:
        patterns_detected.append("logging")

    metadata["patterns"] = patterns_detected
    return metadata


def generate_enriched_embedding_text(chunk: Dict, metadata: Dict) -> str:
    """
    Generate an enriched text representation that combines code with semantic context.
    This text will be embedded, making the embedding more semantically aware.
    """
    prefix_parts = []

    chunk_type = metadata.get("chunk_type", "code")
    name = metadata.get("name", "unnamed")
    prefix_parts.append(f"[{chunk_type.upper()}: {name}]")

    context = chunk.get("context", {})
    if context.get("description"):
        prefix_parts.append(f"Description: {context.get('description')}")

    if metadata.get("public_api"):
        prefix_parts.append(f"API: {', '.join(metadata['public_api'])}")

    if "parameters" in context:
        params = context.get("parameters", [])
        if params:
            prefix_parts.append(f"Parameters: {', '.join(params)}")

    if metadata.get("patterns"):
        prefix_parts.append(f"Patterns: {', '.join(metadata['patterns'])}")

    if metadata.get("imports"):
        prefix_parts.append(f"Imports: {', '.join(metadata['imports'][:3])}")

    prefix = "\n".join(prefix_parts)
    code = chunk.get("text", "")
    return f"{prefix}\n\n{code}"


def embed_chunks(chunks: List[Dict]) -> List[Dict]:
    """
    Embed a list of chunks with semantic enrichment.
    Returns chunks with embedding vectors attached.
    """
    enriched = []

    for chunk in chunks:
        text = chunk.get("text", "").strip()
        if not text:
            continue

        try:
            metadata = extract_semantic_metadata(chunk)
            enriched_text = generate_enriched_embedding_text(chunk, metadata)

            # embed() calls groq_client which uses sentence-transformers (768-dim)
            vector = embed(enriched_text)

            if not isinstance(vector, list) or len(vector) != 768:
                print(f"Skipping {chunk.get('name')} - invalid embedding dimension {len(vector) if isinstance(vector, list) else 'N/A'}")
                continue

            chunk["embedding"] = vector
            chunk["metadata"] = metadata
            chunk["enriched_text"] = enriched_text
            chunk["token_count"] = len(enriched_text.split())

            enriched.append(chunk)
            print(f"✓ Embedded {chunk.get('name')} ({metadata.get('chunk_type')})")

        except Exception as e:
            print(f"✗ Failed to embed {chunk.get('name')}: {e}")
            continue

    print(f"\nTotal chunks embedded: {len(enriched)}")
    return enriched


def boost_embedding_score(chunk: Dict, query: str, base_score: float) -> float:
    """
    Apply semantic boosting to embedding similarity scores.
    Boosts scores for semantically relevant matches.
    """
    boosted_score = base_score
    query_lower = query.lower()
    metadata = chunk.get("metadata", {})

    chunk_type = metadata.get("chunk_type", "")
    if chunk_type in {"class", "function", "method"}:
        boosted_score *= 1.15

    if "test" in query_lower and "test_code" in metadata.get("patterns", []):
        boosted_score *= 1.25
    if "database" in query_lower and "database_interaction" in metadata.get("patterns", []):
        boosted_score *= 1.20
    if "api" in query_lower and "api_handler" in metadata.get("patterns", []):
        boosted_score *= 1.20
    if "error" in query_lower and "error_handling" in metadata.get("patterns", []):
        boosted_score *= 1.20

    complexity = metadata.get("complexity", "low")
    if any(word in query_lower for word in ["architecture", "design", "pattern", "optimize"]):
        if complexity in {"medium", "high"}:
            boosted_score *= 1.15

    if complexity == "low" and len(query_lower.split()) > 8:
        boosted_score *= 0.95

    return boosted_score


__all__ = [
    "embed_chunks",
    "extract_semantic_metadata",
    "generate_enriched_embedding_text",
    "boost_embedding_score",
]