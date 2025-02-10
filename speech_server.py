# api.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import numpy as np
import speech
import brain
import uvicorn
from typing import Optional
import requests
# import speek2

app = FastAPI()

# The URL of your TTS API endpoint (adjust if needed)
api_url = "http://127.0.0.1:9880/tts"

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Whisper model from speech.py
transcriber = speech.VoiceRecorder()

def stream_tts_audio(api_url: str, params: dict):
    """
    Calls the TTS API in streaming mode and returns a generator yielding audio chunks.
    
    Args:
        api_url (str): The TTS API endpoint URL.
        params (dict): The query parameters required by the TTS API.
    
    Returns:
        generator: Yields raw audio data chunks.
    """
    response = requests.get(api_url, params=params, stream=True)
    response.raise_for_status()
    # Return a generator that yields chunks of audio (e.g., 1024 bytes each)
    return response.iter_content(chunk_size=1024)

@app.post("/process")
async def process_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = "en"
):
    """
    Endpoint that:
      1. Receives an uploaded audio file.
      2. Transcribes the audio using Whisper.
      3. Gets an AI response via brain.ask.
      4. Calls the TTS API to synthesize the AI response into speech.
      5. Streams the synthesized audio (live audio) back to the client.
    """
    try:
        # Read and convert the uploaded audio file
        audio_data = await audio.read()
        # Convert to a NumPy array (assuming 16kHz, 16-bit PCM mono audio)
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        # Transcribe using the Whisper model
        segments, info = transcriber.model.transcribe(
            audio_np,
            language=language,
            vad_filter=True,
            beam_size=5
        )
        transcription = " ".join(segment.text.strip() for segment in segments)
        if not transcription:
            raise HTTPException(status_code=400, detail="No speech detected")

        # Get AI response based on the transcription
        ai_response = brain.ask(transcription)

        # Prepare parameters for the TTS API call
        # (Change "ref_audio_path" and "aux_ref_audio_paths" as needed.)
        tts_params = {
            "text": ai_response,         # the text to be synthesized
            "text_lang": "en",           # language for TTS
            "ref_audio_path": "sayu.ogg",  # reference audio file (must exist on TTS server)
            "prompt_text": "Recon confirms, no sign of the shrine maiden within a 3-mile radius. Moving to the next phase",
            "prompt_lang": "en",
            "text_split_method": "cut5",
            "batch_size": 1,
            "media_type": "wav",
            "streaming_mode": True,      # enable live streaming from the TTS API
            "aux_ref_audio_paths": [
                "VO_Sayu_Good_Afternoon.ogg",
                "VO_Sayu_Good_Morning.ogg",
                "VO_Sayu_When_the_Wind_Is_Blowing.ogg",
                "VO_Sayu_When_Thunder_Strikes.ogg"
            ]
        }

        # Call the TTS API to get a streaming generator of audio data
        audio_gen = stream_tts_audio(api_url, tts_params)
        
        # Return the audio stream to the client.
        # The client will receive a continuous audio/wav stream.
        return StreamingResponse(audio_gen, media_type="audio/wav")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7853)
