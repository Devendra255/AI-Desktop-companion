import requests
import sounddevice as sd
import time
from collections import deque
import threading

# Global buffer to store audio chunks
audio_buffer = deque()
buffer_lock = threading.Lock()

# Flag to signal when playback is complete
done = threading.Event()

# Function to stream audio in real-time using SoundDevice's RawOutputStream
def stream_audio(streaming_url, audio_stream, sample_rate=26000):
    """Streams and plays audio data in real-time."""
    try:
        # Fetch the audio stream from the TTS API
        response = requests.get(streaming_url, stream=True)
        response.raise_for_status()
        first_chunk = True

        print("Streaming audio...")
        for chunk in response.iter_content(chunk_size=2048):  # Adjust chunk size as needed
            if first_chunk:
                first_chunk = False
            else:
                if chunk:  # If the chunk contains data
                    with buffer_lock:
                        # Add chunk to the global buffer
                        audio_buffer.append(chunk)
                        audio_stream.write(chunk)

    except requests.RequestException as e:
        print(f"Error during audio streaming: {e}")

# Function to continuously play audio from the global buffer
def play_audio_from_buffer(sample_rate=26000):
    """Plays audio in real-time from the buffer while new data is being streamed."""
    with sd.RawOutputStream(samplerate=sample_rate, channels=1, dtype='int16') as audio_stream:
        while not done.is_set() or audio_buffer:
            with buffer_lock:
                if audio_buffer:
                    chunk = audio_buffer.popleft()
                    audio_stream.write(chunk)
            time.sleep(0.002)  # Prevents excessive CPU usage

# Function to handle TTS playback sequentially
# def tts_play(text_array, sample_rate=26000):
#     voice = "female_01.wav"
#     output_file = "stream_output.wav"
#     language = "en"

#     # Start the playback thread
#     play_thread = threading.Thread(target=play_audio_from_buffer, args=(sample_rate,))
#     play_thread.start()

#     # Stream each sentence sequentially (one at a time)
#     for num, text in enumerate(text_array):
#         encoded_text = requests.utils.quote(text)
#         streaming_url = f"http://localhost:7851/api/tts-generate-streaming?text={encoded_text}&voice={voice}&language={language}&output_file={output_file}"
        
#         print(f"Playing {num + 1}/{len(text_array)}: {text}")
#         stream_audio(streaming_url)  # Stream one sentence at a time

#     # Signal that all audio has been streamed
#     done.set()

#     # Wait for playback to finish
#     play_thread.join()
#     print("Finished playing all text.")

def tts_play(text_array, sample_rate=26000):
    voice = "female_01.wav"
    output_file = "stream_output.wav"
    language = "en"

    # Create a persistent RawOutputStream
    with sd.RawOutputStream(samplerate=sample_rate, channels=1, dtype='int16') as audio_stream:
        for num, text in enumerate(text_array):
            encoded_text = requests.utils.quote(text)
            streaming_url = f"http://localhost:7851/api/tts-generate-streaming?text={encoded_text}&voice={voice}&language={language}&output_file={output_file}"
            print(f"Playing text {num + 1}/{len(text_array)}: {text}")
            # Stream audio for the current text
            stream_audio(streaming_url, audio_stream, sample_rate)


if __name__ == "__main__":
    # Example text input
    sample = """ My mother was the most incredible person. She was always so dignified and elegant, always smiling, no matter what situation she might be facing. She had so much to deal with in the clan on so many levels, but she took it all in stride. it was like nothing could ever faze her. Everything about her was perfect, and I say that without exaggerating. *sigh* But the moment she passed away, I realized... I couldn't hide behind my mother any longer. I wasn't little Ayaka any more."""
    
    # Split the text into sentences
    split_text = [sentence.strip() for sentence in sample.replace("\n", " ").split(". ") if sentence.strip()]
    
    # Start TTS playback
    tts_play(split_text)
