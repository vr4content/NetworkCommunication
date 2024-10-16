from datetime import datetime
import tkinter as tk
from tkinter import ttk
import configparser
import os
import threading
import time
from udp_data_handler import UDPListener
from lsl_streams_handler import LSLStreamHandler  # Import LSLStreamHandler
import csv

class DataControlCenter:
    CONFIG_FILE = "config.ini"

    def __init__(self, root):
        self.listener = UDPListener()
        self.lsl_handler = LSLStreamHandler()  # Initialize LSLStreamHandler
        self.config = configparser.ConfigParser()
        self.load_config()
        self.lsl_streams_active = False  # To keep track of LSL streams state

        # Window title
        root.title("Data Control Center")

        # Top text
        title_label = tk.Label(root, text="Data Control Center", font=("Arial", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # UDP Input Frame (left column)
        udp_frame = tk.LabelFrame(root, text="UDP Input", padx=10, pady=10)
        udp_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n")

        # UDP Start/Stop button
        self.udp_button = tk.Button(udp_frame, text="Start UDP Listening", command=self.start_stop_udp_listening, bg="red", fg="black")
        self.udp_button.pack(pady=10)

        # Data tables for Vector3, Float, and Events
        self.vector3_data_table = self.create_data_table(udp_frame, "Vector3 Data")
        self.float_data_table = self.create_data_table(udp_frame, "Float Data")
        self.event_data_table = self.create_data_table(udp_frame, "Event Data")

        # LSL Output Frame (right column)
        lsl_frame = tk.LabelFrame(root, text="LSL Output", padx=10, pady=10)
        lsl_frame.grid(row=1, column=1, padx=10, pady=10, sticky="n")

        # Samples per second input
        tk.Label(lsl_frame, text="Samples/second:").pack()
        self.samples_entry = tk.Entry(lsl_frame)
        self.samples_entry.pack()
        self.samples_entry.insert(0, "30")  # Default value

        # LSL Start/Stop button
        self.lsl_button = tk.Button(lsl_frame, text="Start LSL Streams", command=self.start_stop_lsl_streams, bg="red", fg="black")
        self.lsl_button.pack(pady=10)

        # Update data loop
        self.update_data()

        # Save config on close
        root.protocol("WM_DELETE_WINDOW", self.on_close)

     
    
        

    def create_data_table(self, parent, label):
        columns = ('Key', 'Value')
        frame = tk.LabelFrame(parent, text=label, padx=10, pady=10)
        frame.pack(fill="x", pady=5)

        table_frame = tk.Frame(frame)
        table_frame.pack(fill="both", expand=True)

        # Add scrollbar
        scrollbar = tk.Scrollbar(table_frame, orient="vertical")
        table = ttk.Treeview(table_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=table.yview)
        scrollbar.pack(side="right", fill="y")

        table.heading('Key', text='Key')
        table.heading('Value', text='Value')
        table.pack(fill="both", expand=True)  # Make table fill available space

        # Set a fixed height for the table
        table.configure(height=5)  # Adjust this value to set the number of rows shown

        return table

    def start_stop_udp_listening(self):
        if self.udp_button['text'] == "Start UDP Listening":
            # Start listening on all UDP ports
            self.listener.start_listener("Vector3", 8081)
            self.listener.start_listener("Float", 8082)
            self.listener.start_listener("Event", 8083)
            self.udp_button.config(text="Stop UDP Listening", bg="green", fg="black")
            self.flash_button(self.udp_button)
        else:
            # Stop listening on all UDP ports
            self.listener.stop_listener("Vector3")
            self.listener.stop_listener("Float")
            self.listener.stop_listener("Event")
            self.udp_button.config(text="Start UDP Listening", bg="red", fg="black")

    def start_stop_lsl_streams(self):
        if self.lsl_button['text'] == "Start LSL Streams":
            # Start LSL streams
            self.start_lsl_streams()
            self.lsl_button.config(text="Stop LSL Streams", bg="green", fg="black")
            self.flash_button(self.lsl_button)
        else:
            # Stop LSL streams
            self.stop_lsl_streams()
            self.lsl_button.config(text="Start LSL Streams", bg="red", fg="black")

    def start_lsl_streams(self):
        try:
            sampling_rate = float(self.samples_entry.get())
        except ValueError:
            sampling_rate = 0.0  # Or default to some value
        self.lsl_sampling_rate = sampling_rate
        self.lsl_streams_active = True

        # Create and start threads for Vector3 and Float data
        self.lsl_vector3_thread = threading.Thread(target=self.push_vector3_data)
        self.lsl_vector3_thread.start()

        self.lsl_float_thread = threading.Thread(target=self.push_float_data)
        self.lsl_float_thread.start()

    def stop_lsl_streams(self):
        self.lsl_streams_active = False
        # Stop threads
        if hasattr(self, 'lsl_vector3_thread'):
            self.lsl_vector3_thread.join()
        if hasattr(self, 'lsl_float_thread'):
            self.lsl_float_thread.join()
        # Stop all LSL streams
        self.lsl_handler.stop_all_streams()

    def push_vector3_data(self):
        interval = 1.0 / self.lsl_sampling_rate if self.lsl_sampling_rate > 0 else 0
        while self.lsl_streams_active:
            vector3_data = self.listener.get_vector3_data()
            for key, value in vector3_data.items():
                # Create LSL stream if not already created
                if key not in self.lsl_handler.streams:
                    self.lsl_handler.create_vector3_stream(name=key, stream_type="Vector3", channel_id=key, sampling_rate=self.lsl_sampling_rate)
                # Push data
                x, y, z = value['x'], value['y'], value['z']
                self.lsl_handler.push_vector_data(channel_id=key, x=x, y=y, z=z)
            time.sleep(interval)

    def push_float_data(self):
        interval = 1.0 / self.lsl_sampling_rate if self.lsl_sampling_rate > 0 else 0
        while self.lsl_streams_active:
            float_data = self.listener.get_float_data()
            for key, value in float_data.items():
                if key not in self.lsl_handler.streams:
                    self.lsl_handler.create_float_stream(name=key, stream_type="Float", channel_id=key, sampling_rate=self.lsl_sampling_rate)
                # Push data
                self.lsl_handler.push_float_data(channel_id=key, value=value)
                
            time.sleep(interval)

    def flash_button(self, button):
        current_color = button.cget("bg")
        new_color = "green" if current_color == "white" else "white"
        button.config(bg=new_color)
        if button['text'] == "Stop UDP Listening" or button['text'] == "Stop LSL Streams":
            button.after(500, lambda: self.flash_button(button))  # Continue flashing

    def update_data(self):
        # Update Vector3 data
        self.update_table(self.vector3_data_table, self.listener.get_vector3_data())

        # Update Float data
        self.update_table(self.float_data_table, self.listener.get_float_data())

        # Update Event data
        self.update_table(self.event_data_table, self.listener.get_event_data())

        # If LSL streams are active, push event data
        if self.lsl_streams_active:
            # For Events, we have one marker stream
            if 'event_marker' not in self.lsl_handler.streams:
                self.lsl_handler.create_marker_stream(name="EventMarker", stream_type="Markers", channel_id="event_marker")
            event_data = self.listener.get_event_data()
            event_keys = list(event_data.keys())
            for key in event_keys:
                value = event_data[key]
                # Push event data
                self.lsl_handler.push_marker_data(channel_id="event_marker", key=key, value=value)
                print("sending lsl "+key+" "+value)
                if key=="provant_id":
                    #save global variable for provant_id
                    self.provant_id = value
                    #self.provant_id_timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
                    #self.csv_file_name = self.provant_id + self.provant_id_timestamp + ".csv"
                    now = datetime.now()
                    formatted_time = now.strftime("%Y%m%d_%H%M%S")

                    self.csv_file_name = formatted_time+"_"+self.provant_id + "_"+".csv"
                    
                    print("pronvat_id "+self.provant_id)
                    #save global timestamp
                   
                if key=="level_title":
                    #save global variable for level_title
                    self.level_title = value
                    print("level_title "+self.level_title)
                if key=="answer":
                    #save global variable for level_title
                    self.answer = value
                    print("answer: "+self.answer)
                    print("adding a line "+self.level_title)
                    self.AddCSVLine(self.csv_file_name, [str(time.time()), str(self.provant_id), self.level_title, self.answer])

                

                #Remove the event to avoid pushing it again
                del self.listener.event_dict[key]

        # Schedule next update
        root.after(5, self.update_data)

    def update_table(self, table, data_dict):
        # Clear table
        for row in table.get_children():
            table.delete(row)
        # Insert updated data
        for key, value in data_dict.items():
            if isinstance(value, dict):
                # For vector3 data, show x, y, z
                formatted_value = f"x: {value['x']}, y: {value['y']}, z: {value['z']}"
            else:
                formatted_value = value
            table.insert("", "end", values=(key, formatted_value))

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            self.config.read(self.CONFIG_FILE)
        else:
            self.config["Ports"] = {}

    def save_config(self):
        # Save any necessary configuration here
        with open(self.CONFIG_FILE, "w") as configfile:
            self.config.write(configfile)

    def on_close(self):
        self.save_config()
        root.destroy()

    def AddCSVLine(self,filename, row_data):
        # Define the full path to the file in the root of D:
        print("AddCSVLine file  "+filename+" "+row_data[0]+" "+row_data[1]+" "+row_data[2])
        file_path = os.path.join('D:\\', filename)

        # Check if the file exists
        file_exists = os.path.isfile(file_path)

        # Open the file in append mode ('a'), which creates the file if it does not exist
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
        
            # If the file does not exist, write the header (optional)
            if not file_exists:
                writer.writerow(["timestamp", "provant_id","key", "value"])  # Change headers as needed
        
            # Write the new row data
            writer.writerow(row_data)

if __name__ == "__main__":
    root = tk.Tk()
    app = DataControlCenter(root)
    root.mainloop()


#provantId
