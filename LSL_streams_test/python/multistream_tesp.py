import threading
import time
import numpy as np

from lsl_streams_handler import LSLStreamHandler

# Assuming the LSLStreamHandler class is defined in the same script or imported properly
# from lsl_stream_handler import LSLStreamHandler

lsl_handler = LSLStreamHandler()

# Create 15 vector3 streams with a 1Hz sinusoidal signal
for i in range(1, 16):
    name = f"signal_v3_{i}"
    stream_type = "vector3"
    channel_id = f"v3_channel_{i}"
    sampling_rate = 30  # Sampling at 100Hz
    lsl_handler.create_vector3_stream(name, stream_type, channel_id, sampling_rate)

# Create 15 float streams with a 1Hz sinusoidal signal
for i in range(1, 16):
    name = f"signal_float_{i}"
    stream_type = "float"
    channel_id = f"float_channel_{i}"
    sampling_rate = 30  # Sampling at 100Hz
    lsl_handler.create_float_stream(name, stream_type, channel_id, sampling_rate)

# Create one SveneEvent marker stream
lsl_handler.create_marker_stream("SveneEvent", "marker", "marker_channel")

# Flag to control the running state of the threads
running = True

def push_vector3_data():
    start_time = time.time()
    while running:
        current_time = time.time() - start_time
        t = current_time
        # 1Hz sinusoidal signal
        value = np.sin(2 * np.pi * 1 * t)
        x = value
        y = value
        z = value
        for i in range(1, 16):
            channel_id = f"v3_channel_{i}"
            lsl_handler.push_vector_data(channel_id, x, y, z)
        time.sleep(1/30)  # Sleep to maintain 100Hz sampling rate

def push_float_data():
    start_time = time.time()
    while running:
        current_time = time.time() - start_time
        t = current_time
        # 1Hz sinusoidal signal
        value = np.sin(2 * np.pi * 1 * t)
        for i in range(1, 16):
            channel_id = f"float_channel_{i}"
            lsl_handler.push_float_data(channel_id, value)
        time.sleep(1/30)  # Sleep to maintain 100Hz sampling rate

def push_marker_data():
    i = 1
    while running:
        key = f"key_{i}"
        value = f"value for key {i}"
        channel_id = "marker_channel"
        lsl_handler.push_marker_data(channel_id, key, value)
        i += 1
        time.sleep(1)  # Send marker every second

# Start the data pushing threads
vector3_thread = threading.Thread(target=push_vector3_data)
float_thread = threading.Thread(target=push_float_data)
marker_thread = threading.Thread(target=push_marker_data)

vector3_thread.start()
float_thread.start()
marker_thread.start()

try:
    while True:
        time.sleep(1)  # Keep the main thread alive
except KeyboardInterrupt:
    print("Stopping streams...")
    running = False
    vector3_thread.join()
    float_thread.join()
    marker_thread.join()
    lsl_handler.stop_all_streams()
    print("All streams stopped.")
