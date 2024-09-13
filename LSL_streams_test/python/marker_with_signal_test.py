import tkinter as tk
from tkinter import ttk
import random
import time
import threading
import socket
import math
from datetime import datetime
from lsl_streams_handler import LSLStreamHandler
import sys

# Function to get local IP address
def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Unknown IP"

# Tkinter UI class
class MarkerFloatTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scene Events Marker and Float Test")
        self.stream_handler = LSLStreamHandler()

        # Create UI elements
        self.create_widgets()

        # Variables for event generation
        self.min_delay = 1.0
        self.max_delay = 5.0
        self.running = False
        self.marker_thread = None
        self.float_thread = None

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

        # Minimum delay input
        ttk.Label(param_frame, text="Min Delay (seconds):").grid(row=0, column=0, sticky="W")
        self.min_delay_entry = ttk.Entry(param_frame, width=10)
        self.min_delay_entry.grid(row=0, column=1, sticky="W")
        self.min_delay_entry.insert(0, "1.0")

        # Maximum delay input
        ttk.Label(param_frame, text="Max Delay (seconds):").grid(row=1, column=0, sticky="W")
        self.max_delay_entry = ttk.Entry(param_frame, width=10)
        self.max_delay_entry.grid(row=1, column=1, sticky="W")
        self.max_delay_entry.insert(0, "5.0")

        # Amplitude input for float stream
        ttk.Label(param_frame, text="Amplitude:").grid(row=2, column=0, sticky="W")
        self.amplitude_entry = ttk.Entry(param_frame, width=10)
        self.amplitude_entry.grid(row=2, column=1, sticky="W")
        self.amplitude_entry.insert(0, "100")

        # Frequency input for float stream
        ttk.Label(param_frame, text="Frequency (Hz):").grid(row=3, column=0, sticky="W")
        self.frequency_entry = ttk.Entry(param_frame, width=10)
        self.frequency_entry.grid(row=3, column=1, sticky="W")
        self.frequency_entry.insert(0, "1.0")

        # Samples per second input for float stream
        ttk.Label(param_frame, text="Samples Per Second:").grid(row=4, column=0, sticky="W")
        self.sps_entry = ttk.Entry(param_frame, width=10)
        self.sps_entry.grid(row=4, column=1, sticky="W")
        self.sps_entry.insert(0, "30")

        # Start and Stop buttons
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=5, column=0, padx=10, pady=10, sticky="W")

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_streams)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_streams)
        self.stop_button.grid(row=0, column=1, padx=5)
        self.stop_button["state"] = "disabled"

        # Update clock every 100ms
        self.update_clock()

    def update_clock(self):
        now = datetime.now()
        self.clock_label.config(text=f"System Clock: {now.strftime('%H:%M:%S:%f')[:-3]}")
        self.root.after(100, self.update_clock)

    def generate_marker_events(self):
        # Parse user inputs
        self.min_delay = float(self.min_delay_entry.get())
        self.max_delay = float(self.max_delay_entry.get())

        counter = 1

        # Create and register the marker stream for scene events
        self.stream_handler.create_marker_stream(name="SceneEvents", stream_type="Markers", channel_id="SceneEvents")

        try:
            while self.running:
                # Generate key-value pair
                key = f"key_{counter}"
                value = f"value for {key}"

                # Push marker data to the LSL stream
                self.stream_handler.push_marker_data(channel_id="SceneEvents", key=key, value=value)

                # Increment counter for the next event
                counter += 1

                # Sleep for a random time between min and max delay
                delay = random.uniform(self.min_delay, self.max_delay)
                time.sleep(delay)
        except Exception as e:
            print(f"Error during marker event generation: {e}")
        finally:
            self.stream_handler.stop_all_streams()

    def generate_float_wave(self):
        # Parse user inputs
        amplitude = float(self.amplitude_entry.get())
        frequency = float(self.frequency_entry.get())
        samples_per_second = int(self.sps_entry.get())

        # Create and register the float stream
        self.stream_handler.create_float_stream(name="FloatStream", stream_type="Float", channel_id="FloatStream", sampling_rate=samples_per_second)

        t = 0.0
        try:
            while self.running:
                # Generate sine wave data
                value = amplitude * math.sin(2 * math.pi * frequency * t)
                self.stream_handler.push_float_data(channel_id="FloatStream", value=value)

                # Increment time step
                t += 1 / samples_per_second
                time.sleep(1 / samples_per_second)
        except Exception as e:
            print(f"Error during float data generation: {e}")
        finally:
            self.stream_handler.stop_all_streams()

    def start_streams(self):
        self.running = True

        # Start marker stream thread
        self.marker_thread = threading.Thread(target=self.generate_marker_events)
        self.marker_thread.start()

        # Start float stream thread
        self.float_thread = threading.Thread(target=self.generate_float_wave)
        self.float_thread.start()

        self.start_button["state"] = "disabled"
        self.stop_button["state"] = "normal"

    def stop_streams(self):
        self.running = False
        if self.marker_thread is not None:
            self.marker_thread.join()
        if self.float_thread is not None:
            self.float_thread.join()
        self.stream_handler.stop_all_streams()
        self.start_button["state"] = "normal"
        self.stop_button["state"] = "disabled"

    def on_close(self):
        """Handle window close to ensure resources are freed."""
        self.stop_streams()
        self.root.destroy()

# Global exception handler to ensure cleanup on unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    print(f"Unhandled exception: {exc_value}")
    if app:
        app.stop_streams()
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = handle_exception

# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = MarkerFloatTestApp(root)
    root.mainloop()
