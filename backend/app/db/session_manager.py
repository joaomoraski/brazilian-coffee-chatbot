from contextlib import contextmanager
from functools import lru_cache

import psycopg
from langchain_postgres import PostgresChatMessageHistory
from psycopg_pool import ConnectionPool

from app.settings import settings

# Connection pool for database
_connection_pool: ConnectionPool | None = None
_table_initialized: bool = False


def get_connection_pool() -> ConnectionPool:
    """Get or create sync connection pool."""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = ConnectionPool(
            conninfo=settings.DATABASE_URL,
            min_size=2,
            max_size=20,  # Increased for better concurrency
            open=True,
        )
    return _connection_pool


def _ensure_table_exists():
    """Ensure the chat_history table exists."""
    global _table_initialized
    if _table_initialized:
        return
    
    pool = get_connection_pool()
    connection = pool.getconn()
    
    try:
        with connection.cursor() as cursor:
            # Create table if not exists (from langchain-postgres schema)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    message JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_chat_history_session_id 
                ON chat_history(session_id);
            """)
            connection.commit()
        
        _table_initialized = True
    finally:
        pool.putconn(connection)


@contextmanager
def get_session_history(session_id: str):
    """
    Context manager for PostgresChatMessageHistory.
    
    Properly manages connection pool lifecycle:
    - Gets a connection from the pool
    - Yields PostgresChatMessageHistory
    - Returns connection to pool after use
    
    Usage:
        with get_session_history(session_id) as history:
            messages = history.messages
            history.add_user_message(...)
    """
    _ensure_table_exists()
    
    pool = get_connection_pool()
    
    # Use pool's context manager to automatically return connection
    with pool.connection() as conn:
        history = PostgresChatMessageHistory(
            "chat_history",
            session_id,
            sync_connection=conn,
        )
        yield history
