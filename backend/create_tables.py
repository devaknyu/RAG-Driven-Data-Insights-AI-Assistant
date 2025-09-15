from backend.database import engine, Base
from backend import models  # This imports and registers all models

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully!")
