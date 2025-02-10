import speech
import api_acsess_test

import wave

with wave.open('/home/devendra/Desktop/female_03.wav', 'rb') as f:
    audio_data = f.readframes(f.getnframes())  # Read only audio frames
    api_acsess_test.send_audio_to_api(audio_buffer=audio_data)