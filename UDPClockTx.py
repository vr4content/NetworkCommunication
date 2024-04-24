import socket
import threading
from datetime import datetime
import time
from tkinter import Tk, Label, Button, Entry, StringVar

def send_time():
    global running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    target_ip = ip_var.get()
    target_port = int(port_var.get())

    try:
        while running:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            sock.sendto(now.encode(), (target_ip, target_port))
            time_label.config(text=now)
            #tx frequency (every 10 miliseconds)
            time.sleep(0.01)
    finally:
        sock.close()

def start_sending():
    global running
    running = True
    start_button.config(state="disabled")
    stop_button.config(state="normal")
    thread = threading.Thread(target=send_time)
    thread.daemon = True
    thread.start()

def stop_sending():
    global running
    running = False
    stop_button.config(state="disabled")
    start_button.config(state="normal")

# Main UI setup
root = Tk()
root.title("UDP Time Sender")
titleLabel = Label(root, text="UDP Time Sender", font=('Helvetica', 20))
titleLabel.pack(pady=20)
titleLabel.pack(side="top", fill="both", expand=True)

# Variables for IP and port
ip_var = StringVar(value="127.0.0.1")
port_var = StringVar(value="5005")

# Time display
time_label = Label(root, text="", font=("Helvetica", 18))  # Increased font size
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
start_button = Button(root, text="Start Sending", command=start_sending, state="normal")
start_button.pack(pady=10)
start_button.pack(ipady=20)

stop_button = Button(root, text="Stop Sending", command=stop_sending, state="disabled")
stop_button.pack(pady=10)
stop_button.pack(ipady=20)

root.mainloop()
