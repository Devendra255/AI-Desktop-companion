import pyaudio
import numpy as np
import keyboard
from faster_whisper import WhisperModel
import threading
import time
from collections import deque

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
MIN_RECORD_DURATION = 0.3  # 300 milliseconds minimum
DEBOUNCE_TIME = 0.1  # 100ms

class VoiceRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = deque()
        self.is_recording = False
        self.lock = threading.Lock()
        self.model = WhisperModel("large", device="cuda", compute_type="float32")
        # Or use this for CPU-only:
        # self.model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
        self.last_event_time = 0
        self.transcription = ""
        self.audio_data = b""

    def start_recording(self):
        self.transcription = ""
        with self.lock:
            if self.is_recording:
                return

            self.frames.clear()
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE,
                stream_callback=self.audio_callback,
                start=False
            )
            self.stream.start_stream()
            self.is_recording = True
            print("Recording started...")

    def stop_recording(self):
        with self.lock:
            if not self.is_recording:
                return

            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            
            self.audio_data = b''.join(self.frames)
            if not self.audio_data:
                print("No audio captured")
                return

            # Calculate actual audio duration
            duration = len(self.audio_data) / (SAMPLE_RATE * 2)  # 2 bytes per sample
            if duration < MIN_RECORD_DURATION:
                print(f"Too short ({duration:.2f}s), ignoring")
                return

            print(f"Processing {duration:.2f}s audio...")
            # self.process_audio(self.audio_data) # run only in local
            return self.audio_data

    def audio_callback(self, in_data, frame_count, time_info, status):
        self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    def process_audio(self, audio_data):
        try:
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            segments, info = self.model.transcribe(
                audio_np,
                language="en",
                vad_filter=True,
                beam_size=5
            )
            
            self.transcription = " ".join(segment.text.strip() for segment in segments)
            print("\nTranscription:", self.transcription)
            return " ".join(segment.text.strip() for segment in segments)
        except Exception as e:
            print(f"Error: {str(e)}")

def key_handler(recorder):
    def handle_key(event):
        if event.event_type == keyboard.KEY_DOWN and event.name == 'v':
            if time.time() - recorder.last_event_time > DEBOUNCE_TIME:
                recorder.last_event_time = time.time()
                threading.Thread(target=recorder.start_recording).start()
        
        elif event.event_type == keyboard.KEY_UP and event.name == 'v':
            recorder.last_event_time = time.time()
            threading.Thread(target=recorder.stop_recording).start()

    keyboard.hook(handle_key)

if __name__ == "__main__":
    recorder = VoiceRecorder()
    key_handler(recorder)
    
    print("Press & hold 'v' to record. Works in background.")
    print("Release 'v' to transcribe. Ctrl+C to exit.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        recorder.audio.terminate()