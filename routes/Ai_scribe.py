# routes\Ai_scribe.py
from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect
from starlette.websockets import WebSocketState

from routes.Deepgram import DeepgramService

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint that dynamically selects a service (Deepgram or TranscribeManager)
    based on configuration and handles the WebSocket connection.
    """
    await websocket.accept()
    # await websocket.send_text("Connected")  # Send "Connected" message
    try:
        deepgram_service = DeepgramService()
        await deepgram_service.process(websocket)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Error in WebSocket endpoint: {e}")
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()

