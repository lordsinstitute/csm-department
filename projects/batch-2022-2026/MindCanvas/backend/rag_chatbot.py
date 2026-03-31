"""
Production-Ready RAG Chatbot for MindCanvas
Implements intelligent Q&A with proper error handling and validation
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from fastapi import HTTPException
from pydantic import BaseModel, Field, validator

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

# Constants
MAX_CONTEXT_ITEMS = 10
MIN_SIMILARITY_THRESHOLD = 0.1
MAX_CONVERSATION_HISTORY = 20
VALID_OPENAI_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1-mini-2025-04-14",
    "gpt-4.1-nano-2025-04-14",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
]

# -----------------------------
# Pydantic Models with Validation
# -----------------------------

class ChatMessage(BaseModel):
    """A single message in a conversation."""
    role: str
    content: str
    timestamp: Optional[datetime] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant', 'system']:
            raise ValueError('Role must be user, assistant, or system')
        return v
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        if len(v) > 10000:
            raise ValueError('Content too long (max 10000 characters)')
        return v.strip()


class ChatRequest(BaseModel):
    """An incoming chat request from the client."""
    message: str
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    use_rag: bool = True
    max_context_items: int = Field(default=5, ge=1, le=MAX_CONTEXT_ITEMS)
    similarity_threshold: float = Field(default=0.3, ge=MIN_SIMILARITY_THRESHOLD, le=1.0)
    conversation_id: Optional[str] = None
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v) > 5000:
            raise ValueError('Message too long (max 5000 characters)')
        return v.strip()
    
    @validator('conversation_history')
    def validate_history(cls, v):
        if len(v) > MAX_CONVERSATION_HISTORY:
            return v[-MAX_CONVERSATION_HISTORY:]
        return v


class ChatResponse(BaseModel):
    """A chat response sent back to the client."""
    response: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.0
    processing_time: float = 0.0
    tokens_used: int = 0
    conversation_id: str = ""
    rag_used: bool = False
    context_count: int = 0


@dataclass
class KnowledgeContext:
    """Internal representation of retrieved knowledge."""
    content: str
    title: str
    url: str
    content_type: str
    quality_score: float
    similarity: float
    summary: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'title': self.title,
            'url': self.url,
            'content_type': self.content_type,
            'quality_score': self.quality_score,
            'similarity': self.similarity,
            'summary': self.summary
        }


# -----------------------------
# Lightweight Conversation Memory
# -----------------------------

class _SimpleChatHistory:
    """Minimal, dependency-free message history holder."""
    def __init__(self, max_messages: int = MAX_CONVERSATION_HISTORY) -> None:
        self.messages: List[Any] = []
        self.max_messages = max_messages

    def add_user_message(self, content: str) -> None:
        self.messages.append(HumanMessage(content=content))
        self._trim_history()

    def add_ai_message(self, content: str) -> None:
        self.messages.append(AIMessage(content=content))
        self._trim_history()
    
    def _trim_history(self) -> None:
        """Keep only recent messages to prevent context overflow."""
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def clear(self) -> None:
        self.messages.clear()


class _SimpleConversationMemory:
    """Lightweight conversation memory manager."""
    def __init__(self) -> None:
        self.chat_memory = _SimpleChatHistory()

    def clear(self) -> None:
        self.chat_memory.clear()


# -----------------------------
# Core RAG Chatbot
# -----------------------------

class RAGChatbot:
    """Production-ready RAG chatbot with proper error handling."""
    
    def __init__(self, db, openai_key: Optional[str] = None):
        if not openai_key:
            raise ValueError("OpenAI API key is required for RAG chatbot")
        
        self.db = db
        self.openai_api_key = openai_key
        
        # Get model from environment with validation
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if model_name not in VALID_OPENAI_MODELS:
            logger.warning(f"Model '{model_name}' not in validated list, using gpt-4o-mini")
            model_name = "gpt-4o-mini"
        
        try:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0.3,
                api_key=openai_key,
                request_timeout=30,
                max_retries=2
            )
            logger.info(f"✅ LLM initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            raise

        # System prompts
        self.non_rag_prompt = """You are MindCanvas AI, a helpful assistant for exploring personal knowledge.

