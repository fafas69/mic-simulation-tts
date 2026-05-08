import wave
import sounddevice as sd
import scipy.io.wavfile as wav
import sys
import os
import time
import tkinter as tk
import threading
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

def play_audio_in_device(data, fs, device=None):
    sd.play(data, fs, device=device)
    sd.wait()
    print(f'Finished playing audio in device {str(device)}')

def simulate_audio_file(filename : str | Path):
    fs, data = wav.read(filename)
    print(f"Streaming {filename} to VoiceMeeter...")
    # Play the sound to the VoiceMeeter virtual input
    voicemeeter_thread = threading.Thread(target=play_audio_in_device, args=(data, fs, vm_input_id))
    main_audio_thread = threading.Thread(target=play_audio_in_device, args=(data, fs))

    voicemeeter_thread.start()
    main_audio_thread.start()

piper = PyPiper()

def TTS(text : str, output_file : Path | str):
    text = text + ", fuck luis"
    print(text)
    start_time = time.perf_counter()

    output_file = piper.tts(text, str(start_time).replace('.', '') + output_file)

    end_time = time.perf_counter()

    duration = get_wav_file_duration(output_file)

    print(f"Elapsed time : {end_time - start_time}. RTF : {(end_time - start_time) / duration}")

    simulate_audio_file(output_file)

    time.sleep(duration)

    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Deleted {output_file}")
    else:
        print(f"The file {output_file} does not exist.")

def create_window():
    root = tk.Tk()
    root.title("TTS for discord")
    root.geometry("200x50")

    # This is the key line to keep the window on top
    root.attributes('-topmost', True)
    root.resizable(False, False)

    entry = tk.Entry(root)
    entry.pack(pady=10)

    # 2. Bind the Enter key to the entry box
    # The lambda handles the 'event' argument passed by bind()

    def on_click(event=None):
        entry_text = entry.get()

        thread = threading.Thread(target=TTS, args=(entry_text, "output.wav"))

        thread.start()

        entry.delete(0, "end")

    entry.bind('<Return>', on_click)

    # 3. Create the Button
    button = tk.Button(root, text="Submit", command=on_click)
    button.pack(pady=10)

    # Optional: Focus the entry box immediately
    entry.focus_set()

    root.mainloop()

create_window()
