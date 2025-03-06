from fastapi import APIRouter, Depends, HTTPException
import asyncpg
import os

# Set your database URLs
DB_URL = os.getenv("DB_URL") # Replace with your primary PostgreSQL database URL
PG_DATABASE_URL = os.getenv("DATABASE_URL")  # Replace with your secondary PostgreSQL database URL

router = APIRouter(
    prefix="/integration",
    tags=["integration"],
    responses={404: {"description": "Not found"}}
)

# Dependency to get a database connection
async def get_db():
    conn = await asyncpg.connect(DB_URL)
    try:
        yield conn
    finally:
        await conn.close()

async def get_pg_db():
    conn = await asyncpg.connect(PG_DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

# Get all records from soap_note table
@router.get("/soap_notes", response_model=list[dict])
async def get_soap_notes(db=Depends(get_db)):
    try:
        query = "SELECT * FROM soap_notes"
        records = await db.fetch(query)
        return [dict(record) for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all records from users table
@router.get("/users", response_model=list[dict])
async def get_users(db=Depends(get_db)):
    try:
        query = "SELECT * FROM users"
        records = await db.fetch(query)
        return [dict(record) for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all records from appointment table
@router.get("/appointments", response_model=list[dict])
async def get_appointments(db=Depends(get_db)):
    try:
        query = "SELECT * FROM webhook_data"
        records = await db.fetch(query)
        return [dict(record) for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all records from evaluation table (uses PG_DATABASE_URL)
@router.get("/evaluations", response_model=list[dict])
async def get_evaluations(db=Depends(get_pg_db)):
    try:
        query = "SELECT * FROM evaluation"
        records = await db.fetch(query)
        return [dict(record) for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
