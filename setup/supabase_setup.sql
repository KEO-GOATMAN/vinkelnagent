-- Supabase Setup Script for News Agent Vector Database
-- This script creates the necessary tables and enables pg_vector extension

-- Enable the pg_vector extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the news_articles table for storing vectorized news content
CREATE TABLE IF NOT EXISTS news_articles (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384),  -- 384-dimensional vectors for all-MiniLM-L6-v2
    metadata JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS news_articles_embedding_idx 
ON news_articles USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Create index on metadata for filtering
CREATE INDEX IF NOT EXISTS news_articles_metadata_idx 
ON news_articles USING GIN (metadata);

-- Create index on creation date for time-based queries
CREATE INDEX IF NOT EXISTS news_articles_created_at_idx 
ON news_articles (created_at DESC);

-- Create index on id for faster lookups
CREATE INDEX IF NOT EXISTS news_articles_id_idx 
ON news_articles (id);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at timestamp
CREATE TRIGGER update_news_articles_updated_at 
    BEFORE UPDATE ON news_articles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create a function for similarity search (cosine similarity)
CREATE OR REPLACE FUNCTION similarity_search(
    query_embedding vector(384),
    similarity_threshold float DEFAULT 0.5,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id text,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        news_articles.id,
        news_articles.content,
        news_articles.metadata,
        1 - (news_articles.embedding <=> query_embedding) as similarity
    FROM news_articles
    WHERE 1 - (news_articles.embedding <=> query_embedding) > similarity_threshold
    ORDER BY news_articles.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Create a function to search by political bias
CREATE OR REPLACE FUNCTION search_by_bias(
    political_bias text,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id text,
    content text,
    metadata jsonb,
    created_at timestamp with time zone
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        news_articles.id,
        news_articles.content,
        news_articles.metadata,
        news_articles.created_at
    FROM news_articles
    WHERE news_articles.metadata->>'political_bias' = political_bias
    ORDER BY news_articles.created_at DESC
    LIMIT match_count;
END;
$$;

-- Create a function to get recent articles
CREATE OR REPLACE FUNCTION get_recent_articles(
    hours_back int DEFAULT 24,
    match_count int DEFAULT 20
)
RETURNS TABLE (
    id text,
    content text,
    metadata jsonb,
    created_at timestamp with time zone
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        news_articles.id,
        news_articles.content,
        news_articles.metadata,
        news_articles.created_at
    FROM news_articles
    WHERE news_articles.created_at > (CURRENT_TIMESTAMP - INTERVAL '1 hour' * hours_back)
    ORDER BY news_articles.created_at DESC
    LIMIT match_count;
END;
$$;

-- Sample data insertion for testing (optional)
-- Uncomment the following lines to insert test data

-- INSERT INTO news_articles (id, content, embedding, metadata) VALUES 
-- ('test_1', 
--  'This is a test news article about Swedish politics.', 
--  '[0.1, 0.2, 0.3]'::vector,  -- This would be a real 384-dimensional vector in practice
--  '{"title": "Test Article", "source": "Test Source", "political_bias": "Center", "url": "https://test.com"}'::jsonb
-- );

-- Grant necessary permissions (adjust for your security requirements)
-- These permissions allow the application to read/write to the table

-- For development (adjust these for production security)
-- GRANT ALL ON news_articles TO postgres;
-- GRANT ALL ON news_articles TO anon;
-- GRANT ALL ON news_articles TO authenticated;

-- Create view for statistics (optional)
CREATE OR REPLACE VIEW news_statistics AS
SELECT 
    metadata->>'political_bias' as bias,
    COUNT(*) as article_count,
    MAX(created_at) as latest_article,
    MIN(created_at) as earliest_article
FROM news_articles 
GROUP BY metadata->>'political_bias';

-- Print success message
DO $$
BEGIN
    RAISE NOTICE 'News Agent database setup completed successfully!';
    RAISE NOTICE 'Created table: news_articles';
    RAISE NOTICE 'Enabled extension: vector';
    RAISE NOTICE 'Created indexes for optimal performance';
    RAISE NOTICE 'Created helper functions for similarity search and filtering';
END $$; 