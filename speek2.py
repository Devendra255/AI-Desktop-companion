import requests
import pyaudio
import wave
from io import BytesIO

def stream_tts_audio(api_url, params):
    """
    Call the TTS API in streaming mode and yield audio chunks.

    Args:
        api_url (str): The full URL of the TTS endpoint (e.g., "http://127.0.0.1:9880/tts").
        params (dict): Query parameters required by the API.

    Yields:
        bytes: Chunks of audio data from the response.
    
    Note:
        When using media_type "wav" with streaming_mode True, the first chunk is expected to be a WAV header.
    """
    print("Requesting streaming TTS from API...")
    response = requests.get(api_url, params=params, stream=True)
    response.raise_for_status()
    stream_iterator = response.iter_content(chunk_size=1024)
    for chunk in stream_iterator:
        yield chunk

def play_audio_stream(audio_stream_generator):
    """
    Play audio data from a streaming generator using PyAudio.

    This function expects the first chunk from the generator to be a valid WAV header
    which is used to extract playback parameters.

    Args:
        audio_stream_generator (generator): A generator yielding audio data (bytes).
    """
    # Retrieve the WAV header (first chunk)
    try:
        wav_header = next(audio_stream_generator)
    except StopIteration:
        print("No audio data received from the stream.")
        return

    # Parse the WAV header to extract audio parameters
    try:
        header_io = BytesIO(wav_header)
        with wave.open(header_io, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            sample_rate = wav_file.getframerate()
            sample_width = wav_file.getsampwidth()
        print(f"Audio parameters: Channels={channels}, Sample Rate={sample_rate} Hz, Sample Width={sample_width} bytes")
    except Exception as e:
        print("Error parsing WAV header:", e)
        return

    # Initialize PyAudio with parameters obtained from the WAV header.
    p = pyaudio.PyAudio()
    # Map sample width (in bytes) to PyAudio format.
    format_map = {1: pyaudio.paInt8, 2: pyaudio.paInt16, 4: pyaudio.paInt32}
    if sample_width not in format_map:
        print("Unsupported sample width:", sample_width)
        return
    audio_format = format_map[sample_width]

    stream_out = p.open(format=audio_format,
                        channels=channels,
                        rate=sample_rate,
                        output=True)

    print("Starting live audio playback...")
    try:
        # Do not write the header to the output; use it only to configure playback.
        for chunk in audio_stream_generator:
            if chunk:
                stream_out.write(chunk)
    except Exception as e:
        print("Error during audio streaming:", e)
    finally:
        stream_out.stop_stream()
        stream_out.close()
        p.terminate()
        print("Audio playback finished.")

# Example usage (for testing or direct execution)
if __name__ == "__main__":
    # API endpoint (adjust host/port as needed)
    api_url = "http://127.0.0.1:9880/tts"
    text = "honestly, i don't really know... i'm more of a 'watch someone else code' kinda person... but if we have to choose, can we just pick one that's not too hard?"
    
    # Parameters for synthesis (ensure the reference audio exists on the server)
    params = {
        "text": text,
        "text_lang": "en",
        "ref_audio_path": "sayu.ogg",  # change to your reference audio file path
        "prompt_text": "Recon confirms, no sign of the shrine maiden within a 3-mile radius. Moving to the next phase",
        "prompt_lang": "en",
        "text_split_method": "cut5",
        "batch_size": 1,
        "media_type": "wav",
        "streaming_mode": True,  # enable live streaming
        "aux_ref_audio_paths": ["VO_Sayu_Good_Afternoon.ogg", "VO_Sayu_Good_Morning.ogg", "VO_Sayu_When_the_Wind_Is_Blowing.ogg", "VO_Sayu_When_Thunder_Strikes.ogg"]
    }

    # Get the streaming audio generator from the API.
    audio_gen = stream_tts_audio(api_url, params)
    
    # Play the audio stream.
    play_audio_stream(audio_gen)
