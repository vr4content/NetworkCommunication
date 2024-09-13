import tkinter as tk
from tkinter import ttk
from random import randint
import time
from datetime import datetime
from lsl_streams_handler import LSLStreamHandler
import threading
import sys

# Tkinter UI class for string stream test
class StringStreamTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("String Stream Event Test")
        self.stream_handler = LSLStreamHandler()

        # Variables for event generation
        self.min_interval = 1
        self.max_interval = 5
        self.running = False
        self.thread = None

        # UI Elements
        self.create_widgets()

        # Handle the window close event to clean up resources
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        # Frame for parameters input
        param_frame = ttk.Frame(self.root, padding="10")
        param_frame.grid(row=0, column=0, padx=10, pady=10, sticky="W")

        # Minimum interval input
        ttk.Label(param_frame, text="Min Time Between Events (s):").grid(row=0, column=0, sticky="W")
        self.min_interval_entry = ttk.Entry(param_frame, width=10)
        self.min_interval_entry.grid(row=0, column=1, sticky="W")
        self.min_interval_entry.insert(0, "1")

        # Maximum interval input
        ttk.Label(param_frame, text="Max Time Between Events (s):").grid(row=1, column=0, sticky="W")
        self.max_interval_entry = ttk.Entry(param_frame, width=10)
        self.max_interval_entry.grid(row=1, column=1, sticky="W")
        self.max_interval_entry.insert(0, "5")

        # Last event display
        ttk.Label(param_frame, text="Last Key:").grid(row=2, column=0, sticky="W")
        self.last_key_label = ttk.Label(param_frame, text="N/A")
        self.last_key_label.grid(row=2, column=1, sticky="W")

        ttk.Label(param_frame, text="Last Value:").grid(row=3, column=0, sticky="W")
        self.last_value_label = ttk.Label(param_frame, text="N/A")
        self.last_value_label.grid(row=3, column=1, sticky="W")

        ttk.Label(param_frame, text="Timestamp:").grid(row=4, column=0, sticky="W")
        self.timestamp_label = ttk.Label(param_frame, text="N/A")
        self.timestamp_label.grid(row=4, column=1, sticky="W")

        # Start and Stop buttons
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="W")

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_stream)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_stream)
        self.stop_button.grid(row=0, column=1, padx=5)
        self.stop_button["state"] = "disabled"

    def generate_random_events(self):
        # Parse user inputs
        self.min_interval = float(self.min_interval_entry.get())
        self.max_interval = float(self.max_interval_entry.get())

        event_count = 0

        # Create string stream for sending events
        channel_id = "event_stream"
        self.stream_handler.create_string_stream(name="event_stream", stream_type="Events", channel_id=channel_id)

        try:
            while self.running:
                event_count += 1
                key = f"key_{event_count}"
                value = f"value_{event_count}"

                # Push event data to the LSL stream
                self.stream_handler.push_string_data(channel_id=channel_id, key=key, value=value)

                # Update UI with the last event sent
                self.update_last_event(key, value)

                # Random sleep between events
                random_interval = randint(int(self.min_interval * 1000), int(self.max_interval * 1000)) / 1000
                time.sleep(random_interval)

        except Exception as e:
            print(f"Error during event generation: {e}")
        finally:
            self.stream_handler.stop_all_streams()

    def update_last_event(self, key, value):
        now = datetime.now().strftime('%H:%M:%S:%f')[:-3]
        self.last_key_label.config(text=key)
        self.last_value_label.config(text=value)
        self.timestamp_label.config(text=now)

    def start_stream(self):
        self.running = True
        self.thread = threading.Thread(target=self.generate_random_events)
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
    app = StringStreamTestApp(root)
    root.mainloop()
