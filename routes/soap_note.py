from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from google import generativeai as genai
import os
import time
import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

# Load environment variables
load_dotenv()

router = APIRouter(
    prefix="/soap",
    tags=["soap-note"],
    responses={404: {"description": "Not found"}}
)

# Configure Gemini API
genai.configure(api_key=os.getenv("Gemini_api_key"))

# PostgreSQL connection details
DB_URL = os.getenv("DB_URL")

# Example JSON structure
example_json = {
    "subjective": "Patient's chief complaint, history, and reported symptoms.",
    "objective": "Clinical findings from the examination (e.g., oral exam, radiographs, vitals).",
    "assessment": "Professional diagnosis using dental terminology.",
    "plan": "Treatment plan, recommendations, and follow-up instructions.",
    "summary": "A concise overview for quick reference."
}

# Advanced prompt template for generating a SOAP note
SOAP_NOTE_PROMPT_TEMPLATE = """
You are an expert dental professional tasked with creating a SOAP note from a dentist's perspective to reduce documentation workload. Based on the provided patient information and clinical findings, generate a structured SOAP note with the following sections:
1. Subjective: Patient's chief complaint, history, and reported symptoms.
2. Objective: Clinical findings from the examination (e.g., oral exam, radiographs, vitals).
3. Assessment: Professional diagnosis using dental terminology.
4. Plan: Treatment plan, recommendations, and follow-up instructions.
5. Summary: A concise overview for quick reference.
Respond only in JSON like {example_json} with no other text or ```json
Patient Information and Findings:
{patient_info}
"""

def get_db_connection():
    """Establish a connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def save_soap_note(patient_id: str, soap_note: dict, generated_at: str):
    """Save the SOAP note to the PostgreSQL database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soap_notes (
                id SERIAL PRIMARY KEY,
                patient_id VARCHAR(50) NOT NULL,
                soap_note JSONB NOT NULL,
                generated_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Convert dictionary to proper JSON string
        soap_note_json = json.dumps(soap_note)

        # Insert the SOAP note
        cursor.execute("""
            INSERT INTO soap_notes (patient_id, soap_note, generated_at)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (patient_id, soap_note_json, generated_at))

        conn.commit()
        note_id = cursor.fetchone()[0]
        return note_id
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save SOAP note: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/generate")
async def generate_soap_note(patient_id: str, patient_info: str):
    """
    Generate a SOAP note based on patient information and clinical findings, and save it to the database
    Example input: "Patient: John Doe, 30-year-old male. Chief complaint: Routine dental check-up. Findings: No visible cavities, healthy gums, no plaque, no malocclusion, no pain or sensitivity."
    """
    try:
        # Validate input
        if not patient_id or not patient_info or len(patient_info.strip()) < 20:
            raise HTTPException(
                status_code=400,
                detail="Please provide a valid patient_id and detailed patient information (minimum 20 characters)"
            )

        # Configure Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')  # Adjust model name as needed

        # Format the prompt with actual patient information
        soap_note_prompt = SOAP_NOTE_PROMPT_TEMPLATE.format(
            example_json=example_json,
            patient_info=patient_info
        )

        # Generate the SOAP note
        response = model.generate_content(
            contents=[soap_note_prompt],
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,  # Low temperature for precise, professional output
                max_output_tokens=1500  # Allow for detailed SOAP notes
            )
        )

        # Parse the response as JSON
        try:
            cleaned_response = response.text.replace("```json", "").replace("```", "").strip()
            soap_note = json.loads(cleaned_response)
            if not isinstance(soap_note, dict):
                raise ValueError("Response is not a valid JSON object")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse SOAP note: {str(e)}")

        # Generate timestamp
        generated_at = time.strftime("%Y-%m-%d %H:%M:%S")

        # Save to database
        note_id = save_soap_note(patient_id, soap_note, generated_at)

        # Prepare result
        result = {
            "patient_id": patient_id,
            "patient_info": patient_info,
            "soap_note": soap_note,
            "generated_at": generated_at,
            "note_id": note_id
        }

        return JSONResponse(content={
            "message": "SOAP note generated and saved successfully",
            "data": result
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SOAP note generation or saving failed: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "SOAP note generation service is running"}