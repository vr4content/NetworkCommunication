import socket
import json
import struct
import time

def send_udp_vector3_data(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Example Vector3 data
    vector3_data = {
        'vector3': [
            {'vector_name': 'vector1', 'x': 1.0, 'y': 2.0, 'z': 3.0},
            {'vector_name': 'vector2', 'x': 4.0, 'y': 5.0, 'z': 6.0}
        ]
    }
    
    # Serialize data to JSON
    utf8_text = json.dumps(vector3_data).encode('utf-8')
    
    # Prepend the length of the JSON string (as a 4-byte big-endian integer)
    header = struct.pack('>I', len(utf8_text))
    
    # Combine the header and the JSON data
    message = header + utf8_text
    
    # Send the message
    sock.sendto(message, (host, port))
    print(f"Sent Vector3 data to {host}:{port}")
    sock.close()

def send_udp_float_data(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Example Float data
    float_data = {
        'float': {
            'float1': 0.123,
            'float2': 0.456
        }
    }
    
    # Serialize data to JSON
    utf8_text = json.dumps(float_data).encode('utf-8')
    
    # Prepend the length of the JSON string (as a 4-byte big-endian integer)
    header = struct.pack('>I', len(utf8_text))
    
    # Combine the header and the JSON data
    message = header + utf8_text
    
    # Send the message
    sock.sendto(message, (host, port))
    print(f"Sent Float data to {host}:{port}")
    sock.close()

if __name__ == "__main__":
    udp_host = '127.0.0.1'  # or your specific IP address
    vector3_port = 8080
    float_port = 8081

    while True:
        # Send Vector3 data
        send_udp_vector3_data(udp_host, vector3_port)
        
        # Send Float data
        send_udp_float_data(udp_host, float_port)
        
        # Wait 1 second
        time.sleep(1)
