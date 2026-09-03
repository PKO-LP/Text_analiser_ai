import sqlite3
import aiosqlite
from config import config
import os


def init_db():
    db_path_abs = os.path.abspath(config.DB_PATH)
    db_dir = os.path.dirname(db_path_abs)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path_abs)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PROCESSING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(
            content,
            file_id UNINDEXED,
            chunk_index UNINDEXED
        )
    """)

    conn.commit()
    conn.close()


async def add_file(filename: str) -> int:
    async with aiosqlite.connect(config.DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO files (filename, status) VALUES (?, ?)",
            (filename, "PROCESSING")
        )
        await db.commit()
        return cursor.lastrowid


async def update_file_status(file_id: int, status: str):
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "UPDATE files SET status = ? WHERE id = ?",
            (status, file_id)
        )
        await db.commit()


async def get_file(file_id: int) -> dict | None:
    async with aiosqlite.connect(config.DB_PATH) as db:
        async with db.execute(
            "SELECT id, filename, status FROM files WHERE id = ?", (file_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"id": row[0], "filename": row[1], "status": row[2]}
            return None


async def get_files() -> list[dict]:
    async with aiosqlite.connect(config.DB_PATH) as db:
        async with db.execute(
            "SELECT id, filename, status FROM files ORDER BY created_at DESC"
        ) as cursor:
            rows = await cursor.fetchall()
            return [{"id": r[0], "filename": r[1], "status": r[2]} for r in rows]


async def save_chunks(file_id: int, chunks: list[str]):
    async with aiosqlite.connect(config.DB_PATH) as db:
        for idx, chunk in enumerate(chunks):
            await db.execute(
                "INSERT INTO chunks (file_id, chunk_index, content) VALUES (?, ?, ?)",
                (file_id, idx, chunk)
            )
            await db.execute(
                "INSERT INTO fts_chunks (content, file_id, chunk_index) VALUES (?, ?, ?)",
                (chunk, file_id, idx)
            )
        await db.commit()


async def search_chunks(query: str, top_k: int = 5) -> list[dict]:
    # Защита: пустой MATCH ломает FTS5
    if not query or not query.strip():
        return []

    async with aiosqlite.connect(config.DB_PATH) as db:
        sql = """
            SELECT content, file_id, chunk_index
            FROM fts_chunks
            WHERE fts_chunks MATCH ?
            ORDER BY rank
            LIMIT ?
        """
        async with db.execute(sql, (query, top_k)) as cursor:
            rows = await cursor.fetchall()
            return [{"content": r[0], "file_id": r[1], "chunk_index": r[2]} for r in rows]
