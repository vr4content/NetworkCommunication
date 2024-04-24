import socket
import threading
from datetime import datetime
from tkinter import Tk, Label, Button, Entry, StringVar

def receive_time():
    global running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip_var.get(), int(port_var.get())))

    try:
        while running:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            now = data.decode()
            time_label.config(text=now)
    finally:
        sock.close()

def start_listening():
    global running
    running = True
    start_button.config(state="disabled")
    stop_button.config(state="normal")
    thread = threading.Thread(target=receive_time)
    thread.daemon = True
    thread.start()

def stop_listening():
    global running
    running = False
    stop_button.config(state="disabled")
    start_button.config(state="normal")

# Main UI setup
root = Tk()
root.title("UDP Time Receiver")
titleLabel = Label(root, text="UDP Time Receiver", font=('Helvetica', 20))
titleLabel.pack(pady=20)
titleLabel.pack(side="top", fill="both", expand=True)

# Variables for IP and port
ip_var = StringVar(value="127.0.0.1")
port_var = StringVar(value="5005")

# Time display
time_label = Label(root, text="", font=("Helvetica", 18))  # Display area for incoming time
time_label.pack(pady=50)
time_label.pack(padx=50)

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
time_label.config(text=now)

# IP configuration
ip_entry = Entry(root, textvariable=ip_var, font=("Helvetica", 12), width=15)
ip_entry.pack(pady=5)

# Port configuration
port_entry = Entry(root, textvariable=port_var, font=("Helvetica", 12), width=8)
port_entry.pack(pady=5)

# Control buttons
start_button = Button(root, text="Start Listening", command=start_listening, state="normal")
start_button.pack(pady=10)
start_button.pack(ipady=20)

stop_button = Button(root, text="Stop Listening", command=stop_listening, state="disabled")
stop_button.pack(pady=10)
stop_button.pack(ipady=20)

root.mainloop()
