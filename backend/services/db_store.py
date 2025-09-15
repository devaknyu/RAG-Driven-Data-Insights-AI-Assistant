import sqlite3

# Connect to SQLite (creates file if not exists)
conn = sqlite3.connect("rag_chunks.db", check_same_thread=False)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL
    )
""")
conn.commit()

def store_chunks(chunks: list[str]):
    cursor.executemany("INSERT INTO chunks (content) VALUES (?)", [(chunk,) for chunk in chunks])
    conn.commit()

def get_chunks_by_indices(indices: list[int]) -> list[str]:
    placeholders = ",".join(["?"] * len(indices))
    cursor.execute(f"SELECT content FROM chunks WHERE id IN ({placeholders})", indices)
    rows = cursor.fetchall()
    return [row[0] for row in rows]
