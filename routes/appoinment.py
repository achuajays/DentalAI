from fastapi import APIRouter, Depends, HTTPException
import asyncpg
import os

DATABASE_URL = os.getenv("DB_URL")  # Replace with your PostgreSQL connection URL

router = APIRouter()

# Dependency to get a database connection
async def get_db():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

# Get all records from the table
@router.get("/data", response_model=list[dict])
async def get_all_data(db=Depends(get_db)):
    try:
        query = "SELECT * FROM webhook_data"
        records = await db.fetch(query)
        return [dict(record) for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get records for a specific patient
@router.get("/data/{patient_id}", response_model=list[dict])
async def get_data_by_patient(patient_id: int, db=Depends(get_db)):
    try:
        query = "SELECT * FROM webhook_data WHERE patient_id = $1"
        records = await db.fetch(query, patient_id)
        if not records:
            raise HTTPException(status_code=404, detail="No records found for this patient")
        return [dict(record) for record in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
