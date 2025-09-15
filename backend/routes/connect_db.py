# backend/routes/connect_db.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, text
import pandas as pd

from backend.services.embedder import embed_chunks
from backend.services.vector_store import store_vectors
from backend.database import get_db
from backend.models import Chunk
from backend.state import user_file_map

router = APIRouter()

class DBConnectionRequest(BaseModel):
    dialect: str         # e.g., "postgresql", "mysql", "sqlite", "mssql"
    username: str
    password: str
    host: str
    port: str
    database: str

@router.post("/connect-db")
def connect_to_live_db(payload: DBConnectionRequest, db: Session = Depends(get_db)):
    try:
        db_url = f"{payload.dialect}://{payload.username}:{payload.password}@{payload.host}:{payload.port}/{payload.database}"
        engine = create_engine(db_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if not tables:
            raise HTTPException(status_code=400, detail="No tables found in database.")

        chunks = []
        for table in tables:
            schema = f"Live Table: {table}\n"
            columns = inspector.get_columns(table)
            schema += "Columns: " + ", ".join([col["name"] for col in columns]) + "\n"

            try:
                with engine.connect() as conn:
                    result = pd.read_sql(text(f"SELECT * FROM {table} LIMIT 5"), conn)
                    schema += "Sample Rows:\n" + result.to_string(index=False) + "\n"
            except Exception:
                schema += "(Could not fetch sample rows)\n"

            chunks.append(schema.strip())

        # Embed & store vectors
        vectors = embed_chunks(chunks)
        store_vectors(vectors, chunks)

        # Save in local DB
        source_label = f"LiveDB:{payload.database}"
        for chunk in chunks:
            db.add(Chunk(content=chunk, file_name=source_label))
        db.commit()

        # Track upload for session
        uploaded = user_file_map.get("test_user", [])
        uploaded.append(source_label)
        user_file_map["test_user"] = list(set(uploaded))

        return {"message": f"Connected to {payload.database}, processed {len(chunks)} tables."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect: {e}")
