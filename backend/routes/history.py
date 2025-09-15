# backend/routes/history.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import ChatHistory, Chunk
from backend.services.vector_store import clear_vector_store
from backend.state import user_file_map

router = APIRouter()

@router.get("/history")
def get_chat_history(db: Session = Depends(get_db)):
    history = db.query(ChatHistory).order_by(ChatHistory.timestamp.desc()).all()
    return [
        {
            "id": entry.id,
            "question": entry.question,
            "answer": entry.answer,
            "timestamp": entry.timestamp.isoformat(),
            "file_name": entry.file_name 
        }
        for entry in history
    ]

@router.delete("/history")
def delete_chat_history(db: Session = Depends(get_db)):
    db.query(ChatHistory).delete()
    db.commit()
    return {"message": "Chat history cleared"}

@router.delete("/reset")
def reset_all_data(db: Session = Depends(get_db)):
    db.query(ChatHistory).delete()
    db.query(Chunk).delete()
    db.commit()
    clear_vector_store()
    user_file_map.clear()
    return {"message": "All data (chunks, vectors, filenames, chat history) has been reset."}
