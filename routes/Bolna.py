from fastapi import APIRouter, HTTPException, Request
import requests
import os
import logging

router = APIRouter()

# Environment variables for API configuration
BOLNA_API_URL = "https://api.bolna.dev/call"
BOLNA_AGENT_ID = os.getenv("BOLNA_AGENT_ID", "123e4567-e89b-12d3-a456-426655440000")
BOLNA_AUTH_TOKEN = os.getenv("BOLNA_AUTH_TOKEN", "<your_api_token_here>")


# API to initiate a call
@router.post("/make-call")
def make_call(recipient_phone_number: str):
    try:
        payload = {
            "agent_id": BOLNA_AGENT_ID,
            "recipient_phone_number": recipient_phone_number,
        }
        headers = {
            "Authorization": f"Bearer {BOLNA_AUTH_TOKEN}",
            "Content-Type": "application/json",
        }

        response = requests.post(BOLNA_API_URL, json=payload, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return {"message": "Call initiated successfully", "response": response.json()}

    except Exception as e:
        logging.exception("Error in making call")
        raise HTTPException(status_code=500, detail=str(e))


