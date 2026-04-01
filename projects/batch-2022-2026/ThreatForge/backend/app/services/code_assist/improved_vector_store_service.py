"""
Improved vector store service using FAISS with rich metadata.
"""

import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple

BASE_INDEX_DIR = Path("data/vector_index")


def get_index_path(repo_id: str):
    """Get the path for a repository's vector index."""
    return BASE_INDEX_DIR / repo_id


def store_embeddings(repo_id: str, items: List) -> None:
    """
    Store embeddings and metadata in FAISS with rich metadata preservation.
    
    Args:
        repo_id: Repository identifier
        items: List of chunks with 'embedding' and 'metadata' keys
    """
    index_dir = get_index_path(repo_id)
    index_dir.mkdir(parents=True, exist_ok=True)
    
    # === Validate and extract embeddings ===
    valid_embeddings = []
    valid_items = []
    
    for item in items:
        embedding = item.get("embedding")
        
        # Validate embedding
        if not isinstance(embedding, list):
            continue
        if len(embedding) != 768:
            print(f"Skipping {item.get('name')} - invalid embedding dimension {len(embedding)}")
            continue
        
        # Validate has required metadata
        if 'name' not in item:
            continue
        
        valid_embeddings.append(embedding)
        valid_items.append(item)
    
    if not valid_embeddings:
        raise ValueError("No valid embeddings to store")
    
    # === Create FAISS index ===
    vectors = np.array(valid_embeddings).astype("float32")
    dim = vectors.shape[1]
    
    # Use IndexFlatL2 for semantic similarity search
    # L2 distance works well with normalized embeddings
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    
    # === Save index and metadata ===
    index_path = index_dir / "index.faiss"
    metadata_path = index_dir / "metadata.pkl"
    
    faiss.write_index(index, str(index_path))
    print(f"✓ FAISS index saved: {index_path}")
    
    with open(metadata_path, "wb") as f:
        pickle.dump(valid_items, f)
    print(f"✓ Metadata saved: {metadata_path} ({len(valid_items)} chunks)")
    
    # === Save stats for debugging ===
    stats = {
        "total_chunks": len(valid_items),
        "embedding_dimension": dim,
        "chunk_types": {},
        "files": set()
    }
    
    for item in valid_items:
        metadata = item.get('metadata', {})
        chunk_type = metadata.get('chunk_type', 'unknown')
        stats['chunk_types'][chunk_type] = stats['chunk_types'].get(chunk_type, 0) + 1
        
        file_path = item.get('file_path')
        if file_path:
            stats['files'].add(file_path)
    
    stats['files'] = list(stats['files'])
    stats['total_files'] = len(stats['files'])
    
    stats_path = index_dir / "stats.json"
    import json
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"✓ Statistics saved: {stats_path}")


def load_index(repo_id: str) -> Tuple[object, List]:
    """
    Load FAISS index and metadata for a repository.
    
    Returns:
        Tuple of (faiss_index, metadata_list)
    """
    index_dir = get_index_path(repo_id)
    
    index_path = index_dir / "index.faiss"
    metadata_path = index_dir / "metadata.pkl"
    
    if not index_path.exists():
        raise FileNotFoundError(f"No FAISS index found for repo '{repo_id}'")
    
    if not metadata_path.exists():
        raise FileNotFoundError(f"No metadata found for repo '{repo_id}'")
    
    # Load FAISS index
    index = faiss.read_index(str(index_path))
    print(f"✓ Loaded FAISS index: {index.ntotal} vectors")
    
    # Load metadata
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)
    print(f"✓ Loaded metadata: {len(metadata)} chunks")
    
    return index, metadata


def search(
    repo_id: str,
    query_vector: np.ndarray,
    k: int = 10
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Search the index for similar vectors.
    
    Args:
        repo_id: Repository identifier
        query_vector: Query embedding vector
        k: Number of results to return
    
    Returns:
        Tuple of (distances, indices)
    """
    index, metadata = load_index(repo_id)
    
    if len(query_vector.shape) == 1:
        query_vector = query_vector.reshape(1, -1)
    
    # Ensure correct dtype
    query_vector = query_vector.astype("float32")
    
    distances, indices = index.search(query_vector, min(k, index.ntotal))
    
    return distances, indices


def delete_index(repo_id: str) -> bool:
    """Delete the index for a repository."""
    import shutil
    
    index_dir = get_index_path(repo_id)
    if index_dir.exists():
        shutil.rmtree(index_dir)
        print(f"✓ Deleted index for {repo_id}")
        return True
    return False


def get_index_stats(repo_id: str) -> dict:
    """Get statistics about the index."""
    index_dir = get_index_path(repo_id)
    stats_path = index_dir / "stats.json"
    
    if not stats_path.exists():
        return {}
    
    import json
    with open(stats_path, 'r') as f:
        return json.load(f)


def list_indexed_repos() -> List[str]:
    """List all repositories that have been indexed."""
    if not BASE_INDEX_DIR.exists():
        return []
    
    return [d.name for d in BASE_INDEX_DIR.iterdir() if d.is_dir()]


__all__ = [
    'store_embeddings',
    'load_index',
    'search',
    'delete_index',
    'get_index_stats',
    'list_indexed_repos',
    'get_index_path'
]
