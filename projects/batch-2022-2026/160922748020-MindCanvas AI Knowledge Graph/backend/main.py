# backend/main.py - Fixed RAG chatbot integration
"""
MindCanvas - Fixed Implementation with Working RAG Chatbot
Clean FastAPI backend with Supabase vector database and functional chat
"""

import asyncio
import httpx
import json
import os
import logging
import re
import hashlib
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
from collections import Counter

# Import the fixed RAG chatbot and Supabase DB
from rag_chatbot import RAGChatbot, ChatRequest, ChatResponse, ChatMessage
from supabase_db import SimpleVectorDB, ContentItem, init_db

# Configuration — load from .env file directly
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Simple settings
BATCH_SIZE = 10
MAX_CONTENT_LENGTH = 1500
MIN_CONTENT_LENGTH = 30

# Excluded domains
EXCLUDED_DOMAINS = {
    'google.com', 'bing.com', 'facebook.com', 'twitter.com', 'x.com',
    'instagram.com', 'linkedin.com', 'tiktok.com', 'reddit.com'
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global database and RAG chatbot
db: SimpleVectorDB = None
rag_chatbot: RAGChatbot = None

# In-memory cache for the graph export (avoids re-running expensive AI call on every fetch)
_graph_cache: dict = {"result": None, "ts": 0.0, "node_count": 0}
_GRAPH_CACHE_TTL = 600  # seconds (10 minutes)

# Models
class HistoryItem(BaseModel):
    url: str
    title: str
    lastVisitTime: float

class SearchRequest(BaseModel):
    query: str
    limit: int = 20

# Utility functions
def is_valid_url(url: str) -> bool:
    """Check if URL should be processed"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')
        
        if domain in EXCLUDED_DOMAINS:
            return False
        
        if not parsed.scheme in ['http', 'https']:
            return False
            
        return True
    except:
        return False

def get_content_hash(content: str) -> str:
    """Generate hash for content deduplication"""
    return hashlib.sha256(content[:500].encode()).hexdigest()[:16]

def clean_title(title: str) -> str:
    """Clean up page title"""
    if not title:
        return "Untitled"
    
    # Remove common suffixes
    for suffix in [' - Google Search', ' - Bing', ' | Facebook']:
        if title.endswith(suffix):
            title = title[:-len(suffix)]
    
    return title.strip()[:100] or "Untitled"

def calculate_quality_score(title: str, content: str, url: str) -> int:
    """Simple quality scoring 1-10"""
    score = 5  # Base score
    
    if len(title) > 10:
        score += 1
    if len(content) > 200:
        score += 1
    if len(content) > 500:
        score += 1
    if any(word in url.lower() for word in ['tutorial', 'guide', 'docs']):
        score += 1
    if len(content) < MIN_CONTENT_LENGTH:
        score -= 2
    
    return max(1, min(10, score))

# Content extraction
async def fetch_html(url: str) -> str:
    """Fetch HTML content from URL"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; MindCanvas/1.0)'
            })
            response.raise_for_status()
            return response.text
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return ""

def extract_content(html: str, url: str, title: str) -> Dict[str, str]:
    """Extract main content from HTML"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        # Try to find main content
        main_content = None
        for selector in ['article', 'main', '.content', '.post-content']:
            element = soup.select_one(selector)
            if element and len(element.get_text(strip=True)) > 50:
                main_content = element
                break
        
        if not main_content:
            main_content = soup.body or soup
        
        # Extract text
        content_text = main_content.get_text(separator=' ', strip=True)
        content_text = re.sub(r'\s+', ' ', content_text)
        
        if len(content_text) < MIN_CONTENT_LENGTH:
            return None
        
        return {
            'url': url,
            'title': clean_title(title),
            'content': content_text[:MAX_CONTENT_LENGTH],
            'domain': urlparse(url).netloc
        }
        
    except Exception as e:
        logger.error(f"Content extraction failed for {url}: {e}")
        return None

# LLM Processing
class LLMProcessor:
    def __init__(self):
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    
    async def process_content(self, content_items: List[Dict]) -> List[Dict]:
        """Process content with LLM in batches to minimise API calls."""
        results = []
        for i in range(0, len(content_items), BATCH_SIZE):
            batch = content_items[i:i + BATCH_SIZE]
            try:
                batch_results = await self._process_batch(batch)
                results.extend(batch_results)
            except Exception as e:
                logger.error(f"Batch {i//BATCH_SIZE + 1} failed: {e}")
                results.extend([self._basic_process(item) for item in batch])
        return results

    async def _process_batch(self, batch: List[Dict]) -> List[Dict]:
        """Send a whole batch to OpenAI in one call and parse the JSON array response."""
        # Truncate content per item so we stay within token limits
        items_text = ""
        for idx, item in enumerate(batch, 1):
            snippet = item['content'][:400].replace('\n', ' ')
            items_text += (
                f"\n--- Item {idx} ---\n"
                f"URL: {item['url']}\n"
                f"Title: {item['title']}\n"
                f"Content: {snippet}\n"
            )

        prompt = f"""Analyze each webpage below and return a JSON object with an "items" array — one entry per webpage, in the same order.

