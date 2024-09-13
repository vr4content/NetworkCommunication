import tkinter as tk
from tkinter import ttk
import numpy as np
import time
import socket
from datetime import datetime
from lsl_streams_handler import LSLStreamHandler
import threading
import sys

# Function to get local IP address
def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Unknown IP"

# List of MetaHuman face expression features
face_features = [
    "brow_inner_up", "brow_down_left", "brow_down_right", "brow_outer_up_left", 
    "brow_outer_up_right", "cheek_puff", "cheek_squint_left", "cheek_squint_right",
    "eye_blink_left", "eye_blink_right", "eye_look_down_left", "eye_look_down_right", 
    "eye_look_in_left", "eye_look_in_right", "eye_look_out_left", "eye_look_out_right", 
    "eye_look_up_left", "eye_look_up_right", "eye_squint_left", "eye_squint_right", 
    "eye_wide_left", "eye_wide_right", "jaw_forward", "jaw_left", "jaw_open", "jaw_right",
    "mouth_close", "mouth_dimple_left", "mouth_dimple_right", "mouth_frown_left", 
    "mouth_frown_right", "mouth_funnel", "mouth_left", "mouth_lower_down_left", 
    "mouth_lower_down_right", "mouth_press_left", "mouth_press_right", "mouth_pucker", 
    "mouth_right", "mouth_roll_lower", "mouth_roll_upper", "mouth_shrug_lower", 
    "mouth_shrug_upper", "mouth_smile_left", "mouth_smile_right", "mouth_stretch_left", 
    "mouth_stretch_right", "mouth_upper_up_left", "mouth_upper_up_right", 
    "nose_sneer_left", "nose_sneer_right"
]

# Tkinter UI class
class FloatTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MetaHuman Face Feature Float Test")
        self.stream_handler = LSLStreamHandler()

        # Create UI elements
        self.create_widgets()

        # Variables for sine wave generation
        self.frequency = 1.0
        self.samples_per_second = 24
        self.running = False
        self.thread = None

        # Handle the window close event to clean up resources
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        # Frame for system info
        system_frame = ttk.Frame(self.root, padding="10")
        system_frame.grid(row=0, column=0, padx=10, pady=10, sticky="W")

        # IP label
        self.ip_label = ttk.Label(system_frame, text=f"Local IP: {get_local_ip()}")
        self.ip_label.grid(row=0, column=0, sticky="W")

        # System clock label
        self.clock_label = ttk.Label(system_frame, text="System Clock: 00:00:00:000")
        self.clock_label.grid(row=1, column=0, sticky="W")

        # Frame for parameters input
        param_frame = ttk.Frame(self.root, padding="10")
        param_frame.grid(row=1, column=0, padx=10, pady=10, sticky="W")

        # Samples per second input
        ttk.Label(param_frame, text="Samples Per Second:").grid(row=0, column=0, sticky="W")
        self.samples_entry = ttk.Entry(param_frame, width=10)
        self.samples_entry.grid(row=0, column=1, sticky="W")
        self.samples_entry.insert(0, "24")

        # Frequency input
        ttk.Label(param_frame, text="Frequency:").grid(row=1, column=0, sticky="W")
        self.frequency_entry = ttk.Entry(param_frame, width=10)
        self.frequency_entry.grid(row=1, column=1, sticky="W")
        self.frequency_entry.insert(0, "1")

        # Start and Stop buttons
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=3, column=0, padx=10, pady=10, sticky="W")

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_stream)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_stream)
        self.stop_button.grid(row=0, column=1, padx=5)
        self.stop_button["state"] = "disabled"

        # Update clock every 100ms
        self.update_clock()

    def update_clock(self):
        now = datetime.now()
        self.clock_label.config(text=f"System Clock: {now.strftime('%H:%M:%S:%f')[:-3]}")
        self.root.after(100, self.update_clock)

    def generate_sine_wave(self):
        # Parse user inputs
        self.frequency = float(self.frequency_entry.get())
        self.samples_per_second = float(self.samples_entry.get())
        time_step = 1 / self.samples_per_second

        start_time = time.time()

        # Create and register float streams for each face feature
        for feature in face_features:
            self.stream_handler.create_float_stream(name=feature, stream_type="FaceFeature", channel_id=feature, sampling_rate=self.samples_per_second)

        try:
            while self.running:
                elapsed_time = time.time() - start_time

                for feature in face_features:
                    # Generate sine wave values for each face feature (amplitude 0-1)
                    value = 0.5 * (1 + np.sin(2 * np.pi * self.frequency * elapsed_time))

                    # Push the float data to the LSL stream
                    self.stream_handler.push_float_data(channel_id=feature, value=value)

                # Sleep to maintain the sample rate
                time.sleep(time_step)
        except Exception as e:
            print(f"Error during sine wave generation: {e}")
        finally:
            self.stream_handler.stop_all_streams()

    def start_stream(self):
        self.running = True
        self.thread = threading.Thread(target=self.generate_sine_wave)
        self.thread.start()
        self.start_button["state"] = "disabled"
        self.stop_button["state"] = "normal"

    def stop_stream(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()
        self.stream_handler.stop_all_streams()
        self.start_button["state"] = "normal"
        self.stop_button["state"] = "disabled"

    def on_close(self):
        """Handle window close to ensure resources are freed."""
        self.stop_stream()
        self.root.destroy()

# Global exception handler to ensure cleanup on unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    print(f"Unhandled exception: {exc_value}")
    if app:
        app.stop_stream()
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = handle_exception

# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = FloatTestApp(root)
    root.mainloop()
