from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
import PIL.Image
import io
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter(
    prefix="/reports",
    tags=["report-summary"],
    responses={404: {"description": "Not found"}}
)

# Configure Gemini API client
client = genai.Client(api_key=os.getenv("Gemini_api_key"))

# Directory to temporarily store uploaded reports
UPLOAD_DIR = Path("uploads/reports")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file types for medical reports
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# System prompt for processing medical reports
SYSTEM_PROMPT = """
You are an expert dental professional tasked with analyzing a dental medical report.
Review the provided image and generate a concise summary including:
1. Patient demographics (name, age, gender, if available)
2. Key findings from the examination
3. Diagnosis in professional dental terminology
4. Recommended actions or follow-ups
5. Any notable observations or concerns for the doctor
Use professional dental terminology and format the summary as a doctor's clinical note.
"""

@router.post("/upload")
async def upload_and_summarize_report(file: UploadFile = File(...)):
    """
    Upload a medical report (image), pass it to Gemini API, and generate a summary.
    """
    file_path = None
    try:
        # Validate file extension
        if Path(file.filename).suffix.lower() not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Validate file size (max 10MB)
        contents = await file.read()
        file_size = len(contents)
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

        # Load image from memory
        image = PIL.Image.open(io.BytesIO(contents))

        # Send image to Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[SYSTEM_PROMPT, image]
        )

        summary = response.text if response.text else "No summary generated."

        # Metadata and summary
        metadata = {
            "filename": file.filename,
            "size_bytes": file_size,
            "upload_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": summary
        }

        return JSONResponse(content={
            "message": "Report uploaded and summarized successfully",
            "metadata": metadata
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload and summarization failed: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Report summary service is running"}
