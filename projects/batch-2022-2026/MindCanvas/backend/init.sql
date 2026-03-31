-- MindCanvas PostgreSQL schema — runs automatically on first `docker compose up`

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS processed_content (
    id                BIGSERIAL PRIMARY KEY,
    url               TEXT UNIQUE NOT NULL,
    title             TEXT NOT NULL,
    summary           TEXT,
    content           TEXT,
    content_type      TEXT DEFAULT 'Web Content',
    key_topics        JSONB DEFAULT '[]',
    quality_score     INTEGER DEFAULT 5,
    processing_method TEXT DEFAULT 'basic',
    content_hash      TEXT,
    visit_timestamp   TIMESTAMPTZ,
    embedding         vector(384),
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pc_embedding
    ON processed_content USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_pc_quality
    ON processed_content (quality_score DESC);

CREATE OR REPLACE FUNCTION match_processed_content(
    query_embedding vector(384),
    match_count     int   DEFAULT 10,
    match_threshold float DEFAULT 0.3
)
RETURNS TABLE (
    id            bigint,
    url           text,
    title         text,
    summary       text,
    content_type  text,
    key_topics    jsonb,
    quality_score int,
    similarity    float
)
LANGUAGE sql STABLE AS $$
    SELECT id, url, title, summary, content_type, key_topics, quality_score,
           1 - (embedding <=> query_embedding) AS similarity
    FROM processed_content
    WHERE embedding IS NOT NULL
      AND 1 - (embedding <=> query_embedding) > match_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;
