from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from google import generativeai as genai
from PIL import Image
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

# Configure Gemini API
genai.configure(api_key=os.getenv("Gemini_api_key"))

# Directory to temporarily store uploaded reports
UPLOAD_DIR = Path("uploads/reports")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file types for medical reports
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}

# Advanced prompt for summarizing medical reports
SUMMARY_PROMPT = """
You are an expert dental professional tasked with summarizing a dental medical report from a doctor's perspective. Review the provided report image and generate a concise summary including:
1. Patient demographics (name, age, gender)
2. Key findings from the examination
3. Diagnosis in professional dental terminology
4. Recommended actions or follow-ups
5. Any notable observations or concerns for the doctor
Use professional dental terminology, and format the summary as a doctor's clinical note for easy reference.
"""

def validate_file_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

async def summarize_report(image: Image.Image) -> str:
    """Summarize the report using Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            [SUMMARY_PROMPT, image],
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=1000
            )
        )
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report summarization failed: {str(e)}")

@router.post("/upload")
async def upload_and_summarize_report(file: UploadFile = File(...)):
    """
    Upload a medical report (PDF or image), and summarize it from a doctor's perspective
    """
    file_path = None
    try:
        # Validate file extension
        if not validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Validate file size (max 10MB)
        contents = await file.read()
        file_size = len(contents)
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

        # Generate unique filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / filename

        # Save the file temporarily
        with open(file_path, "wb") as f:
            f.write(contents)

        # Open image and pass to Gemini
        image = Image.open(io.BytesIO(contents))
        summary = await summarize_report(image)

        # Metadata and summary
        metadata = {
            "filename": filename,
            "original_filename": file.filename,
            "size_bytes": file_size,
            "upload_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": summary
        }

        # Delete the file after processing
        if file_path.exists():
            os.remove(file_path)

        return JSONResponse(content={
            "message": "Report uploaded, summarized, and deleted successfully",
            "metadata": metadata
        })

    except Exception as e:
        # Clean up file if it exists and an error occurs
        if file_path and file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload and summarization failed: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Report summary service is running"}  
