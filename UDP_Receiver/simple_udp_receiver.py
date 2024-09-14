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
            
            # Updated to handle new vector3 format (as a dictionary)
            vector3_dict = json_data.get('vector3', {})
            
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

def udp_listener_float(host='0.0.0.0', port=8081):
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
            
            # Print the float data
            print("Received Float data:")
            for key, value in json_data.get('float', {}).items():
                print(f"Key: {key}, Value: {value}")
            print("-" * 30)  # Separator for better readability
        
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON data. Error: {e.msg}")
            print(f"Error location: line {e.lineno}, column {e.colno}")
            print(f"Received UTF-8 text: {utf8_text}")

def udp_listener_event(host='0.0.0.0', port=8082):
    # Create a UDP socket for event data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind the socket to the specified port
    sock.bind((host, port))
    print(f"Listening for Event UDP packets on {host}:{port}...")

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
            
            # Handle the event data
            event_dict = json_data.get('event', {})
            
            # Print the event data
            print("Received Event data:")
            for key, value in event_dict.items():
                print(f"Event Key: {key}, Value: {value}")
            print("-" * 30)  # Separator for better readability
        
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON data. Error: {e.msg}")
            print(f"Error location: line {e.lineno}, column {e.colno}")
            print(f"Received UTF-8 text: {utf8_text}")

if __name__ == "__main__":
    # Create three threads to listen on different ports for vector3, float, and event data
    vector3_thread = threading.Thread(target=udp_listener_vector3, args=('0.0.0.0', 8080))
    float_thread = threading.Thread(target=udp_listener_float, args=('0.0.0.0', 8081))
    event_thread = threading.Thread(target=udp_listener_event, args=('0.0.0.0', 8082))

    # Start all threads
    vector3_thread.start()
    float_thread.start()
    event_thread.start()

    # Join threads to keep them running
    vector3_thread.join()
    float_thread.join()
    event_thread.join()
