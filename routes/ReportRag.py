from fastapi import APIRouter, UploadFile, File, HTTPException
from google import generativeai as genai
import os
from dotenv import load_dotenv
from routes.Rag_page import RAGSystem
from google import genai

load_dotenv()

router = APIRouter(
    prefix="/ReportRag",
    tags=["ReportRag"],
    responses={404: {"description": "Not found"}}
)

@router.post("/analyze")
async def analyze_xray(text: str):
    try:
        rag_system = RAGSystem()





        # Structure the response

        relevant_text = rag_system.fetch_relevant_text( "Report" , text)
        print(relevant_text)


        client = genai.Client(api_key=os.getenv("Gemini_api_key"))

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[f"""You are an AI assistant that performs retrieval-augmented generation (RAG) to answer questions based on the provided knowledge base. Follow these steps:

Retrieve relevant content from the RAG knowledge source.
Check if the retrieved content directly answers the user's question.
If an answer is found, generate a clear and concise response based only on the retrieved content.
If no relevant information is found, respond with: 'No idea.'
Now, answer the following question based on the available RAG content:

User Question - {text} , Extracted content - {relevant_text}"""])

        print(response.text)
        rag_system.close()
        analysis_result = {
            "Response": response.text.replace("\n", "").replace("\r", "").replace("**", " "),
        }

        return analysis_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "X-ray analysis service is running"}