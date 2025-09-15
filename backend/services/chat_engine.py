from backend.services.vector_store import get_top_k, initialize_vector_store
from backend.db import get_db_session
from backend.models import Chunk
from backend.services.embedder import model as embedding_model

initialize_vector_store()

def get_answer_from_query(question: str, k: int = 3):
    # Embed question
    question_vec = embedding_model.encode([question])

    # Search FAISS to get chunk IDs
    matched_chunk_ids = get_top_k(question_vec[0], k)

    # Fetch chunks text from DB
    db = get_db_session()
    chunks = db.query(Chunk).filter(Chunk.id.in_(matched_chunk_ids)).all()

    # Extract text in the original order of IDs found
    id_to_chunk = {chunk.id: chunk.text for chunk in chunks}
    matched_chunks = [id_to_chunk.get(cid, "") for cid in matched_chunk_ids]

    return {
        "answer": "Here's what I found relevant to your question.",
        "sources": matched_chunks
    }