{items_text}

Return a JSON object in this exact shape:
{{
  "items": [
    {{
      "title": "cleaned title",
      "summary": "2-3 sentence summary",
      "content_type": "Article|Tutorial|Documentation|News|Blog",
      "key_topics": ["topic1", "topic2", "topic3"]
    }}
  ]
}}

The "items" array must have exactly {len(batch)} entries."""

        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4.1-nano-2025-04-14",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150 * len(batch),
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                raw = response.choices[0].message.content.strip()
                return self._parse_batch_response(batch, raw)
            except Exception as e:
                logger.warning(f"OpenAI batch failed: {e}")

        return [self._basic_process(item) for item in batch]

    def _parse_batch_response(self, batch: List[Dict], response: str) -> List[Dict]:
        """Parse a json_object response containing an 'items' array."""
        try:
            parsed_obj = json.loads(response)
            parsed = parsed_obj.get("items", [])
            if not isinstance(parsed, list):
                raise ValueError("'items' is not a list")
        except Exception as e:
            logger.error(f"Failed to parse batch LLM response: {e}")
            return [self._basic_process(item) for item in batch]

        results = []
        for i, item in enumerate(batch):
            if i < len(parsed):
                results.append(self._parse_llm_response(item, json.dumps(parsed[i]), 'openai'))
            else:
                logger.warning(f"Batch response missing item {i+1}, using basic fallback")
                results.append(self._basic_process(item))
        return results
    
    def _parse_llm_response(self, item: Dict, response: str, method: str) -> Dict:
        """Parse LLM JSON response"""
        try:
            # Clean JSON
            json_str = response.strip()
            if '```json' in json_str:
                json_str = json_str.split('```json')[1].split('```')[0]
            elif '{' in json_str and '}' in json_str:
                start = json_str.find('{')
                end = json_str.rfind('}') + 1
                json_str = json_str[start:end]
            
            parsed = json.loads(json_str)
            
            quality_score = calculate_quality_score(
                parsed.get('title', item['title']),
                item['content'],
                item['url']
            )
            
            return {
                'url': item['url'],
                'title': parsed.get('title', item['title'])[:100],
                'summary': parsed.get('summary', '')[:400],
                'content_type': parsed.get('content_type', 'Web Content'),
                'key_topics': parsed.get('key_topics', ['General'])[:3],
                'quality_score': quality_score,
                'processing_method': method,
                'content_hash': get_content_hash(item['content']),
                'content': item['content']
            }
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._basic_process(item)
    
    def _basic_process(self, item: Dict) -> Dict:
        """Basic processing without LLM"""
        # Detect content type from URL
        url_lower = item['url'].lower()
        if 'tutorial' in url_lower or 'guide' in url_lower:
            content_type = 'Tutorial'
        elif 'docs' in url_lower or 'documentation' in url_lower:
            content_type = 'Documentation'
        elif 'blog' in url_lower or 'article' in url_lower:
            content_type = 'Article'
        else:
            content_type = 'Web Content'
        
        # Extract basic topics
        content_lower = item['content'].lower()
        topics = []
        tech_terms = ['python', 'javascript', 'react', 'ai', 'machine learning']
        for term in tech_terms:
            if term in content_lower:
                topics.append(term.title())
        
        if not topics:
            topics = ['General']
        
        # Basic summary (first sentence or two)
        sentences = item['content'].split('.')[:2]
        summary = '. '.join(s.strip() for s in sentences if s.strip())[:200]
        
        quality_score = calculate_quality_score(item['title'], item['content'], item['url'])
        
        return {
            'url': item['url'],
            'title': item['title'],
            'summary': summary or f"Content from {item['domain']}",
            'content_type': content_type,
            'key_topics': topics[:3],
            'quality_score': quality_score,
            'processing_method': 'basic',
            'content_hash': get_content_hash(item['content']),
            'content': item['content']
        }

# Initialize components
llm_processor = LLMProcessor()

# Main processing function
async def process_urls(items: List[HistoryItem]) -> Dict[str, int]:
    """Process URLs and store in vector database"""
    
    # Filter valid URLs
    valid_items = [item for item in items if is_valid_url(item.url)]
    logger.info(f"Processing {len(valid_items)}/{len(items)} valid URLs")
    
    if not valid_items:
        return {"processed": 0, "total": len(items), "new": 0}
    
    # Check existing URLs
    new_items = []
    existing_count = 0
    
    for item in valid_items:
        try:
            if await db.url_exists(item.url):
                existing_count += 1
                continue
        except:
            pass
        new_items.append(item)
    
    if not new_items:
        return {"processed": existing_count, "total": len(items), "new": 0}
    
    logger.info(f"Processing {len(new_items)} new URLs")
    
    # Fetch and extract content
    content_items = []
    for item in new_items:
        html = await fetch_html(item.url)
        if html:
            extracted = extract_content(html, item.url, item.title)
            if extracted:
                extracted['visit_time'] = item.lastVisitTime
                content_items.append(extracted)
    
    logger.info(f"Extracted content from {len(content_items)} URLs")
    
    if not content_items:
        return {"processed": existing_count, "total": len(items), "new": 0}
    
    # Process with LLM
    processed_items = await llm_processor.process_content(content_items)
    
    # Store in database
    stored_count = 0
    for original_item, processed_item in zip(content_items, processed_items):
        try:
            content_item = ContentItem(
                url=processed_item['url'],
                title=processed_item['title'],
                summary=processed_item['summary'],
                content=processed_item['content'],
                content_type=processed_item['content_type'],
                key_topics=processed_item['key_topics'],
                quality_score=processed_item['quality_score'],
                processing_method=processed_item['processing_method'],
                visit_timestamp=datetime.fromtimestamp(original_item['visit_time'] / 1000.0),
                content_hash=processed_item['content_hash']
            )
            
            # Also generate and store embedding
            embedding = await db.generate_embedding(
                f"{content_item.title} {content_item.summary}", 
                use_openai=bool(OPENAI_API_KEY)
            )
            content_item.embedding = embedding
            
            success = await db.store_content(content_item)
            if success:
                stored_count += 1
            
        except Exception as e:
            logger.error(f"Failed to store {processed_item['url']}: {e}")
    
    logger.info(f"Stored {stored_count} items in vector database")
    
    return {
        "processed": stored_count + existing_count,
        "total": len(items),
        "new": stored_count,
        "existing": existing_count
    }

# Startup - Fixed deprecation warning
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db, rag_chatbot

    # Initialize database with OpenAI API key for embeddings
    try:
        db = await init_db(OPENAI_API_KEY)
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.warning("⚠️ Running without database — set SUPABASE_URL and SUPABASE_KEY in .env")
        db = None

    # Initialize RAG chatbot with better error handling
    try:
        rag_chatbot = RAGChatbot(db, OPENAI_API_KEY)
        logger.info("✅ RAG Chatbot initialized successfully")
    except Exception as e:
        logger.error(f"❌ RAG Chatbot initialization failed: {e}")
        rag_chatbot = None

    logger.info("✅ MindCanvas started")
    yield
    # Shutdown (if needed)

# Initialize app with lifespan
app = FastAPI(title="MindCanvas", version="1.0", lifespan=lifespan)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.post("/api/ingest")
async def ingest_history(items: List[HistoryItem]):
    """Process browser history URLs"""
    if not items:
        return {"status": "success", "processed": 0, "total": 0}
    
    try:
        results = await process_urls(items)
        # Invalidate graph cache so next fetch gets fresh AI clustering
        _graph_cache["result"] = None
        return {
            "status": "success",
            **results,
            "message": f"Processed {results['processed']} URLs ({results['new']} new)"
        }
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "processed": 0,
            "total": len(items)
        }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_knowledge_base(request: ChatRequest):
    """Chat with AI using knowledge base context"""
    try:
        if not rag_chatbot:
            return ChatResponse(
                response="I'm sorry, the AI assistant is currently unavailable. Please ensure OpenAI API key is configured.",
                sources=[],
                confidence=0.1,
                processing_time=0.0,
                tokens_used=0,
                conversation_id=""
            )
        
        response = await rag_chatbot.process_chat_request(request)
        return response
    except Exception as e:
        logger.error(f"Chat request failed: {e}")
        return ChatResponse(
            response=f"I encountered an error: {str(e)}. Please try again.",
            sources=[],
            confidence=0.1,
            processing_time=0.0,
            tokens_used=0,
            conversation_id=""
        )

@app.get("/api/chat/suggestions")
async def get_chat_suggestions(limit: int = 5):
    """Get suggested questions based on knowledge base"""
    try:
        if not rag_chatbot:
            return {
                "suggestions": [
                    "What topics have I been learning about?",
                    "Can you help me explore my knowledge?",
                    "What would you recommend I learn next?",
                    "Show me my recent browsing patterns"
                ],
                "timestamp": datetime.now().isoformat()
            }
        
        suggestions = await rag_chatbot.get_suggested_questions(limit)
        return {
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        return {
            "suggestions": ["How can I help you today?"],
            "timestamp": datetime.now().isoformat()
        }


@app.post("/api/chat/insights")
async def get_conversation_insights(conversation_history: List[ChatMessage]):
    """Analyze conversation for insights"""
    if not rag_chatbot:
        raise HTTPException(status_code=503, detail="RAG chatbot not available")
    
    try:
        insights = await rag_chatbot.get_conversation_insights(conversation_history)
        return {
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to analyze conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/context/{query}")
async def get_chat_context(query: str, limit: int = 5, threshold: float = 0.3):
    """Get relevant context for a query (for debugging/preview)"""
    if not rag_chatbot:
        raise HTTPException(status_code=503, detail="RAG chatbot not available")
    
    query_preview = query[:80] + "..." if len(query) > 80 else query
    logger.info(f"API: Getting chat context for query: \"{query_preview}\"")
    try:
        # Corrected: Use semantic_search instead of non-existent get_documents_by_query
        # The results from semantic_search are already dictionaries, not Document objects
        # unless you have a LangChain vector store wrapper.
        # Assuming db.semantic_search returns a list of dicts as defined in SimpleVectorDB
        docs = await db.semantic_search(query, limit, threshold)
        
        formatted_context = []
        for doc in docs:
            formatted_context.append({
                "title": doc.metadata.get("title", "Unknown"),
                "summary": doc.metadata.get("summary", ""),
                "content_type": doc.metadata.get("content_type", "Unknown"),
                "quality_score": doc.metadata.get("quality_score", 0),
                "similarity": round(doc.metadata.get("similarity", 0), 3),
                "url": doc.metadata.get("url", ""),
                # Assuming 'summary' can act as a preview, or you might need to fetch full content if not already in 'doc'
                "content_preview": doc.get("summary", "")[:200] + "..." 
            })
        
        return {
            "query": query,
            "context_items": formatted_context,
            "total_found": len(formatted_context)
        }
    except Exception as e:
        logger.error(f"Failed to get context for query \"{query_preview}\": {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/health")
async def chat_health_check():
    """Check chatbot system health"""
    openai_configured = bool(OPENAI_API_KEY)
    rag_initialized = rag_chatbot is not None
    db_connection_ok = False
    
    # Lightweight DB check
    if db:
        try:
            await db.ping()
            db_connection_ok = True
        except Exception as e:
            logger.error(f"Chat health DB check failed: {e}")
            db_connection_ok = False

    status = "healthy"
    components_status = {
        "openai_api_configured": "ok" if openai_configured else "warning",
        "rag_chatbot_initialized": "ok" if rag_initialized else "error",
        "database_connection": "ok" if db_connection_ok else "error",
    }

    # Determine overall status
    if not db_connection_ok or not rag_initialized: # Critical components
        status = "unhealthy"
    elif not all(s == "ok" for s in components_status.values()):
         # If any component is not 'ok' but critical ones are fine, it's 'degraded'
        if any(s == "error" for s in components_status.values()): # if any error, then unhealthy
            status = "unhealthy"
        else: # only warnings
            status = "degraded"
            
    return {
        "status": status,
        "components": components_status,
        "timestamp": datetime.now().isoformat()
    }
    
@app.get("/api/content")
async def get_content(limit: int = 100):
    """Get processed content"""
    try:
        rows = await db.get_content_list(limit)
        content = []
        for row in rows:
            content.append({
                "id": row['id'],
                "url": row['url'],
                "title": row['title'],
                "description": row['summary'],
                "content_type": row['content_type'],
                "key_details": row['key_topics'] or [],
                "quality_score": row['quality_score'],
                "processing_method": row['processing_method']
            })

        return {"content": content, "total": len(content)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search/semantic")
async def semantic_search(request: SearchRequest):
    """Vector similarity search"""
    try:
        results = await db.semantic_search(request.query, request.limit)
        return {
            "results": results,
            "total": len(results),
            "query": request.query,
            "search_type": "semantic"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def text_search(q: str, limit: int = 50):
    """Basic text search"""
    try:
        rows = await db.text_search(q, limit)
        results = []
        for row in rows:
            results.append({
                "id": row['id'],
                "url": row['url'],
                "title": row['title'],
                "description": row['summary'],
                "content_type": row['content_type'],
                "key_details": row['key_topics'] or [],
                "quality_score": row['quality_score']
            })

        return {
            "results": results,
            "total": len(results),
            "query": q,
            "search_type": "text"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/related/{content_id}")
async def get_related(content_id: int, limit: int = 10):
    """Find related content"""
    try:
        results = await db.get_related_content(content_id, limit)
        return {
            "related_content": results,
            "total": len(results),
            "source_id": content_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cluster")
async def cluster_content():
    """Get content clusters - Fixed to use GET method"""
    try:
        clusters = await db.cluster_content()
        return {
            "clusters": clusters,
            "total": len(clusters),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Clustering failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trending")
async def get_trending(limit: int = 15):
    """Get trending topics"""
    try:
        trending = await db.get_trending_topics(limit)
        return {
            "trending_topics": trending,
            "total": len(trending)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
async def get_analytics():
    """Get analytics"""
    try:
        analytics = await db.get_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommendations")
async def get_recommendations(limit: int = 10):
    """Get content recommendations"""
    try:
        rows = await db.get_recommendations(limit)
        recommendations = []
        for row in rows:
            recommendations.append({
                "id": row['id'],
                "url": row['url'],
                "title": row['title'],
                "summary": row['summary'],
                "content_type": row['content_type'],
                "quality_score": row['quality_score']
            })

        return {
            "recommendations": recommendations,
            "total": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _ai_graph_structure(items: list) -> dict:
    """
    Single AI call that produces BOTH cluster assignments AND edges.
    Returns {
        "id_to_cluster":  { str(id): (cluster_name, cluster_int_id) },
        "edges":          [ {"source": str, "target": str, "reason": str} ]
    }
    """
    if not OPENAI_API_KEY:
        logger.warning("No OpenAI API key — cannot use AI graph structure")
        return {"id_to_cluster": {}, "edges": []}

    node_descriptions = []
    for item in items:
        topics = item.get('key_topics') or []
        summary = (item.get('summary') or '')[:120].strip()
        node_descriptions.append({
            "id": str(item['id']),
            "title": item.get('title', ''),
            "summary": summary,
            "topics": topics[:5],
            "type": item.get('content_type', ''),
        })

    prompt = f"""You are a knowledge graph architect. Given these content nodes, decide:
