import socket
import tkinter as tk
from tkinter import messagebox
import time
from datetime import datetime

# Function to get local IP
def get_local_ip():
    return socket.gethostbyname(socket.gethostname())

# Function to send UDP start/stop command
def send_command():
    global is_recording
    if not target_ip_entry.get() or not filename_entry.get():
        messagebox.showerror("Input Error", "Please enter target IP and filename.")
        return

    # Generate the filename with timestamp
    timestamp = datetime.now().strftime('_%Y_%m_%d_%H%M%S')
    generated_filename = filename_entry.get() + timestamp

    # Form the command with filename
    command = f"{'start' if not is_recording else 'stop'}:{generated_filename}"
    
    # Send the UDP message
    udp_socket.sendto(command.encode(), (target_ip_entry.get(), 12345))
    
    # Display the final filename in the UI
    final_filename_label.config(text=f"Final Filename: {generated_filename}")
    
    # Toggle recording status and update button color/animation
    is_recording = not is_recording
    status_label.config(text=f"Status: {'Recording' if is_recording else 'Not Recording'}")
    update_button_feedback()

# Clock update function
def update_clock():
    current_time = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
    clock_label.config(text=current_time)
    root.after(10, update_clock)

# Function to update button feedback
def update_button_feedback():
    if is_recording:
        start_stop_button.config(bg="green", activebackground="green", fg="white")
        start_stop_button.flash_counter = 0
        flash_button()
    else:
        start_stop_button.config(bg="red", activebackground="red", fg="white")

# Function to make the button flash when recording
def flash_button():
    if is_recording:
        current_color = start_stop_button.cget("bg")
        new_color = "green" if current_color == "white" else "white"
        start_stop_button.config(bg=new_color)
        start_stop_button.flash_counter += 1
        if start_stop_button.flash_counter < 1000:  # Limiting flashing cycles
            root.after(500, flash_button)

# Initializing UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
is_recording = False

# Setup Tkinter window
root = tk.Tk()
root.title("UDP Audio Controller - Computer A")
start_time = time.time()

# Large title label
tk.Label(root, text="AudioRecorder (Sender)", font=("Helvetica", 24, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

# Local IP display
tk.Label(root, text="Local IP:").grid(row=1, column=0)
local_ip_label = tk.Label(root, text=get_local_ip())
local_ip_label.grid(row=1, column=1)

# Clock display
clock_label = tk.Label(root, text="00:00:00.000")
clock_label.grid(row=2, column=0, columnspan=2)

# Target IP entry
tk.Label(root, text="Target IP:").grid(row=3, column=0)
target_ip_entry = tk.Entry(root)
target_ip_entry.insert(0, "127.0.0.1")
target_ip_entry.grid(row=3, column=1)

# Filename entry
tk.Label(root, text="Filename:").grid(row=4, column=0)
filename_entry = tk.Entry(root)
filename_entry.insert(0, "provantIdxxx")
filename_entry.grid(row=4, column=1)

# Final filename display
final_filename_label = tk.Label(root, text="Final Filename:")
final_filename_label.grid(row=5, column=0, columnspan=2)

# Start/Stop button
status_label = tk.Label(root, text="Status: Not Recording")
status_label.grid(row=6, column=0, columnspan=2)

start_stop_button = tk.Button(root, text="Start/Stop Recording", command=send_command, width=20, height=2, font=("Helvetica", 16))
start_stop_button.grid(row=7, column=0, columnspan=2, pady=10)
start_stop_button.config(bg="red", fg="white")

# Update the clock every 10 ms
update_clock()

root.mainloop()
