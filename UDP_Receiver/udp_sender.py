import socket
import json
import struct
import time
import math

def send_udp_message(data, port, host='127.0.0.1'):
    # Convert the JSON data to a string and then to bytes
    json_text = json.dumps(data)
    json_bytes = json_text.encode('utf-8')
    
    # Create the packet: first 4 bytes are the length of the UTF-8 part, followed by the actual UTF-8 bytes
    utf8_size = struct.pack('>I', len(json_bytes))  # '>I' for big-endian unsigned int
    packet = utf8_size + json_bytes

    # Create a UDP socket and send the packet
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(packet, (host, port))
    # print(f"Sent data to port {port}: {json_text}")

def generate_sine_wave(amplitude, frequency, time):
    return amplitude * math.sin( frequency * time)

def test_vector3_data(time_point):
    vector3_data = {
        "vector3": {
            "user_head_position": {
                "x": generate_sine_wave(100000, 1, time_point),
                "y": generate_sine_wave(100000, 1, time_point + 0.33),
                "z": generate_sine_wave(100000, 1, time_point + 0.66)
            },
            "user_head_rotation": {
                "x": generate_sine_wave(180, 1, time_point),
                "y": generate_sine_wave(180, 1, time_point + 0.33),
                "z": generate_sine_wave(180, 1, time_point + 0.66)
            },
            "avatar_head_position": {
                "x": generate_sine_wave(100000, 1, time_point),
                "y": generate_sine_wave(100000, 1, time_point + 0.33),
                "z": generate_sine_wave(100000, 1, time_point + 0.66)
            },
            "avatar_head_rotation": {
                "x": generate_sine_wave(180, 1, time_point),
                "y": generate_sine_wave(180, 1, time_point + 0.33),
                "z": generate_sine_wave(180, 1, time_point + 0.66)
            },
             "head_gaze_collision": {
                "x": generate_sine_wave(100000, 1, time_point),
                "y": generate_sine_wave(100000, 1, time_point + 0.33),
                "z": generate_sine_wave(100000, 1, time_point + 0.66)
            },
              "eye_gaze_collision": {
                "x": generate_sine_wave(100000, 1, time_point),
                "y": generate_sine_wave(100000, 1, time_point + 0.33),
                "z": generate_sine_wave(100000, 1, time_point + 0.66)
            },
        }
    }
    send_udp_message(vector3_data, 8080)

def test_float_data(time_point):
    float_data = {
        "float": {
            "blendshape_smile": generate_sine_wave(1, 1, time_point),
            "blendshape_left_eye_open": generate_sine_wave(1, 1, time_point),
            "blendshape_right_eye_open": generate_sine_wave(1, 1, time_point)
        }
    }
    send_udp_message(float_data, 8081)

def test_event_data():
    event_data = {
        "event": {
            "start_time": "10:00",
            "end_time": "10:30",
            "status": "active"
        }
    }
    send_udp_message(event_data, 8082)

if __name__ == "__main__":
    start_time = time.time()
    
    while True:
        # Calculate time elapsed since start to control sine wave generation
        elapsed_time = time.time() - start_time

        # Test sending vector3 data with sine waves
        test_vector3_data(elapsed_time)
        
        # Test sending float data
        test_float_data()
        
        # Test sending event data
        test_event_data()
        
        # Wait a little before sending the next set of data (at 24 FPS)
        time.sleep(1/24)
