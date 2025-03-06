import requests
import os
from fastapi import APIRouter, HTTPException

# Define the router
router = APIRouter()

# RapidAPI details
RAPIDAPI_URL = "https://drug-info-and-price-history.p.rapidapi.com/1/druginfo"
RAPIDAPI_KEY = os.getenv("Rapidapi_key")  # Replace with your actual API key
RAPIDAPI_HOST = "drug-info-and-price-history.p.rapidapi.com"

# Get drug information
@router.get("/drug_info")
async def get_drug_info(drug: str):
    try:
        querystring = {"drug": drug}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST
        }
        response = requests.get(RAPIDAPI_URL, headers=headers, params=querystring)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch drug info")

        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
