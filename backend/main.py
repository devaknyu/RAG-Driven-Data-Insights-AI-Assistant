from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import upload, chat, history,files, upload_db, connect_db
from backend.services.vector_store import initialize_vector_store
from .database import init_db
from dotenv import load_dotenv
load_dotenv()



app = FastAPI()

# Enable CORS so React frontend can call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(upload.router, prefix="/api")
app.include_router(upload_db.router, prefix="/api")
app.include_router(connect_db.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(files.router, prefix="/api") 


@app.on_event("startup")
def on_startup():
    init_db()

initialize_vector_store()