1. How to cluster them into meaningful semantic groups.
2. Which pairs of nodes should be connected by an edge.

CLUSTERING RULES:
- Create 3–12 clusters based on distinct themes.
- Cluster name: short label (2–4 words), e.g. "Python Programming", "Machine Learning".
- Every node must be in exactly one cluster.
- Base decisions on title + summary, not just keywords.
- Closely related nodes (e.g. two Python tutorials) MUST share a cluster.

EDGE RULES:
- Only connect nodes that share a meaningful semantic relationship.
- Aim for 2–4 edges per node on average — not too sparse, not a hairball.
- Prefer connecting nodes within the same cluster, but cross-cluster edges are fine when genuinely related.
- Do NOT add edges just because nodes share a generic topic like "programming" or "learning".
- Each edge must have a short reason (5–10 words).

Nodes:
{json.dumps(node_descriptions, indent=2)}

Respond with a single JSON object:
{{
  "clusters": [
    {{
      "name": "Cluster Name",
      "node_ids": ["1", "5", "12"]
    }}
  ],
  "edges": [
    {{
      "source": "1",
      "target": "5",
      "reason": "Both cover Python data structures"
    }}
  ]
}}"""

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4.1-mini-2025-04-14",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=4000,
        )

        result = json.loads(response.choices[0].message.content)
        clusters_list = result.get("clusters", [])
        edges_list    = result.get("edges", [])

        if not clusters_list:
            logger.warning("AI graph structure returned empty clusters")
            return {"id_to_cluster": {}, "edges": []}

        id_to_cluster = {}
        for idx, cluster in enumerate(clusters_list, 1):
            name = cluster.get("name", f"Cluster {idx}")
            for node_id in cluster.get("node_ids", []):
                id_to_cluster[str(node_id)] = (name, idx)

        # Validate edges — only keep pairs where both IDs exist
        valid_ids = set(id_to_cluster.keys())
        valid_edges = [
            e for e in edges_list
            if str(e.get("source")) in valid_ids and str(e.get("target")) in valid_ids
               and str(e.get("source")) != str(e.get("target"))
        ]

        logger.info(
            f"✅ AI graph (gpt-4.1-mini): {len(clusters_list)} clusters, "
            f"{len(id_to_cluster)} nodes, {len(valid_edges)} edges"
        )
        return {"id_to_cluster": id_to_cluster, "edges": valid_edges}

    except Exception as e:
        logger.error(f"AI graph structure failed: {e}")
        return {"id_to_cluster": {}, "edges": []}


def _normalize_topic(topic: str, all_topics_lower: list, first_word_counts: Counter) -> str:
    """
    Normalize a topic to its canonical base form.
    Strategy 1: Find the shortest topic that is a word-boundary prefix.
      "Python Programming" → "python" (if "python" exists in topics list)
    Strategy 2: If no prefix match, and the first word appears in 2+ topics,
      normalize to the first word alone (handles "SAP Basis"/"SAP Skills" → "sap").
    """
    t_lower = topic.lower().strip()
    # Strategy 1: prefix match with an existing shorter topic
    for candidate in sorted(all_topics_lower, key=len):
        if candidate == t_lower:
            continue
        if t_lower.startswith(candidate):
            rest = t_lower[len(candidate):]
            if rest and rest[0] in (' ', '-', '_', '/'):
                return candidate
    # Strategy 2: first-word collapse (e.g. "sap basis", "sap skills" → "sap")
    words = t_lower.split()
    if words and first_word_counts[words[0]] >= 2 and len(words) > 1:
        return words[0]
    return t_lower


def _topic_specificity_clustering(items: list) -> dict:
    """
    Smart topic-based clustering when embeddings are unavailable.
    Step 1: Normalize topics to canonical forms so "Python Programming" and
            "Python Data Types" both map to "Python".
    Step 2: Use frequency analysis — topics appearing in ≥2 nodes form cluster seeds.
    Step 3: Assign each node to its most specific (least globally common) seed topic.
    Returns dict: str(id) -> (cluster_name, cluster_int_id)
    """
    n = len(items)
    if n == 0:
        return {}

    # Collect all unique topics (lowercase)
    all_raw_topics = []
    for item in items:
        for t in (item.get('key_topics') or []):
            if t:
                all_raw_topics.append(t.strip())
    all_topics_lower = sorted(set(t.lower() for t in all_raw_topics), key=len)

    # Count how many topics share each first word (for Strategy 2 normalization)
    first_word_counts: Counter = Counter()
    for t in all_topics_lower:
        words = t.split()
        if words:
            first_word_counts[words[0]] += 1

    # Build normalization map: original_lower → canonical_lower
    norm_map = {}
    for t in all_raw_topics:
        t_lower = t.lower().strip()
        if t_lower not in norm_map:
            norm_map[t_lower] = _normalize_topic(t, all_topics_lower, first_word_counts)

    # Build a display name map: canonical_lower → best display name (title-cased original)
    display_name = {}
    for t in sorted(all_raw_topics, key=len):  # prefer shorter originals for display
        canonical = norm_map[t.lower().strip()]
        if canonical not in display_name:
            display_name[canonical] = t.title()

    # Count frequency using CANONICAL topics
    topic_counts = Counter()
    for item in items:
        seen = set()
        for t in (item.get('key_topics') or []):
            canonical = norm_map.get(t.lower().strip(), t.lower().strip())
            if canonical not in seen:
                topic_counts[canonical] += 1
                seen.add(canonical)

    # Topics that form meaningful groups: appear in ≥2 nodes but <70% of nodes
    min_support = 2
    max_support = max(2, int(n * 0.70))
    group_topics = {t for t, c in topic_counts.items() if min_support <= c <= max_support}

    # Assign each node to its most SPECIFIC group topic (least globally common)
    id_to_cluster = {}
    for item in items:
        sid = str(item['id'])
        node_canonicals = []
        seen = set()
        for t in (item.get('key_topics') or []):
            canonical = norm_map.get(t.lower().strip(), t.lower().strip())
            if canonical in group_topics and canonical not in seen:
                node_canonicals.append(canonical)
                seen.add(canonical)

        if node_canonicals:
            # Most representative = highest global frequency among node's group-forming topics
            # This keeps Python nodes in "Python" rather than drifting to generic "Software Development"
            best = max(node_canonicals, key=lambda t: (topic_counts[t], t))
            id_to_cluster[sid] = best
        else:
            # No group-forming topic: use first canonical topic or content_type
            raw = item.get('key_topics') or []
            if raw:
                id_to_cluster[sid] = norm_map.get(raw[0].lower().strip(), raw[0].lower().strip())
            else:
                id_to_cluster[sid] = item.get('content_type', 'General').lower()

    # Merge singleton clusters into best alternative group topic
    cluster_sizes = Counter(id_to_cluster.values())
    singletons = {c for c, sz in cluster_sizes.items() if sz == 1}
    if singletons:
        for item in items:
            sid = str(item['id'])
            if id_to_cluster.get(sid) in singletons:
                node_canonicals = []
                seen = set()
                for t in (item.get('key_topics') or []):
                    canonical = norm_map.get(t.lower().strip(), t.lower().strip())
                    if canonical in group_topics and canonical not in seen:
                        node_canonicals.append(canonical)
                        seen.add(canonical)
                # Merge singleton into the most representative alternative group topic
                alternatives = [t for t in node_canonicals if t != id_to_cluster[sid]]
                if alternatives:
                    id_to_cluster[sid] = max(alternatives, key=lambda t: (topic_counts[t], t))

    # Assign integer IDs to canonical cluster names
    unique_clusters = sorted(set(id_to_cluster.values()))
    cluster_name_to_id = {name: i + 1 for i, name in enumerate(unique_clusters)}

    return {
        sid: (display_name.get(name, name.title()), cluster_name_to_id[name])
        for sid, name in id_to_cluster.items()
    }


@app.get("/api/reindex")
async def reindex_embeddings():
    """Backfill embeddings for all existing nodes that have none (needed for DBSCAN clustering)"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        items_to_reindex = await db.get_all_for_reindex()
        if not items_to_reindex:
            return {"reindexed": 0, "message": "No content found"}

        updated = 0
        failed = 0
        for item in items_to_reindex:
            try:
                text = f"{item.get('title', '')} {item.get('summary', '')}"
                embedding = await db.generate_embedding(text, use_openai=bool(OPENAI_API_KEY))
                if embedding:
                    await db.update_embedding(item['id'], embedding)
                    updated += 1
            except Exception as e:
                logger.warning(f"Failed to embed node {item['id']}: {e}")
                failed += 1

        logger.info(f"✅ Reindexed {updated} nodes, {failed} failed")
        return {"reindexed": updated, "failed": failed,
                "message": f"Embeddings generated for {updated} nodes. Refresh the graph to see improved clustering."}
    except Exception as e:
        logger.error(f"Reindex failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-graph/export")
