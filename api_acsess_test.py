import requests
import sounddevice as sd
import numpy as np
import wave
import io
import speek2

# API endpoint
# API_URL = "http://localhost:7851/process"
API_URL = "https://b863-152-58-47-220.ngrok-free.app/"+"process" # ngrok forwarding port 7853

# Audio recording settings
SAMPLE_RATE = 16000  # 16kHz, matching Whisper's recommended rate
CHANNELS = 1
DURATION = 5  # Recording duration in seconds


def record_audio(duration=DURATION, sample_rate=SAMPLE_RATE, channels=CHANNELS):
    """Records audio for a given duration and returns it as a WAV file in memory."""
    print("Recording... Speak now!")
    
    # Record audio
    audio_data = sd.rec(
        int(duration * sample_rate), 
        samplerate=sample_rate, 
        channels=channels, 
        dtype=np.int16
    )
    sd.wait()  # Wait until recording is finished
    print("Recording complete.")

    # Save to an in-memory WAV file
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit audio (2 bytes per sample)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

    buffer.seek(0)  # Reset buffer position
    return buffer


def send_audio_to_api(audio_buffer):
    """Sends recorded audio to the API and prints the response."""
    files = {"audio": ("recorded_audio.wav", audio_buffer, "audio/wav")}
    response = requests.post(API_URL, files=files)

    if response.status_code == 200:
        response.raise_for_status()
        stream_iterator = response.iter_content(chunk_size=1024)
        for chunk in stream_iterator:
            speek2.play_audio_stream(chunk)

    else:
        print(f"Error: {response.status_code} - {response.json()['detail']}")


if __name__ == "__main__":
    audio_buffer = record_audio()
    send_audio_to_api(audio_buffer)
