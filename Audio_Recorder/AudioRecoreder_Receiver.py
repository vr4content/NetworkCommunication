import socket
import pyaudio
import wave
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import json
import re

# Initialize variables
recording = False
frames = []
file_path = ""
filename = ""
listening = False
audio_thread = None
config_file = "config.json"

# UDP Setup
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("127.0.0.1", 12345))

# Function to load the last selected folder
def load_last_folder():
    global file_path
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            if 'last_folder' in config and os.path.isdir(config['last_folder']):
                file_path = config['last_folder']
                folder_label.config(text=file_path)
                path_button.config(bg="green")
                return True
    return False

# Function to save the selected folder
def save_folder(path):
    with open(config_file, 'w') as f:
        json.dump({'last_folder': path}, f)

# Function to start/stop listening
def toggle_listening():
    global listening
    if not file_path:
        messagebox.showerror("Path Error", "Please select an output folder first.")
        path_button.config(bg="red")
        return

    if not listening:
        listening_status.config(text="Listening", bg="green", fg="white", font=("Helvetica", 16, "bold"))
        root.after(100, listen_for_commands)
    else:
        listening_status.config(text="Not Listening", bg="red", fg="white", font=("Helvetica", 16, "bold"))

    listening = not listening

# Function to listen for start/stop commands
def listen_for_commands():
    global recording, frames, filename
    try:
        udp_socket.settimeout(0.1)
        message, addr = udp_socket.recvfrom(1024)
        print("message received... ")
        print(message.decode())
        message = message.decode().split(':')
        if "start" in message[0]:
            filename = re.sub(r'[^\w\-_\. ]', '', message[1])  # Allow only valid filename characters
            filename_display.config(text=filename)  # Update the filename display
            start_recording()
        elif "stop" in message[0]:
            stop_recording()
    except socket.timeout:
        pass

    if listening:
        root.after(100, listen_for_commands)

# Function to start recording audio
def start_recording():
    global frames, recording, audio_thread
    audio_status_label.config(text="Recording...", bg="green", fg="white", font=("Helvetica", 16, "bold"))
    recording = True
    frames = []
    # Start a new thread for audio recording
    audio_thread = threading.Thread(target=record_audio)
    audio_thread.start()
    flash_recording()

def flash_recording():
    if recording:
        current_color = audio_status_label.cget("bg")
        new_color = "green" if current_color == "white" else "white"
        audio_status_label.config(bg=new_color)
        root.after(500, flash_recording)

# Function to record audio in a separate thread
def record_audio():
    global frames, recording, stream
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    while recording:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        except OSError as e:
            print(f"Error reading stream: {e}")

# Function to stop recording and save file
def stop_recording():
    global recording
    if not recording:
        return

    recording = False
    audio_thread.join()  # Wait for the audio thread to finish
    stream.stop_stream()
    stream.close()

    # Save the recorded audio to a file
    output_filename = os.path.join(file_path, filename + ".wav")
    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    audio_status_label.config(text="Not Recording", bg="red", fg="white")

# Select folder function
def select_folder():
    global file_path
    file_path = filedialog.askdirectory()
    folder_label.config(text=file_path)
    if file_path:
        path_button.config(bg="green")
        save_folder(file_path)
    else:
        path_button.config(bg="red")

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
audio = pyaudio.PyAudio()

# Tkinter setup
root = tk.Tk()
root.title("AudioRecorder (Receiver)")

# Large title label
tk.Label(root, text="AudioRecorder (Receiver)", font=("Helvetica", 24, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

# Local IP display
tk.Label(root, text="Local IP:").grid(row=1, column=0)
local_ip_label = tk.Label(root, text=socket.gethostbyname(socket.gethostname()))
local_ip_label.grid(row=1, column=1)

# Filename display (updated dynamically from UDP message)
tk.Label(root, text="Filename:").grid(row=2, column=0)
filename_display = tk.Label(root, text="Waiting for filename...")
filename_display.grid(row=2, column=1)

# Output folder selection
tk.Label(root, text="Output folder:").grid(row=3, column=0)
folder_label = tk.Label(root, text="No folder selected")
folder_label.grid(row=3, column=1)
path_button = tk.Button(root, text="Select folder", command=select_folder)
path_button.grid(row=3, column=2)
path_button.config(bg="red")

# Start/Stop listening button
listening_status = tk.Label(root, text="Not Listening", bg="red", fg="white", font=("Helvetica", 16, "bold"))
listening_status.grid(row=4, column=0, columnspan=2)

start_stop_button = tk.Button(root, text="Start/Stop Listening", command=toggle_listening)
start_stop_button.grid(row=5, column=0, columnspan=2)

# Recording status
audio_status_label = tk.Label(root, text="Not Recording", bg="red", fg="white", font=("Helvetica", 16, "bold"))
audio_status_label.grid(row=6, column=0, columnspan=2)

# Load last folder and auto start listening if valid
if load_last_folder():
    toggle_listening()

root.mainloop()
