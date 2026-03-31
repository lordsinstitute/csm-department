-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
-- Create processed_content table
CREATE TABLE IF NOT EXISTS processed_content (
    id BIGSERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    content_type TEXT,
    key_topics JSONB,
    quality_score INTEGER,
    processing_method TEXT,
    visit_timestamp TIMESTAMP,
    content_hash TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
-- Create index on embedding column
CREATE INDEX IF NOT EXISTS processed_content_embedding_idx ON processed_content USING ivfflat (embedding vector_cosine_ops);
-- Create vector search function
CREATE OR REPLACE FUNCTION match_processed_content(
        query_embedding vector(1536),
        match_count int DEFAULT 5,
        match_threshold float8 DEFAULT 0.3
    ) RETURNS TABLE (
        id bigint,
        content text,
        title text,
        url text,
        content_type text,
        summary text,
        key_topics jsonb,
        quality_score int,
        content_hash text,
        similarity float8
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT pc.id,
    pc.content,
    pc.title,
    pc.url,
    pc.content_type,
    pc.summary,
    pc.key_topics,
    pc.quality_score,
    pc.content_hash,
    1 - (pc.embedding <=> query_embedding) AS similarity
FROM processed_content pc
WHERE 1 - (pc.embedding <=> query_embedding) > match_threshold
ORDER BY similarity DESC
LIMIT match_count;
END;
$$;