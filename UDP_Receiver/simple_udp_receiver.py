import socket
import struct
import json
import threading

def udp_listener_vector3(host='0.0.0.0', port=8080):
    # Create a UDP socket for vector3 data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind the socket to the specified port
    sock.bind((host, port))
    print(f"Listening for Vector3 UDP packets on {host}:{port}...")

    while True:
        # Receive data from the socket
        data, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes
        
        if len(data) < 4:
            print("Received packet too short to contain a valid header.")
            continue

        # Extract the first 4 bytes (header) to get the size of the UTF-8 part
        utf8_size = struct.unpack('>I', data[:4])[0]  # '>I' for big-endian unsigned int
        
        # Check if we received enough data for the UTF-8 portion
        if len(data) < 4 + utf8_size:
            print("Incomplete packet received.")
            continue
        
        # Get the exact UTF-8 text part
        utf8_text = data[4:4 + utf8_size].decode('utf-8', errors='ignore').rstrip('\x00')

        # Parse the JSON message
        try:
            json_data = json.loads(utf8_text)
            
            # Create a dictionary with vector names as keys
            vector3_dict = {item['vector_name']: {'x': item['x'], 'y': item['y'], 'z': item['z']} 
                            for item in json_data.get('vector3', [])}
            
            # Print the dictionary in a cleaner format
            print("Received Vector3 data:")
            for vector_name, values in vector3_dict.items():
                print(f"Vector Name: {vector_name}")
                print(f"  x: {values['x']}")
                print(f"  y: {values['y']}")
                print(f"  z: {values['z']}")
                print("-" * 30)  # Separator for better readability
        
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON data. Error: {e.msg}")
            print(f"Error location: line {e.lineno}, column {e.colno}")
            print(f"Received UTF-8 text: {utf8_text}")

def udp_listener_float(host='0.0.0.0', port=8081, float_dict=None):
    # Create a UDP socket for float data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind the socket to the specified port
    sock.bind((host, port))
    print(f"Listening for Float UDP packets on {host}:{port}...")

    while True:
        # Receive data from the socket
        data, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes
        
        if len(data) < 4:
            print("Received packet too short to contain a valid header.")
            continue

        # Extract the first 4 bytes (header) to get the size of the UTF-8 part
        utf8_size = struct.unpack('>I', data[:4])[0]  # '>I' for big-endian unsigned int
        
        # Check if we received enough data for the UTF-8 portion
        if len(data) < 4 + utf8_size:
            print("Incomplete packet received.")
            continue
        
        # Get the exact UTF-8 text part
        utf8_text = data[4:4 + utf8_size].decode('utf-8', errors='ignore').rstrip('\x00')

        # Parse the JSON message
        try:
            json_data = json.loads(utf8_text)
            
            # Update the float_dict with the received float data
            float_dict.update({item['key']: item['value'] for item in json_data.get('float', [])})
            
            # Print the float data
            print("Received Float data:")
            for key, value in float_dict.items():
                print(f"Key: {key}, Value: {value}")
            print("-" * 30)  # Separator for better readability
        
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON data. Error: {e.msg}")
            print(f"Error location: line {e.lineno}, column {e.colno}")
            print(f"Received UTF-8 text: {utf8_text}")

if __name__ == "__main__":
    # Dictionary to store float data
    float_dict = {}

    # Create two threads to listen on different ports
    vector3_thread = threading.Thread(target=udp_listener_vector3, args=('0.0.0.0', 8080))
    float_thread = threading.Thread(target=udp_listener_float, args=('0.0.0.0', 8081, float_dict))

    # Start both threads
    vector3_thread.start()
    float_thread.start()

    # Join threads to keep them running
    vector3_thread.join()
    float_thread.join()


# {
#     "float": [
#         {
#             "key": "eye_left",
#             "value": 0.1 
#         },
#         {
#             "key": "eye_right",
#             "value": 0.9
#         }
#     ]
# }


# {
#     "vector3": [
#         {
#             "vector_name": "user_head_position",
#             "x": -197.7,
#             "y": 197.78,
#             "z": 297.4
#         },
#         {
#             "vector_name": "user_head_rotation",
#             "x": 79.63,
#             "y": 79.63,
#             "z": 79.65
#         }
#     ]
# }
