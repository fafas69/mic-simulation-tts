import wave
import sounddevice as sd
import scipy.io.wavfile as wav
import sys
import time
from pathlib import Path
from pypipertts import PyPiper

# Find the ID of 'VoiceMeeter Input (VB-Audio Virtual VAIO)'
devices = sd.query_devices()
vm_input_name = "VoiceMeeter Input (VB-Audio VoiceMeeter VAIO)"
vm_input_id = 37
for i, dev in enumerate(devices):
    if vm_input_name in dev["name"]:
        vm_input_id = i
        break

if vm_input_id is None:
    print("VoiceMeeter Input not found.")
    sys.exit()


# Get the path of the current script (inside /src)
current_path = Path(__file__).resolve()

# Go up one level to the project root, then into the target folder
# Example: Project/data/config.json
model_path = current_path.parent.parent / "piper-models/en-US/ryan/low/en_US-ryan-low.onnx"

def get_wav_file_duration(wav_file_path : str | Path):
    with wave.open(wav_file_path, 'r') as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        
    return duration

piper = PyPiper()

def simulate_audio_file(filename : str | Path):
    fs, data = wav.read(filename)
    print(f"Streaming {filename} to VoiceMeeter...")
    # Play the sound to the VoiceMeeter virtual input
    sd.play(data, fs, device=vm_input_id)
    sd.wait()

def TTS(text : str, output_file : Path | str):
    start_time = time.perf_counter()

    streamed_audio = piper.tts(text, output_file)

    end_time = time.perf_counter()

    print(f"Elapsed time : {end_time - start_time}. RTF : {(end_time - start_time) / get_wav_file_duration(output_file)}")

    simulate_audio_file(output_file)

#TTS("Fuck you luis, you piece of shit.", "output.wav")
TTS("Fuck you luis, you piece of shit", "output.wav")