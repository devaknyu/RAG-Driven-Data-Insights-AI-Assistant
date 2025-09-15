# backend/routes/chat.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.services.embedder import model
from backend.services.vector_store import get_top_k, initialize_vector_store
from backend.database import get_db
from backend.services.llm import generate_answer
from sqlalchemy.orm import Session
from backend.models import ChatHistory, User, Chunk
from backend.state import user_file_map

router = APIRouter()

initialize_vector_store()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    # ✅ Get or create test user
    user = db.query(User).filter_by(username="test_user").first()
    if not user:
        user = User(username="test_user")
        db.add(user)
        db.commit()
        db.refresh(user)

    question = request.question
    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")

    # ✅ Check that we have data in vector store
    if not get_top_k([0] * model.get_sentence_embedding_dimension(), 1):
        raise HTTPException(status_code=400, detail="No data available — upload or connect first.")

    # ✅ Embed and retrieve top matches
    question_vec = model.encode([question])[0]
    matched_chunks = get_top_k(question_vec, k=5)
    context = "\n".join(matched_chunks)

    file_name = None
    file_type = "uploaded data"  # default fallback

    # ✅ Attempt to extract file_name from DB chunks
    for chunk_text in matched_chunks:
        chunk_record = (
            db.query(Chunk)
            .filter(Chunk.content.like(f"%{chunk_text[:30]}%"))
            .first()
        )
        if chunk_record:
            file_name = chunk_record.file_name or chunk_record.source
            if file_name:
                break

    # ✅ Fallback to memory-tracked uploaded files
    if not file_name:
        uploaded_files = user_file_map.get("test_user", [])
        file_name = ", ".join(uploaded_files) if uploaded_files else "unknown"

    # ✅ Determine file type from name
    if file_name:
        if file_name.endswith(".xlsx"):
            file_type = "Excel spreadsheet"
        elif file_name.endswith(".db") or file_name.endswith(".sqlite"):
            file_type = "SQLite database"
        elif file_name == "live_postgres":
            file_type = "PostgreSQL live database"
    else:
        file_type = "uploaded data"

    # ✅ Generate final response
    answer = generate_answer(context, question, file_name, file_type)

    # ✅ Save interaction
    chat_entry = ChatHistory(
        user_id=user.id,
        question=question,
        answer=answer,
        file_name=file_name
    )
    db.add(chat_entry)
    db.commit()

    return {"answer": answer}

@router.get("/history")
def get_chat_history(db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username="test_user").first()
    if not user:
        return []

    history = (
        db.query(ChatHistory)
        .filter_by(user_id=user.id)
        .order_by(ChatHistory.timestamp.desc())
        .all()
    )
    return [
        {
            "question": h.question,
            "answer": h.answer,
            "timestamp": h.timestamp.isoformat(),
            "file_name": h.file_name
        }
        for h in history
    ]
