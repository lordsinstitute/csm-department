from app.knowledge_base.build_index import get_collection


def query(text: str, problem_name: str, k: int = 3) -> list[dict]:
    """Return up to k snippets, preferring ones tagged with problem_name, else pure similarity."""
    collection = get_collection()
    result = collection.query(query_texts=[text], n_results=collection.count())

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]

    candidates = [
        {
            "content": documents[i],
            "title": metadatas[i]["title"],
            "source": metadatas[i]["source"],
            "tags": metadatas[i]["problem_tags"].split(","),
        }
        for i in range(len(documents))
    ]

    matched = [c for c in candidates if problem_name in c["tags"]]
    unmatched = [c for c in candidates if problem_name not in c["tags"]]

    top = (matched + unmatched)[:k]
    return [{"content": c["content"], "title": c["title"], "source": c["source"]} for c in top]
