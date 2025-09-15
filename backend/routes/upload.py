# ✅ backend/routes/upload.py (edited)
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from backend.services.embedder import embed_chunks
from backend.services.vector_store import store_vectors, initialize_vector_store
from backend.database import get_db
from backend.models import Chunk
import pandas as pd
import io
from sqlalchemy.orm import Session
from backend.state import user_file_map

router = APIRouter()
initialize_vector_store()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        buffer = io.BytesIO(content)
        df = pd.read_excel(buffer)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Excel file")

    uploaded_filename = file.filename

    # ✅ Accumulate files per user
    user_files = user_file_map.get("test_user", [])
    if uploaded_filename not in user_files:
        user_files.append(uploaded_filename)
    user_file_map["test_user"] = user_files

    chunks = []
    for _, row in df.iterrows():
        chunk = ", ".join([f"{col}: {row[col]}" for col in df.columns])
        chunks.append(chunk)

    vectors = embed_chunks(chunks)

    saved_chunks = []
    for chunk_text in chunks:
        db_chunk = Chunk(content=chunk_text, file_name=uploaded_filename)
        db.add(db_chunk)
        saved_chunks.append(db_chunk)

    db.commit()
    for c in saved_chunks:
        db.refresh(c)

    store_vectors(vectors, chunks)

    return {"message": f"Uploaded and stored {len(chunks)} chunks."}
