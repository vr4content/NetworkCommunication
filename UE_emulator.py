import json
import math
import socket
import threading
from datetime import datetime
import time
from tkinter import Tk, Label, Button, Entry, StringVar, Frame, Scale, HORIZONTAL

def send_data():
    global running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    target_ip = ip_var.get()
    target_port = int(port_var.get())

    try:
        while running:
            #todo update data
            global start_time
            global data
            elapsed_time = time.time() - start_time
            data["properties"][0]["HeadPosition"]["x"] = round(100 * math.sin((1/20) * elapsed_time),2)
            data["properties"][0]["HeadPosition"]["y"] = round(100 * math.sin((1/21) * elapsed_time),2)
            data["properties"][0]["HeadPosition"]["z"] = round(100 * math.sin((1/19) * elapsed_time),2)
            data["properties"][1]["HeadRotation"]["x"] = round(360 * math.sin((1/10) * elapsed_time),2)
            data["properties"][1]["HeadRotation"]["y"] = round(360 * math.sin((1/11) * elapsed_time),2)
            data["properties"][1]["HeadRotation"]["z"] = round(360 * math.sin((1/9) * elapsed_time),2)

            # Update the UI
            update_ui()

            # Serialize JSON and send
            message = json.dumps(data)
            sock.sendto(message.encode(), (target_ip, target_port))

            # Sleep interval based on the slider value
            frequency = frequency_slider.get()
            time.sleep(1.0 / frequency)

    finally:
        sock.close()

def start_sending():
    global running
    running = True
    start_button.config(state="disabled")
    stop_button.config(state="normal")
    thread = threading.Thread(target=send_data)
    thread.daemon = True
    thread.start()

def stop_sending():
    global running
    running = False
    stop_button.config(state="disabled")
    start_button.config(state="normal")

def update_ui():
    # Assuming you have stored your labels in a list of lists or a similar structure
    for row_index, prop in enumerate(properties):
        keys = list(prop.keys())
        propertyName = keys[0]
        label_list[row_index][1].config(text=str(prop[propertyName]["x"]))  # Update X label
        label_list[row_index][2].config(text=str(prop[propertyName]["y"]))  # Update Y label
        label_list[row_index][3].config(text=str(prop[propertyName]["z"]))  # Update Z label
    # Update the samples per second display
    frequency = frequency_slider.get()
    time_label.config(text=f"Samples/Sec")

# Main UI setup
root = Tk()
root.title("UE Emulator")
root.minsize(300, 300)
titleLabel = Label(root, text="UE Emulator", font=('Helvetica', 20))
titleLabel.pack(pady=20)
titleLabel.pack(side="top", fill="both", expand=True)

#capture the time at start
start_time = time.time()
data = {
    "properties": [
        {
            "HeadPosition": {"x": 0, "y": 0, "z": 0}
        },
        {
            "HeadRotation": {"x": 0, "y": 0, "z": 0}
        }
    ]
}
data["properties"][0]["HeadPosition"]["x"] = round(100 * math.sin(20 * start_time),2)
data["properties"][0]["HeadPosition"]["y"] = round(100 * math.sin(21 * start_time),2)
data["properties"][0]["HeadPosition"]["z"] = round(100 * math.sin(19 * start_time),2)
data["properties"][1]["HeadRotation"]["x"] = round(360 * math.sin(10 * start_time),2)
data["properties"][1]["HeadRotation"]["y"] = round(360 * math.sin(11 * start_time),2)
data["properties"][1]["HeadRotation"]["z"] = round(360 * math.sin(9 * start_time),2)

#ui table
frame = Frame(root)
frame.pack(padx=10, pady=10)
# Extract data and create a table in the GUI
properties = data["properties"]


# Headers
headers = ["Property Name", "X", "Y", "Z"]
for i, header in enumerate(headers):
   Label(frame, text=header, font=('Helvetica', 10, 'bold'), borderwidth=0, relief='groove').grid(row=0, column=i)

label_list = []  # List to store label references for updating
for row_index, prop in enumerate(properties):
    row_labels = []
    keys = list(prop.keys())
    propertyName = keys[0]
    row_labels.append(Label(frame, text=propertyName, borderwidth=0, relief='groove'))
    row_labels[0].grid(row=row_index + 1, column=0)
    for i in range(3):
        lab = Label(frame, text=prop[propertyName][["x", "y", "z"][i]], borderwidth=0, relief='groove',width=12)
        lab.grid(row=row_index + 1, column=i+1)
        row_labels.append(lab)
    label_list.append(row_labels)

# Create a slider for controlling the frequency
frequency_slider = Scale(root, from_=1, to=100, orient=HORIZONTAL, label="Samples/Sec", length=300)
frequency_slider.set(18)  # Default frequency set to 10 samples per second
frequency_slider.pack(pady=10)

# Variables for IP and port
ip_var = StringVar(value="127.0.0.1")
port_var = StringVar(value="5006")

# Data UI display
time_label = Label(root, text="", font=("Helvetica", 8))  # Increased font size
time_label.pack(pady=50)
time_label.pack(padx=50)
time_label = Label(root, text=f"Samples/Sec", font=("Helvetica", 8))


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