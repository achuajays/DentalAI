from fastapi import APIRouter, HTTPException
from google import generativeai as genai
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

router = APIRouter(
    prefix="/treatment",
    tags=["treatment-plan"],
    responses={404: {"description": "Treatment plan not found"}}
)

# Configure Gemini API
genai.configure(api_key=os.getenv("Gemini_api_key"))

# Advanced prompt for treatment planning
TREATMENT_PLAN_PROMPT = """
You are an expert dental AI assistant specializing in treatment planning. Based on the provided dental condition or analysis, create a detailed treatment plan including:
1. Primary diagnosis
2. Recommended procedures (in order of priority)
3. Estimated treatment timeline
4. Materials/tools recommended
5. Potential risks/complications
6. Follow-up recommendations
7. Patient instructions
Use professional dental terminology and provide a structured, step-by-step plan. If the input is insufficient, request specific details about the dental condition.
Input condition: {condition}
"""

@router.post("/generate-plan")
async def generate_treatment_plan(condition: str):
    """
    Generate a treatment plan based on a dental condition description
    Example condition: "Moderate caries in upper right molar #3 with potential pulpal involvement"
    """
    try:
        # Validate input
        if not condition or len(condition.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Please provide a detailed description of the dental condition"
            )

        # Configure Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')  # Using text-only model since we're passing text

        # Format the prompt with the condition
        formatted_prompt = TREATMENT_PLAN_PROMPT.format(condition=condition)

        # Generate treatment plan
        response = model.generate_content(
            formatted_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,  # Slightly higher for more practical suggestions
                max_output_tokens=1500  # Allow for detailed treatment plans
            )
        )

        # Structure the response
        treatment_plan = {
            "condition": condition,
            "treatment_plan": response.text,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        return treatment_plan

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Treatment plan generation failed: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Treatment plan service is running"}