from fastapi import APIRouter, UploadFile, File, HTTPException
from google import generativeai as genai
from PIL import Image
import io
import os
from dotenv import load_dotenv
from routes.Rag_page import RAGSystem


# Load environment variables
load_dotenv()

router = APIRouter(
    prefix="/xray",
    tags=["xray-analysis"],
    responses={404: {"description": "Not found"}}
)


db_config = {
            "dbname": "mydatabase",
            "user": "myuser",
            "password": "mypassword",
            "host": "localhost",
            "port": 5432
        }



# Configure Gemini API
genai.configure(api_key=os.getenv("Gemini_api_key"))

# Advanced prompt for detailed dental analysis
DENTAL_ANALYSIS_PROMPT = """
You are an expert dental AI assistant specializing in X-ray analysis. Analyze the provided dental X-ray image and provide:
1. Whether any defects or abnormalities are present (yes/no)
2. If defects are found, detailed description including:
   - Type of defect (caries, fracture, bone loss, etc.)
   - Location in the image
   - Severity level (mild, moderate, severe)
   - Potential clinical implications
3. If no defects, confirm normal structures observed
4. Any recommendations for the dentist
Use technical dental terminology and provide a structured response.
"""

@router.post("/analyze")
async def analyze_xray(file: UploadFile = File(...)):
    try:
        rag_system = RAGSystem()

        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Please upload an image file")

        # Read and convert image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # Configure Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')  # Adjust model name as needed

        # Generate analysis with advanced prompting
        response = model.generate_content(
            [DENTAL_ANALYSIS_PROMPT, image],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Low temperature for more precise responses
                max_output_tokens=1000  # Allow detailed responses
            )
        )

        # Structure the response

        relevant_text = rag_system.fetch_relevant_text( "Xray" , response.text)
        print(relevant_text)
        analysis = rag_system.get_answer_from_gpt(response.text, relevant_text)
        rag_system.close()
        analysis_result = {
            "filename": file.filename,
            "analysis": analysis.replace("\n", "").replace("\r", "").replace("**", " "),
        }

        return analysis_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "X-ray analysis service is running"}