from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pgvector.sqlalchemy import Vector
import os
import logging

# Import Google GenAI SDK (unchanged)
from google import genai

router = APIRouter()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/mydatabase")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# SQLAlchemy model for storing evaluations
class Evaluation(Base):
    __tablename__ = "evaluation"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    vector = Column(Vector(768))  # Ensure PostgreSQL has pgvector extension enabled
    text = Column(String, nullable=False)


# Pydantic model for input validation
class TextInput(BaseModel):
    text: str
    type: str


# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create table if it does not exist
def init_db():
    try:
        with engine.connect() as conn:
            # Enable pgvector extension if not enabled
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()

        # Create the table if it doesn't exist
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully.")
    except Exception as e:
        logging.exception(f"Error initializing the database: {str(e)}")


# Initialize the database on startup
init_db()


# API endpoint to save text along with its embedding
@router.post("/save-text")
def save_text(input_data: TextInput, db: Session = Depends(get_db)):
    try:
        # Gemini embedding code (unchanged)
        result = genai.Client(api_key=os.getenv("Gemini_api_key")).models.embed_content(
            model="text-embedding-004",
            contents=[input_data.text]
        )
        if not result or not hasattr(result, "embeddings") or not result.embeddings:
            raise HTTPException(status_code=500, detail="Failed to retrieve embeddings.")

        embedding = result.embeddings[0].values

        # Create a new evaluation record in the database
        db_eval = Evaluation(
            text=input_data.text,
            type=input_data.type,
            vector=embedding
        )
        db.add(db_eval)
        db.commit()
        db.refresh(db_eval)

        return {"message": "Text saved successfully", "id": db_eval.id}

    except Exception as e:
        db.rollback()
        logging.exception("Error saving text and embedding")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# API endpoint to retrieve all saved texts and embeddings
@router.get("/get-texts")
def get_texts(db: Session = Depends(get_db)):
    try:
        results = db.query(Evaluation).all()
        return [
            {
                "id": row.id,
                "vector": row.vector.tolist() if row.vector else None,  # Convert vector to list for JSON response
                "text": row.text
            }
            for row in results
        ]
    except Exception as e:
        logging.exception("Error retrieving texts")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
