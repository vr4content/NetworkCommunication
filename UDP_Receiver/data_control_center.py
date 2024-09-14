import tkinter as tk
from tkinter import ttk
from udp_data_handler import UDPListener

class DataControlCenter:
    def __init__(self, root):
        self.listener = UDPListener()
        
        # Window title
        root.title("Data Control Center")
        
        # Top text
        title_label = tk.Label(root, text="Data Control Center", font=("Arial", 16))
        title_label.pack(pady=10)
        
        # UDP Input Frame
        udp_frame = tk.LabelFrame(root, text="UDP Input", padx=10, pady=10)
        udp_frame.pack(padx=10, pady=10, fill="x")

        # Subframe for Vector3
        self.vector3_frame = self.create_listener_frame(udp_frame, "Vector3", 8080, self.start_stop_vector3)
        self.vector3_data_table = self.create_data_table(self.vector3_frame)

        # Subframe for Float
        self.float_frame = self.create_listener_frame(udp_frame, "Float", 8081, self.start_stop_float)
        self.float_data_table = self.create_data_table(self.float_frame)

        # Subframe for Events
        self.event_frame = self.create_listener_frame(udp_frame, "Event", 8082, self.start_stop_event)
        self.event_data_table = self.create_data_table(self.event_frame)
        
        # Update data loop
        self.update_data()

    def create_listener_frame(self, parent, label, default_port, button_command):
        subframe = tk.LabelFrame(parent, text=label, padx=10, pady=10)
        subframe.pack(fill="x", pady=5)

        # Port input
        tk.Label(subframe, text="Port:").grid(row=0, column=0)
        port_entry = tk.Entry(subframe)
        port_entry.insert(0, str(default_port))  # Set default port
        port_entry.grid(row=0, column=1)

        # Start/Stop button
        toggle_button = tk.Button(subframe, text="Start listening", command=lambda: button_command(port_entry, toggle_button), bg="red", fg="black")
        toggle_button.grid(row=0, column=2)

        return subframe

    def create_data_table(self, frame):
        columns = ('Key', 'Value')
        table_frame = tk.Frame(frame)
        table_frame.grid(row=1, column=0, columnspan=3, pady=5, sticky="nsew")

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

    def update_data(self):
        # Update Vector3 data
        self.update_table(self.vector3_data_table, self.listener.get_vector3_data())
        # Update Float data
        self.update_table(self.float_data_table, self.listener.get_float_data())
        # Update Event data
        self.update_table(self.event_data_table, self.listener.get_event_data())
        # Schedule next update
        root.after(1000, self.update_data)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = DataControlCenter(root)
    root.mainloop()
