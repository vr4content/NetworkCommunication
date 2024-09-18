import socket
import struct
import json
import threading

# Common function to handle received data
def udp_listener(data_type, port, process_func, host='0.0.0.0'):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind the socket to the specified port
    sock.bind((host, port))
    print(f"Listening for {data_type} UDP packets on {host}:{port}...")

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
            process_func(json_data)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON data. Error: {e.msg}")
            print(f"Error location: line {e.lineno}, column {e.colno}")
            print(f"Received UTF-8 text: {utf8_text}")

# Separate processing functions for each type of data
def process_vector3(json_data):
    vector3_dict = json_data.get('vector3', {})
    print("Received Vector3 data:")
    for vector_name, values in vector3_dict.items():
        print(f"Vector Name: {vector_name}")
        print(f"  x: {values['x']}")
        print(f"  y: {values['y']}")
        print(f"  z: {values['z']}")
    print("-" * 30)  # Separator for better readability

def process_float(json_data):
    print("Received Float data:")
    for key, value in json_data.get('float', {}).items():
        print(f"Key: {key}, Value: {value}")
    print("-" * 30)  # Separator for better readability

def process_event(json_data):
    print("Received Event data:")
    for key, value in json_data.get('event', {}).items():
        print(f"Event Key: {key}, Value: {value}")
    print("-" * 30)  # Separator for better readability

if __name__ == "__main__":
    # Define the types and corresponding processing functions
    listeners = [
        ('Vector3', 8080, process_vector3),
        ('Float', 8081, process_float),
        ('Event', 8082, process_event)
    ]

    # Create and start threads for each listener
    threads = []
    for data_type, port, process_func in listeners:
        thread = threading.Thread(target=udp_listener, args=(data_type, port, process_func))
        thread.start()
        threads.append(thread)

    # Join threads to keep them running
    for thread in threads:
        thread.join()
