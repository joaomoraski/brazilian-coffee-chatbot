from functools import lru_cache

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
            max_size=10,
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


def get_session_history(session_id: str) -> PostgresChatMessageHistory:
    """Get chat history for a session using langchain_postgres."""
    # Ensure table exists first
    _ensure_table_exists()
    
    pool = get_connection_pool()
    connection = pool.getconn()

    # PostgresChatMessageHistory - positional args: table_name, session_id
    return PostgresChatMessageHistory(
        "chat_history",  # table_name (positional)
        session_id,      # session_id (positional)
        sync_connection=connection,  # keyword argument
    )


def return_connection(history: PostgresChatMessageHistory):
    """Return connection to pool after use."""
    pool = get_connection_pool()
    if history.sync_connection:
        pool.putconn(history.sync_connection)
