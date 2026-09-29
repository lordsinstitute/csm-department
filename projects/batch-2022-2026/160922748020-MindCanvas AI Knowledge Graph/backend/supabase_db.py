"""
MindCanvas Vector Database — local PostgreSQL + pgvector
Replaces Supabase cloud with a self-hosted Postgres instance running in Docker.
"""

import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

import asyncpg
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize

import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Load environment variables from .env file
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/mindcanvas")


@dataclass
class ContentItem:
    url: str
    title: str
    summary: str
    content: str
    content_type: str
    key_topics: List[str]
    quality_score: int
    processing_method: str
    visit_timestamp: datetime
    content_hash: str
    embedding: Optional[List[float]] = None


class SimpleVectorDB:
    def __init__(self, pool: asyncpg.Pool, st_embedder=None):
        self.pool = pool
        self.st_embedder = st_embedder
        logger.info("✅ Connected to local PostgreSQL with pgvector")

    @staticmethod
    def _parse_topics(raw) -> List[str]:
        """Return key_topics as a list regardless of storage format."""
        if not raw:
            return []
        if isinstance(raw, list):
            return raw
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return []
        return []

    # ──────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────

    async def _fetch(self, sql: str, *args) -> List[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql, *args)

    async def _fetchrow(self, sql: str, *args) -> Optional[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(sql, *args)

    async def _execute(self, sql: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(sql, *args)

    # ──────────────────────────────────────────────────────────────
    # New helper methods called by main.py and rag_chatbot.py
    # ──────────────────────────────────────────────────────────────

    async def ping(self):
        """Lightweight connectivity check."""
        await self._fetch("SELECT 1 FROM processed_content LIMIT 1")

    async def url_exists(self, url: str) -> bool:
        """Return True if a row with this URL already exists."""
        row = await self._fetchrow(
            "SELECT id FROM processed_content WHERE url = $1", url
        )
        return row is not None

    async def get_content_list(self, limit: int = 100) -> List[Dict]:
        rows = await self._fetch(
            """SELECT id, url, title, summary, content_type, key_topics,
                      quality_score, processing_method
               FROM processed_content
               ORDER BY quality_score DESC
               LIMIT $1""",
            limit,
        )
        return [dict(r) for r in rows]

    async def text_search(self, q: str, limit: int = 50) -> List[Dict]:
        rows = await self._fetch(
            """SELECT id, url, title, summary, content_type, key_topics, quality_score
               FROM processed_content
               WHERE title ILIKE $1 OR summary ILIKE $1
               LIMIT $2""",
            f"%{q}%",
            limit,
        )
        return [dict(r) for r in rows]

    async def get_recommendations(self, limit: int = 10) -> List[Dict]:
        rows = await self._fetch(
            """SELECT id, url, title, summary, content_type, quality_score
               FROM processed_content
               WHERE quality_score >= 7
               ORDER BY quality_score DESC
               LIMIT $1""",
            limit,
        )
        return [dict(r) for r in rows]

    async def get_all_for_reindex(self) -> List[Dict]:
        rows = await self._fetch(
            "SELECT id, title, summary FROM processed_content"
        )
        return [dict(r) for r in rows]

    async def update_embedding(self, item_id: int, embedding: List[float]):
        from pgvector.asyncpg import register_vector
        async with self.pool.acquire() as conn:
            await register_vector(conn)
            await conn.execute(
                "UPDATE processed_content SET embedding = $1 WHERE id = $2",
                embedding,
                item_id,
            )

    async def get_all_for_export(self) -> List[Dict]:
        rows = await self._fetch(
            """SELECT id, url, title, summary, content_type, key_topics,
                      quality_score, processing_method, visit_timestamp
               FROM processed_content"""
        )
        return [dict(r) for r in rows]

    async def delete_all(self):
        await self._execute("DELETE FROM processed_content")

    async def get_top_content(self, limit: int = 100) -> List[Dict]:
        rows = await self._fetch(
            """SELECT id, title, summary, content_type, key_topics, quality_score, url
               FROM processed_content
               ORDER BY quality_score DESC
               LIMIT $1""",
            limit,
        )
        return [dict(r) for r in rows]

    async def get_suggestions_content(self, limit: int = 20) -> List[Dict]:
        rows = await self._fetch(
            """SELECT title, key_topics, content_type
               FROM processed_content
               WHERE quality_score >= 7
               ORDER BY quality_score DESC
               LIMIT $1""",
            limit,
        )
        return [
            {**dict(r), "key_topics": self._parse_topics(r["key_topics"])}
            for r in rows
        ]

    # ──────────────────────────────────────────────────────────────
    # Embeddings
    # ──────────────────────────────────────────────────────────────

    async def generate_embedding(self, text: str, use_openai: bool = True) -> List[float]:
        """Generate a 384-dim embedding using SentenceTransformer."""
        target_dimension = 384
        text_preview = text[:80] + "..." if len(text) > 80 else text
        try:
            if self.st_embedder:
                embedding = await asyncio.to_thread(self.st_embedder.encode, text)
                return embedding.tolist()
            logger.warning(f"No embedder available for '{text_preview}'")
            return [0.0] * target_dimension
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return [0.0] * target_dimension

    # ──────────────────────────────────────────────────────────────
    # Core CRUD
    # ──────────────────────────────────────────────────────────────

    async def store_content(self, item: ContentItem) -> bool:
        """Upsert content. Existing embeddings are preserved on conflict."""
        try:
            if not item.embedding:
                text = f"{item.title} {item.summary}"
                item.embedding = await self.generate_embedding(text)

            # Handle visit_timestamp: accept both datetime and ISO string
            vts = item.visit_timestamp
            if isinstance(vts, str):
                try:
                    vts = datetime.fromisoformat(vts)
                except Exception:
                    vts = None

            from pgvector.asyncpg import register_vector
            async with self.pool.acquire() as conn:
                await register_vector(conn)
                await conn.execute(
                    """INSERT INTO processed_content
                           (url, title, summary, content, content_type, key_topics,
                            quality_score, processing_method, visit_timestamp,
                            content_hash, embedding)
                       VALUES ($1,$2,$3,$4,$5,$6::jsonb,$7,$8,$9,$10,$11)
                       ON CONFLICT (url) DO UPDATE SET
                           title             = EXCLUDED.title,
                           summary           = EXCLUDED.summary,
                           content           = EXCLUDED.content,
                           content_type      = EXCLUDED.content_type,
                           key_topics        = EXCLUDED.key_topics,
                           quality_score     = EXCLUDED.quality_score,
                           processing_method = EXCLUDED.processing_method,
                           visit_timestamp   = EXCLUDED.visit_timestamp,
                           content_hash      = EXCLUDED.content_hash,
                           embedding         = COALESCE(EXCLUDED.embedding,
                                                        processed_content.embedding)
                    """,
                    item.url,
                    item.title,
                    item.summary,
                    item.content,
                    item.content_type,
                    item.key_topics,
                    item.quality_score,
                    item.processing_method,
                    vts,
                    item.content_hash,
                    item.embedding,
                )
            return True
        except Exception as e:
            logger.error(f"Store failed for {item.url}: {e}")
            return False

    # ──────────────────────────────────────────────────────────────
    # Search
    # ──────────────────────────────────────────────────────────────

    async def semantic_search(self, query: str, limit: int = 20, threshold: float = 0.3) -> List[Dict]:
        """Vector similarity search using pgvector."""
        query_preview = query[:80] + "..." if len(query) > 80 else query
        logger.info(f"🔍 Semantic search: '{query_preview}'")

        try:
            query_embedding = await self.generate_embedding(query)
            if not query_embedding or len(query_embedding) == 0:
                logger.error(f"Invalid query embedding for '{query_preview}'")
                return []

            from pgvector.asyncpg import register_vector
            async with self.pool.acquire() as conn:
                await register_vector(conn)
                rows = await conn.fetch(
                    """WITH scored AS (
                           SELECT id, url, title, summary, content_type, key_topics, quality_score,
                                  1 - (embedding <=> $1) AS similarity
                           FROM processed_content WHERE embedding IS NOT NULL
                       )
                       SELECT * FROM scored WHERE similarity > $2
                       ORDER BY similarity DESC LIMIT $3""",
                    query_embedding,
                    threshold,
                    limit,
                )

            results = [
                {
                    "id": r["id"],
                    "url": r["url"],
                    "title": r["title"],
                    "summary": r["summary"],
                    "content_type": r["content_type"],
                    "key_topics": self._parse_topics(r["key_topics"]),
                    "quality_score": r["quality_score"],
                    "similarity": round(float(r["similarity"]), 3),
                }
                for r in rows
            ]
            logger.info(f"✅ Found {len(results)} results via pgvector")
            return results

        except Exception as e:
            logger.error(f"Semantic search failed: {e}", exc_info=True)
            return []

    # ──────────────────────────────────────────────────────────────
    # Clustering
    # ──────────────────────────────────────────────────────────────

    async def cluster_content(self) -> List[Dict]:
        """DBSCAN clustering on embeddings + semantic topic analysis."""
        try:
            logger.info("🎯 Starting advanced clustering...")

            rows = await self._fetch(
                """SELECT id, title, content_type, quality_score, key_topics, summary, embedding
                   FROM processed_content"""
            )

            if not rows or len(rows) < 3:
                logger.warning("Insufficient data for clustering")
                return []

            items = [dict(r) for r in rows]

            embeddings = []
            valid_items = []
            target_dim = None
            for item in items:
                emb = item.get("embedding")
                if emb is not None and len(emb) > 0:
                    if target_dim is None:
                        target_dim = len(emb)
                    if len(emb) == target_dim:
                        embeddings.append(list(emb))
                        valid_items.append(item)

            if len(embeddings) < 3:
                logger.warning("Not enough valid embeddings for clustering")
                return self._fallback_clustering(items)

            embeddings_array = np.array(embeddings)
            embeddings_normalized = normalize(embeddings_array)

            n = len(valid_items)
            eps = 0.4
            min_samples = max(2, min(4, n // 8))

            clustering = DBSCAN(eps=eps, min_samples=min_samples, metric="cosine", n_jobs=-1)
            labels = clustering.fit_predict(embeddings_normalized)

            clusters_dict = defaultdict(list)
            for idx, label in enumerate(labels):
                clusters_dict[int(label)].append(valid_items[idx])

            clusters = []
            for cluster_id, cluster_items in clusters_dict.items():
                if cluster_id == -1:
                    continue
                if len(cluster_items) < 2:
                    continue

                all_topics = []
                for item in cluster_items:
                    all_topics.extend(self._parse_topics(item.get("key_topics")))

                topic_counts = Counter(all_topics)
                top_topics = [topic for topic, _ in topic_counts.most_common(5)]

                avg_quality = sum(item.get("quality_score", 5) for item in cluster_items) / len(cluster_items)

                if len(top_topics) >= 2:
                    cluster_name = f"{top_topics[0].title()} & {top_topics[1].title()}"
                elif top_topics:
                    cluster_name = top_topics[0].title()
                else:
                    cluster_name = f"Cluster {cluster_id + 1}"

                content_types = [item.get("content_type", "Unknown") for item in cluster_items]
                type_counts = Counter(content_types)
                dominant_type = type_counts.most_common(1)[0][0] if type_counts else "Mixed"

                clusters.append({
                    "id": cluster_id + 1,
                    "name": cluster_name,
                    "description": f"{len(cluster_items)} items - {dominant_type}",
                    "content_count": len(cluster_items),
                    "top_topics": top_topics,
                    "average_quality": round(avg_quality, 1),
                    "content_types": dict(type_counts),
                    "items": [item["id"] for item in cluster_items],
                    "representative_title": cluster_items[0]["title"],
                })

            clusters.sort(key=lambda x: (x["content_count"], x["average_quality"]), reverse=True)
            logger.info(f"✅ Created {len(clusters)} semantic clusters using DBSCAN")
            return clusters

        except Exception as e:
            logger.error(f"Advanced clustering failed: {e}", exc_info=True)
            return self._fallback_clustering(items if "items" in locals() else [])

    def _fallback_clustering(self, items: List[Dict]) -> List[Dict]:
        """Fallback clustering by content type."""
        logger.info("Using fallback clustering by content type")
        clusters_dict = defaultdict(list)
        for item in items:
            clusters_dict[item.get("content_type", "Unknown")].append(item)

        clusters = []
        for idx, (content_type, cluster_items) in enumerate(clusters_dict.items(), 1):
            if not cluster_items:
                continue
            all_topics = []
            for item in cluster_items:
                all_topics.extend(self._parse_topics(item.get("key_topics")))
            topic_counts = Counter(all_topics)
            top_topics = [t for t, _ in topic_counts.most_common(5)]
            avg_quality = sum(item.get("quality_score", 5) for item in cluster_items) / len(cluster_items)
            clusters.append({
                "id": idx,
                "name": f"{content_type} Cluster",
                "description": f"{len(cluster_items)} {content_type.lower()} items",
                "content_count": len(cluster_items),
                "top_topics": top_topics,
                "average_quality": round(avg_quality, 1),
                "content_types": {content_type: len(cluster_items)},
                "items": [item["id"] for item in cluster_items],
            })
        return clusters

    # ──────────────────────────────────────────────────────────────
    # Related content
    # ──────────────────────────────────────────────────────────────

    async def get_related_content(self, content_id: int, limit: int = 10) -> List[Dict]:
        """Find semantically related content via pgvector."""
        try:
            from pgvector.asyncpg import register_vector
            async with self.pool.acquire() as conn:
                await register_vector(conn)
                source = await conn.fetchrow(
                    "SELECT embedding, title, summary FROM processed_content WHERE id = $1",
                    content_id,
                )
                if not source or source["embedding"] is None:
                    return []

                rows = await conn.fetch(
                    """WITH scored AS (
                           SELECT id, url, title, summary, content_type,
                                  1 - (embedding <=> $1) AS similarity
                           FROM processed_content
                           WHERE embedding IS NOT NULL AND id != $2
                       )
                       SELECT * FROM scored WHERE similarity > 0.3
                       ORDER BY similarity DESC LIMIT $3""",
                    list(source["embedding"]),
                    content_id,
                    limit,
                )

            return [
                {
                    "id": r["id"],
                    "url": r["url"],
                    "title": r["title"],
                    "summary": r["summary"],
                    "content_type": r["content_type"],
                    "similarity": round(float(r["similarity"]), 3),
                }
                for r in rows
            ]
        except Exception as e:
            logger.error(f"Related content failed: {e}")
            return []

    # ──────────────────────────────────────────────────────────────
    # Trending topics
    # ──────────────────────────────────────────────────────────────

    async def get_trending_topics(self, limit: int = 10) -> List[Dict]:
        """Get most frequent topics across all content."""
        try:
            rows = await self._fetch(
                "SELECT key_topics, quality_score FROM processed_content"
            )
            if not rows:
                return []

            topic_counts: Dict[str, Dict] = {}
            for row in rows:
                topics = self._parse_topics(row["key_topics"])
                quality = row["quality_score"] or 5
                for topic in topics:
                    if topic not in topic_counts:
                        topic_counts[topic] = {"count": 0, "total_quality": 0}
                    topic_counts[topic]["count"] += 1
                    topic_counts[topic]["total_quality"] += quality

            trending = [
                {
                    "topic": topic,
                    "count": data["count"],
                    "average_quality": round(data["total_quality"] / data["count"], 1),
                }
                for topic, data in topic_counts.items()
            ]
            trending.sort(key=lambda x: x["count"], reverse=True)
            return trending[:limit]
        except Exception as e:
            logger.error(f"Trending topics failed: {e}")
            return []

    # ──────────────────────────────────────────────────────────────
    # Export / Analytics
    # ──────────────────────────────────────────────────────────────

    async def export_data(self) -> Dict:
        """Export knowledge graph with enhanced semantic edges."""
        try:
            logger.info("📊 Exporting enhanced knowledge graph...")

            from pgvector.asyncpg import register_vector
            async with self.pool.acquire() as conn:
                await register_vector(conn)
                rows = await conn.fetch(
                    """SELECT id, title, summary, content_type, key_topics, quality_score,
                              url, visit_timestamp, processing_method, embedding
                       FROM processed_content"""
                )

            if not rows:
                return {
                    "nodes": [], "edges": [], "links": [],
                    "metadata": {
                        "total_nodes": 0, "total_edges": 0,
                        "exported_at": datetime.now().isoformat(),
                    },
                }

            items = [dict(r) for r in rows]
            nodes = []
            embeddings_map = {}

            for item in items:
                node = {
                    "id": str(item["id"]),
                    "name": item.get("title", f"Content {item['id']}"),
                    "title": item.get("title", f"Content {item['id']}"),
                    "type": item.get("content_type", "Unknown"),
                    "content_type": item.get("content_type", "Unknown"),
                    "quality": item.get("quality_score", 5),
                    "quality_score": item.get("quality_score", 5),
                    "summary": item.get("summary", ""),
                    "topics": self._parse_topics(item.get("key_topics")),
                    "key_topics": self._parse_topics(item.get("key_topics")),
                    "url": item.get("url", ""),
                    "visit_timestamp": item.get("visit_timestamp"),
                    "processing_method": item.get("processing_method", "unknown"),
                }
                nodes.append(node)
                emb = item.get("embedding")
                if emb is not None and len(emb) > 0:
                    embeddings_map[str(item["id"])] = list(emb)

            edges = []
            edge_id = 0
            for i, node1 in enumerate(nodes):
                topics1 = set(node1.get("topics", []))
                id1 = node1["id"]
                for j, node2 in enumerate(nodes[i + 1:], i + 1):
                    topics2 = set(node2.get("topics", []))
                    id2 = node2["id"]
                    shared_topics = topics1.intersection(topics2)

                    if len(shared_topics) >= 1:
                        similarity = len(shared_topics) / max(len(topics1), len(topics2), 1)
                        edges.append({
                            "id": f"edge_{edge_id}",
                            "source": id1, "target": id2,
                            "shared_topics": list(shared_topics),
                            "weight": len(shared_topics),
                            "similarity": round(similarity, 3),
                            "type": "topic",
                        })
                        edge_id += 1
                    elif id1 in embeddings_map and id2 in embeddings_map:
                        emb_similarity = self._cosine_similarity(
                            embeddings_map[id1], embeddings_map[id2]
                        )
                        if emb_similarity > 0.5:
                            edges.append({
                                "id": f"edge_{edge_id}",
                                "source": id1, "target": id2,
                                "shared_topics": [],
                                "weight": 1,
                                "similarity": round(emb_similarity, 3),
                                "type": "semantic",
                            })
                            edge_id += 1
                    elif (
                        node1.get("content_type") == node2.get("content_type")
                        and node1.get("content_type") != "Unknown"
                        and edge_id < len(nodes) * 2
                    ):
                        edges.append({
                            "id": f"edge_{edge_id}",
                            "source": id1, "target": id2,
                            "shared_topics": [],
                            "weight": 1,
                            "similarity": 0.3,
                            "type": "content_type",
                        })
                        edge_id += 1

            edges.sort(key=lambda x: x["similarity"], reverse=True)
            max_edges = min(len(edges), len(nodes) * 3)
            edges = edges[:max_edges]

            graph_data = {
                "nodes": nodes,
                "links": edges,
                "edges": edges,
                "metadata": {
                    "total_nodes": len(nodes),
                    "total_links": len(edges),
                    "exported_at": datetime.now().isoformat(),
                    "edge_types": {
                        "topic": len([e for e in edges if e["type"] == "topic"]),
                        "semantic": len([e for e in edges if e["type"] == "semantic"]),
                        "content_type": len([e for e in edges if e["type"] == "content_type"]),
                    },
                },
            }
            logger.info(f"✅ Exported graph: {len(nodes)} nodes, {len(edges)} edges")
            return graph_data

        except Exception as e:
            logger.error(f"Knowledge graph export failed: {e}", exc_info=True)
            return {
                "nodes": [], "edges": [], "links": [],
                "metadata": {
                    "total_nodes": 0, "total_edges": 0,
                    "exported_at": datetime.now().isoformat(),
                    "error": str(e),
                },
            }

    async def get_analytics(self) -> Dict:
        """Aggregate processing analytics."""
        try:
            rows = await self._fetch(
                "SELECT processing_method, content_type, quality_score, created_at FROM processed_content"
            )
            data = [dict(r) for r in rows]
            if not data:
                return {}

            total = len(data)
            by_method: Dict[str, int] = {}
            by_type: Dict[str, int] = {}
            quality_sum = 0

            for item in data:
                method = item.get("processing_method", "unknown")
                content_type = item.get("content_type", "unknown")
                quality = item.get("quality_score", 0)
                by_method[method] = by_method.get(method, 0) + 1
                by_type[content_type] = by_type.get(content_type, 0) + 1
                quality_sum += quality

            return {
                "total_content": total,
                "by_processing_method": by_method,
                "by_content_type": by_type,
                "average_quality": round(quality_sum / total, 2) if total > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Analytics failed: {e}")
            return {}

    async def health_check(self) -> Dict:
        """Health check."""
        db_connected = False
        error_message = None
        try:
            await self.ping()
            db_connected = True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            error_message = str(e)

        embedding_configured = self.st_embedder is not None
        status = "healthy" if db_connected and embedding_configured else "degraded"
        if error_message:
            status = "unhealthy"

        result = {
            "status": status,
            "database_connected": db_connected,
            "embedding_service_configured": embedding_configured,
            "timestamp": datetime.now().isoformat(),
        }
        if error_message:
            result["error"] = error_message
        return result

    # ──────────────────────────────────────────────────────────────
    # Utility
    # ──────────────────────────────────────────────────────────────

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        try:
            vec_a = np.array(a)
            vec_b = np.array(b)
            if len(vec_a) != len(vec_b) or len(vec_a) == 0:
                return 0.0
            dot_product = np.dot(vec_a, vec_b)
            norm_a = np.linalg.norm(vec_a)
            norm_b = np.linalg.norm(vec_b)
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return float(dot_product / (norm_a * norm_b))
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0


async def init_db(openai_api_key=None):
    """
    Initialize database.
    - Loads SentenceTransformer in a worker thread (avoids blocking the event loop).
    - Creates asyncpg connection pool with pgvector + JSONB codecs registered.
    - openai_api_key param kept for backwards compatibility with main.py call.
    """
    logger.info("⏳ Loading SentenceTransformer model (may take a moment)...")
    try:
        st_embedder = await asyncio.to_thread(SentenceTransformer, "all-MiniLM-L6-v2")
        logger.info("✅ SentenceTransformer loaded")
    except Exception as e:
        logger.warning(f"SentenceTransformer failed to load: {e} — embeddings unavailable")
        st_embedder = None

    logger.info(f"⏳ Connecting to PostgreSQL: {DATABASE_URL}")
    try:
        from pgvector.asyncpg import register_vector

        async def _init_conn(conn):
            await register_vector(conn)
            await conn.set_type_codec(
                "jsonb",
                encoder=json.dumps,
                decoder=json.loads,
                schema="pg_catalog",
                format="text",
            )

        pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10,
            init=_init_conn,
        )
        logger.info("✅ asyncpg pool created")
    except Exception as e:
        logger.error(f"Failed to create asyncpg pool: {e}")
        raise

    db = SimpleVectorDB(pool, st_embedder=st_embedder)
    health = await db.health_check()
    logger.info(f"Database status: {health['status']}")
    return db
