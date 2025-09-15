from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Chunk

router = APIRouter()

@router.get("/uploaded-files")
def get_uploaded_files(db: Session = Depends(get_db)):
    files = db.query(Chunk.file_name).distinct().all()
    return [f[0] for f in files]
