import tkinter as tk
from tkinter import ttk
import configparser
import os
from udp_data_handler import UDPListener

class DataControlCenter:
    CONFIG_FILE = "config.ini"

    def __init__(self, root):
        self.listener = UDPListener()
        self.config = configparser.ConfigParser()
        self.load_config()

        # Window title
        root.title("Data Control Center")
        
        # Top text
        title_label = tk.Label(root, text="Data Control Center", font=("Arial", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # UDP Input Frame (left column)
        udp_frame = tk.LabelFrame(root, text="UDP Input", padx=10, pady=10)
        udp_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n")

        # Subframe for Vector3
        self.vector3_frame = self.create_listener_frame(udp_frame, "Vector3", 8080, self.start_stop_vector3)
        self.vector3_data_table = self.create_data_table(self.vector3_frame)
        self.vector3_packets_label, self.vector3_error_label = self.create_packets_and_error_label(self.vector3_frame)

        # Subframe for Float
        self.float_frame = self.create_listener_frame(udp_frame, "Float", 8081, self.start_stop_float)
        self.float_data_table = self.create_data_table(self.float_frame)
        self.float_packets_label, self.float_error_label = self.create_packets_and_error_label(self.float_frame)

        # Subframe for Events
        self.event_frame = self.create_listener_frame(udp_frame, "Event", 8082, self.start_stop_event)
        self.event_data_table = self.create_data_table(self.event_frame)
        self.event_packets_label, self.event_error_label = self.create_packets_and_error_label(self.event_frame)

        # Button to start/stop listening on all ports
        self.all_button = tk.Button(udp_frame, text="Start Listening All Ports", command=self.start_stop_all, bg="red", fg="black")
        self.all_button.pack(pady=10)

        # LSL Output Frame (right column)
        lsl_frame = tk.LabelFrame(root, text="LSL Output", padx=10, pady=10)
        lsl_frame.grid(row=1, column=1, padx=10, pady=10, sticky="n")

        # Subframe for LSL Vector3 Output
        self.lsl_vector3_frame = self.create_lsl_output_frame(lsl_frame, "Vector3")
        
        # Subframe for LSL Float Output
        self.lsl_float_frame = self.create_lsl_output_frame(lsl_frame, "Float")
        
        # Subframe for LSL Event Output
        self.lsl_event_frame = self.create_lsl_output_frame(lsl_frame, "Event")

        # Update data loop
        self.update_data()

        # Save config on close
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_listener_frame(self, parent, label, default_port, button_command):
        subframe = tk.LabelFrame(parent, text=label, padx=10, pady=10)
        subframe.pack(fill="x", pady=5)

        # Port input
        tk.Label(subframe, text="Port:").grid(row=0, column=0)
        port_entry = tk.Entry(subframe)
        saved_port = self.config.get("Ports", label, fallback=str(default_port))
        port_entry.insert(0, saved_port)  # Set saved or default port
        port_entry.grid(row=0, column=1)

        # Start/Stop button
        toggle_button = tk.Button(subframe, text="Start listening", command=lambda: button_command(port_entry, toggle_button), bg="red", fg="black")
        toggle_button.grid(row=0, column=4)

        setattr(self, f"{label.lower()}_port_entry", port_entry)  # Save port entry for later reference
        setattr(self, f"{label.lower()}_toggle_button", toggle_button)  # Save button reference

        return subframe

    def create_lsl_output_frame(self, parent, label):
        subframe = tk.LabelFrame(parent, text=label, padx=10, pady=10)
        subframe.pack(fill="x", pady=5)

        # Samples/second input
        tk.Label(subframe, text="Samples/second:").grid(row=0, column=0)
        samples_entry = tk.Entry(subframe)
        samples_entry.grid(row=0, column=1)

        # Start/Stop button
        toggle_button = tk.Button(subframe, text="Start LSL", bg="red", fg="black")
        toggle_button.grid(row=0, column=2)

        return subframe

    def create_data_table(self, frame):
        columns = ('Key', 'Value')
        table_frame = tk.Frame(frame)
        table_frame.grid(row=1, column=0, columnspan=5, pady=5, sticky="nsew")

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

    def create_packets_and_error_label(self, frame):
        packets_label = tk.Label(frame, text="0 packets/s", font=("Arial", 10))
        packets_label.grid(row=0, column=2)  # Place it between port input and the button

        error_label = tk.Label(frame, text="No Error", font=("Arial", 10), bg="green")
        error_label.grid(row=0, column=3)  # Add error flag next to packet rate label

        return packets_label, error_label

    def start_stop_vector3(self, port_entry, toggle_button):
        self.toggle_listener("Vector3", port_entry, toggle_button)

    def start_stop_float(self, port_entry, toggle_button):
        self.toggle_listener("Float", port_entry, toggle_button)

    def start_stop_event(self, port_entry, toggle_button):
        self.toggle_listener("Event", port_entry, toggle_button)

    def toggle_listener(self, data_type, port_entry, toggle_button):
        port = int(port_entry.get())
        if toggle_button['text'] == "Start listening":
            self.listener.start_listener(data_type, port)
            toggle_button.config(text="Listening...", fg="black", bg="green", activebackground="green")
            self.flash_button(toggle_button)
        else:
            self.listener.stop_listener(data_type)
            toggle_button.config(text="Start listening", bg="red", activebackground="red", fg="black")

    def flash_button(self, button):
        current_color = button.cget("bg")
        new_color = "green" if current_color == "white" else "white"
        button.config(bg=new_color)
        if button['text'] == "Listening...":
            button.after(500, lambda: self.flash_button(button))  # Continue flashing

    def start_stop_all(self):
        if self.all_button['text'] == "Start Listening All Ports":
            self.start_all_listeners()
            self.all_button.config(text="Stop Listening All Ports", bg="green", fg="black")
            self.flash_button(self.all_button)
        else:
            self.stop_all_listeners()
            self.all_button.config(text="Start Listening All Ports", bg="red", fg="black")

    def start_all_listeners(self):
        self.start_stop_vector3(self.vector3_port_entry, self.vector3_toggle_button)
        self.start_stop_float(self.float_port_entry, self.float_toggle_button)
        self.start_stop_event(self.event_port_entry, self.event_toggle_button)

    def stop_all_listeners(self):
        self.start_stop_vector3(self.vector3_port_entry, self.vector3_toggle_button)
        self.start_stop_float(self.float_port_entry, self.float_toggle_button)
        self.start_stop_event(self.event_port_entry, self.event_toggle_button)

    def update_data(self):
        # Update Vector3 data
        self.update_table(self.vector3_data_table, self.listener.get_vector3_data())
        self.update_packets_rate_and_error(self.vector3_packets_label, self.vector3_error_label, "Vector3")

        # Update Float data
        self.update_table(self.float_data_table, self.listener.get_float_data())
        self.update_packets_rate_and_error(self.float_packets_label, self.float_error_label, "Float")

        # Update Event data
        self.update_table(self.event_data_table, self.listener.get_event_data())
        self.update_packets_rate_and_error(self.event_packets_label, self.event_error_label, "Event")

        # Schedule next update
        root.after(50, self.update_data)

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

    def update_packets_rate_and_error(self, packets_label, error_label, data_type):
        # Update packet rate
        packet_rate = self.listener.get_packet_rate(data_type)
        packets_label.config(text=f"{packet_rate} packets/s")
        
        # Update error flag
        error_flag = self.listener.get_error_flag(data_type)
        if error_flag:
            error_label.config(text="Error", bg="red")
        else:
            error_label.config(text="No Error", bg="green")

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            self.config.read(self.CONFIG_FILE)
        else:
            self.config["Ports"] = {}

    def save_config(self):
        self.config["Ports"]["Vector3"] = self.vector3_port_entry.get()
        self.config["Ports"]["Float"] = self.float_port_entry.get()
        self.config["Ports"]["Event"] = self.event_port_entry.get()
        with open(self.CONFIG_FILE, "w") as configfile:
            self.config.write(configfile)

    def on_close(self):
        self.save_config()
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DataControlCenter(root)
    root.mainloop()
