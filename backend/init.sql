-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Note: The following tables will be created automatically:
-- 1. langchain_pg_collection - by PGVector (collection metadata)
-- 2. langchain_pg_embedding - by PGVector (documents and embeddings)
-- 3. chat_history - by PostgresChatMessageHistory (chat messages)
-- All tables are created programmatically on first use