The user asked a question, but no relevant documents were found in their knowledge base.

Guidelines:
1. Answer based on general knowledge since no specific information was found in their MindCanvas.
2. DO NOT invent sources or pretend to have context from their knowledge base.
3. Be conversational and helpful.
4. Suggest adding related content to their knowledge base for better answers in the future."""

        self.rag_system_prompt = """You are MindCanvas AI, an intelligent assistant that helps users explore and understand their personal knowledge base.

GUIDELINES:
1. **Primary Source**: Prefer information from the 'Context' section when it is relevant and helpful.
2. **Cite Sources**: When drawing from the context, cite sources as [Source: Title].
3. **Supplement with Knowledge**: If the context is partial or missing details, you may supplement with your general knowledge — but clearly distinguish what comes from the user's saved content vs. your own knowledge.
4. **Be a Synthesizer**: Connect ideas across sources, summarize findings, and provide actionable insights.
5. **Be Honest**: If nothing relevant is in the context, say so, but still try to answer helpfully using your general knowledge.
6. **Be Conversational**: Maintain a helpful, concise, and engaging tone.

The context from their knowledge base follows:"""

        # Conversation memories
        self.conversation_memories: Dict[str, _SimpleConversationMemory] = {}
        
        logger.info("✅ RAG Chatbot initialized successfully")

    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """Main chat processing pipeline with proper error handling."""
        start_time = datetime.now()
        conversation_id = request.conversation_id or f"chat_{int(start_time.timestamp())}"
        
        try:
            # Initialize or get memory
            if conversation_id not in self.conversation_memories:
                self.conversation_memories[conversation_id] = _SimpleConversationMemory()
            
            memory = self.conversation_memories[conversation_id]
            
            # Sync conversation history
            if request.conversation_history:
                memory.clear()
                for msg in request.conversation_history[-MAX_CONVERSATION_HISTORY:]:
                    if msg.role == "user":
                        memory.chat_memory.add_user_message(msg.content)
                    elif msg.role == "assistant":
                        memory.chat_memory.add_ai_message(msg.content)
            
            # RAG Retrieval
            context_items: List[KnowledgeContext] = []
            rag_used = False
            
            if request.use_rag:
                logger.info(f"RAG: Retrieving context for query: {request.message[:80]}")
                context_items = await self._retrieve_relevant_context(
                    request.message,
                    request.max_context_items,
                    request.similarity_threshold,
                )
                rag_used = len(context_items) > 0
                logger.info(f"RAG: Retrieved {len(context_items)} context items")
            
            # Generate response
            response_text, tokens_used, confidence = await self._generate_response(
                request.message,
                context_items,
                memory,
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ChatResponse(
                response=response_text,
                sources=[self._format_source(item) for item in context_items],
                confidence=confidence,
                processing_time=processing_time,
                tokens_used=tokens_used,
                conversation_id=conversation_id,
                rag_used=rag_used,
                context_count=len(context_items)
            )
            
        except Exception as e:
            logger.error(f"❌ Chat processing failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

    async def _retrieve_relevant_context(
        self,
        query: str,
        max_items: int,
        threshold: float,
    ) -> List[KnowledgeContext]:
        """Retrieve relevant content — tries vector search first, falls back to keyword search."""
        try:
            results = await self.db.semantic_search(query, max_items, threshold)
            context_items: List[KnowledgeContext] = []

            for result in results:
                try:
                    # Use summary directly — avoid an extra N+1 query for 'content'
                    # which is often empty or not stored in the DB.
                    summary = result.get("summary", "") or ""
                    content = summary  # summary is reliable; full content column may be empty

                    if not content or len(content) < 5:
                        logger.warning(f"Skipping item {result['id']} — no usable text")
                        continue

                    context_items.append(KnowledgeContext(
                        content=content,
                        title=result.get("title", "Untitled"),
                        url=result.get("url", ""),
                        content_type=result.get("content_type", "Unknown"),
                        quality_score=float(result.get("quality_score", 0.0)),
                        similarity=float(result.get("similarity", 0.0)),
                        summary=summary,
                    ))
                except Exception as e:
                    logger.error(f"Failed to process result {result.get('id')}: {e}")
                    continue

            if context_items:
                logger.info(f"Vector search: {len(context_items)} context items")
                return context_items

            # ── Keyword fallback ───────────────────────────────────────────────────
            # Vector search returned nothing (no embeddings or dimension mismatch).
            # Score all stored content by keyword overlap so the AI always has context.
            logger.info("Vector search empty — trying keyword fallback")
            return await self._keyword_fallback(query, max_items)

        except Exception as e:
            logger.error(f"Context retrieval failed: {e}", exc_info=True)
            return await self._keyword_fallback(query, max_items)

    async def _keyword_fallback(self, query: str, max_items: int) -> List[KnowledgeContext]:
        """Return top-quality content scored by keyword overlap with the query."""
        try:
            items = await self.db.get_top_content(100)
            if not items:
                return []

            stop_words = {
                'the','a','an','is','are','was','were','in','on','at','to','for',
                'of','and','or','my','i','me','did','what','how','when','where',
                'which','who','have','has','been','about','with','from','this',
                'that','be','do','does','some','any','all','their','they','we',
                'you','your','tell','show','find','get','give','let','know',
            }
            query_words = {w for w in query.lower().split() if len(w) > 2 and w not in stop_words}

            scored = []
            for item in items:
                title   = item.get('title', '') or ''
                summary = item.get('summary', '') or ''
                topics  = ' '.join(item.get('key_topics', []) or [])
                blob    = f"{title} {summary} {topics}".lower()

                score   = sum(1 for w in query_words if w in blob) if query_words else 0
                quality = item.get('quality_score', 5) or 5
                scored.append((score, quality, item))

            scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

            context_items = []
            for score, quality, item in scored[:max_items]:
                summary = item.get('summary', '') or item.get('title', '')
                if not summary:
                    continue
                sim = min(0.9, 0.3 + score * 0.1) if query_words else 0.3
                context_items.append(KnowledgeContext(
                    content=summary,
                    title=item.get('title', 'Untitled'),
                    url=item.get('url', ''),
                    content_type=item.get('content_type', 'Unknown'),
                    quality_score=float(quality),
                    similarity=sim,
                    summary=summary,
                ))

            logger.info(f"Keyword fallback: {len(context_items)} context items")
            return context_items

        except Exception as e:
            logger.error(f"Keyword fallback failed: {e}", exc_info=True)
            return []

    async def _generate_response(
        self,
        query: str,
        context_items: List[KnowledgeContext],
        memory: _SimpleConversationMemory,
    ) -> tuple[str, int, float]:
        """Generate response with proper error handling."""
        
        try:
            # Choose prompt based on context availability
            if not context_items:
                # Non-RAG path
                logger.info("Generating response without RAG context")
                messages = [
                    SystemMessage(content=self.non_rag_prompt),
                    HumanMessage(content=f"Question: {query}")
                ]
            else:
                # RAG path
                logger.info(f"Generating response with {len(context_items)} context items")
                context_str = self._build_context_string(context_items)
                
                messages = [
                    SystemMessage(content=self.rag_system_prompt),
                    *memory.chat_memory.messages,
                    HumanMessage(content=f"Context:\n{context_str}\n\n---\n\nQuestion: {query}")
                ]
            
            # Call LLM
            response = await self.llm.ainvoke(messages)
            response_text = response.content
            
            # Extract token usage
            usage = getattr(response, "usage_metadata", None) or {}
            tokens_used = (
                usage.get("total_tokens") or
                (usage.get("input_tokens", 0) + usage.get("output_tokens", 0)) or
                0
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(context_items, response_text)
            
            # Update memory
            memory.chat_memory.add_user_message(query)
            memory.chat_memory.add_ai_message(response_text)
            
            return response_text, int(tokens_used), float(confidence)
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}", exc_info=True)
            return self._generate_fallback_response(query, context_items), 0, 0.2

    def _build_context_string(self, context_items: List[KnowledgeContext]) -> str:
        """Build formatted context string."""
        if not context_items:
            return ""
        
        parts: List[str] = []
        for i, item in enumerate(context_items, 1):
            # Limit content length to prevent token overflow
            content_preview = item.content[:800] if item.content else ""
            
            context_part = f"""