async def export_knowledge_graph(force: bool = False):
    """Export knowledge graph with AI-based semantic clustering (DBSCAN on embeddings, topic fallback)"""
    import time
    try:
        # Get all content from database
        items = await db.get_all_for_export()

        if not items:
            return {
                "nodes": [],
                "links": [],
                "metadata": {
                    "total_nodes": 0,
                    "total_links": 0,
                    "exported_at": datetime.now().isoformat()
                }
            }

        # ── Cache check: return cached result if fresh and node count unchanged ──
        now = time.time()
        cached = _graph_cache["result"]
        if (
            not force
            and cached is not None
            and (now - _graph_cache["ts"]) < _GRAPH_CACHE_TTL
            and _graph_cache["node_count"] == len(items)
        ):
            logger.info(f"📦 Returning cached graph ({len(items)} nodes, age={(now - _graph_cache['ts']):.0f}s)")
            return cached

        # ── 1. AI produces clusters + edges in one call ───────────────────────────
        id_to_cluster = {}
        id_to_cluster_id = {}
        ai_edges = []
        used_method = "topic_specificity"

        try:
            ai_result = await _ai_graph_structure(items)
            ai_id_to_cluster = ai_result.get("id_to_cluster", {})
            if ai_id_to_cluster and len(ai_id_to_cluster) >= len(items) * 0.5:
                for sid, (cname, cid) in ai_id_to_cluster.items():
                    id_to_cluster[sid] = cname
                    id_to_cluster_id[sid] = cid
                ai_edges = ai_result.get("edges", [])
                used_method = "ai_gpt4.1-mini"
                logger.info(f"✅ AI graph: {len(set(id_to_cluster.values()))} clusters, {len(ai_edges)} edges")
        except Exception as e:
            logger.warning(f"AI graph structure failed: {e}")

        # ── 2. Fallback clustering (no AI edges) ──────────────────────────────────
        if used_method == "topic_specificity":
            topic_result = _topic_specificity_clustering(items)
            for sid, (cname, cid) in topic_result.items():
                id_to_cluster[sid] = cname
                id_to_cluster_id[sid] = cid
            logger.info(f"✅ Topic clustering fallback: {len(set(id_to_cluster.values()))} clusters")

        # Fill any nodes the AI skipped
        if used_method.startswith("ai_"):
            unassigned = [item for item in items if str(item['id']) not in id_to_cluster]
            if unassigned:
                fallback = _topic_specificity_clustering(unassigned)
                max_id = max(id_to_cluster_id.values()) if id_to_cluster_id else 0
                for sid, (cname, cid) in fallback.items():
                    id_to_cluster[sid] = cname
                    id_to_cluster_id[sid] = cid + max_id

        # ── 3. Build nodes ────────────────────────────────────────────────────────
        nodes = []
        for item in items:
            sid = str(item['id'])
            topics = item.get('key_topics') or []
            cluster_name = id_to_cluster.get(sid) or (topics[0].title() if topics else 'General')
            cluster_id = id_to_cluster_id.get(sid, 0)
            node = {
                "id": sid,
                "name": item.get('title', f"Content {item['id']}"),
                "title": item.get('title', f"Content {item['id']}"),
                "type": item.get('content_type', 'Unknown'),
                "content_type": item.get('content_type', 'Unknown'),
                "quality": item.get('quality_score', 5),
                "quality_score": item.get('quality_score', 5),
                "summary": item.get('summary', ''),
                "description": item.get('summary', ''),
                "topics": topics,
                "key_topics": topics,
                "url": item.get('url', ''),
                "processing_method": item.get('processing_method', 'unknown'),
                "visit_timestamp": item.get('visit_timestamp'),
                "cluster": cluster_name,
                "cluster_id": cluster_id,
                "cluster_method": used_method,
            }
            nodes.append(node)

        # ── 4. Build edge list from AI output ─────────────────────────────────────
        node_cluster_map = {n["id"]: n["cluster"] for n in nodes}
        seen_pairs = set()
        links = []
        link_id = 0

        if ai_edges:
            # Use AI-generated edges directly
            for e in ai_edges:
                src, tgt = str(e.get("source")), str(e.get("target"))
                pair = (min(src, tgt), max(src, tgt))
                if pair in seen_pairs or src not in node_cluster_map or tgt not in node_cluster_map:
                    continue
                seen_pairs.add(pair)
                same = node_cluster_map[src] == node_cluster_map[tgt]
                links.append({
                    "id": f"link_{link_id}",
                    "source": src,
                    "target": tgt,
                    "shared_topics": [e.get("reason", "")],
                    "weight": 2 if same else 1,
                    "similarity": 0.8 if same else 0.5,
                    "same_cluster": same,
                })
                link_id += 1
        else:
            # Fallback: connect same-cluster pairs (topic_specificity path, no AI)
            cluster_to_nodes = {}
            for node in nodes:
                cluster_to_nodes.setdefault(node["cluster"], []).append(node["id"])
            for nids in cluster_to_nodes.values():
                for ii, nid1 in enumerate(nids):
                    for nid2 in nids[ii+1:]:
                        pair = (min(nid1, nid2), max(nid1, nid2))
                        if pair not in seen_pairs:
                            seen_pairs.add(pair)
                            links.append({
                                "id": f"link_{link_id}",
                                "source": nid1, "target": nid2,
                                "shared_topics": [], "weight": 1,
                                "similarity": 0.3, "same_cluster": True,
                            })
                            link_id += 1

        graph_data = {
            "nodes": nodes,
            "links": links,
            "edges": links,  # Also provide as 'edges' for compatibility
            "metadata": {
                "total_nodes": len(nodes),
                "total_links": len(links),
                "exported_at": datetime.now().isoformat(),
                "connection_types": ["topic_similarity", "content_type"],
                "min_similarity": min([link['similarity'] for link in links]) if links else 0,
                "max_similarity": max([link['similarity'] for link in links]) if links else 0
            }
        }
        
        # Store in cache
        _graph_cache["result"] = graph_data
        _graph_cache["ts"] = time.time()
        _graph_cache["node_count"] = len(items)

        logger.info(f"Exported knowledge graph: {len(nodes)} nodes, {len(links)} links")
        return graph_data
        
    except Exception as e:
        logger.error(f"Knowledge graph export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Get processing statistics"""
    try:
        analytics = await db.get_analytics()
        return {
            "total_content": analytics.get("total_content", 0),
            "by_processing_method": analytics.get("by_processing_method", {}),
            "by_content_type": analytics.get("by_content_type", {}),
            "quality_distribution": {},
            "average_quality": analytics.get("average_quality", 0),
            "database": "supabase_vector"
        }
    except Exception as e:
        return {
            "total_content": 0,
            "error": str(e),
            "database": "supabase_vector"
        }

@app.delete("/api/reset")
async def reset_database():
    """Reset all data"""
    try:
        await db.delete_all()
        _graph_cache["result"] = None  # invalidate cache
        return {
            "status": "success",
            "message": "Database reset successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/load-sample-data")
async def load_sample_data():
    """Load bundled sample data (same as running load_sample_data.ps1)"""
    import pathlib
    sample_path = pathlib.Path(__file__).parent / "sample" / "sample_data.json"
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="sample_data.json not found")
    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        items = [HistoryItem(**entry) for entry in raw]
        # Reuse the existing ingest endpoint logic
        result = await ingest_history(items)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Check system health"""
    try:
        health = await db.health_check()
        return health
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Mount static files for frontend
try:
    # Point to sibling directory ../frontend/build
    frontend_build_dir = os.path.join(os.path.dirname(BASE_DIR), "frontend", "build")
    if os.path.exists(frontend_build_dir):
        app.mount("/static", StaticFiles(directory=frontend_build_dir), name="static")
        logger.info(f"✅ Static files mounted from {frontend_build_dir}")
    else:
        logger.warning(f"⚠️ Static files directory not found at: {frontend_build_dir}")
except Exception as e:
    logger.warning(f"⚠️ Static files not mounted: {e}")

@app.get("/")
async def root():
    return {
        "message": "MindCanvas - AI Knowledge Graph with RAG Chatbot",
        "version": "1.0",
        "features": [
            "vector_search",
            "content_clustering", 
            "dual_llm_processing",
            "supabase_database",
            "rag_chatbot"
        ],
        "endpoints": {
            "ingest": "POST /api/ingest",
            "search": "POST /api/search/semantic",
            "content": "GET /api/content",
            "chat": "POST /api/chat",
            "chat_health": "GET /api/chat/health"
        },
        "chat_status": "available" if rag_chatbot else "unavailable"
    }

if __name__ == "__main__":
    import uvicorn
    # Use different port if 8000 is blocked
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=False)