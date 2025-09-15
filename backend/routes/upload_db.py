# backend/routes/upload_db.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import sqlite3
import io
import pandas as pd
import traceback

from backend.services.embedder import embed_chunks
from backend.services.vector_store import store_vectors
from backend.database import get_db
from backend.models import Chunk
from backend.state import user_file_map

router = APIRouter()

@router.post("/upload-db")
async def upload_db(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".db") and not file.filename.endswith(".sqlite"):
        raise HTTPException(status_code=400, detail="Only .db or .sqlite files are supported.")

    content = await file.read()

    try:
        # Save uploaded file temporarily to disk
        with open("temp.db", "wb") as f:
            f.write(content)

        disk_conn = sqlite3.connect("temp.db")
        cursor = disk_conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if not tables:
            raise HTTPException(status_code=400, detail="No tables found in database.")

        chunks = []
        for (table_name,) in tables:
            schema = f"Table: {table_name}\n"
            
            # ✅ Use quotes around table name for safety
            cursor.execute(f'PRAGMA table_info("{table_name}");')
            cols = cursor.fetchall()
            schema += "Columns: " + ", ".join([col[1] for col in cols]) + "\n"

            # ✅ Try fetching a sample of rows safely
            try:
                df = pd.read_sql_query(f'SELECT * FROM "{table_name}" LIMIT 5;', disk_conn)
                schema += "Sample Rows:\n" + df.to_string(index=False) + "\n"
            except Exception as e:
                schema += "(Could not fetch sample rows)\n"

            chunks.append(schema.strip())

        disk_conn.close()

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to read database: {e}")

    # Embed & store
    vectors = embed_chunks(chunks)

    saved_chunks = []
    for chunk_text in chunks:
        db_chunk = Chunk(content=chunk_text, file_name=file.filename)
        db.add(db_chunk)
        saved_chunks.append(db_chunk)

    db.commit()
    for c in saved_chunks:
        db.refresh(c)

    store_vectors(vectors, chunks)

    # Track uploaded DB file
    uploaded = user_file_map.get("test_user", [])
    uploaded.append(file.filename)
    user_file_map["test_user"] = list(set(uploaded))

    return {"message": f"Uploaded and processed {len(tables)} tables from {file.filename}."}
