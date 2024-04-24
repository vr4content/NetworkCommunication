import json
import math
import socket
import threading
from tkinter import Tk, Label, Button, Entry, StringVar, Frame


def receive_udp_data():
    global running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_data_rx_ip_var.get(), int(udp_data_rx_port_var.get())))

    try:
        while running:
            message, _ = sock.recvfrom(1024)
            data = json.loads(message.decode())

            # Update the UI
            update_ui_udp_data(data["properties"])

    finally:
        sock.close()

def click_on_start_receiving_udp_data():
    global running
    running = True
    udp_data_rx_start_button.config(state="disabled")
    udp_data_rx_stop_button.config(state="normal")
    thread = threading.Thread(target=receive_udp_data)
    thread.daemon = True
    thread.start()


def click_on_stop_receiving_udp_data():
    global running
    running = False
    udp_data_rx_stop_button.config(state="disabled")
    udp_data_rx_start_button.config(state="normal")


def update_ui_udp_data(properties):
    for row_index, prop in enumerate(properties):
        keys = list(prop.keys())
        propertyName = keys[0]
        udp_data_rx_label_list[row_index][1].config(text=str(prop[propertyName]["x"]))  # Update X label
        udp_data_rx_label_list[row_index][2].config(text=str(prop[propertyName]["y"]))  # Update Y label
        udp_data_rx_label_list[row_index][3].config(text=str(prop[propertyName]["z"]))  # Update Z label

# Main UI
root = Tk()
root.title("Multi Receiver")

# UDP DATA UI part
root.minsize(300, 300)
udp_data_rx_title_Label = Label(root, text="UDP Data Receiver", font=('Helvetica', 20))
udp_data_rx_title_Label.pack(pady=20)
udp_data_rx_title_Label.pack(side="top", fill="both", expand=True)

udp_data_rx_frame = Frame(root)
udp_data_rx_frame.pack(padx=10, pady=10)

udp_data_rx_headers = ["Property Name", "X", "Y", "Z"]
for i, header in enumerate(udp_data_rx_headers):
    Label(udp_data_rx_frame, text=header, font=('Helvetica', 10, 'bold'), borderwidth=0, relief='groove').grid(row=0, column=i)

udp_data_rx_label_list = []  # List to store label references for updating
udp_data_rx_properties = [{"HeadPosition": {"x": 0, "y": 0, "z": 0}}, {"HeadRotation": {"x": 0, "y": 0, "z": 0}}]
for row_index, prop in enumerate(udp_data_rx_properties):
    row_labels = []
    keys = list(prop.keys())
    propertyName = keys[0]
    row_labels.append(Label(udp_data_rx_frame, text=propertyName, borderwidth=0, relief='groove'))
    row_labels[0].grid(row=row_index + 1, column=0)
    for i in range(3):
        lab = Label(udp_data_rx_frame, text=prop[propertyName][["x", "y", "z"][i]], borderwidth=0, relief='groove', width=12)
        lab.grid(row=row_index + 1, column=i + 1)
        row_labels.append(lab)
    udp_data_rx_label_list.append(row_labels)

udp_data_rx_ip_var = StringVar(value="127.0.0.1")
udp_data_rx_port_var = StringVar(value="5006")

udp_data_rx_ip_frame = Frame(root)
udp_data_rx_ip_frame.pack(pady=10)

udp_data_rx_ip_entry = Entry(udp_data_rx_ip_frame, textvariable=udp_data_rx_ip_var, font=("Helvetica", 12), width=15)
udp_data_rx_ip_entry.pack(side="left", ipady=2)

udp_data_rx_port_entry = Entry(udp_data_rx_ip_frame, textvariable=udp_data_rx_port_var, font=("Helvetica", 12), width=8)
udp_data_rx_port_entry.pack(side="left", ipady=2)

udp_data_rx_button_frame = Frame(root)
udp_data_rx_button_frame.pack(pady=10)

udp_data_rx_start_button = Button(udp_data_rx_button_frame, text="Start", command=click_on_start_receiving_udp_data, state="normal")
udp_data_rx_start_button.pack(side="left", padx=5, ipady=20)  # Pack button on the left side of its frame

udp_data_rx_stop_button = Button(udp_data_rx_button_frame, text="Stop", command=click_on_stop_receiving_udp_data, state="disabled")
udp_data_rx_stop_button.pack(side="left", padx=5, ipady=20)  # Pack button on the left side of its frame

root.mainloop()


