from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import requests
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

router = APIRouter(
    prefix="/exercises",
    tags=["exercise-fetch"],
    responses={404: {"description": "Not found"}}
)

# API configuration from environment variables
RAPIDAPI_KEY = os.getenv("Rapidapi_key")
RAPIDAPI_HOST = "exercisedb.p.rapidapi.com"

# Valid body parts for the ExerciseDB API (based on API documentation)
VALID_BODY_PARTS = {
    "back", "cardio", "chest", "lower arms", "lower legs",
    "neck", "shoulders", "upper arms", "upper legs", "waist"
}

headers = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST
}

@router.get("/bodypart/{bodypart}")
async def fetch_exercises_by_bodypart(
    bodypart: str,
    limit: Optional[int] = 10,
    offset: Optional[int] = 0
):
    """
    Fetch exercises for a specific body part from ExerciseDB API
    Example: /exercises/bodypart/back?limit=10&offset=0
    """
    try:
        # Validate body part
        if bodypart.lower() not in VALID_BODY_PARTS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid body part. Valid options: {', '.join(VALID_BODY_PARTS)}"
            )

        # Validate limit and offset
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
        if offset < 0:
            raise HTTPException(status_code=400, detail="Offset must be non-negative")

        # Construct the URL and query parameters
        url = f"https://exercisedb.p.rapidapi.com/exercises/bodyPart/{bodypart.lower()}"
        querystring = {"limit": str(limit), "offset": str(offset)}

        # Make the API request
        response = requests.get(url, headers=headers, params=querystring)

        # Check for API errors
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"ExerciseDB API error: {response.text}"
            )

        # Parse the response
        exercises = response.json()

        # Return structured response
        return JSONResponse(content={
            "message": f"Successfully fetched exercises for body part: {bodypart}",
            "bodypart": bodypart,
            "limit": limit,
            "offset": offset,
            "data": exercises
        })

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch exercises: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Exercise fetch service is running"}