[Source {i}: {item.title}]
Type: {item.content_type}
Quality: {item.quality_score}/10
Relevance: {item.similarity:.2f}
Summary: {item.summary}
Content: {content_preview}...
URL: {item.url}
---""".strip()
            parts.append(context_part)
        
        return "\n\n".join(parts)

    def _calculate_confidence(
        self,
        context_items: List[KnowledgeContext],
        response: str,
    ) -> float:
        """Calculate heuristic confidence score."""
        if not context_items:
            return 0.3
        
        # Weighted scoring
        avg_similarity = sum(item.similarity for item in context_items) / len(context_items)
        avg_quality = sum(item.quality_score for item in context_items) / (len(context_items) * 10)
        
        citation_count = response.count("[Source:")
        citation_factor = min(citation_count / len(context_items), 1.0) * 0.2
        
        length_factor = min(len(response) / 500.0, 1.0) * 0.2
        
        confidence = (
            avg_similarity * 0.4 +
            avg_quality * 0.2 +
            citation_factor +
            length_factor
        )
        
        return float(max(0.1, min(0.95, confidence)))

    def _generate_fallback_response(
        self,
        query: str,
        context_items: List[KnowledgeContext],
    ) -> str:
        """Generate helpful fallback response."""
        if context_items:
            sources_list = "\n".join([f"- {item.title}" for item in context_items[:3]])
            return (
                f'I found relevant content for "{query}":\n\n{sources_list}\n\n'
                "However, I'm temporarily unable to process this information. "
                "Please try again or view these sources directly."
            )
        
        return (
            f'I don\'t have specific information about "{query}" in your knowledge base.\n\n'
            "Suggestions:\n"
            "1. Add more content on this topic\n"
            "2. Use the search function to explore related content\n"
            "3. Check the knowledge graph for related topics"
        )

    def _format_source(self, context_item: KnowledgeContext) -> Dict[str, Any]:
        """Format context for API response."""
        return {
            "title": context_item.title,
            "url": context_item.url,
            "content_type": context_item.content_type,
            "quality_score": context_item.quality_score,
            "similarity": round(context_item.similarity, 3),
            "summary": context_item.summary[:200] + "..." if len(context_item.summary) > 200 else context_item.summary
        }

    async def get_suggested_questions(self, limit: int = 5) -> List[str]:
        """Generate suggested questions from content."""
        return self._get_default_suggestions()[:limit]
    
    def _get_default_suggestions(self) -> List[str]:
        """Default suggestions when generation fails."""
        return [
            "What topics have I been learning about?",
            "Show me my knowledge graph overview",
            "What connections exist between my saved content?",
            "What are my top quality sources?",
            "Help me discover new learning paths"
        ]

    async def get_conversation_insights(
        self,
        conversation_history: List[ChatMessage],
    ) -> Dict[str, Any]:
        """Analyze conversation for insights."""
        if not conversation_history:
            return {"patterns": [], "topics": [], "suggestions": []}
        
        try:
            user_messages = [msg.content for msg in conversation_history if msg.role == "user"]
            
            # Extract common topics
            word_freq = {}
            for message in user_messages:
                words = message.lower().split()
                for word in words:
                    cleaned = ''.join(c for c in word if c.isalnum())
                    if len(cleaned) > 4:  # Skip short words
                        word_freq[cleaned] = word_freq.get(cleaned, 0) + 1
            
            top_topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "patterns": [f"You frequently discuss {topic}" for topic, count in top_topics if count > 1],
                "topics": [topic for topic, _ in top_topics],
                "suggestions": [
                    "Explore connections between these topics",
                    "Save more content on frequently discussed topics",
                    "Review related content in your knowledge base"
                ]
            }
            
        except Exception as e:
            logger.error(f"Conversation analysis failed: {e}")
            return {"patterns": [], "topics": [], "suggestions": []}