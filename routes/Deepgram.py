import base64
import json
import os
from dotenv import load_dotenv
from typing import Dict, Callable
from deepgram import Deepgram
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
import logger

logger = logger.Logger("Deepgram Live Audio Transcription", "detailed")

load_dotenv()


class DeepgramService:
    def __init__(self):
        try:
            self.client = Deepgram(os.getenv("DEEPGRAM_API_KEY"))
            self.audio_header = None  # Store first 4 bytes of the stream
            self.config = {'model': 'nova-2-medical', 'punctuate': True, 'interim_results': False}

        except Exception as e:

            raise

    async def process(self, websocket: WebSocket):
        """
        Handles audio data processing using Deepgram for live transcription.
        Accepts `appt_id` to associate transcription with a specific appointment.
        """
        transcription_result = []  # To store transcribed content
        appt_id = None  # To store appointment ID

        async def on_transcript_received(data: Dict) -> None:
            try:

                if 'channel' in data:
                    transcript = data['channel']['alternatives'][0]['transcript']
                    if transcript:
                        transcription_result.append(transcript)  # Save transcript to list
                        response = {
                            "appt_id": appt_id,
                            "transcription": transcript
                        }
                        await websocket.send_text(json.dumps(response))

            except Exception as e:
                print(e)

        try:
            deepgram_socket = await self.connect_to_deepgram(on_transcript_received, self.config)

            while True:
                try:
                    message = await websocket.receive_text()

                    data = json.loads(message)
                    print(data)

                    if "type" in data:
                        deepgram_socket.send(json.dumps(data))
                        continue
                    # Extract appt_id if provided
                    if "appt_id" in data:
                        appt_id = data["appt_id"]


                    if "audio" in data:
                        audio_data = base64.b64decode(data["audio"])


                        if self.audio_header is None and len(audio_data) >= 4:
                            self.audio_header = audio_data[:4]


                        # Send the audio data to Deepgram
                        deepgram_socket.send(audio_data)

                except WebSocketDisconnect:

                    break
                except Exception as e:

                    break
        except Exception as e:
           print(e)
        finally:
            if websocket.application_state == WebSocketState.CONNECTED:
                print("*" * 50)
                await websocket.close()

    async def connect_to_deepgram(self, transcript_received_handler: Callable[[Dict], None], config):
        """
        Establish a connection to Deepgram's live transcription WebSocket.
        """
        try:
            socket = await self.client.transcription.live(config)
            # You need to provide a handler function here, not just the event
            socket.registerHandler(socket.event.CLOSE, lambda c: logger.info(f"Connection closed with code {c}."))
            socket.registerHandler(socket.event.TRANSCRIPT_RECEIVED, transcript_received_handler)

            return socket
        except Exception as e:
            raise
