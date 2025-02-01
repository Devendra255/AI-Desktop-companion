# api.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import speech
import brain
import uvicorn
from typing import Optional

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessResponse(BaseModel):
    transcription: str
    ai_response: str

# Initialize the Whisper model from speech.py
transcriber = speech.VoiceRecorder()

@app.post("/process")
async def process_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = "en"
) -> ProcessResponse:
    """Endpoint that handles both transcription and AI response"""
    try:
        # Read and convert audio file
        audio_data = await audio.read()
        
        # Convert audio to numpy array (assuming 16kHz, 16-bit PCM mono audio)
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        # Transcribe using Whisper
        segments, info = transcriber.model.transcribe(
            audio_np,
            language=language,
            vad_filter=True,
            beam_size=5
        )
        
        transcription = " ".join(segment.text.strip() for segment in segments)
        
        if not transcription:
            raise HTTPException(status_code=400, detail="No speech detected")

        # Get AI response
        response = brain.ask(transcription)
        
        return ProcessResponse(
            transcription=transcription,
            ai_response=response
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7853)