# backend/services/vector_store.py
import faiss
import numpy as np
import os
import pickle

INDEX_PATH = "vector_store/faiss.index"
CHUNKS_PATH = "vector_store/chunks.pkl"

EMBED_DIM = 384

# Initialize FAISS index and chunk_store list
index = faiss.IndexFlatL2(EMBED_DIM)
chunk_store = []

def initialize_vector_store():
    load_index()
    load_chunks()

def store_vectors(vectors, chunks):
    global chunk_store
    vectors_np = np.array(vectors).astype('float32')
    index.add(vectors_np)
    chunk_store.extend(chunks)
    save_index()
    save_chunks()

def get_top_k(query_embedding, k=5):
    if index.ntotal == 0:
        return []
    D, I = index.search(np.array([query_embedding]).astype('float32'), k)
    matched_chunks = [chunk_store[i] for i in I[0] if i < len(chunk_store)]
    return matched_chunks

def save_index():
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

def load_index():
    global index
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
    else:
        index = faiss.IndexFlatL2(EMBED_DIM)

def save_chunks():
    os.makedirs(os.path.dirname(CHUNKS_PATH), exist_ok=True)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunk_store, f)

def load_chunks():
    global chunk_store
    if os.path.exists(CHUNKS_PATH):
        with open(CHUNKS_PATH, "rb") as f:
            chunk_store = pickle.load(f)
    else:
        chunk_store = []

def clear_vector_store():
    global index, chunk_store
    index = faiss.IndexFlatL2(EMBED_DIM)
    chunk_store = []
    # Optionally remove saved files from disk too:
    if os.path.exists(INDEX_PATH):
        os.remove(INDEX_PATH)
    if os.path.exists(CHUNKS_PATH):
        os.remove(CHUNKS_PATH)
