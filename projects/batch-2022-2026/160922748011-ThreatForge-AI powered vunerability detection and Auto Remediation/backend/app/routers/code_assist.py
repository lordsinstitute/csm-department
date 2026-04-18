"""Code assist API endpoints with semantic code search."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from pydantic import BaseModel

from backend.app.services.code_assist.improved_ingestion_service import (
    ingest_repository_from_path
)
from backend.app.services.code_assist.improved_query_service import ask_question

router = APIRouter(prefix="/code-assist", tags=["Code Assist"])


# class IndexRequest(BaseModel):
#     """Request to index a repository."""
#     repo_id: str
#     repo_path: str  # Path to repository on disk


class QueryRequest(BaseModel):
    """Request to query about the codebase."""
    question: str
    model: str = "deepseek-coder:6.7b"


@router.post("/index/{repo_id}")
def index_repo(repo_id: str):
    """
    Index a repository for semantic code search.
    
    This endpoint:
    1. Extracts project metadata and README
    2. Chunks all code files semantically (at function/class boundaries)
    3. Generates enriched embeddings
    4. Stores in FAISS vector database
    
    Example request:
    ```json
    {
        "repo_id": "my-project",
        "repo_path": "/path/to/repository"
    }
    ```
    """
    try:
        repo_path = Path("data/repos") / repo_id

        if not repo_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Repository '{repo_id}' not found in data/repos"
            )

        result = ingest_repository_from_path(
            repo_id,
            str(repo_path)
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask/{repo_id}")
def ask_about_code(repo_id: str, request: QueryRequest):
    """
    Ask questions about a repository that has been indexed.
    
    This endpoint uses multi-stage semantic retrieval:
    1. Vector similarity search (semantic meaning)
    2. Keyword matching for specificity
    3. Metadata-based ranking
    4. Context-aware LLM prompting
    
    Example requests:
    
    ```json
    {
        "question": "How does the authentication system work?"
    }
    ```
    
    ```json
    {
        "question": "Show me the API endpoints and their handlers"
    }
    ```
    
    ```json
    {
        "question": "What are the database models and relationships?"
    }
    ```
    """
    try:
        result = ask_question(repo_id, request.question, request.model)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repos")
def list_indexed_repos():
    """List all repositories that have been indexed."""
    from backend.app.services.code_assist.improved_vector_store_service import list_indexed_repos
    
    repos = list_indexed_repos()
    return {
        "count": len(repos),
        "repositories": repos
    }


@router.get("/stats/{repo_id}")
def get_repo_stats(repo_id: str):
    """Get indexing statistics for a repository."""
    from backend.app.services.code_assist.improved_vector_store_service import get_index_stats
    
    try:
        stats = get_index_stats(repo_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"No index found for {repo_id}")
    

@router.get("/projects")
def list_indexed_projects():
    """
    Return all repositories that already have a vector index.
    This allows users to directly ask questions without re-indexing.
    """

    try:
        vector_index_dir = Path("data/vector_index")

        if not vector_index_dir.exists():
            return {
                "count": 0,
                "projects": []
            }

        projects = []

        for repo_dir in vector_index_dir.iterdir():
            if repo_dir.is_dir():
                projects.append({
                    "repo_id": repo_dir.name,
                    "indexed": True
                })

        return {
            "count": len(projects),
            "projects": projects
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))