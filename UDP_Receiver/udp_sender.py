import socket
import json
import struct
import time

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
    print(f"Sent data to port {port}: {json_text}")

def test_vector3_data():
    vector3_data = {
        "vector3": {
            "head_position": {"x": 0.1, "y": 0.2, "z": 0.3},
            "hand_position": {"x": 0.4, "y": 0.5, "z": 0.6}
        }
    }
    send_udp_message(vector3_data, 8080)

def test_float_data():
    float_data = {
        "float": {
            "blendshape_smile": 0.9,
            "blendshape_frown": 0.1,
            "blendshape_surprised": 0.75
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
    while True:
        # Test sending vector3 data
        test_vector3_data()
        
        # Test sending float data
        test_float_data()
        
        # Test sending event data
        test_event_data()
        
        # Wait a little before sending the next set of data
        time.sleep(1/24)
