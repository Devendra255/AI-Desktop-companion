import requests
import sounddevice as sd
import time
from collections import deque
import threading

class TTSSpeaker:
    def __init__(self):
        self.audio_buffer = deque()
        self.buffer_lock = threading.Lock()
        self.done = threading.Event()
        self.playback_active = False
        self.current_stream_thread = None
        self.api = "https://2d82-152-58-47-220.ngrok-free.app/"

    def stream_audio(self, streaming_url):
        """Streams audio data from TTS API"""
        try:
            response = requests.get(streaming_url, stream=True)
            response.raise_for_status()
            
            for chunk in response.iter_content(chunk_size=2048):
                if chunk and self.playback_active:
                    with self.buffer_lock:
                        self.audio_buffer.append(chunk)
                else:
                    break

        except requests.RequestException as e:
            print(f"Error during audio streaming: {e}")

    def play_audio_from_buffer(self, sample_rate=26000):
        """Plays audio from buffer continuously"""
        with sd.RawOutputStream(samplerate=sample_rate, channels=1, dtype='int16') as audio_stream:
            while self.playback_active or self.audio_buffer:
                with self.buffer_lock:
                    if self.audio_buffer:
                        chunk = self.audio_buffer.popleft()
                        audio_stream.write(chunk)
                time.sleep(0.002)

    def tts_play(self, text_array, sample_rate=26000):
        """Handles complete TTS playback sequence"""
        # Stop any existing playback
        self.playback_active = False
        if self.current_stream_thread and self.current_stream_thread.is_alive():
            self.current_stream_thread.join()

        # Reset state for new playback
        self.playback_active = True
        self.done.clear()
        with self.buffer_lock:
            self.audio_buffer.clear()

        # Start playback thread
        play_thread = threading.Thread(target=self.play_audio_from_buffer, args=(sample_rate,))
        play_thread.start()

        # Process each text segment
        voice = "female_01.wav"
        output_file = "stream_output.wav"
        language = "en"

        for num, text in enumerate(text_array):
            if not self.playback_active:
                break
            
            print(f"Playing {num + 1}/{len(text_array)}: {text}")    
            encoded_text = requests.utils.quote(text)
            streaming_url = f"{self.api}/api/tts-generate-streaming?text={encoded_text}&voice={voice}&language={language}&output_file={output_file}"
            
            # Start streaming in separate thread
            self.current_stream_thread = threading.Thread(target=self.stream_audio, args=(streaming_url,))
            self.current_stream_thread.start()
            self.current_stream_thread.join()  # Wait for this stream to complete

        # Cleanup
        self.playback_active = False
        play_thread.join()
        print("Finished playing all text.")

# Create a global instance
tts_speaker = TTSSpeaker()

def tts_play(text_array):
    tts_speaker.tts_play(text_array)