from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from google import generativeai as genai
from PIL import Image
import io
import os
import time
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter(
    prefix="/scans",
    tags=["scan-upload"],
    responses={404: {"description": "Not found"}}
)

# Configure Gemini API
genai.configure(api_key=os.getenv("Gemini_api_key"))

# Directory to temporarily store uploaded scans
UPLOAD_DIR = Path("uploads/scans")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file types for dental scans
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".dcm"}

# Advanced prompt for scan analysis
SCAN_ANALYSIS_PROMPT = """
You are an expert dental AI assistant specializing in X-ray and dental scan analysis. Analyze the provided dental scan image and provide:
1. Whether any defects or abnormalities are present (yes/no)
2. If defects are found, detailed description including:
   - Type of defect (caries, fracture, bone loss, etc.)
   - Location in the image (e.g., specific tooth number if applicable)
   - Severity level (mild, moderate, severe)
   - Potential clinical implications
3. If no defects, confirm normal structures observed
4. Confidence level of the analysis (percentage)
Use technical dental terminology and provide a structured response.
"""

def validate_file_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

async def analyze_scan(image: Image.Image) -> str:
    """Analyze the scan using Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')  # Adjust model name as needed
        response = model.generate_content(
            [SCAN_ANALYSIS_PROMPT, image],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Low temperature for precise responses
                max_output_tokens=1000  # Allow detailed responses
            )
        )
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan analysis failed: {str(e)}")

@router.post("/upload")
async def upload_and_analyze_scan(file: UploadFile = File(...)):
    """
    Upload a single dental scan file, analyze it, and delete it afterward
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

        # Convert to PIL Image for analysis
        image = Image.open(io.BytesIO(contents))

        # Generate unique filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / filename

        # Save the file temporarily
        with open(file_path, "wb") as f:
            f.write(contents)

        # Analyze the scan
        analysis_result = await analyze_scan(image)

        # Metadata and analysis result
        metadata = {
            "filename": filename,
            "original_filename": file.filename,
            "size_bytes": file_size,
            "upload_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "analysis": analysis_result
        }

        # Delete the file after analysis
        if file_path.exists():
            os.remove(file_path)

        return JSONResponse(content={
            "message": "Scan uploaded, analyzed, and deleted successfully",
            "metadata": metadata
        })

    except Exception as e:
        # Clean up file if it exists and an error occurs
        if file_path and file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload and analysis failed: {str(e)}")

@router.post("/upload-multiple")
async def upload_and_analyze_multiple_scans(files: List[UploadFile] = File(...)):
    """
    Upload multiple dental scan files, analyze them, and delete them afterward
    """
    uploaded_files = []
    files_to_cleanup = []

    try:
        for file in files:
            if not validate_file_extension(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type for {file.filename}. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )

            contents = await file.read()
            file_size = len(contents)
            if file_size > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds 10MB limit")

            # Convert to PIL Image
            image = Image.open(io.BytesIO(contents))

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = UPLOAD_DIR / filename

            # Save the file temporarily
            with open(file_path, "wb") as f:
                f.write(contents)

            # Track files for cleanup
            files_to_cleanup.append(file_path)

            # Analyze the scan
            analysis_result = await analyze_scan(image)

            uploaded_files.append({
                "filename": filename,
                "original_filename": file.filename,
                "size_bytes": file_size,
                "upload_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "analysis": analysis_result
            })

            # Delete the file after analysis
            if file_path.exists():
                os.remove(file_path)

        return JSONResponse(content={
            "message": f"Successfully uploaded, analyzed, and deleted {len(uploaded_files)} scan(s)",
            "metadata": uploaded_files
        })

    except Exception as e:
        # Clean up any remaining files if an error occurs
        for file_path in files_to_cleanup:
            if file_path.exists():
                os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Multiple upload and analysis failed: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Scan upload and analysis service is running"}