import os
import psycopg2
from contextlib import contextmanager

# O Render fornece a URL do banco na variável DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

@contextmanager
def get_db_connection():
    # Conecta ao banco de dados usando a URL fornecida
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Cria as tabelas necessárias se elas não existirem."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Tabela de Crianças
            cur.execute("""
                CREATE TABLE IF NOT EXISTS children (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    default_address TEXT,
                    notes TEXT,
                    shift TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Tabela de Presença (Attendance)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id SERIAL PRIMARY KEY,
                    child_id INTEGER REFERENCES children(id) ON DELETE CASCADE,
                    date DATE NOT NULL,
                    status TEXT NOT NULL,
                    address TEXT,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    UNIQUE(child_id, date)
                );
            """)
            conn.commit()
          
