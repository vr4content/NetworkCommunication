import socket
import struct
import json
import threading
import time

class UDPListener:
    def __init__(self):
        self.listeners = {}
        self.vector3_dict = {}
        self.float_dict = {}
        self.event_dict = {}
        self.threads = {}
        self.running_flags = {}  # Flags to control thread execution
        self.packet_counters = {}  # Stores the number of packets per second per listener
        self.packet_rates = {}  # Stores the calculated packet rate per second per listener
        self.error_flags = {}  # Stores error flags for JSON parsing per listener


    def start_listener(self, data_type, port):
        if data_type in self.threads and self.running_flags[data_type]:
            print(f"{data_type} listener is already running on port {port}.")
            return
        
        # Create running flag, packet counter, and error flag for this listener
        self.running_flags[data_type] = True
        self.packet_counters[data_type] = 0
        self.packet_rates[data_type] = 0
        self.error_flags[data_type] = False  # Reset error flag

        # Start listener thread
        thread = threading.Thread(target=self.udp_listener, args=(data_type, port))
        thread.daemon = True
        thread.start()
        self.threads[data_type] = thread
        print(f"{data_type} listener started on port {port}.")

        # Start packet rate calculator thread
        rate_thread = threading.Thread(target=self.calculate_packet_rate, args=(data_type,))
        rate_thread.daemon = True
        rate_thread.start()

    def stop_listener(self, data_type):
        if data_type not in self.threads or not self.running_flags[data_type]:
            print(f"{data_type} listener is not running.")
            return
        
        # Set the running flag to False to stop the thread
        self.running_flags[data_type] = False
        print(f"{data_type} listener stopping...")
        # Reset packet rate and counter
        self.packet_counters[data_type] = 0
        self.packet_rates[data_type] = 0

    def udp_listener(self, data_type, port, host='0.0.0.0'):
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((host, port))
        print(f"Listening for {data_type} UDP packets on {host}:{port}...")

        self.listeners[data_type] = {'socket': sock}

        while self.running_flags[data_type]:
            sock.settimeout(1.0)  # Timeout to avoid blocking forever
            try:
                data, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes
                self.packet_counters[data_type] += 1  # Increment packet counter
            except socket.timeout:
                continue  # Continue the loop and check the flag again

            if len(data) < 4:
                print("Received packet too short to contain a valid header.")
                continue

            utf8_size = struct.unpack('>I', data[:4])[0]

            if len(data) < 4 + utf8_size:
                print("Incomplete packet received.")
                continue

            utf8_text = data[4:4 + utf8_size].decode('utf-8', errors='ignore').rstrip('\x00')

            try:
                json_data = json.loads(utf8_text)
                if data_type == 'Vector3':
                    self.process_vector3(json_data)
                elif data_type == 'Float':
                    self.process_float(json_data)
                elif data_type == 'Event':
                    self.process_event(json_data)
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON data. Error: {e.msg}")
                print(f"Error location: line {e.lineno}, column {e.colno}")
                print(f"Received UTF-8 text: {utf8_text}")
                self.error_flags[data_type] = True  # Set error flag

        sock.close()

    def process_vector3(self, json_data):
        vector3_data = json_data.get('vector3', {})
        self.vector3_dict.update(vector3_data)
        print("Received Vector3 data:")
        for vector_name, values in vector3_data.items():
            print(f"Vector Name: {vector_name}, x: {values['x']}, y: {values['y']}, z: {values['z']}")
        print("-" * 30)

    def process_float(self, json_data):
        float_data = json_data.get('float', {})
        self.float_dict.update(float_data)
        print("Received Float data:")
        for key, value in float_data.items():
            print(f"Key: {key}, Value: {value}")
        print("-" * 30)

    def process_event(self, json_data):
        event_data = json_data.get('event', {})
        self.event_dict.update(event_data)
        print("Received Event data:")
        for key, value in event_data.items():
            print(f"Event Key: {key}, Value: {value}")
        print("-" * 30)

    def calculate_packet_rate(self, data_type):
        while self.running_flags.get(data_type, False):
            time.sleep(1)
            self.packet_rates[data_type] = self.packet_counters[data_type]
            self.packet_counters[data_type] = 0  # Reset counter after calculating the rate
            print(f"{data_type} packet rate: {self.packet_rates[data_type]} packets/sec")

    def get_packet_rate(self, data_type):
        return self.packet_rates.get(data_type, 0)

    def get_error_flag(self, data_type):
        return self.error_flags.get(data_type, False)

    def get_vector3_data(self):
        return self.vector3_dict

    def get_float_data(self):
        return self.float_dict

    def get_event_data(self):
        return self.event_dict
